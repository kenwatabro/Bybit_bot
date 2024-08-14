import asyncio
import pytz
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.indicators import calculate_rsi, calculate_bollinger_bands

class RSIBollingerStrategy:
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.logger = get_logger(__name__)
        self.position = None

    async def execute(self):
        while True:
            await self.wait_for_next_interval()
            await self.process_data()

    async def wait_for_next_interval(self):
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(jst)
        next_interval = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0) + timedelta(minutes=5)
        wait_seconds = (next_interval - now).total_seconds()
        await asyncio.sleep(wait_seconds)

    async def process_data(self):
        try:
            symbol = self.config["pair"]
            klines_response = await self.api.get_klines(symbol, interval="5", limit=100)

            if 'result' not in klines_response or 'list' not in klines_response['result']:
                self.logger.error(f"Unexpected API response format: {klines_response}")
                return

            klines = klines_response['result']['list']
            close_prices = []
            for k in klines:
                if isinstance(k, list) and len(k) >= 5:
                    try:
                        close_prices.append(float(k[4]))  # Assuming close price is at index 4
                    except ValueError:
                        self.logger.warning(f"Invalid close price data: {k[4]}")
                else:
                    self.logger.warning(f"Invalid kline data format: {k}")

        except Exception as e:
            self.logger.error(f"API error occurred: {e}")
            return

        if len(close_prices) < 2:
            self.logger.warning("Not enough valid price data to calculate indicators")
            return

        rsi = calculate_rsi(close_prices, period=14)
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
            close_prices, period=20, num_std_dev=2
        )

        current_price = close_prices[-1]

        if self.position is None:
            if rsi[-1] < 35 and current_price < bb_lower[-1]:
                try:
                    order = await self.api.place_order(
                        symbol=symbol, side="Buy", qty=self.config["amount"]
                    )
                    self.logger.info(f"Buy order placed: {order}")
                    self.position = "long"
                except Exception as e:
                    self.logger.error(f"Error placing buy order: {e}")
        elif self.position == "long":
            if bb_upper[-1] < current_price:
                try:
                    order = await self.api.place_order(
                        symbol=symbol, side="Sell", qty=self.config["amount"]
                    )
                    self.logger.info(f"Sell order placed: {order}")
                    self.position = None
                except Exception as e:
                    self.logger.error(f"Error placing sell order: {e}")

        self.logger.info(
            f"Current RSI: {rsi[-1]:.2f}, Current price: {current_price:.2f}, Lower BB: {bb_lower[-1]:.2f}, Upper BB: {bb_upper[-1]:.2f}"
        )
