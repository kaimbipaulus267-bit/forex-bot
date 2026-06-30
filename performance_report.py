import os
import pandas as pd

from config import TRADES_FILE, REPORT_FILE, RESULTS_DIR


def calculate_max_drawdown(balance_series):
    highest_balance = balance_series.cummax()
    drawdown = balance_series - highest_balance
    max_drawdown = drawdown.min()

    return max_drawdown


def generate_report():
    print("Generating Performance Report...")

    try:
        trades = pd.read_csv(TRADES_FILE)
    except FileNotFoundError:
        print(f"{TRADES_FILE} not found. Run backtester.py first.")
        return False

    if trades.empty:
        print(f"No trades found in {TRADES_FILE}.")
        return False

    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_trades = len(trades)

    winning_trades = trades[trades["profit_loss"] > 0]
    losing_trades = trades[trades["profit_loss"] < 0]

    number_of_wins = len(winning_trades)
    number_of_losses = len(losing_trades)

    win_rate = (number_of_wins / total_trades) * 100

    total_profit = winning_trades["profit_loss"].sum()
    total_loss = losing_trades["profit_loss"].sum()
    net_profit_loss = total_profit + total_loss

    average_win = winning_trades["profit_loss"].mean() if number_of_wins > 0 else 0
    average_loss = losing_trades["profit_loss"].mean() if number_of_losses > 0 else 0

    best_trade = trades["profit_loss"].max()
    worst_trade = trades["profit_loss"].min()

    if total_loss != 0:
        profit_factor = total_profit / abs(total_loss)
        profit_factor_text = round(profit_factor, 2)
    else:
        profit_factor_text = "No losses"

    final_balance = trades["balance"].iloc[-1]
    max_drawdown = calculate_max_drawdown(trades["balance"])

    report = f"""
Performance Report
------------------
Total Trades: {total_trades}
Winning Trades: {number_of_wins}
Losing Trades: {number_of_losses}
Win Rate: {round(win_rate, 2)}%

Profit Details
--------------
Total Profit: ${round(total_profit, 2)}
Total Loss: ${round(total_loss, 2)}
Net Profit/Loss: ${round(net_profit_loss, 2)}
Average Win: ${round(average_win, 2)}
Average Loss: ${round(average_loss, 2)}
Best Trade: ${round(best_trade, 2)}
Worst Trade: ${round(worst_trade, 2)}
Profit Factor: {profit_factor_text}

Account Details
---------------
Final Balance: ${round(final_balance, 2)}
Maximum Drawdown: ${round(max_drawdown, 2)}
"""

    print(report)

    with open(REPORT_FILE, "w") as file:
        file.write(report)

    print(f"Report saved to {REPORT_FILE}")

    return True


if __name__ == "__main__":
    generate_report()