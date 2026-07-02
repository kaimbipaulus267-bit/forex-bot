import os
import pandas as pd
from datetime import datetime
from data_source import get_signal_data_file

from config import (
    RESULTS_DIR,
    DATA_FILE,
    SIGNAL_FILE,
    SIGNAL_HISTORY_FILE,
    SYMBOL,
    MT5_SYMBOL,
    STRATEGY_NAME,
    SIGNAL_DATA_SOURCE,
)

from strategy import prepare_indicators, generate_signal
from backtester import get_stop_loss_price, get_take_profit_price
from risk_manager import calculate_lot_size
from pair_utils import get_pip_size


def save_signal_history(signal_data):
    """
    Saves every scanned signal to signal_history.csv.
    """

    signal_df = pd.DataFrame([signal_data])

    if os.path.exists(SIGNAL_HISTORY_FILE):
        old_history = pd.read_csv(SIGNAL_HISTORY_FILE)
        updated_history = pd.concat([old_history, signal_df], ignore_index=True)
    else:
        updated_history = signal_df

    updated_history.to_csv(SIGNAL_HISTORY_FILE, index=False)


def scan_latest_signal():
    print("Scanning latest forex signal...")

    signal_data_file = get_signal_data_file()

    if SIGNAL_DATA_SOURCE == "MT5":
        active_symbol = MT5_SYMBOL
    else:
        active_symbol = SYMBOL

    try:
       data = pd.read_csv(signal_data_file)
    except FileNotFoundError:
        print(f"{signal_data_file} not found.")
        print("If using YAHOO, run download_data.py or run_all.py first.")
        print("If using MT5, run mt5_live_data.py first.")
        return False

    if data.empty:
        print("Market data is empty.")
        return False

    os.makedirs(RESULTS_DIR, exist_ok=True)

    data["time"] = pd.to_datetime(data["time"])
    data = prepare_indicators(data)

    signal = generate_signal(data)

    latest = data.iloc[-1]

    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_time = latest["time"]
    close_price = float(latest["close"])

    lot_size = calculate_lot_size()
    pip_size = get_pip_size(active_symbol)

    stop_loss = None
    take_profit = None
    entry_price = None

    if signal == "BUY":
        entry_price = close_price
        stop_loss = get_stop_loss_price(close_price, "BUY", active_symbol)
        take_profit = get_take_profit_price(close_price, "BUY", active_symbol)

    elif signal == "SELL":
        entry_price = close_price
        stop_loss = get_stop_loss_price(close_price, "SELL", active_symbol)
        take_profit = get_take_profit_price(close_price, "SELL", active_symbol)

    signal_data = {
        "scan_time": scan_time,
        "symbol": active_symbol,
        "strategy": STRATEGY_NAME,
        "data_source": SIGNAL_DATA_SOURCE,
        "market_time": latest_time,
        "close_price": round(close_price, 5),
        "pip_size": pip_size,
        "lot_size": lot_size,
        "signal": signal,
        "entry_price": round(entry_price, 5) if entry_price is not None else "",
        "stop_loss": round(stop_loss, 5) if stop_loss is not None else "",
        "take_profit": round(take_profit, 5) if take_profit is not None else "",
    }

    save_signal_history(signal_data)

    report = f"""
Latest Signal Report
--------------------

Scan Time: {scan_time}
Symbol: {active_symbol}
Data Source: {SIGNAL_DATA_SOURCE}
Strategy: {STRATEGY_NAME}
Market Time: {latest_time}
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
    print(f"Signal history updated at {SIGNAL_HISTORY_FILE}")

    return True


if __name__ == "__main__":
    scan_latest_signal()