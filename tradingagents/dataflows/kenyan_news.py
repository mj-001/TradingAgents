"""
Kenyan financial news scraper for Business Daily Africa and Kenyan Wall Street.
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
    Accepts both bare NSE symbols (SCOM) and Yahoo Finance form (SCOM.NR).
    start_date / end_date match the standard get_news interface.
    Returns a formatted text block suitable for LLM consumption.
    """
    curr_date = end_date or start_date
    bare = from_yfinance_ticker(ticker) if ticker.upper().endswith(".NR") else ticker.upper()
    articles = _scrape_business_daily(bare) + _scrape_kenyan_wall_street(bare)

    if not articles:
        return (
            f"No recent Kenyan market news found for {bare} as of {curr_date}. "
            f"Consider checking businessdailyafrica.com and kenyanwallstreet.com manually."
        )

    lines = [f"Recent Kenyan market news for {bare} (as of {curr_date}):"]
    lines.append("")
    lines.append("| Source | Headline | Summary |")
    lines.append("|--------|----------|---------|")
    for a in articles[:15]:
        snippet = a["snippet"].replace("|", "-")
        title = a["title"].replace("|", "-")
        lines.append(f"| {a['source']} | {title} | {snippet} |")

    return "\n".join(lines)


def get_kenyan_global_news(curr_date: str) -> str:
    """
    Fetch East African macroeconomic and market-wide news.
    Returns formatted text for macro/global context in agent prompts.
    """
    sources = [
        ("Kenyan Wall Street – Economy", "https://kenyanwallstreet.com/category/economy/"),
        ("Kenyan Wall Street – Markets",  "https://kenyanwallstreet.com/category/nse/"),
    ]
    all_articles = []
    for label, url in sources:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            sel = Selector(text=resp.text)
            for item in sel.css("article, .post")[:7]:
                title = (item.css("h2 a::text, h3 a::text").get("") or "").strip()
                snippet = (item.css(".entry-summary p::text, p::text").get("") or "").strip()
                if title:
                    all_articles.append(f"- [{label}] {title}: {snippet[:150]}")
        except Exception:
            continue

    if not all_articles:
        return (
            f"East African macro news unavailable as of {curr_date}. "
            f"Key indicators to consider: CBK benchmark rate, KES/USD rate, NSE NASI index."
        )

    header = f"East African Macro & Market News (as of {curr_date}):"
    return header + "\n" + "\n".join(all_articles[:15])
