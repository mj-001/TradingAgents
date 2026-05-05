# examples/kenya_nse_example.py
"""
Example: Analyse a Kenyan NSE stock with TradingAgents.
Requires: OPENAI_API_KEY (or other LLM API key) in .env
"""
import copy
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.markets import to_yfinance_ticker

load_dotenv()

config = copy.deepcopy(DEFAULT_CONFIG)
config["quick_think_llm"]  = "gpt-4o-mini"
config["deep_think_llm"]   = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["market"]   = "kenya"
config["exchange"] = "NSE"
config["currency"] = "KES"
config["data_vendors"] = dict(config.get("data_vendors", {}))
config["data_vendors"]["news_data"] = "kenyan_news"

ta = TradingAgentsGraph(debug=True, config=config)

# Analyse Safaricom (NSE: SCOM) — auto-expanded to SCOM.NR for Yahoo Finance
ticker = to_yfinance_ticker("SCOM")   # -> "SCOM.NR"
_, decision = ta.propagate(ticker, "2026-01-15")
print(decision)
