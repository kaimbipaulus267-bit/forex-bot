import os
import pandas as pd
import yfinance as yf

from config import (
    PAIRS_TO_TEST,
    PERIOD,
    INTERVAL,
    RESULTS_DIR,
    MULTI_PAIR_FILE,
)

from strategy_comparison import run_strategy_backtest


STRATEGIES_TO_TEST = [
    "MOVING_AVERAGE",
    "RSI",
]


def download_pair_data(symbol):
    print(f"Downloading data for {symbol}...")

    data = yf.download(
        symbol,
        period=PERIOD,
        interval=INTERVAL,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        print(f"No data downloaded for {symbol}.")
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] for column in data.columns]

    data = data.reset_index()

    if "Datetime" in data.columns:
        time_column = "Datetime"
    elif "Date" in data.columns:
        time_column = "Date"
    else:
        print(f"No time column found for {symbol}.")
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
            print(f"Missing column {column} for {symbol}.")
            return None

    data = data[required_columns]
    data = data.dropna()

    if data.empty:
        print(f"Data became empty after cleaning for {symbol}.")
        return None

    data["time"] = pd.to_datetime(data["time"])

    return data


def compare_pairs():
    print("Starting multi-pair test...")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    results = []

    for pair in PAIRS_TO_TEST:
        pair_name = pair["name"]
        symbol = pair["symbol"]

        print(f"\nTesting pair: {pair_name} ({symbol})")

        data = download_pair_data(symbol)

        if data is None:
            continue

        for strategy_name in STRATEGIES_TO_TEST:
            print(f"Testing {strategy_name} on {pair_name}")

            result = run_strategy_backtest(strategy_name, data, symbol=symbol)
            result["pair"] = pair_name
            result["symbol"] = symbol

            results.append(result)

    if len(results) == 0:
        print("No pair results created.")
        return False

    results_df = pd.DataFrame(results)

    preferred_columns = [
        "pair",
        "symbol",
        "strategy",
        "total_trades",
        "winning_trades",
        "losing_trades",
        "win_rate",
        "total_profit_loss",
        "final_balance",
        "profit_factor",
    ]

    results_df = results_df[preferred_columns]

    results_df = results_df.sort_values(
        by="total_profit_loss",
        ascending=False
    )

    results_df.to_csv(MULTI_PAIR_FILE, index=False)

    print("\nMulti-Pair Results")
    print("------------------")
    print(results_df)

    best_result = results_df.iloc[0]

    print("\nBest Pair and Strategy")
    print("----------------------")
    print(f"Pair: {best_result['pair']}")
    print(f"Strategy: {best_result['strategy']}")
    print(f"Profit/Loss: ${best_result['total_profit_loss']}")
    print(f"Final Balance: ${best_result['final_balance']}")
    print(f"Win Rate: {best_result['win_rate']}%")

    print(f"\nMulti-pair results saved to {MULTI_PAIR_FILE}")

    return True


if __name__ == "__main__":
    compare_pairs()