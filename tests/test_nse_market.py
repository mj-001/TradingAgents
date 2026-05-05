import pytest
from datetime import time
from tradingagents.markets import (
    get_market_config,
    is_nse_ticker,
    to_yfinance_ticker,
    from_yfinance_ticker,
)
from tradingagents.dataflows.nse_utils import (
    normalize_nse_ticker,
    get_nse_instrument_context,
)
from tradingagents.agents.utils.agent_utils import build_instrument_context

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


@pytest.mark.unit
class TestAgentUtils:
    def test_build_instrument_context_nse_nr_ticker(self):
        ctx = build_instrument_context("SCOM.NR")
        assert "NSE" in ctx
        assert "KES" in ctx

    def test_build_instrument_context_bare_nse_symbol(self):
        # bare NSE known symbols should also get Kenya context
        ctx = build_instrument_context("EQTY")
        assert "NSE" in ctx

    def test_build_instrument_context_us_stock_no_nse(self):
        # US stocks must NOT contain NSE context
        ctx = build_instrument_context("NVDA")
        assert "NSE" not in ctx
        assert "NVDA" in ctx  # original ticker still in output

    def test_build_instrument_context_nse_contains_t3(self):
        ctx = build_instrument_context("KCB.NR")
        assert "T+3" in ctx

    def test_build_instrument_context_nse_contains_cma(self):
        ctx = build_instrument_context("KPLC.NR")
        assert "CMA" in ctx
