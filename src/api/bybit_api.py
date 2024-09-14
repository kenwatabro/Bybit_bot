from pybit.unified_trading import HTTP, WebSocket
import asyncio
from datetime import datetime
import pytz


def convert_utc_to_jst(utc_timestamp):
    utc_time = datetime.utcfromtimestamp(utc_timestamp / 1000)
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
    return jst_time


class BybitAPI:
    def __init__(self, api_key, api_secret, testnet):
        self.http = HTTP(testnet=testnet, api_key=api_key, api_secret=api_secret)
        self.ws = WebSocket(testnet=testnet, channel_type="spot")

    async def get_ticker(self, symbol):
        response = await asyncio.to_thread(
            self.http.get_tickers, category="spot", symbol=symbol
        )
        return response

    async def place_order(self, symbol, side, qty, order_type="Market"):
        return await asyncio.to_thread(
            self.http.place_order,
            category="spot",
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=qty,
        )

    async def get_klines(self, symbol, interval, limit):
        return await asyncio.to_thread(
            self.http.get_kline,
            category="spot",
            symbol=symbol,
            interval=interval,
            limit=limit,
        )

    async def close_session(self):
        if hasattr(self.http, "close"):
            await asyncio.to_thread(self.http.close)
