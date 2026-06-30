import os

from config import DATA_FILE, TRADES_FILE
from download_data import download_forex_data
from backtester import run_backtest
from performance_report import generate_report
from chart import plot_trades
from strategy_comparison import compare_strategies
from optimizer import run_optimizer
from bot_logger import setup_logger
from multi_pair_tester import compare_pairs

logger = setup_logger()


def check_file_exists(file_name):
    if not os.path.exists(file_name):
        logger.error(f"{file_name} does not exist.")
        return False

    return True


def run_step(step_name, function):
    logger.info(step_name)
    logger.info("-" * len(step_name))

    try:
        result = function()

        if result is False:
            logger.error(f"{step_name} failed.")
            return False

        return True

    except Exception as error:
        logger.error(f"{step_name} crashed with an error: {error}")
        return False


def run_all():
    logger.info("==============================")
    logger.info("FOREX BOT FULL TEST STARTED")
    logger.info("==============================")

    data_downloaded = run_step("Step 1: Downloading data", download_forex_data)

    if not data_downloaded:
        logger.error("Stopping system because data download failed.")
        return

    if not check_file_exists(DATA_FILE):
        logger.error("Stopping system because data file is missing.")
        return

    backtest_completed = run_step("Step 2: Running backtest", run_backtest)

    if not backtest_completed:
        logger.error("Stopping system because backtest failed.")
        return

    if not check_file_exists(TRADES_FILE):
        logger.error("Stopping system because trades file is missing.")
        return

    report_completed = run_step("Step 3: Generating report", generate_report)

    if not report_completed:
        logger.warning("Report failed, but the system will still try to continue.")

    chart_completed = run_step("Step 4: Creating chart", plot_trades)

    if not chart_completed:
        logger.warning("Chart creation failed.")

    comparison_completed = run_step("Step 5: Comparing strategies", compare_strategies)

    if not comparison_completed:
        logger.warning("Strategy comparison failed.")

    optimizer_completed = run_step("Step 6: Optimizing strategy settings", run_optimizer)

    if not optimizer_completed:
        logger.warning("Strategy optimization failed.")

    multi_pair_completed = run_step("Step 7: Testing multiple currency pairs", compare_pairs)

    if not multi_pair_completed:
        logger.warning("Multi-pair testing failed.")

    logger.info("==============================")
    logger.info("FOREX BOT FULL TEST COMPLETED")
    logger.info("==============================")


if __name__ == "__main__":
    run_all()