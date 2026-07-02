import os

# =========================
# Folder settings
# =========================

RESULTS_DIR = "results"

DATA_FILE = os.path.join(RESULTS_DIR, "data.csv")
TRADES_FILE = os.path.join(RESULTS_DIR, "trades.csv")
REPORT_FILE = os.path.join(RESULTS_DIR, "report.txt")
CHART_FILE = os.path.join(RESULTS_DIR, "backtest_chart.png")
COMPARISON_FILE = os.path.join(RESULTS_DIR, "strategy_comparison.csv")
OPTIMIZATION_FILE = os.path.join(RESULTS_DIR, "optimization_results.csv")
MULTI_PAIR_FILE = os.path.join(RESULTS_DIR, "multi_pair_results.csv")
WALK_FORWARD_FILE = os.path.join(RESULTS_DIR, "walk_forward_results.csv")
READINESS_FILE = os.path.join(RESULTS_DIR, "readiness_report.txt")
SIGNAL_FILE = os.path.join(RESULTS_DIR, "latest_signal.txt")
SIGNAL_HISTORY_FILE = os.path.join(RESULTS_DIR, "signal_history.csv")
MT5_ORDER_PREVIEW_FILE = os.path.join(RESULTS_DIR, "mt5_order_preview.txt")

# =========================
# MetaTrader 5 settings
# =========================

MT5_ENABLED = False
MT5_ALLOW_TRADING = False

# Broker symbols may be different.
# Examples: "EURUSD", "EURUSDm", "EURUSD.a"
MT5_SYMBOL = "XAUUSDm"

MT5_TIMEFRAME = "M15"
MT5_CANDLES = 300
MT5_LIVE_DATA_FILE = os.path.join(RESULTS_DIR, "mt5_live_data.csv")

MT5_DEVIATION = 20
MT5_MAGIC_NUMBER = 202606

# =========================
# Signal data source
# =========================

SIGNAL_DATA_SOURCE = "MT5"
# Options:
# "YAHOO" = use results/data.csv
# "MT5" = use results/mt5_live_data.csv

# =========================
# Market data settings
# =========================

SYMBOL = "EURUSD=X"
PERIOD = "60d"
INTERVAL = "15m"

PAIRS_TO_TEST = [
    {"name": "EUR/USD", "symbol": "EURUSD=X"},
    {"name": "GBP/USD", "symbol": "GBPUSD=X"},
    {"name": "AUD/USD", "symbol": "AUDUSD=X"},
    {"name": "NZD/USD", "symbol": "NZDUSD=X"},
    {"name": "USD/CAD", "symbol": "CAD=X"},
    {"name": "USD/CHF", "symbol": "CHF=X"},
    {"name": "USD/JPY", "symbol": "JPY=X"},
]

# =========================
# Strategy settings
# =========================

# =========================
# Strategy settings
# =========================

STRATEGY_NAME = "RSI"
# Options:
# "MOVING_AVERAGE"
# "RSI"

FAST_MA_PERIOD = 5
SLOW_MA_PERIOD = 10

RSI_PERIOD = 14
RSI_BUY_LEVEL = 30
RSI_SELL_LEVEL = 70


# =========================
# Account and risk settings
# =========================

ACCOUNT_BALANCE = 1000
RISK_PERCENT = 1

STOP_LOSS_PIPS = 20
TAKE_PROFIT_PIPS = 40

PIP_VALUE_PER_STANDARD_LOT = 10

SPREAD_PIPS = 2
COMMISSION_PER_TRADE = 0

MAX_TRADES_PER_DAY = 3
DAILY_LOSS_LIMIT_PERCENT = 3