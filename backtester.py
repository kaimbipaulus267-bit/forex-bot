import pandas as pd

from strategy import prepare_indicators, generate_signal
from risk_manager import calculate_lot_size
from config import (
    DATA_FILE,
    TRADES_FILE,
    FAST_MA_PERIOD,
    SLOW_MA_PERIOD,
    ACCOUNT_BALANCE,
    STOP_LOSS_PIPS,
    TAKE_PROFIT_PIPS,
    PIP_VALUE_PER_STANDARD_LOT,
    SPREAD_PIPS,
    COMMISSION_PER_TRADE,
    MAX_TRADES_PER_DAY,
    DAILY_LOSS_LIMIT_PERCENT,
)

PIP_SIZE = 0.0001


def calculate_pips(entry_price, exit_price, trade_type):
    if trade_type == "BUY":
        return (exit_price - entry_price) / PIP_SIZE

    elif trade_type == "SELL":
        return (entry_price - exit_price) / PIP_SIZE

    return 0


def calculate_net_pips(raw_pips):
    return raw_pips - SPREAD_PIPS


def calculate_money_result(net_pips, lot_size):
    gross_result = net_pips * PIP_VALUE_PER_STANDARD_LOT * lot_size
    net_result = gross_result - COMMISSION_PER_TRADE
    return net_result


def get_stop_loss_price(entry_price, trade_type):
    if trade_type == "BUY":
        return entry_price - (STOP_LOSS_PIPS * PIP_SIZE)

    elif trade_type == "SELL":
        return entry_price + (STOP_LOSS_PIPS * PIP_SIZE)


def get_take_profit_price(entry_price, trade_type):
    if trade_type == "BUY":
        return entry_price + (TAKE_PROFIT_PIPS * PIP_SIZE)

    elif trade_type == "SELL":
        return entry_price - (TAKE_PROFIT_PIPS * PIP_SIZE)


def close_trade(
    trades,
    trade_type,
    entry_time,
    exit_time,
    entry_price,
    exit_price,
    stop_loss,
    take_profit,
    exit_reason,
    lot_size,
    balance,
):
    raw_pips = calculate_pips(entry_price, exit_price, trade_type)
    net_pips = calculate_net_pips(raw_pips)
    money_result = calculate_money_result(net_pips, lot_size)

    balance += money_result

    trades.append({
        "type": trade_type,
        "entry_time": entry_time,
        "exit_time": exit_time,
        "entry_price": round(entry_price, 5),
        "exit_price": round(exit_price, 5),
        "stop_loss": round(stop_loss, 5),
        "take_profit": round(take_profit, 5),
        "exit_reason": exit_reason,
        "raw_pips": round(raw_pips, 1),
        "net_pips": round(net_pips, 1),
        "spread_pips": SPREAD_PIPS,
        "lot_size": lot_size,
        "profit_loss": round(money_result, 2),
        "balance": round(balance, 2)
    })

    return balance


def run_backtest():
    print("Starting Backtest...")

    data = pd.read_csv(DATA_FILE)
    data["time"] = pd.to_datetime(data["time"])

    data = prepare_indicators(data)

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

    for i in range(10, len(data)):
        current_data = data.iloc[: i + 1]

        current_candle = data.iloc[i]
        current_time = current_candle["time"]
        current_date = current_time.date()
        current_close = current_candle["close"]
        current_high = current_candle["high"]
        current_low = current_candle["low"]

        # Reset daily limits when a new day starts
        if current_day != current_date:
            current_day = current_date
            trades_today = 0
            daily_start_balance = balance
            stop_trading_today = False

            print(f"\nNew trading day: {current_day}")

        # Check daily loss limit
        daily_loss_limit_amount = daily_start_balance * (DAILY_LOSS_LIMIT_PERCENT / 100)
        current_daily_loss = daily_start_balance - balance

        if current_daily_loss >= daily_loss_limit_amount:
            stop_trading_today = True

        # Manage open BUY trade
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
                    balance
                )

                position = None
                continue

        # Manage open SELL trade
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
                    balance
                )

                position = None
                continue

        # Only open new trades if safety rules allow it
        if position is None:
            if stop_trading_today:
                continue

            if trades_today >= MAX_TRADES_PER_DAY:
                continue

            signal = generate_signal(current_data)

            if signal == "BUY":
                position = "BUY"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "BUY")
                take_profit = get_take_profit_price(entry_price, "BUY")
                trades_today += 1

                print(f"BUY opened at {entry_price}")

            elif signal == "SELL":
                position = "SELL"
                entry_price = current_close
                entry_time = current_time
                stop_loss = get_stop_loss_price(entry_price, "SELL")
                take_profit = get_take_profit_price(entry_price, "SELL")
                trades_today += 1

                print(f"SELL opened at {entry_price}")

    print("\nBacktest Results")
    print("----------------")

    if len(trades) == 0:
        print("No closed trades yet.")
        return

    trades_df = pd.DataFrame(trades)
    trades_df.to_csv(TRADES_FILE, index=False)

    total_raw_pips = trades_df["raw_pips"].sum()
    total_net_pips = trades_df["net_pips"].sum()
    total_profit_loss = trades_df["profit_loss"].sum()

    winning_trades = trades_df[trades_df["profit_loss"] > 0]
    losing_trades = trades_df[trades_df["profit_loss"] < 0]

    for trade in trades:
        print(
            f"{trade['type']} | "
            f"Entry: {trade['entry_price']} | "
            f"Exit: {trade['exit_price']} | "
            f"Reason: {trade['exit_reason']} | "
            f"Raw Pips: {trade['raw_pips']} | "
            f"Net Pips: {trade['net_pips']} | "
            f"P/L: ${trade['profit_loss']} | "
            f"Balance: ${trade['balance']}"
        )

    print("\nSummary")
    print("-------")
    print(f"Starting Balance: ${ACCOUNT_BALANCE}")
    print(f"Final Balance: ${round(balance, 2)}")
    print(f"Lot Size: {lot_size}")
    print(f"Stop Loss: {STOP_LOSS_PIPS} pips")
    print(f"Take Profit: {TAKE_PROFIT_PIPS} pips")
    print(f"Spread: {SPREAD_PIPS} pips")
    print(f"Commission: ${COMMISSION_PER_TRADE}")
    print(f"Maximum Trades Per Day: {MAX_TRADES_PER_DAY}")
    print(f"Daily Loss Limit: {DAILY_LOSS_LIMIT_PERCENT}%")
    print(f"Total Trades: {len(trades_df)}")
    print(f"Winning Trades: {len(winning_trades)}")
    print(f"Losing Trades: {len(losing_trades)}")
    print(f"Total Raw Pips: {round(total_raw_pips, 1)}")
    print(f"Total Net Pips After Spread: {round(total_net_pips, 1)}")
    print(f"Total Profit/Loss: ${round(total_profit_loss, 2)}")

    print(f"\nTrades saved to {TRADES_FILE}")


if __name__ == "__main__":
    run_backtest()