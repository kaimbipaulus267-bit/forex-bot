import os
import pandas as pd
import yfinance as yf

from config import SYMBOL, PERIOD, INTERVAL, DATA_FILE, RESULTS_DIR


def download_forex_data():
    try:
        os.makedirs(RESULTS_DIR, exist_ok=True)

        print("Downloading forex data...")
        print(f"Symbol: {SYMBOL}")
        print(f"Period: {PERIOD}")
        print(f"Interval: {INTERVAL}")

        data = yf.download(
            SYMBOL,
            period=PERIOD,
            interval=INTERVAL,
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            print("Error: No data downloaded.")
            return False

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [column[0] for column in data.columns]

        data = data.reset_index()

        if "Datetime" in data.columns:
            time_column = "Datetime"
        elif "Date" in data.columns:
            time_column = "Date"
        else:
            print("Error: No time column found in downloaded data.")
            return False

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
                return False

        data = data[required_columns]
        data = data.dropna()

        if data.empty:
            print("Error: Data became empty after cleaning.")
            return False

        data.to_csv(DATA_FILE, index=False)

        print(f"\nSaved {len(data)} candles to {DATA_FILE}")
        print(data.tail())

        return True

    except Exception as error:
        print("Error while downloading forex data:")
        print(error)
        return False


if __name__ == "__main__":
    download_forex_data()