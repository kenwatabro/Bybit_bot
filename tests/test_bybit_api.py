import pytest
import asyncio
from unittest.mock import Mock, patch
from src.api.bybit_api import BybitAPI

@pytest.fixture
def api():
    return BybitAPI("test_api_key", "test_api_secret", testnet=True)

@pytest.mark.asyncio
async def test_get_ticker(api):
    with patch.object(api.session, 'get_tickers') as mock_get_tickers:
        mock_get_tickers.return_value = {"result": {"list": [{"lastPrice": "50000"}]}}
        result = await api.get_ticker("BTCUSDT")
        assert result["result"]["list"][0]["lastPrice"] == "50000"

@pytest.mark.asyncio
async def test_place_order(api):
    with patch.object(api.session, 'place_order') as mock_place_order:
        mock_place_order.return_value = {"orderId": "12345"}
        result = await api.place_order("BTCUSDT", "Buy", 0.001)
        assert result["orderId"] == "12345"
