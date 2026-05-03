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
        # Verify correct NSE trading hours
        from datetime import time
        assert cfg["trading_hours"]["open"] == time(9, 0)
        assert cfg["trading_hours"]["close"] == time(15, 0)

    def test_get_market_config_unknown_returns_empty(self):
        assert get_market_config("mars") == {}

    def test_is_nse_ticker_with_nr_suffix(self):
        assert is_nse_ticker("SCOM.NR") is True

    def test_is_nse_ticker_bare_known_symbol(self):
        assert is_nse_ticker("EQTY") is True

    def test_is_nse_ticker_us_stock(self):
        assert is_nse_ticker("NVDA") is False

    def test_is_nse_ticker_rejects_bare_suffix(self):
        assert is_nse_ticker(".NR") is False

    def test_to_yfinance_ticker_bare(self):
        assert to_yfinance_ticker("SCOM") == "SCOM.NR"

    def test_to_yfinance_ticker_already_suffixed(self):
        assert to_yfinance_ticker("SCOM.NR") == "SCOM.NR"

    def test_to_yfinance_ticker_unknown_bare(self):
        assert to_yfinance_ticker("XYZ") == "XYZ.NR"

    def test_from_yfinance_ticker(self):
        assert from_yfinance_ticker("SCOM.NR") == "SCOM"
        assert from_yfinance_ticker("EQTY.NR") == "EQTY"


from tradingagents.dataflows.nse_utils import (
    normalize_nse_ticker,
    get_nse_instrument_context,
)

@pytest.mark.unit
class TestNSEDataUtils:
    def test_normalize_bare_known_symbol(self):
        assert normalize_nse_ticker("SCOM") == "SCOM.NR"

    def test_normalize_already_suffixed(self):
        assert normalize_nse_ticker("KCB.NR") == "KCB.NR"

    def test_normalize_non_nse_passthrough(self):
        assert normalize_nse_ticker("NVDA") == "NVDA"

    def test_instrument_context_contains_kes(self):
        ctx = get_nse_instrument_context("SCOM.NR")
        assert "KES" in ctx
        assert "NSE" in ctx
        assert "EAT" in ctx or "UTC+3" in ctx

    def test_instrument_context_contains_bare_symbol(self):
        ctx = get_nse_instrument_context("EQTY.NR")
        assert "EQTY" in ctx
