import MetaTrader5 as mt5

from config import MT5_SYMBOL, MT5_ALLOW_TRADING


def get_trade_mode_name(trade_mode):
    """
    Converts MT5 account trade mode number into readable text.
    """

    demo_mode = getattr(mt5, "ACCOUNT_TRADE_MODE_DEMO", None)
    contest_mode = getattr(mt5, "ACCOUNT_TRADE_MODE_CONTEST", None)
    real_mode = getattr(mt5, "ACCOUNT_TRADE_MODE_REAL", None)

    if trade_mode == demo_mode:
        return "DEMO"

    if trade_mode == contest_mode:
        return "CONTEST"

    if trade_mode == real_mode:
        return "REAL"

    return f"UNKNOWN ({trade_mode})"


def initialize_mt5():
    """
    Starts connection to the opened MetaTrader 5 terminal.
    """

    if not mt5.initialize():
        print("MT5 initialization failed.")
        print("Last error:", mt5.last_error())
        return False

    print("MT5 initialized successfully.")
    return True


def shutdown_mt5():
    """
    Safely closes MT5 Python connection.
    """

    mt5.shutdown()
    print("MT5 connection closed.")


def show_terminal_info():
    """
    Shows MetaTrader terminal information.
    """

    terminal_info = mt5.terminal_info()

    if terminal_info is None:
        print("Could not read terminal info.")
        print("Last error:", mt5.last_error())
        return False

    terminal_dict = terminal_info._asdict()

    print("\nTerminal Info")
    print("-------------")
    print(f"Name: {terminal_dict.get('name')}")
    print(f"Company: {terminal_dict.get('company')}")
    print(f"Path: {terminal_dict.get('path')}")
    print(f"Connected: {terminal_dict.get('connected')}")
    print(f"Trade Allowed: {terminal_dict.get('trade_allowed')}")

    return True


def show_account_info():
    """
    Shows logged-in trading account information.
    """

    account_info = mt5.account_info()

    if account_info is None:
        print("Could not read account info.")
        print("Last error:", mt5.last_error())
        return False

    account = account_info._asdict()
    trade_mode_name = get_trade_mode_name(account.get("trade_mode"))

    print("\nAccount Info")
    print("------------")
    print(f"Login: {account.get('login')}")
    print(f"Server: {account.get('server')}")
    print(f"Name: {account.get('name')}")
    print(f"Currency: {account.get('currency')}")
    print(f"Balance: {account.get('balance')}")
    print(f"Equity: {account.get('equity')}")
    print(f"Leverage: 1:{account.get('leverage')}")
    print(f"Trade Mode: {trade_mode_name}")

    if trade_mode_name == "REAL":
        print("\nWARNING: This is a REAL account.")
        print("Trading execution must stay disabled.")

    return True


def check_symbol(symbol=MT5_SYMBOL):
    """
    Checks whether the broker symbol exists and can be selected.
    """

    print("\nSymbol Check")
    print("------------")
    print(f"Checking symbol: {symbol}")

    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f"Symbol {symbol} not found.")
        print("Your broker may use a different name like EURUSDm or EURUSD.a.")
        print("Open MT5 Market Watch and check the exact symbol name.")
        return False

    if not symbol_info.visible:
        selected = mt5.symbol_select(symbol, True)

        if not selected:
            print(f"Could not select symbol {symbol}.")
            print("Last error:", mt5.last_error())
            return False

    symbol_info = mt5.symbol_info(symbol)
    symbol_data = symbol_info._asdict()

    print(f"Symbol found: {symbol}")
    print(f"Description: {symbol_data.get('description')}")
    print(f"Digits: {symbol_data.get('digits')}")
    print(f"Spread: {symbol_data.get('spread')}")
    print(f"Volume Min: {symbol_data.get('volume_min')}")
    print(f"Volume Max: {symbol_data.get('volume_max')}")
    print(f"Volume Step: {symbol_data.get('volume_step')}")

    return True


def show_live_tick(symbol=MT5_SYMBOL):
    """
    Shows the latest live bid and ask price.
    """

    tick = mt5.symbol_info_tick(symbol)

    if tick is None:
        print(f"Could not read live tick for {symbol}.")
        print("Last error:", mt5.last_error())
        return False

    tick_data = tick._asdict()

    print("\nLive Price")
    print("----------")
    print(f"Symbol: {symbol}")
    print(f"Bid: {tick_data.get('bid')}")
    print(f"Ask: {tick_data.get('ask')}")
    print(f"Last: {tick_data.get('last')}")
    print(f"Time: {tick_data.get('time')}")

    return True


def run_mt5_connection_test():
    """
    Runs a safe MT5 connection test.
    No trades are placed.
    """

    print("Starting MT5 connection test...")

    print("\nTrading Allowed In Config:")
    print("--------------------------")
    print(f"MT5_ALLOW_TRADING = {MT5_ALLOW_TRADING}")

    if MT5_ALLOW_TRADING:
        print("WARNING: MT5_ALLOW_TRADING is True.")
        print("For this stage, set it back to False.")
        return False

    connected = initialize_mt5()

    if not connected:
        return False

    try:
        show_terminal_info()
        show_account_info()
        symbol_ok = check_symbol(MT5_SYMBOL)

        if symbol_ok:
            show_live_tick(MT5_SYMBOL)

    finally:
        shutdown_mt5()

    print("\nMT5 connection test completed.")
    print("No trades were placed.")

    return True


if __name__ == "__main__":
    run_mt5_connection_test()