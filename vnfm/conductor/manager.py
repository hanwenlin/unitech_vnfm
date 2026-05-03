import json
import logging
from typing import Dict, Any

from aio_pika import connect_robust, Message, ExchangeType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from vnfm.common.settings import settings
from vnfm.common.constants import TaskState, LcmOperationStatus
from vnfm.conductor.fsm import VnfFsm, FSMEvent
from vnfm.drivers.manager import vim_manager
from vnfm.db.session import AsyncSessionLocal
from vnfm.db.models import VnfInstance, LifecycleEvent, VnfResource

logger = logging.getLogger(__name__)


class ConductorManager:
    TASK_QUEUE = "vnfm.tasks"
    RESULT_EXCHANGE = "vnfm.results"

    def __init__(self):
        self.connection = None
        self.channel = None

    async def start(self):
        self.connection = await connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        await self.channel.declare_exchange(self.RESULT_EXCHANGE, ExchangeType.FANOUT)
        queue = await self.channel.declare_queue(self.TASK_QUEUE, durable=True)
        await queue.consume(self._on_message)
        logger.info("Conductor manager started, listening on %s", self.TASK_QUEUE)

    async def stop(self):
        if self.connection:
            await self.connection.close()

    async def _on_message(self, message):
        async with message.process():
            try:
                body = json.loads(message.body.decode())
                await self._process_task(body)
            except Exception as e:
                logger.exception("Failed to process task: %s", e)

    async def _process_task(self, task: Dict[str, Any]):
        vnf_id = task["vnf_instance_id"]
        operation = task["operation"]
        params = task.get("params", {})

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(VnfInstance)
                .where(VnfInstance.id == vnf_id)
                .options(selectinload(VnfInstance.vim))
            )
            instance = result.scalar_one_or_none()
            if not instance:
                logger.error("VNF instance not found: %s", vnf_id)
                return

            event = FSMEvent(operation)
            VnfFsm.transition(instance, event)
            await session.commit()
            await session.refresh(instance)

            lifecycle = LifecycleEvent(
                vnf_instance_id=vnf_id,
                operation=operation,
                operation_status=LcmOperationStatus.PROCESSING,
                user_id=task.get("user_id"),
                tenant_id=task.get("tenant_id"),
                params=params,
            )
            session.add(lifecycle)
            await session.commit()
            await session.refresh(lifecycle)

            try:
                vim_type = instance.vim.vim_type.value if instance.vim else "KUBERNETES"
                driver_method = VnfFsm.get_driver_method(event)
                if driver_method:
                    context = {"vim_auth": instance.vim, "session": session}
                    result_data = await vim_manager.call(vim_type, driver_method, context, instance, params)
                    logger.info("Driver result for %s: %s", vnf_id, result_data)

                VnfFsm.transition(instance, FSMEvent.COMPLETE)
                if operation in ("TERMINATE", "DELETE"):
                    instance.instantiation_state = "NOT_INSTANTIATED"
                elif operation == "INSTANTIATE":
                    instance.instantiation_state = "INSTANTIATED"

                lifecycle.operation_status = LcmOperationStatus.COMPLETED
                lifecycle.resource_changes = result_data if isinstance(result_data, dict) else {"result": str(result_data)}
            except Exception as e:
                logger.exception("LCM operation failed for %s", vnf_id)
                VnfFsm.transition(instance, FSMEvent.FAIL)
                lifecycle.operation_status = LcmOperationStatus.FAILED
                lifecycle.error = str(e)

            await session.commit()
            await self._publish_result(vnf_id, instance.task_state.value)

    async def _publish_result(self, vnf_id: str, state: str):
        exchange = await self.channel.get_exchange(self.RESULT_EXCHANGE)
        message = Message(
            json.dumps({"vnf_instance_id": vnf_id, "state": state}).encode(),
            content_type="application/json",
        )
        await exchange.publish(message, routing_key="")


conductor_manager = ConductorManager()
