import os
import MetaTrader5 as mt5

from config import (
    RESULTS_DIR,
    MT5_SYMBOL,
    MT5_ALLOW_TRADING,
    MT5_DEVIATION,
    MT5_MAGIC_NUMBER,
    MT5_ORDER_PREVIEW_FILE,
    SIGNAL_FILE,
)

from mt5_connector import initialize_mt5, shutdown_mt5, check_symbol
from risk_manager import calculate_lot_size
from backtester import get_stop_loss_price, get_take_profit_price


def read_latest_signal():
    if not os.path.exists(SIGNAL_FILE):
        print(f"{SIGNAL_FILE} not found. Run signal_scanner.py first.")
        return None

    with open(SIGNAL_FILE, "r") as file:
        content = file.read()

    if "Signal: BUY" in content:
        return "BUY"

    if "Signal: SELL" in content:
        return "SELL"

    if "Signal: NO TRADE" in content:
        return "NO TRADE"

    return None


def build_order_request(signal):
    tick = mt5.symbol_info_tick(MT5_SYMBOL)

    if tick is None:
        print(f"Could not read tick for {MT5_SYMBOL}.")
        print("Last error:", mt5.last_error())
        return None

    lot_size = calculate_lot_size()

    if signal == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        stop_loss = get_stop_loss_price(price, "BUY", MT5_SYMBOL)
        take_profit = get_take_profit_price(price, "BUY", MT5_SYMBOL)

    elif signal == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        stop_loss = get_stop_loss_price(price, "SELL", MT5_SYMBOL)
        take_profit = get_take_profit_price(price, "SELL", MT5_SYMBOL)

    else:
        print("No valid BUY or SELL signal found.")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": MT5_SYMBOL,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": MT5_DEVIATION,
        "magic": MT5_MAGIC_NUMBER,
        "comment": "Forex bot order preview only",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return request


def run_order_preview():
    print("Starting MT5 order preview...")

    if MT5_ALLOW_TRADING:
        print("MT5_ALLOW_TRADING is True.")
        print("For this preview stage, set it back to False.")
        return False

    signal = read_latest_signal()

    if signal is None:
        print("Could not read latest signal.")
        return False

    if signal == "NO TRADE":
        report = """
MT5 Order Preview
-----------------

Latest signal is NO TRADE.

No order request was created.
No trade was placed.
"""
        print(report)

        os.makedirs(RESULTS_DIR, exist_ok=True)

        with open(MT5_ORDER_PREVIEW_FILE, "w") as file:
            file.write(report)

        return True

    connected = initialize_mt5()

    if not connected:
        return False

    try:
        symbol_ok = check_symbol(MT5_SYMBOL)

        if not symbol_ok:
            return False

        request = build_order_request(signal)

        if request is None:
            return False

        check_result = mt5.order_check(request)

        if check_result is None:
            print("order_check failed.")
            print("Last error:", mt5.last_error())
            return False

        result_dict = check_result._asdict()

        report = f"""
MT5 Order Preview
-----------------

IMPORTANT:
This used mt5.order_check() only.
No trade was placed.

Signal: {signal}
Symbol: {MT5_SYMBOL}
Volume: {request["volume"]}
Price: {request["price"]}
Stop Loss: {request["sl"]}
Take Profit: {request["tp"]}
Deviation: {request["deviation"]}
Magic Number: {request["magic"]}

MT5 Check Result
----------------
Retcode: {result_dict.get("retcode")}
Comment: {result_dict.get("comment")}
Balance: {result_dict.get("balance")}
Equity: {result_dict.get("equity")}
Margin: {result_dict.get("margin")}
Margin Free: {result_dict.get("margin_free")}
Margin Level: {result_dict.get("margin_level")}
Profit: {result_dict.get("profit")}
"""

        print(report)

        os.makedirs(RESULTS_DIR, exist_ok=True)

        with open(MT5_ORDER_PREVIEW_FILE, "w") as file:
            file.write(report)

        print(f"Order preview saved to {MT5_ORDER_PREVIEW_FILE}")

        return True

    finally:
        shutdown_mt5()


if __name__ == "__main__":
    run_order_preview()