import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestKenyanNews:
    def _mock_response(self, html: str):
        mock = MagicMock()
        mock.text = html
        mock.raise_for_status = MagicMock()
        return mock

    @patch("tradingagents.dataflows.kenyan_news.requests.get")
    def test_get_kenyan_news_returns_string(self, mock_get):
        html = """
        <article>
          <h2><a href="/story">Safaricom posts record profits</a></h2>
          <p>Revenue grew 15% year-on-year...</p>
        </article>
        """
        mock_get.return_value = self._mock_response(html)
        from tradingagents.dataflows.kenyan_news import get_kenyan_news
        result = get_kenyan_news("SCOM.NR", "2026-05-03")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("tradingagents.dataflows.kenyan_news.requests.get")
    def test_get_kenyan_news_contains_ticker_bare(self, mock_get):
        html = "<article><h2><a>KCB raises dividend</a></h2><p>Solid Q1</p></article>"
        mock_get.return_value = self._mock_response(html)
        from tradingagents.dataflows.kenyan_news import get_kenyan_news
        result = get_kenyan_news("KCB.NR", "2026-05-03")
        assert "KCB" in result

    @patch("tradingagents.dataflows.kenyan_news.requests.get",
           side_effect=Exception("timeout"))
    def test_get_kenyan_news_handles_network_error(self, mock_get):
        from tradingagents.dataflows.kenyan_news import get_kenyan_news
        result = get_kenyan_news("EQTY.NR", "2026-05-03")
        assert isinstance(result, str)  # graceful degradation
        assert len(result) > 0          # fallback message is non-empty

    @patch("tradingagents.dataflows.kenyan_news.requests.get")
    def test_get_kenyan_global_news_returns_string(self, mock_get):
        html = "<article><h2><a>CBK holds rates at 13%</a></h2><p>Inflation steady</p></article>"
        mock_get.return_value = self._mock_response(html)
        from tradingagents.dataflows.kenyan_news import get_kenyan_global_news
        result = get_kenyan_global_news("2026-05-03")
        assert isinstance(result, str)
        assert len(result) > 0
