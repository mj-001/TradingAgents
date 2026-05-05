"""
NSE ticker normalisation and instrument context helpers.
Used by the data layer and agent prompts to handle Kenyan market stocks.
"""
from tradingagents.markets import (
    is_nse_ticker,
    to_yfinance_ticker,
    from_yfinance_ticker,
    get_nse_config,
)


def normalize_nse_ticker(ticker: str) -> str:
    """
    Return Yahoo Finance-ready ticker string.
    NSE tickers (bare known symbols or .NR-suffixed) get the .NR suffix added/preserved.
    Non-NSE tickers pass through unchanged.
    """
    if is_nse_ticker(ticker):
        return to_yfinance_ticker(ticker)
    return ticker


def get_nse_instrument_context(ticker: str) -> str:
    """
    Return a Kenyan market context string for injection into agent system prompts.
    Works for both bare NSE symbols (SCOM) and Yahoo Finance form (SCOM.NR).
    """
    cfg = get_nse_config()
    bare = from_yfinance_ticker(ticker)
    return (
        f"Stock: {bare} listed on the Nairobi Securities Exchange (NSE), Kenya. "
        f"Currency: {cfg['currency']} ({cfg['currency_symbol']} — Kenyan Shilling). "
        f"Trading hours: 9:00 AM – 3:00 PM EAT (UTC+3, Africa/Nairobi — no DST). "
        f"Settlement cycle: T+{cfg['settlement_days']} business days. "
        f"Market segments: {', '.join(cfg['segments'])}. "
        f"Regulated by the {cfg['regulatory_body']}. "
        f"Analyse in the context of the East African economic environment, "
        f"Kenyan macroeconomic indicators (inflation, CBK interest rate, KES/USD), "
        f"and regional political/regulatory developments."
    )
