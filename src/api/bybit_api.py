from pybit.unified_trading import HTTP
import asyncio


class BybitAPI:
    def __init__(self, api_key, api_secret):
        self.session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)

    async def get_ticker(self, symbol):
        return await asyncio.to_thread(
            self.session.get_tickers, category="linear", symbol=symbol
        )

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