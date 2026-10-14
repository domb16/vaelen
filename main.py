import asyncio
import logging
import time
import httpx
import uvicorn
from async_rithmic import RithmicClient
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from core import auth
from core.tape_broadcaster import TapeBroadcaster
from contextlib import asynccontextmanager

from core.topstep_feed import TopstepXFeed
from dotenv import dotenv_values

logging.getLogger("rithmic").setLevel(logging.DEBUG)

class TradingJournalApp:
    config = dotenv_values(".env")
    def __init__(self) -> None:
        self.broadcaster = TapeBroadcaster()
        self.feed = TopstepXFeed(broadcaster=self.broadcaster,
                                 username=self.config["USERNAME"],
                                 api_key=self.config["PROJECTX_API"],
                                 symbol="CON.F.US.EP.U26")

        self.app = FastAPI(title="Pro Trading Journal Tape", lifespan=self.lifespan)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.include_router(auth.router)
        self.app.include_router(self.app.router, dependencies=[Depends(auth.current_user)])

        self.http_client = httpx.AsyncClient(timeout=5.0)

        self.macro_cache = {
            "data": None,
            "last_fetched": 0
        }
        self.CACHE_TTL = 3600  # 1 hour in seconds

        self.active_ws_clients = []
        self.rithmic_un = self.config["RITHMIC_UN"]
        self.rithmic_pass = self.config["RITHMIC_PASS"]
        self.rithmic_sys = self.config["RITHMIC_SYS"]
        self.rithmic_url = self.config["RITHMIC_URL"]

        self._setup_routes()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        await self.feed.start()
        # background task start

        yield

        await self.http_client.aclose()
        await self.feed.stop()

    # async def rithmic_worker(self):
    #     client = RithmicClient(
    #         user=self.rithmic_un,
    #         password=self.rithmic_pass,
    #         system_name=self.rithmic_sys,
    #         app_name="ES Dashboard",
    #         app_version="0.0.1",
    #         url=self.rithmic_url
    #     )
    #     # Only need to login to the order plant of Rithmic Test, and leave the app logged in.
    #     order_plant = client.plants["order"]
    #
    #     try:
    #         await order_plant._connect()
    #         await order_plant._start_background_tasks()
    #         await order_plant._login()
    #         print("Logged in successfully. Press CTRL+C to exit")
    #
    #         print("Sleeping ...")
    #         await asyncio.sleep(3600)
    #
    #     except Exception as e:
    #         print(f"Main exception: {e!r}")
    #
    #     finally:
    #         await order_plant._stop_background_tasks()
    #         #     await client.connect()
    #         #     print("Connected to Rithmic CME Gateway.")
    #         #
    #         #
    #         # except asyncio.CancelledError as e:
    #         #     print("Shutting down...")
    #         #     break
    #         # except Exception as e:
    #         #     print(f"Rithmic Worker disconnected...{e}. Reconnecting in 5 seconds...")
    #         #     await asyncio.sleep(5)

    def _setup_routes(self) -> None:

        @self.app.get("/news")
        async def get_market_news():
            if not self.config['FINNHUB_API']:
                raise HTTPException(status_code=500, detail="API key missing")

            url = f"https://finnhub.io/api/v1/news?category=general&token={self.config['FINNHUB_API']}"

            response = await self.http_client.get(url)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch news")

            return response.json()[:25]

        @self.app.get("/macro")
        async def get_macro_calendar():
            current_time = time.time()

            if self.macro_cache["data"] and (current_time - self.macro_cache["last_fetched"] < self.CACHE_TTL):
                return self.macro_cache["data"]


            url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            try:
                response = await self.http_client.get(url)
                response.raise_for_status()
                events = response.json()

                usd_events = [
                    e for e in events
                    if e.get("country") == "USD"
                       and e.get("impact") in ["High", "Medium"]
                ]


                self.macro_cache["data"] = usd_events
                self.macro_cache["last_fetched"] = current_time

                return usd_events

            except Exception as e:
                if self.macro_cache["data"]:
                    return self.macro_cache["data"]
                return {"error": "Failed to fetch macro data"}


        @self.app.websocket("/ws/tape")
        async def websocket_tape(websocket: WebSocket) -> None:
            await self.broadcaster.connect(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.broadcaster.disconnect(websocket)

journal_system = TradingJournalApp()
app = journal_system.app

if __name__ == "__main__":
    # asyncio.run(journal_system.rithmic_worker())
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, loop="auto")
    except KeyboardInterrupt:
        print("Shutting down...")