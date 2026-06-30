import os
import pandas as pd

from config import (
    DATA_FILE,
    RESULTS_DIR,
    OPTIMIZATION_FILE,
    ACCOUNT_BALANCE,
    MAX_TRADES_PER_DAY,
    DAILY_LOSS_LIMIT_PERCENT,
)

from risk_manager import calculate_lot_size

from backtester import (
    get_stop_loss_price,
    get_take_profit_price,
    close_trade,
)


def add_moving_averages(data, fast_period, slow_period):
    data["fast_ma"] = data["close"].rolling(window=fast_period).mean()
    data["slow_ma"] = data["close"].rolling(window=slow_period).mean()
    return data


def add_rsi(data, period):
    price_change = data["close"].diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.rolling(window=period).mean()
    average_loss = losses.rolling(window=period).mean()

    relative_strength = average_gain / average_loss

    data["rsi"] = 100 - (100 / (1 + relative_strength))

    return data


def generate_ma_signal(data):
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

    return "NO TRADE"


def generate_rsi_signal(data, buy_level, sell_level):
    if len(data) < 2:
        return "NO TRADE"

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    if pd.isna(latest["rsi"]) or pd.isna(previous["rsi"]):
        return "NO TRADE"

    if previous["rsi"] < buy_level and latest["rsi"] >= buy_level:
        return "BUY"

    elif previous["rsi"] > sell_level and latest["rsi"] <= sell_level:
        return "SELL"

    return "NO TRADE"


def calculate_result_summary(strategy_name, settings, trades, final_balance):
    if len(trades) == 0:
        return {
            "strategy": strategy_name,
            "settings": settings,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_profit_loss": 0,
            "final_balance": ACCOUNT_BALANCE,
            "profit_factor": "No trades",
        }

    trades_df = pd.DataFrame(trades)

    total_trades = len(trades_df)

    winning_trades = trades_df[trades_df["profit_loss"] > 0]
    losing_trades = trades_df[trades_df["profit_loss"] < 0]

    number_of_wins = len(winning_trades)
    number_of_losses = len(losing_trades)

    win_rate = (number_of_wins / total_trades) * 100

    total_profit = winning_trades["profit_loss"].sum()
    total_loss = losing_trades["profit_loss"].sum()
    total_profit_loss = trades_df["profit_loss"].sum()

    if total_loss != 0:
        profit_factor = round(total_profit / abs(total_loss), 2)
    else:
        profit_factor = "No losses"

    return {
        "strategy": strategy_name,
        "settings": settings,
        "total_trades": total_trades,
        "winning_trades": number_of_wins,
        "losing_trades": number_of_losses,
        "win_rate": round(win_rate, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "final_balance": round(final_balance, 2),
        "profit_factor": profit_factor,
    }


def run_single_test(strategy_name, original_data, settings):
    data = original_data.copy()

    if strategy_name == "MOVING_AVERAGE":
        fast_period = settings["fast_ma"]
        slow_period = settings["slow_ma"]

        data = add_moving_averages(data, fast_period, slow_period)
        start_index = slow_period + 1

    elif strategy_name == "RSI":
        rsi_period = settings["rsi_period"]

        data = add_rsi(data, rsi_period)
        start_index = rsi_period + 1

    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    position = None
    entry_price = 0
    entry_time = None
    stop_loss = 0
    take_profit = 0

    trades = []

    lot_size = calculate_lot_size()
    balance = ACCOUNT_BALANCE

    current_day = None
    trades_today = 0
    daily_start_balance = balance
    stop_trading_today = False

    for i in range(start_index, len(data)):
        current_data = data.iloc[: i + 1]

        current_candle = data.iloc[i]
        current_time = current_candle["time"]
        current_date = current_time.date()
        current_close = current_candle["close"]
        current_high = current_candle["high"]
        current_low = current_candle["low"]

        if current_day != current_date:
            current_day = current_date
            trades_today = 0
            daily_start_balance = balance
            stop_trading_today = False

        daily_loss_limit_amount = daily_start_balance * (DAILY_LOSS_LIMIT_PERCENT / 100)
        current_daily_loss = daily_start_balance - balance

        if current_daily_loss >= daily_loss_limit_amount:
            stop_trading_today = True

        if position == "BUY":
            exit_price = None
            exit_reason = None

            if current_low <= stop_loss:
                exit_price = stop_loss
                exit_reason = "STOP LOSS"

            elif current_high >= take_profit:
                exit_price = take_profit
                exit_reason = "TAKE PROFIT"

            if exit_price is not None:
                balance = close_trade(
                    trades,
                    "BUY",
                    entry_time,
                    current_time,
                    entry_price,
                    exit_price,
                    stop_loss,
                    take_profit,
                    exit_reason,
                    lot_size,
                    balance,
                )

                position = None
                continue

        elif position == "SELL":
            exit_price = None
            exit_reason = None

            if current_high >= stop_loss:
                exit_price = stop_loss
                exit_reason = "STOP LOSS"

            elif current_low <= take_profit:
                exit_price = take_profit
                exit_reason = "TAKE PROFIT"

            if exit_price is not None:
                balance = close_trade(
                    trades,
                    "SELL",
                    entry_time,
                    current_time,
                    entry_price,
                    exit_price,
                    stop_loss,
                    take_profit,
                    exit_reason,
                    lot_size,
                    balance,
                )

                position = None
                continue

        if position is None:
            if stop_trading_today:
                continue

            if trades_today >= MAX_TRADES_PER_DAY:
                continue

            if strategy_name == "MOVING_AVERAGE":
                signal = generate_ma_signal(current_data)

            elif strategy_name == "RSI":
                signal = generate_rsi_signal(
                    current_data,
                    settings["buy_level"],
                    settings["sell_level"],
                )

            else:
                signal = "NO TRADE"

            if signal == "BUY":
                position = "BUY"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "BUY")
                take_profit = get_take_profit_price(entry_price, "BUY")
                trades_today += 1

            elif signal == "SELL":
                position = "SELL"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "SELL")
                take_profit = get_take_profit_price(entry_price, "SELL")
                trades_today += 1

    return calculate_result_summary(strategy_name, settings, trades, balance)


