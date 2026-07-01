import os
import time
import pandas as pd
import yfinance as yf

from config import SYMBOL, PERIOD, INTERVAL, DATA_FILE, RESULTS_DIR


FALLBACK_SETTINGS = [
    {"period": PERIOD, "interval": INTERVAL},
    {"period": "30d", "interval": "1h"},
    {"period": "10d", "interval": "30m"},
    {"period": "5d", "interval": "15m"},
    {"period": "6mo", "interval": "1d"},
]


def clean_yfinance_data(data):
    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] for column in data.columns]

    data = data.reset_index()

    if "Datetime" in data.columns:
        time_column = "Datetime"
    elif "Date" in data.columns:
        time_column = "Date"
    else:
        print("Error: No time column found.")
        return None

    data = data.rename(columns={
        time_column: "time",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close"
    })

    required_columns = ["time", "open", "high", "low", "close"]

    for column in required_columns:
        if column not in data.columns:
            print(f"Error: Missing column: {column}")
            return None

    data = data[required_columns]
    data = data.dropna()

    if data.empty:
        return None

    return data


def download_forex_data():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Downloading forex data...")
    print(f"Symbol: {SYMBOL}")

    for setting in FALLBACK_SETTINGS:
        period = setting["period"]
        interval = setting["interval"]

        try:
            print(f"\nTrying period={period}, interval={interval}")

            data = yf.download(
                SYMBOL,
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=False
            )

            cleaned_data = clean_yfinance_data(data)

            if cleaned_data is not None:
                cleaned_data.to_csv(DATA_FILE, index=False)

                print(f"\nSuccess!")
                print(f"Saved {len(cleaned_data)} candles to {DATA_FILE}")
                print(cleaned_data.tail())

                return True

            print("No usable data. Trying next fallback...")

        except Exception as error:
            print(f"Download failed for period={period}, interval={interval}")
            print(error)

        time.sleep(2)

    print("\nError: All download attempts failed.")
    print("This may be a temporary Yahoo/yfinance issue. Try again later or use another data provider.")

    return False


if __name__ == "__main__":
    download_forex_data()