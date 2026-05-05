import json
import logging
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from aio_pika import connect_robust, ExchangeType

from vnfm.api.auth.security import decode_token
from vnfm.common.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    def add(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    def remove(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)


manager = ConnectionManager()


def _authenticate(token: Optional[str]) -> Optional[dict]:
    if not token:
        return None
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return None
    return payload


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
):
    payload = _authenticate(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_tenant = payload.get("tenant_id")
    user_role = payload.get("role", "user")
    is_admin = user_role == "admin"

    await websocket.accept()
    manager.add(websocket)
    connection = None
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        exchange = await channel.declare_exchange("vnfm.results", ExchangeType.FANOUT)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key="")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = json.loads(message.body.decode())
                    msg_tenant = body.get("tenant_id")
                    if not is_admin and msg_tenant and msg_tenant != user_tenant:
                        continue
                    await websocket.send_json(body)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("WebSocket error: %s", e)
    finally:
        manager.remove(websocket)
        if connection:
            await connection.close()
