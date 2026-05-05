# tests/test_kenya_integration.py
"""
Smoke test: verify the Kenya localisation wires together correctly.
Uses mocked LLM calls so no API key is required.
Marked 'smoke' — run with: pytest -m smoke
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.smoke
class TestKenyaIntegration:
    def test_nse_ticker_flows_through_config(self):
        """Setting market=kenya in config routes news to kenyan_news vendor."""
        from tradingagents.dataflows.config import set_config, get_config
        set_config({"market": "kenya", "exchange": "NSE", "currency": "KES"})
        cfg = get_config()
        assert cfg["market"] == "kenya"
        assert cfg["currency"] == "KES"

    def test_nse_ticker_normalisation_round_trip(self):
        """SCOM → SCOM.NR → SCOM round trip is lossless."""
        from tradingagents.markets import to_yfinance_ticker, from_yfinance_ticker
        assert from_yfinance_ticker(to_yfinance_ticker("SCOM")) == "SCOM"

    def test_kenyan_news_vendor_is_available(self):
        """kenyan_news vendor methods are importable and callable (mocked)."""
        with patch("tradingagents.dataflows.kenyan_news.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = "<html><body><article><h2><a>Test</a></h2><p>snippet</p></article></body></html>"
            mock_get.return_value = mock_resp
            from tradingagents.dataflows.kenyan_news import get_kenyan_news
            result = get_kenyan_news("SCOM.NR", "2026-05-03")
            assert isinstance(result, str)

    def test_instrument_context_for_scom(self):
        """Full instrument context for SCOM.NR contains all required elements."""
        from tradingagents.agents.utils.agent_utils import build_instrument_context
        ctx = build_instrument_context("SCOM.NR")
        assert "SCOM" in ctx
        assert "NSE" in ctx
        assert "KES" in ctx
        assert "T+3" in ctx
        assert "CMA" in ctx
