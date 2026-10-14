from pydantic import BaseModel


class TradePrint(BaseModel):
    timestamp: float
    symbol: str
    price: float
    size: int
    side: str


