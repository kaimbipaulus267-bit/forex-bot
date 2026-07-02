import os
import pandas as pd
import MetaTrader5 as mt5

from config import (
    RESULTS_DIR,
    MT5_SYMBOL,
    MT5_TIMEFRAME,
    MT5_CANDLES,
    MT5_LIVE_DATA_FILE,
    MT5_ALLOW_TRADING,
)

from mt5_connector import initialize_mt5, shutdown_mt5, check_symbol


def get_mt5_timeframe(timeframe_name):
    """
    Converts readable timeframe text into MT5 timeframe constant.
    """

    timeframes = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
    }

    if timeframe_name not in timeframes:
        raise ValueError(f"Unsupported timeframe: {timeframe_name}")

    return timeframes[timeframe_name]


def download_mt5_live_data():
    """
    Downloads recent candles from MetaTrader 5.
    No trades are placed.
    """

    print("Downloading live MT5 candle data...")

    if MT5_ALLOW_TRADING:
        print("MT5_ALLOW_TRADING is True.")
        print("For this stage, set MT5_ALLOW_TRADING back to False.")
        return False

    connected = initialize_mt5()

    if not connected:
        return False

    try:
        symbol_ok = check_symbol(MT5_SYMBOL)

        if not symbol_ok:
            return False

        timeframe = get_mt5_timeframe(MT5_TIMEFRAME)

        rates = mt5.copy_rates_from_pos(
            MT5_SYMBOL,
            timeframe,
            0,
            MT5_CANDLES
        )

        if rates is None:
            print("Could not download MT5 candle data.")
            print("Last error:", mt5.last_error())
            return False

        if len(rates) == 0:
            print("No candle data returned from MT5.")
            return False

        data = pd.DataFrame(rates)

        data["time"] = pd.to_datetime(data["time"], unit="s")

        data = data.rename(columns={
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "tick_volume": "volume"
        })

        data = data[[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "spread"
        ]]

        os.makedirs(RESULTS_DIR, exist_ok=True)

        data.to_csv(MT5_LIVE_DATA_FILE, index=False)

        print(f"Saved {len(data)} MT5 candles to {MT5_LIVE_DATA_FILE}")
        print(data.tail())

        print("\nNo trades were placed.")

        return True

    finally:
        shutdown_mt5()


if __name__ == "__main__":
    download_mt5_live_data()