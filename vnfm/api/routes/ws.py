import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from aio_pika import connect_robust, ExchangeType

from vnfm.common.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket):
    await manager.connect(websocket)
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
                    await websocket.send_json(body)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("WebSocket error: %s", e)
    finally:
        manager.disconnect(websocket)
        if connection:
            await connection.close()
