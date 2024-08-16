from pybit.unified_trading import HTTP
import asyncio
from datetime import datetime
import pytz

def convert_utc_to_jst(utc_timestamp):
    utc_time = datetime.utcfromtimestamp(utc_timestamp / 1000)  # ミリ秒を秒に変換
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    jst_time = utc_time.astimezone(pytz.timezone('Asia/Tokyo'))
    return jst_time

class BybitAPI:
    def __init__(self, api_key, api_secret):
        self.session = HTTP(testnet=True, api_key=api_key, api_secret=api_secret)

    async def get_ticker(self, symbol):
        response = await asyncio.to_thread(
            self.session.get_tickers, category="linear", symbol=symbol
        )
        print(f"API Response: {response}")  # Added
        if 'time' in response:
            print(f"API Response Time (UTC): {response['time']}")
        return response

    async def place_order(self, symbol, side, qty, order_type="Market"):
        return await asyncio.to_thread(
            self.session.place_order,
            category="linear",
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=qty,
        )

    # 他の必要なAPI呼び出しメソッドを追加
    async def get_klines(self, symbol, interval, limit):
        return await asyncio.to_thread(
            self.session.get_kline,
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=limit
        )
    
    async def close_session(self):
        if hasattr(self.session, 'close'):
            await asyncio.to_thread(self.session.close)