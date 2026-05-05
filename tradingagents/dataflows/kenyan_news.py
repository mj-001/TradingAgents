"""
Kenyan financial news scraper for Business Daily Africa, Kenyan Wall Street,
and official NSE company announcements (via NSE WordPress REST API).
Used as the 'kenyan_news' data vendor when market=kenya.
"""
import requests
from parsel import Selector
from urllib.parse import quote
from tradingagents.markets import from_yfinance_ticker

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
_TIMEOUT = 10

# Map bare NSE ticker -> company name for NSE API search
_TICKER_TO_COMPANY = {
    "SCOM":  "Safaricom",
    "EQTY":  "Equity",
    "KCB":   "KCB",
    "SBIC":  "Stanbic",
    "COOP":  "Co-operative Bank",
    "NCBA":  "NCBA",
    "IMH":   "I&M",
    "DTK":   "Diamond Trust",
    "ABSA":  "Absa",
    "SCBK":  "Standard Chartered",
    "HFCK":  "HF Group",
    "EABL":  "East African Breweries",
    "BAT":   "British American Tobacco",
    "KPLC":  "Kenya Power",
    "KEGN":  "KenGen",
    "TOTL":  "Total Kenya",
    "KQ":    "Kenya Airways",
    "NMG":   "Nation Media",
    "CTUM":  "Centum",
    "BAMB":  "Bamburi",
    "JUBI":  "Jubilee",
    "BRIT":  "Britam",
    "CIC":   "CIC Insurance",
    "UNGA":  "Unga",
    "KUKZ":  "Kakuzi",
    "SASN":  "Sasini",
    "KNRE":  "Kenya Re",
    "CABL":  "East African Cables",
    "CRWN":  "Crown Paints",
}

_NSE_API = "https://www.nse.co.ke/wp-json/wp/v2/media"


def _fetch_nse_announcements(bare_ticker: str) -> list[dict]:
    """
    Fetch official company announcements from the NSE WordPress REST API.
    Returns a list of dicts with title, date, url, source keys.
    """
    company = _TICKER_TO_COMPANY.get(bare_ticker.upper(), bare_ticker)
    try:
        resp = requests.get(
            _NSE_API,
            params={
                "mime_type": "application/pdf",
                "orderby": "date",
                "order": "desc",
                "per_page": 20,
                "search": company,
                "_fields": "id,date,title,source_url",
            },
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json()
        results = []
        for item in items:
            title = item.get("title", {}).get("rendered", "").strip()
            date = item.get("date", "")[:10]  # YYYY-MM-DD
            pdf_url = item.get("source_url", "")
            if title:
                results.append({
                    "title": title,
                    "snippet": f"Official NSE filing ({date}) — PDF: {pdf_url}",
                    "source": "NSE Official",
                })
        return results
    except Exception:
        return []


def _scrape_business_daily(bare_ticker: str) -> list[dict]:
    """Scrape Business Daily Africa search results for a ticker."""
    url = f"https://www.businessdailyafrica.com/search?q={quote(bare_ticker)}"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        sel = Selector(text=resp.text)
        articles = []
        for item in sel.css("article, .article-item, .search-result, .post")[:10]:
            title = (
                item.css("h2 a::text, h3 a::text, .headline::text").get("") or ""
            ).strip()
            snippet = (
                item.css("p::text, .summary::text, .excerpt::text").get("") or ""
            ).strip()
            if title:
                articles.append({
                    "title": title,
                    "snippet": snippet[:200],
                    "source": "Business Daily Africa",
                })
        return articles
    except Exception:
        return []


def _scrape_kenyan_wall_street(bare_ticker: str) -> list[dict]:
    """Scrape Kenyan Wall Street search results for a ticker."""
    url = f"https://kenyanwallstreet.com/?s={quote(bare_ticker)}"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        sel = Selector(text=resp.text)
        articles = []
        for item in sel.css("article, .post")[:10]:
            title = (
                item.css("h2 a::text, h3 a::text").get("") or ""
            ).strip()
            snippet = (
                item.css(".entry-summary p::text, p::text").get("") or ""
            ).strip()
            if title:
                articles.append({
                    "title": title,
                    "snippet": snippet[:200],
                    "source": "Kenyan Wall Street",
                })
        return articles
    except Exception:
        return []


def get_kenyan_news(ticker: str, start_date: str, end_date: str = None) -> str:
    """
    Fetch recent Kenyan financial news for a stock ticker.
    Pulls from three sources:
      1. NSE Official announcements (WordPress REST API — PDFs/filings)
      2. Business Daily Africa (news articles)
      3. Kenyan Wall Street (news articles)
    Accepts both bare NSE symbols (SCOM) and Yahoo Finance form (SCOM.NR).
    start_date / end_date match the standard get_news interface.
    Returns a formatted text block suitable for LLM consumption.
    """
    curr_date = end_date or start_date
    bare = from_yfinance_ticker(ticker) if ticker.upper().endswith(".NR") else ticker.upper()

    nse_items = _fetch_nse_announcements(bare)
    news_items = _scrape_business_daily(bare) + _scrape_kenyan_wall_street(bare)
    all_articles = nse_items + news_items

    if not all_articles:
        return (
            f"No recent Kenyan market news found for {bare} as of {curr_date}. "
            f"Consider checking nse.co.ke, businessdailyafrica.com and kenyanwallstreet.com manually."
        )

    lines = [f"Recent Kenyan market news & official NSE filings for {bare} (as of {curr_date}):"]
    lines.append("")
    lines.append("| Source | Headline | Detail |")
    lines.append("|--------|----------|--------|")
    for a in all_articles[:20]:
        snippet = a["snippet"].replace("|", "-")
        title = a["title"].replace("|", "-")
        lines.append(f"| {a['source']} | {title} | {snippet} |")

    return "\n".join(lines)


def get_kenyan_global_news(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """
    Fetch East African macroeconomic and market-wide news.
    Pulls from Kenyan Wall Street and NSE press releases.
    Returns formatted text for macro/global context in agent prompts.
    """
    # NSE press releases (market-wide, not company-specific)
    nse_items = []
    try:
        resp = requests.get(
            _NSE_API,
            params={
                "mime_type": "application/pdf",
                "orderby": "date",
                "order": "desc",
                "per_page": 10,
                "_fields": "date,title,source_url",
            },
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        for item in resp.json():
            title = item.get("title", {}).get("rendered", "").strip()
            date = item.get("date", "")[:10]
            if title:
                nse_items.append(f"- [NSE Official] {title} ({date})")
    except Exception:
        pass

    # Kenyan Wall Street macro categories
    sources = [
        ("Kenyan Wall Street – Economy", "https://kenyanwallstreet.com/category/economy/"),
        ("Kenyan Wall Street – Markets",  "https://kenyanwallstreet.com/category/nse/"),
    ]
    kws_items = []
    for label, url in sources:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            sel = Selector(text=resp.text)
            for item in sel.css("article, .post")[:7]:
                title = (item.css("h2 a::text, h3 a::text").get("") or "").strip()
                snippet = (item.css(".entry-summary p::text, p::text").get("") or "").strip()
                if title:
                    kws_items.append(f"- [{label}] {title}: {snippet[:150]}")
        except Exception:
            continue

    all_items = nse_items + kws_items

    if not all_items:
        return (
            f"East African macro news unavailable as of {curr_date}. "
            f"Key indicators to consider: CBK benchmark rate, KES/USD rate, NSE NASI index."
        )

    header = f"East African Macro & Market News + NSE Filings (as of {curr_date}):"
    return header + "\n" + "\n".join(all_items[:20])
