import json
import logging
from typing import Optional

from aio_pika import Message, connect_robust
from sqlalchemy.ext.asyncio import AsyncSession

from vnfm.common.decorators import check_vnf_state
from vnfm.common.constants import InstantiationState, TaskState
from vnfm.common.settings import settings
from vnfm.conductor.fsm import FSMEvent
from vnfm.db.models import VnfInstance

logger = logging.getLogger(__name__)


class VnfLcmManager:
    """API-layer lifecycle manager with pre-flight state validation."""

    async def _enqueue(
        self,
        vnf_id: str,
        operation: str,
        params: dict,
        user_id: str,
        tenant_id: Optional[str],
    ) -> None:
        connection = await connect_robust(settings.rabbitmq_url)
        try:
            channel = await connection.channel()
            message = Message(
                json.dumps({
                    "vnf_instance_id": vnf_id,
                    "operation": operation,
                    "params": params,
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                }).encode(),
                content_type="application/json",
                delivery_mode=2,
            )
            await channel.default_exchange.publish(
                message, routing_key="vnfm.tasks"
            )
        finally:
            await connection.close()

    @check_vnf_state(
        action="instantiate",
        instantiation_state=InstantiationState.NOT_INSTANTIATED,
        task_state=TaskState.PENDING,
    )
    async def instantiate(
        self,
        vnf_instance: VnfInstance,
        body,
        user_id: str,
        tenant_id: Optional[str],
    ) -> dict:
        await self._enqueue(
            vnf_instance.id,
            "INSTANTIATE",
            body.params,
            user_id,
            tenant_id,
        )
        return {
            "vnf_instance_id": vnf_instance.id,
            "operation": "INSTANTIATE",
            "status": "accepted",
        }

    @check_vnf_state(
        action="terminate",
        instantiation_state=InstantiationState.INSTANTIATED,
        task_state={TaskState.ACTIVE, TaskState.ERROR},
    )
    async def terminate(
        self,
        vnf_instance: VnfInstance,
        body,
        user_id: str,
        tenant_id: Optional[str],
    ) -> dict:
        await self._enqueue(
            vnf_instance.id,
            "TERMINATE",
            body.params,
            user_id,
            tenant_id,
        )
        return {
            "vnf_instance_id": vnf_instance.id,
            "operation": "TERMINATE",
            "status": "accepted",
        }

    @check_vnf_state(
        action="scale",
        instantiation_state=InstantiationState.INSTANTIATED,
        task_state=TaskState.ACTIVE,
    )
    async def scale(
        self,
        vnf_instance: VnfInstance,
        body,
        user_id: str,
        tenant_id: Optional[str],
    ) -> dict:
        scale_type = body.params.get("type", "scale_out")
        event = FSMEvent.SCALE_OUT if scale_type == "scale_out" else FSMEvent.SCALE_IN
        await self._enqueue(
            vnf_instance.id,
            event.value,
            body.params,
            user_id,
            tenant_id,
        )
        return {
            "vnf_instance_id": vnf_instance.id,
            "operation": event.value,
            "status": "accepted",
        }

    @check_vnf_state(
        action="update",
        instantiation_state=InstantiationState.INSTANTIATED,
        task_state={TaskState.ACTIVE, TaskState.ERROR},
    )
    async def update(
        self,
        vnf_instance: VnfInstance,
        body,
        user_id: str,
        tenant_id: Optional[str],
    ) -> dict:
        await self._enqueue(
            vnf_instance.id,
            "UPDATE",
            body.params,
            user_id,
            tenant_id,
        )
        return {
            "vnf_instance_id": vnf_instance.id,
            "operation": "UPDATE",
            "status": "accepted",
        }

    @check_vnf_state(
        action="delete",
        instantiation_state=InstantiationState.NOT_INSTANTIATED,
        task_state={TaskState.PENDING, TaskState.ERROR},
    )
    async def delete(
        self,
        vnf_instance: VnfInstance,
        db: AsyncSession,
    ) -> None:
        await db.delete(vnf_instance)
        await db.commit()


vnf_lcm_manager = VnfLcmManager()
