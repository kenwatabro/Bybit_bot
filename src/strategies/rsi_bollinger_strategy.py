import asyncio
from datetime import datetime, timedelta
import pytz
from src.utils.logger import get_logger
from src.utils.indicators import calculate_rsi, calculate_bollinger_bands


class RSIBollingerStrategy:
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.logger = get_logger(__name__)
        self.position = None
        self.previous_kline_time = None
        self.testnet = config["testnet"]

    async def execute(self):
        while True:
            await self.wait_for_next_interval()
            await self.process_data()

    async def wait_for_next_interval(self):
        tokyo_tz = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tokyo_tz)
        next_interval = now.replace(
            minute=(now.minute // 5) * 5, second=0, microsecond=0
        ) + timedelta(minutes=5)
        wait_seconds = (next_interval - now).total_seconds()
        await asyncio.sleep(wait_seconds)

    async def process_data(self):
        try:
            symbol = self.config["pair"]
            klines_response = await self.api.get_klines(symbol, interval="5", limit=1)

            if (
                "result" not in klines_response
                or "list" not in klines_response["result"]
            ):
                self.logger.error(f"Unexpected API response format: {klines_response}")
                return

            klines = klines_response["result"]["list"]
            if not klines:
                self.logger.warning("No kline data received")
                return

            latest_kline = klines[-1]
            kline_time = latest_kline[0]  # Assuming timestamp is the first element
            if self.previous_kline_time == kline_time:
                self.logger.info("Already processed this kline")
                return
            self.previous_kline_time = kline_time

            close_price = float(latest_kline[4])  # Close price

            klines_response = await self.api.get_klines(
                symbol,
                interval="5",
                limit=self.config["rsi_period"] + self.config["bb_period"],
            )
            klines = klines_response["result"]["list"]
            close_prices = [
                float(k[4]) for k in klines if isinstance(k, list) and len(k) >= 5
            ]
            if len(close_prices) < max(
                self.config["rsi_period"], self.config["bb_period"]
            ):
                self.logger.warning("Not enough data to calculate indicators")
                return

            rsi = calculate_rsi(close_prices, period=self.config["rsi_period"])
            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
                close_prices,
                period=self.config["bb_period"],
                num_std_dev=self.config["bb_std_dev"],
            )

            current_rsi = rsi[-1]
            current_bb_upper = bb_upper[-1]
            current_bb_lower = bb_lower[-1]

            self.logger.info(
                f"Current RSI: {current_rsi:.2f}, Current price: {close_price:.2f}, Lower BB: {current_bb_lower:.2f}, Upper BB: {current_bb_upper:.2f}"
            )

            await self.trade_logic(
                close_price, current_rsi, current_bb_upper, current_bb_lower
            )

        except Exception as e:
            self.logger.error(f"Error in process_data: {e}", exc_info=True)

    async def trade_logic(self, price, rsi, bb_upper, bb_lower):
        if self.position is None:
            if rsi < self.config["rsi_oversold"] and price < bb_lower:
                await self.buy(price)
        elif self.position == "long":
            if rsi > self.config["rsi_overbought"] or price > bb_upper:
                await self.sell(price)

    async def buy(self, price):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                order = await self.api.place_order(
                    symbol=self.config["pair"], side="Buy", qty=self.config["amount"]
                )
                self.logger.info(f"Buy order placed at {price}: {order}")
                self.position = "long"
                break
            except Exception as e:
                self.logger.error(f"Error placing buy order (Attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(5)
                else:
                    self.logger.error("Failed to place buy order after multiple attempts.")

    async def sell(self, price):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                order = await self.api.place_order(
                    symbol=self.config["pair"], side="Sell", qty=self.config["amount"]
                )
                self.logger.info(f"Sell order placed at {price}: {order}")
                self.position = None
                break
            except Exception as e:
                self.logger.error(f"Error placing sell order (Attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(5)
                else:
                    self.logger.error("Failed to place sell order after multiple attempts.")
