import pandas as pd

from config import (
    STRATEGY_NAME,
    FAST_MA_PERIOD,
    SLOW_MA_PERIOD,
    RSI_PERIOD,
    RSI_BUY_LEVEL,
    RSI_SELL_LEVEL,
)


def add_moving_averages(data, fast_period=FAST_MA_PERIOD, slow_period=SLOW_MA_PERIOD):
    data["fast_ma"] = data["close"].rolling(window=fast_period).mean()
    data["slow_ma"] = data["close"].rolling(window=slow_period).mean()
    return data


def add_rsi(data, period=RSI_PERIOD):
    price_change = data["close"].diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.rolling(window=period).mean()
    average_loss = losses.rolling(window=period).mean()

    relative_strength = average_gain / average_loss

    data["rsi"] = 100 - (100 / (1 + relative_strength))

    return data


def prepare_indicators(data, strategy_name=None):
    if strategy_name is None:
        strategy_name = STRATEGY_NAME

    if strategy_name == "MOVING_AVERAGE":
        data = add_moving_averages(data)

    elif strategy_name == "RSI":
        data = add_rsi(data)

    else:
        raise ValueError(f"Unknown strategy selected: {strategy_name}")

    return data


def generate_moving_average_signal(data):
    if len(data) < 2:
        return "NO TRADE"

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    if pd.isna(latest["fast_ma"]) or pd.isna(latest["slow_ma"]):
        return "NO TRADE"

    if previous["fast_ma"] <= previous["slow_ma"] and latest["fast_ma"] > latest["slow_ma"]:
        return "BUY"

    elif previous["fast_ma"] >= previous["slow_ma"] and latest["fast_ma"] < latest["slow_ma"]:
        return "SELL"

    else:
        return "NO TRADE"


def generate_rsi_signal(data):
    if len(data) < 2:
        return "NO TRADE"

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    if pd.isna(latest["rsi"]) or pd.isna(previous["rsi"]):
        return "NO TRADE"

    if previous["rsi"] < RSI_BUY_LEVEL and latest["rsi"] >= RSI_BUY_LEVEL:
        return "BUY"

    elif previous["rsi"] > RSI_SELL_LEVEL and latest["rsi"] <= RSI_SELL_LEVEL:
        return "SELL"

    else:
        return "NO TRADE"


def generate_signal(data, strategy_name=None):
    if strategy_name is None:
        strategy_name = STRATEGY_NAME

    if strategy_name == "MOVING_AVERAGE":
        return generate_moving_average_signal(data)

    elif strategy_name == "RSI":
        return generate_rsi_signal(data)

    else:
        raise ValueError(f"Unknown strategy selected: {strategy_name}")