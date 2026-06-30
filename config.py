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

# =========================
# Market data settings
# =========================

SYMBOL = "EURUSD=X"
PERIOD = "60d"
INTERVAL = "15m"


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