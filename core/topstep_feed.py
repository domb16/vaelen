import asyncio
import logging

import httpx
from datetime import datetime, timezone
from signalrcore.hub_connection_builder import HubConnectionBuilder

from models.trade_print import TradePrint

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger("SignalRCoreClient")
# logger.setLevel(logging.DEBUG)

class TopstepXFeed:

    def __init__(self, broadcaster, username: str, api_key: str, symbol: str = "CON.F.US.EP.U26") -> None:
        self.broadcaster = broadcaster
        self.username = username
        self.api_key = api_key
        self.symbol = symbol

        self.jwt_token: str = ""
        self.hub_connection = None
        self.running: bool = False

        self.main_loop: asyncio.AbstractEventLoop | None = None
        self._refresh_task: asyncio.Task | None = None

    async def authenticate(self) -> None:
        auth_url = "https://api.topstepx.com/api/Auth/loginKey"
        payload = {
            "userName": self.username,
            "apiKey": self.api_key
        }

        print(f"Authenticating ProjectX API for user {self.username}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(auth_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.jwt_token = data.get("token")
                    print("Successfully authenticated and received JWT.")
                else:
                    raise Exception(f"ProjectX Login Failed: {data.get('errorMessage')}")
            else:
                raise Exception(f"HTTP {response.status_code} on authentication.")

    async def _token_refresh_loop(self) -> None:
        validate_url = "https://api.topstepx.com/api/Auth/validate"

        while self.running:

            await asyncio.sleep(12 * 60 * 60)

            try:
                print("Refreshing ProjectX API Token...")
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                async with httpx.AsyncClient() as client:
                    response = await client.post(validate_url, headers=headers)
                    if response.status_code == 200 and response.json().get("success"):
                        # Update the token in memory
                        self.jwt_token = response.json().get("newToken")
                        print("ProjectX API Token successfully refreshed.")
            except Exception as e:
                print(f"Failed to refresh token: {e}")

    async def start(self) -> None:

        self.running = True

        self.main_loop = asyncio.get_running_loop()


        await self.authenticate()


        self._refresh_task = asyncio.create_task(self._token_refresh_loop())


        ws_url = "wss://rtc.topstepx.com/hubs/market"
        self.hub_connection = (HubConnectionBuilder().with_url(ws_url, options={
            "access_token_factory": lambda: self.jwt_token,
            "skip_negotiation": True
        })
                               # .configure_logging(logging.DEBUG)
                               .with_automatic_reconnect({
            "type": "raw",
            "keep_alive_interval": 10,
            "reconnect_interval": 5,
            "max_attempts": 5
        }).build())


        self.hub_connection.on("GatewayTrade", self._on_trade_received)
        self.hub_connection.on_open(lambda: print("TopstepX Market Hub connected."))
        self.hub_connection.on_error(lambda data: print(f"TopstepX Error: {data.error}"))
        self.hub_connection.on_close(lambda: print("TopstepX Connection closed."))


        self.hub_connection.start()


        await asyncio.sleep(1)
        self.hub_connection.send("SubscribeContractTrades", [self.symbol])
        print(f"Subscribed to Market Data for {self.symbol}")

    async def stop(self) -> None:
        self.running = False
        if self._refresh_task:
            self._refresh_task.cancel()

        if self.hub_connection:
            self.hub_connection.stop()
        print("TopstepX feed gracefully stopped.")

    def _on_trade_received(self, message: list) -> None:

        if not self.main_loop:
            return

        try:
            if len(message) < 2:
                return

            trade_batch = message[1]

            if isinstance(trade_batch, list):
                for data in trade_batch:
                    price = float(data.get("price", 0.0))

                    size = int(data.get("volume", 0))
                    type_raw = data.get("type", -1)
                    side = "neutral"
                    if type_raw == 0:
                        side = "buy"
                    elif type_raw == 1:
                        side = "sell"

                    timestamp_str = data.get("timestamp")
                    if timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamp_sec = dt.timestamp()
                    else:
                        timestamp_sec = datetime.now(timezone.utc).timestamp()

                    trade = TradePrint(
                        timestamp=timestamp_sec,
                        symbol=self.symbol,
                        price=price,
                        size=size,
                        side=side
                    )

                    asyncio.run_coroutine_threadsafe(
                        self.broadcaster.broadcast(trade),
                        self.main_loop
                    )

        except Exception as e:
            print(f"Error parsing TopstepX trade: {e} | Raw payload: {message}")