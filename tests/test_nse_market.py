import pytest
from tradingagents.markets import (
    get_market_config,
    is_nse_ticker,
    to_yfinance_ticker,
    from_yfinance_ticker,
)

@pytest.mark.unit
class TestNSEMarketConfig:
    def test_get_market_config_kenya(self):
        cfg = get_market_config("kenya")
        assert cfg["currency"] == "KES"
        assert cfg["timezone"] == "Africa/Nairobi"
        assert cfg["settlement_days"] == 3
        assert cfg["yfinance_suffix"] == ".NR"
        assert "SCOM" in cfg["tickers"]

    def test_get_market_config_unknown_returns_empty(self):
        assert get_market_config("mars") == {}

    def test_is_nse_ticker_with_nr_suffix(self):
        assert is_nse_ticker("SCOM.NR") is True

    def test_is_nse_ticker_bare_known_symbol(self):
        assert is_nse_ticker("EQTY") is True

    def test_is_nse_ticker_us_stock(self):
        assert is_nse_ticker("NVDA") is False

    def test_to_yfinance_ticker_bare(self):
        assert to_yfinance_ticker("SCOM") == "SCOM.NR"

    def test_to_yfinance_ticker_already_suffixed(self):
        assert to_yfinance_ticker("SCOM.NR") == "SCOM.NR"

    def test_to_yfinance_ticker_unknown_bare(self):
        assert to_yfinance_ticker("XYZ") == "XYZ.NR"

    def test_from_yfinance_ticker(self):
        assert from_yfinance_ticker("SCOM.NR") == "SCOM"
        assert from_yfinance_ticker("EQTY.NR") == "EQTY"
