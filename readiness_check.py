import os
import pandas as pd

from config import (
    RESULTS_DIR,
    TRADES_FILE,
    WALK_FORWARD_FILE,
    READINESS_FILE,
)


def check_bot_readiness():
    print("Checking bot readiness...")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    try:
        trades = pd.read_csv(TRADES_FILE)
    except FileNotFoundError:
        print(f"{TRADES_FILE} not found. Run run_all.py first.")
        return False

    try:
        walk_forward = pd.read_csv(WALK_FORWARD_FILE)
    except FileNotFoundError:
        print(f"{WALK_FORWARD_FILE} not found. Run walk_forward.py first.")
        return False

    if trades.empty:
        print("No trades found.")
        return False

    if walk_forward.empty:
        print("No walk-forward results found.")
        return False

    total_trades = len(trades)
    total_profit_loss = trades["profit_loss"].sum()
    final_balance = trades["balance"].iloc[-1]

    highest_balance = trades["balance"].cummax()
    drawdown = trades["balance"] - highest_balance
    max_drawdown = drawdown.min()

    walk = walk_forward.iloc[0]

    testing_profit = float(walk["testing_profit_loss"])
    testing_win_rate = float(walk["testing_win_rate"])
    testing_trades = int(walk["testing_total_trades"])
    testing_drawdown = float(walk["testing_max_drawdown"])

    warnings = []
    score = 0

    if total_profit_loss > 0:
        score += 1
    else:
        warnings.append("Backtest profit is negative.")

    if testing_profit > 0:
        score += 2
    else:
        warnings.append("Walk-forward testing profit is negative. This suggests overfitting.")

    if testing_win_rate >= 45:
        score += 1
    else:
        warnings.append("Testing win rate is low.")

    if testing_trades >= 5:
        score += 1
    else:
        warnings.append("Testing trade count is too low to trust the result.")

    if abs(testing_drawdown) <= 50:
        score += 1
    else:
        warnings.append("Testing drawdown is too high.")

    if abs(max_drawdown) <= 80:
        score += 1
    else:
        warnings.append("Backtest drawdown is high.")

    if score >= 6:
        status = "READY FOR DEMO SIGNAL TESTING"
        decision = "The bot can be tested on a demo account in signal-only mode."
    elif score >= 4:
        status = "CAUTION"
        decision = "The bot needs more testing before demo trading."
    else:
        status = "NOT READY"
        decision = "Do not connect this bot to trading execution yet."

    report = f"""
Bot Readiness Report
--------------------

Status: {status}

Decision:
{decision}

Score:
{score}/7

Backtest Summary
----------------
Total Trades: {total_trades}
Total Profit/Loss: ${round(total_profit_loss, 2)}
Final Balance: ${round(final_balance, 2)}
Max Drawdown: ${round(max_drawdown, 2)}

Walk-Forward Summary
--------------------
Testing Trades: {testing_trades}
Testing Profit/Loss: ${round(testing_profit, 2)}
Testing Win Rate: {round(testing_win_rate, 2)}%
Testing Max Drawdown: ${round(testing_drawdown, 2)}

Warnings
--------
"""

    if warnings:
        for warning in warnings:
            report += f"- {warning}\n"
    else:
        report += "- No major warnings found.\n"

    report += """
Important Note
--------------
This readiness report does not guarantee profitability.
It only helps decide whether the bot is safe enough for demo signal testing.
Real trading should not be used at this stage.
"""

    print(report)

    with open(READINESS_FILE, "w") as file:
        file.write(report)

    print(f"Readiness report saved to {READINESS_FILE}")

    return True


if __name__ == "__main__":
    check_bot_readiness()