import pandas as pd

from strategy import prepare_indicators, generate_signal
from config import DATA_FILE, STRATEGY_NAME

def main():
    print("Starting Forex Signal Bot...")
    print(f"Selected Strategy: {STRATEGY_NAME}")

    data = pd.read_csv(DATA_FILE)
    data["time"] = pd.to_datetime(data["time"])

    data = prepare_indicators(data)

    signal = generate_signal(data)

    latest = data.iloc[-1]

    print("\nLatest Market Data")
    print("------------------")
    print(f"Time: {latest['time']}")
    print(f"Close Price: {latest['close']}")

    if "fast_ma" in data.columns and "slow_ma" in data.columns:
        print(f"Fast MA: {latest['fast_ma']}")
        print(f"Slow MA: {latest['slow_ma']}")

    if "rsi" in data.columns:
        print(f"RSI: {latest['rsi']}")

    print("\nBot Signal")
    print("----------")
    print(signal)


if __name__ == "__main__":
    main()