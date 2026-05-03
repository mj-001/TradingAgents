import copy
from datetime import time

NSE_CONFIG = {
    "exchange": "NSE",
    "country": "Kenya",
    "currency": "KES",
    "currency_symbol": "KSh",
    "timezone": "Africa/Nairobi",  # UTC+3, no DST
    "trading_hours": {
        "open": time(9, 0),   # was time(9, 31) — that's NYSE, not NSE
        "close": time(15, 0),
    },
    "settlement_days": 3,  # T+3
    "yfinance_suffix": ".NR",
    "segments": ["MIMS", "AIMS", "GEMS", "Fixed Income"],
    "index": "NASI",
    "regulatory_body": "Capital Markets Authority (CMA) Kenya",
    "regulatory_url": "https://www.cma.or.ke",
    "tickers": {
        "SCOM":  "SCOM.NR",
        "EQTY":  "EQTY.NR",
        "KCB":   "KCB.NR",
        "SBIC":  "SBIC.NR",
        "COOP":  "COOP.NR",
        "NCBA":  "NCBA.NR",
        "IMH":   "IMH.NR",
        "DTK":   "DTK.NR",
        "ABSA":  "ABSA.NR",
        "SCBK":  "SCBK.NR",
        "HFCK":  "HFCK.NR",
        "EABL":  "EABL.NR",
        "BAT":   "BAT.NR",
        "KPLC":  "KPLC.NR",
        "KEGN":  "KEGN.NR",
        "TOTL":  "TOTL.NR",
        "KQ":    "KQ.NR",
        "NMG":   "NMG.NR",
        "CTUM":  "CTUM.NR",
        "BAMB":  "BAMB.NR",
        "JUBI":  "JUBI.NR",
        "BRIT":  "BRIT.NR",
        "CIC":   "CIC.NR",
        "UNGA":  "UNGA.NR",
        "KUKZ":  "KUKZ.NR",
        "SASN":  "SASN.NR",
        "KNRE":  "KNRE.NR",
        "CABL":  "CABL.NR",
        "CRWN":  "CRWN.NR",
    },
    "news_sources": [
        "https://www.businessdailyafrica.com",
        "https://kenyanwallstreet.com",
    ],
}


def get_nse_config() -> dict:
    """Return a deep copy of the NSE market configuration."""
    return copy.deepcopy(NSE_CONFIG)
