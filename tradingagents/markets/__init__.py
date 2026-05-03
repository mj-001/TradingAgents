from .kenya import NSE_CONFIG, get_nse_config

_REGISTRY: dict[str, dict] = {
    "kenya": NSE_CONFIG,
    "nse":   NSE_CONFIG,
}


def get_market_config(market: str) -> dict:
    """Return market config dict for a named market, or {} if unknown."""
    return _REGISTRY.get(market.lower(), {}).copy()


def is_nse_ticker(ticker: str) -> bool:
    """True if ticker is an NSE-listed symbol (bare or with .NR suffix)."""
    t = ticker.upper().strip()
    return t.endswith(".NR") or t in NSE_CONFIG["tickers"]


def to_yfinance_ticker(nse_symbol: str) -> str:
    """Map bare NSE symbol or .NR ticker to Yahoo Finance format."""
    s = nse_symbol.upper().strip()
    if s.endswith(".NR"):
        return s
    return NSE_CONFIG["tickers"].get(s, f"{s}.NR")


def from_yfinance_ticker(yf_ticker: str) -> str:
    """Strip .NR suffix to get the bare NSE symbol."""
    return yf_ticker.upper().strip().removesuffix(".NR")
