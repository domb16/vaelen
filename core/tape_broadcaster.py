import asyncio
from typing import Set
from fastapi import WebSocket

from models.trade_print import TradePrint


class TapeBroadcaster:
    """Manages active ws connections and broadcasts tape data"""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, trade: TradePrint) -> None:
        if not self.active_connections:
            return

        message = trade.model_dump_json()

        tasks = [connection.send_text(message) for connection in self.active_connections]
        await asyncio.gather(*tasks, return_exceptions=True)
