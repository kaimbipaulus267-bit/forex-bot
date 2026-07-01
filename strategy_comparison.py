import os
import pandas as pd

from config import (
    DATA_FILE,
    RESULTS_DIR,
    COMPARISON_FILE,
    ACCOUNT_BALANCE,
    MAX_TRADES_PER_DAY,
    DAILY_LOSS_LIMIT_PERCENT,
    SLOW_MA_PERIOD,
    RSI_PERIOD,
)

from risk_manager import calculate_lot_size
from strategy import prepare_indicators, generate_signal

from backtester import (
    get_stop_loss_price,
    get_take_profit_price,
    close_trade,
)


STRATEGIES_TO_TEST = [
    "MOVING_AVERAGE",
    "RSI",
]


def run_strategy_backtest(strategy_name, original_data, symbol=None):
    data = original_data.copy()
    data = prepare_indicators(data, strategy_name=strategy_name)

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

    start_index = max(SLOW_MA_PERIOD, RSI_PERIOD) + 1

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
                    symbol=symbol,
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
                    symbol=symbol,
                )

                position = None
                continue

        if position is None:
            if stop_trading_today:
                continue

            if trades_today >= MAX_TRADES_PER_DAY:
                continue

            signal = generate_signal(current_data, strategy_name=strategy_name)

            if signal == "BUY":
                position = "BUY"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "BUY", symbol)
                take_profit = get_take_profit_price(entry_price, "BUY", symbol)
                trades_today += 1

            elif signal == "SELL":
                position = "SELL"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "SELL", symbol)
                take_profit = get_take_profit_price(entry_price, "SELL", symbol)
                trades_today += 1

    if len(trades) == 0:
        return {
            "strategy": strategy_name,
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

    final_balance = trades_df["balance"].iloc[-1]

    return {
        "strategy": strategy_name,
        "total_trades": total_trades,
        "winning_trades": number_of_wins,
        "losing_trades": number_of_losses,
        "win_rate": round(win_rate, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "final_balance": round(final_balance, 2),
        "profit_factor": profit_factor,
    }


def compare_strategies():
    print("Comparing strategies...")

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

    results = []

    for strategy_name in STRATEGIES_TO_TEST:
        print(f"\nTesting strategy: {strategy_name}")
        result = run_strategy_backtest(strategy_name, data)
        results.append(result)

    results_df = pd.DataFrame(results)
    results_df.to_csv(COMPARISON_FILE, index=False)

    print("\nStrategy Comparison Results")
    print("---------------------------")
    print(results_df)

    best_strategy = results_df.sort_values(
        by="total_profit_loss",
        ascending=False
    ).iloc[0]

    print("\nBest Strategy")
    print("-------------")
    print(f"Strategy: {best_strategy['strategy']}")
    print(f"Profit/Loss: ${best_strategy['total_profit_loss']}")
    print(f"Final Balance: ${best_strategy['final_balance']}")
    print(f"Win Rate: {best_strategy['win_rate']}%")

    print(f"\nComparison saved to {COMPARISON_FILE}")

    return True


if __name__ == "__main__":
    compare_strategies()