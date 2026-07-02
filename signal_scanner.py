import os
import pandas as pd

from config import (
    RESULTS_DIR,
    DATA_FILE,
    SIGNAL_FILE,
    SYMBOL,
    STRATEGY_NAME,
)

from strategy import prepare_indicators, generate_signal
from backtester import get_stop_loss_price, get_take_profit_price
from risk_manager import calculate_lot_size
from pair_utils import get_pip_size


def scan_latest_signal():
    print("Scanning latest forex signal...")

    try:
        data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"{DATA_FILE} not found. Run download_data.py or run_all.py first.")
        return False

    if data.empty:
        print("Market data is empty.")
        return False

    os.makedirs(RESULTS_DIR, exist_ok=True)

    data["time"] = pd.to_datetime(data["time"])
    data = prepare_indicators(data)

    signal = generate_signal(data)

    latest = data.iloc[-1]

    latest_time = latest["time"]
    close_price = float(latest["close"])

    lot_size = calculate_lot_size()
    pip_size = get_pip_size(SYMBOL)

    stop_loss = None
    take_profit = None

    if signal == "BUY":
        stop_loss = get_stop_loss_price(close_price, "BUY", SYMBOL)
        take_profit = get_take_profit_price(close_price, "BUY", SYMBOL)

    elif signal == "SELL":
        stop_loss = get_stop_loss_price(close_price, "SELL", SYMBOL)
        take_profit = get_take_profit_price(close_price, "SELL", SYMBOL)

    report = f"""
Latest Signal Report
--------------------

Symbol: {SYMBOL}
Strategy: {STRATEGY_NAME}
Time: {latest_time}
Close Price: {round(close_price, 5)}
Pip Size: {pip_size}
Lot Size: {lot_size}

Signal: {signal}
"""

    if signal in ["BUY", "SELL"]:
        report += f"""
Trade Plan
----------
Entry Price: {round(close_price, 5)}
Stop Loss: {round(stop_loss, 5)}
Take Profit: {round(take_profit, 5)}

Important:
This is a signal only.
The bot is not placing a real trade.
"""
    else:
        report += """
Trade Plan
----------
No trade setup found right now.

Important:
The safest action is to wait.
"""

    print(report)

    with open(SIGNAL_FILE, "w") as file:
        file.write(report)

    print(f"Latest signal saved to {SIGNAL_FILE}")

    return True


if __name__ == "__main__":
    scan_latest_signal()