def optimize_moving_average(data):
    results = []

    fast_periods = [5, 10, 15]
    slow_periods = [20, 30, 50]

    for fast_period in fast_periods:
        for slow_period in slow_periods:
            if fast_period >= slow_period:
                continue

            settings = {
                "fast_ma": fast_period,
                "slow_ma": slow_period,
            }

            print(f"Testing MA settings: fast={fast_period}, slow={slow_period}")

            result = run_single_test(
                "MOVING_AVERAGE",
                data,
                settings,
            )

            results.append(result)

    return results


def optimize_rsi(data):
    results = []

    rsi_periods = [10, 14, 21]
    buy_levels = [25, 30, 35]
    sell_levels = [65, 70, 75]

    for rsi_period in rsi_periods:
        for buy_level in buy_levels:
            for sell_level in sell_levels:
                if buy_level >= sell_level:
                    continue

                settings = {
                    "rsi_period": rsi_period,
                    "buy_level": buy_level,
                    "sell_level": sell_level,
                }

                print(
                    f"Testing RSI settings: period={rsi_period}, "
                    f"buy={buy_level}, sell={sell_level}"
                )

                result = run_single_test(
                    "RSI",
                    data,
                    settings,
                )

                results.append(result)

    return results


def run_optimizer():
    print("Starting strategy optimizer...")

    try:
        data = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"{DATA_FILE} not found. Run download_data.py first.")
        return False

    if data.empty:
        print("Data file is empty.")
        return False

    os.makedirs(RESULTS_DIR, exist_ok=True)

    data["time"] = pd.to_datetime(data["time"])

    all_results = []

    ma_results = optimize_moving_average(data)
    rsi_results = optimize_rsi(data)

    all_results.extend(ma_results)
    all_results.extend(rsi_results)

    results_df = pd.DataFrame(all_results)

    results_df = results_df.sort_values(
        by="total_profit_loss",
        ascending=False
    )

    results_df.to_csv(OPTIMIZATION_FILE, index=False)

    print("\nOptimization Results")
    print("--------------------")
    print(results_df)

    best_result = results_df.iloc[0]

    print("\nBest Settings")
    print("-------------")
    print(f"Strategy: {best_result['strategy']}")
    print(f"Settings: {best_result['settings']}")
    print(f"Profit/Loss: ${best_result['total_profit_loss']}")
    print(f"Final Balance: ${best_result['final_balance']}")
    print(f"Win Rate: {best_result['win_rate']}%")
    print(f"Total Trades: {best_result['total_trades']}")

    print(f"\nOptimization saved to {OPTIMIZATION_FILE}")

    return True


if __name__ == "__main__":
    run_optimizer()