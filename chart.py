import os
import pandas as pd
import matplotlib.pyplot as plt

from strategy import add_moving_averages
from config import (
    DATA_FILE,
    TRADES_FILE,
    CHART_FILE,
    RESULTS_DIR,
    FAST_MA_PERIOD,
    SLOW_MA_PERIOD,
)


def plot_trades():
    print("Generating chart...")

    try:
        data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"{DATA_FILE} not found. Run download_data.py first.")
        return False

    try:
        trades = pd.read_csv(TRADES_FILE)
    except FileNotFoundError:
        print(f"{TRADES_FILE} not found. Run backtester.py first.")
        return False

    if trades.empty:
        print("No trades found. Chart cannot be created.")
        return False

    os.makedirs(RESULTS_DIR, exist_ok=True)

    data["time"] = pd.to_datetime(data["time"])
    trades["entry_time"] = pd.to_datetime(trades["entry_time"])
    trades["exit_time"] = pd.to_datetime(trades["exit_time"])

    data = add_moving_averages(
        data,
        fast_period=FAST_MA_PERIOD,
        slow_period=SLOW_MA_PERIOD
    )

    plt.figure(figsize=(14, 7))

    plt.plot(data["time"], data["close"], label="Close Price")
    plt.plot(data["time"], data["fast_ma"], label=f"Fast MA {FAST_MA_PERIOD}")
    plt.plot(data["time"], data["slow_ma"], label=f"Slow MA {SLOW_MA_PERIOD}")

    buy_label_used = False
    sell_label_used = False
    exit_label_used = False

    for _, trade in trades.iterrows():
        entry_time = trade["entry_time"]
        exit_time = trade["exit_time"]
        entry_price = trade["entry_price"]
        exit_price = trade["exit_price"]
        trade_type = trade["type"]

        if trade_type == "BUY":
            label = "BUY Entry" if not buy_label_used else ""
            plt.scatter(entry_time, entry_price, marker="^", s=100, label=label)
            buy_label_used = True

        elif trade_type == "SELL":
            label = "SELL Entry" if not sell_label_used else ""
            plt.scatter(entry_time, entry_price, marker="v", s=100, label=label)
            sell_label_used = True

        label = "Exit" if not exit_label_used else ""
        plt.scatter(exit_time, exit_price, marker="x", s=100, label=label)
        exit_label_used = True

    plt.title("Forex Bot Backtest Chart")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(CHART_FILE)
    plt.show()

    print(f"Chart saved as {CHART_FILE}")

    return True


if __name__ == "__main__":
    plot_trades()