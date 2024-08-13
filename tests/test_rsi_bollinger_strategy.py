import pytest
import asyncio
import pytz

from unittest.mock import Mock, AsyncMock, patch
from src.strategies.rsi_bollinger_strategy import RSIBollingerStrategy


@pytest.fixture
def strategy():
    api_mock = Mock()
    config = {"pair": "BTCUSDT", "amount": 0.001, "rsi_period": 14}
    return RSIBollingerStrategy(api_mock, config)


@pytest.mark.asyncio
async def test_execute_buy_signal(strategy):
    strategy.api.get_klines = AsyncMock(return_value=[{"close": "100"} for _ in range(100)])
    strategy.api.place_order = AsyncMock(return_value={"orderId": "12345"})

    with patch(
        "src.strategies.rsi_bollinger_strategy.calculate_rsi", return_value=[29]
    ):
        with patch(
            "src.strategies.rsi_bollinger_strategy.calculate_bollinger_bands",
            return_value=([110], [105], [101]),
        ):
            await strategy.execute()
            strategy.api.place_order.assert_called_once_with(
                symbol="BTCUSDT", side="Buy", qty=0.001
            )


@pytest.mark.asyncio
async def test_execute_sell_signal(strategy):
    strategy.position = "long"
    strategy.api.get_klines = AsyncMock(return_value=[{"close": str(i)} for i in range(100)])
    strategy.api.place_order = AsyncMock(return_value={"orderId": "12345"})

    with patch(
        "src.strategies.rsi_bollinger_strategy.calculate_rsi", return_value=[71]
    ):
        with patch(
            "src.strategies.rsi_bollinger_strategy.calculate_bollinger_bands",
            return_value=([110], [100], [90]),
        ):
            await strategy.execute()
            strategy.api.place_order.assert_called_once_with(
                symbol="BTCUSDT", side="Sell", qty=0.001
            )

@pytest.mark.asyncio
async def test_execute_api_error(strategy):
    strategy.api.get_klines = AsyncMock(side_effect=Exception("API Error"))
    
    await strategy.execute()
    strategy.api.place_order.assert_not_called()

@pytest.mark.asyncio
async def test_execute_invalid_data(strategy):
    strategy.api.get_klines = AsyncMock(return_value=[{"close": "invalid"} for _ in range(100)])
    
    await strategy.execute()
    strategy.api.place_order.assert_not_called()

@pytest.mark.asyncio
async def test_execute_different_parameters(strategy):
    strategy.config["rsi_period"] = 7
    strategy.config["amount"] = 0.002
    strategy.api.get_klines = AsyncMock(return_value=[{"close": "100"} for _ in range(100)])
    strategy.api.place_order = AsyncMock(return_value={"orderId": "12345"})

    with patch("src.strategies.rsi_bollinger_strategy.calculate_rsi", return_value=[29]):
        with patch("src.strategies.rsi_bollinger_strategy.calculate_bollinger_bands", return_value=([110], [105], [101])):
            await strategy.execute()
            strategy.api.place_order.assert_called_once_with(
                symbol="BTCUSDT", side="Buy", qty=0.002
            )