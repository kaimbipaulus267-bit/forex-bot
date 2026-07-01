import os
import ast
import pandas as pd

from config import (
    DATA_FILE,
    RESULTS_DIR,
    WALK_FORWARD_FILE,
)

from optimizer import (
    optimize_moving_average,
    optimize_rsi,
    run_single_test,
)


TRAIN_PERCENT = 0.7


def convert_settings(settings_value):
    """
    Converts settings from text back into a Python dictionary if needed.
    """

    if isinstance(settings_value, dict):
        return settings_value

    if isinstance(settings_value, str):
        return ast.literal_eval(settings_value)

    raise ValueError("Invalid settings format.")


def run_walk_forward_test():
    print("Starting walk-forward test...")

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

    split_index = int(len(data) * TRAIN_PERCENT)

    train_data = data.iloc[:split_index].copy()
    test_data = data.iloc[split_index:].copy()

    print(f"Total candles: {len(data)}")
    print(f"Training candles: {len(train_data)}")
    print(f"Testing candles: {len(test_data)}")

    if len(train_data) < 50 or len(test_data) < 50:
        print("Not enough data for walk-forward testing.")
        return False

    print("\nOptimizing on training data...")
    training_results = []

    training_results.extend(optimize_moving_average(train_data))
    training_results.extend(optimize_rsi(train_data))

    training_df = pd.DataFrame(training_results)

    training_df = training_df.sort_values(
    by="robust_score",
    ascending=False
    )
    best_training_result = training_df.iloc[0]

    best_strategy = best_training_result["strategy"]
    best_settings = convert_settings(best_training_result["settings"])

    print("\nBest training result")
    print("--------------------")
    print(f"Strategy: {best_strategy}")
    print(f"Settings: {best_settings}")
    print(f"Training Profit/Loss: ${best_training_result['total_profit_loss']}")
    print(f"Training Win Rate: {best_training_result['win_rate']}%")

    print("\nTesting best settings on unseen data...")

    test_result = run_single_test(
        best_strategy,
        test_data,
        best_settings
    )

    result = {
    "best_strategy": best_strategy,
    "best_settings": best_settings,

    "training_total_trades": best_training_result["total_trades"],
    "training_win_rate": best_training_result["win_rate"],
    "training_profit_loss": best_training_result["total_profit_loss"],
    "training_final_balance": best_training_result["final_balance"],
    "training_max_drawdown": best_training_result["max_drawdown"],
    "training_robust_score": best_training_result["robust_score"],

    "testing_total_trades": test_result["total_trades"],
    "testing_win_rate": test_result["win_rate"],
    "testing_profit_loss": test_result["total_profit_loss"],
    "testing_final_balance": test_result["final_balance"],
    "testing_profit_factor": test_result["profit_factor"],
    "testing_max_drawdown": test_result["max_drawdown"],
    "testing_robust_score": test_result["robust_score"],
    }

    results_df = pd.DataFrame([result])
    results_df.to_csv(WALK_FORWARD_FILE, index=False)

    print("\nWalk-Forward Results")
    print("--------------------")
    print(results_df)

    print(f"\nWalk-forward results saved to {WALK_FORWARD_FILE}")

    return True


if __name__ == "__main__":
    run_walk_forward_test()