import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from multi_pair_tester import compare_pairs

from config import (
    DATA_FILE,
    TRADES_FILE,
    REPORT_FILE,
    CHART_FILE,
    COMPARISON_FILE,
    OPTIMIZATION_FILE,
    SYMBOL,
    PERIOD,
    INTERVAL,
    STRATEGY_NAME,
    ACCOUNT_BALANCE,
    RISK_PERCENT,
    STOP_LOSS_PIPS,
    TAKE_PROFIT_PIPS,
    SPREAD_PIPS,
    MAX_TRADES_PER_DAY,
    DAILY_LOSS_LIMIT_PERCENT,
    MULTI_PAIR_FILE,
    WALK_FORWARD_FILE,
    READINESS_FILE,
)


st.set_page_config(
    page_title="Forex Bot Dashboard",
    page_icon="📈",
    layout="wide"
)


def add_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #111827 0%, #020617 60%);
        }

        .main-title {
            text-align: center;
            color: #37E3DD;
            font-size: 42px;
            font-weight: 800;
            text-shadow: 0 0 18px rgba(55, 227, 221, 0.8);
            margin-bottom: 5px;
        }

        .sub-title {
            text-align: center;
            color: #CBD5E1;
            font-size: 18px;
            margin-bottom: 30px;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #111827, #1E293B);
            border: 1px solid rgba(55, 227, 221, 0.25);
            padding: 18px;
            border-radius: 18px;
            box-shadow: 0 0 18px rgba(55, 227, 221, 0.08);
        }

        div[data-testid="stMetricLabel"] {
            color: #94A3B8;
        }

        div[data-testid="stMetricValue"] {
            color: #F8FAFC;
            font-size: 26px;
            font-weight: 700;
        }

        h2, h3 {
            color: #37E3DD;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #111827;
            border-radius: 12px;
            padding: 10px 18px;
            color: #CBD5E1;
            border: 1px solid rgba(55, 227, 221, 0.2);
        }

        .stTabs [aria-selected="true"] {
            background-color: #1E293B;
            color: #37E3DD;
            border: 1px solid #37E3DD;
        }

        footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def file_exists(file_path):
    return os.path.exists(file_path)


def load_csv(file_path):
    if file_exists(file_path):
        return pd.read_csv(file_path)

    return None

def show_download_buttons():
    st.sidebar.subheader("⬇️ Download Results")

    files = {
        "Download Trades CSV": TRADES_FILE,
        "Download Report TXT": REPORT_FILE,
        "Download Chart PNG": CHART_FILE,
        "Download Strategy Comparison CSV": COMPARISON_FILE,
        "Download Optimization CSV": OPTIMIZATION_FILE,
        "Download Multi-Pair Results CSV": MULTI_PAIR_FILE,
        "Download Walk-Forward CSV": WALK_FORWARD_FILE,
        "Download Readiness Report TXT": READINESS_FILE,
    }

    for label, file_path in files.items():
        if file_exists(file_path):
            with open(file_path, "rb") as file:
                st.sidebar.download_button(
                    label=label,
                    data=file,
                    file_name=os.path.basename(file_path),
                    mime="application/octet-stream"
                )


def run_python_script(script_name, timeout=900):
    """
    Runs a Python script using the same Python environment as Streamlit.
    """
    try:
        process = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = process.stdout

        if process.stderr:
            output += "\n\nERRORS:\n" + process.stderr

        return process.returncode, output

    except subprocess.TimeoutExpired:
        return 1, f"{script_name} took too long and was stopped."

    except Exception as error:
        return 1, str(error)


def show_sidebar_controls():
    st.sidebar.title("Control Panel")

    st.sidebar.write("Run bot tools directly from the dashboard.")

    if "last_command_output" not in st.session_state:
        st.session_state.last_command_output = ""

    if st.sidebar.button("Run Full Bot Test"):
        with st.spinner("Running full bot test..."):
            code, output = run_python_script("run_all.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Full bot test completed.")
        else:
            st.sidebar.error("Full bot test failed.")

    if st.sidebar.button("Download Data Only"):
        with st.spinner("Downloading data..."):
            code, output = run_python_script("download_data.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Data downloaded.")
        else:
            st.sidebar.error("Download failed.")

    if st.sidebar.button("Run Backtest Only"):
        with st.spinner("Running backtest..."):
            code, output = run_python_script("backtester.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Backtest completed.")
        else:
            st.sidebar.error("Backtest failed.")

    if st.sidebar.button("Run Optimizer Only"):
        with st.spinner("Running optimizer..."):
            code, output = run_python_script("optimizer.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Optimizer completed.")
        else:
            st.sidebar.error("Optimizer failed.")

    if st.sidebar.button("Run Walk-Forward Test"):
        with st.spinner("Running walk-forward test..."):
            code, output = run_python_script("walk_forward.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Walk-forward test completed.")
        else:
            st.sidebar.error("Walk-forward test failed.")

    if st.sidebar.button("Test Multiple Pairs"):
        with st.spinner("Testing multiple currency pairs..."):
            code, output = run_python_script("multi_pair_tester.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Multi-pair test completed.")
        else:
            st.sidebar.error("Multi-pair test failed.")

    if st.sidebar.button("Run Readiness Check"):
        with st.spinner("Checking bot readiness..."):
            code, output = run_python_script("readiness_check.py")

        st.session_state.last_command_output = output

        if code == 0:
            st.sidebar.success("Readiness check completed.")
        else:
            st.sidebar.error("Readiness check failed.")

    if st.sidebar.button("Refresh Dashboard"):
        st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("Generated Files")

    files = {
        "Market Data": DATA_FILE,
        "Trades": TRADES_FILE,
        "Report": REPORT_FILE,
        "Chart": CHART_FILE,
        "Comparison": COMPARISON_FILE,
        "Optimization": OPTIMIZATION_FILE,
        "Multi-Pair": MULTI_PAIR_FILE,
        "Walk Forward": WALK_FORWARD_FILE,
        "Readiness": READINESS_FILE,
    }

    for name, path in files.items():
        if file_exists(path):
            st.sidebar.success(f"{name}: Found")
        else:
            st.sidebar.warning(f"{name}: Missing")

    st.sidebar.divider()

    show_download_buttons()

    st.sidebar.divider()

    if st.session_state.last_command_output:
         with st.sidebar.expander("Last Command Output"):
            st.code(st.session_state.last_command_output)


def show_project_settings():
    st.subheader("Bot Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Symbol", SYMBOL)
        st.metric("Period", PERIOD)
        st.metric("Interval", INTERVAL)

    with col2:
        st.metric("Strategy", STRATEGY_NAME)
        st.metric("Account Balance", f"${ACCOUNT_BALANCE}")
        st.metric("Risk Per Trade", f"{RISK_PERCENT}%")

    with col3:
        st.metric("Stop Loss", f"{STOP_LOSS_PIPS} pips")
        st.metric("Take Profit", f"{TAKE_PROFIT_PIPS} pips")
        st.metric("Spread", f"{SPREAD_PIPS} pips")


def show_trade_summary(trades):
    st.subheader("Trade Summary")

    if trades is None or trades.empty:
        st.warning("No trades found. Run the full bot test first.")
        return

    total_trades = len(trades)
    winning_trades = trades[trades["profit_loss"] > 0]
    losing_trades = trades[trades["profit_loss"] < 0]

    win_rate = 0

    if total_trades > 0:
        win_rate = (len(winning_trades) / total_trades) * 100

    total_profit_loss = trades["profit_loss"].sum()
    final_balance = trades["balance"].iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Trades", total_trades)

    with col2:
        st.metric("Win Rate", f"{round(win_rate, 2)}%")

    with col3:
        st.metric("Profit / Loss", f"${round(total_profit_loss, 2)}")

    with col4:
        st.metric("Final Balance", f"${round(final_balance, 2)}")

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Winning Trades", len(winning_trades))

    with col6:
        st.metric("Losing Trades", len(losing_trades))

    with col7:
        st.metric("Max Trades Per Day", MAX_TRADES_PER_DAY)


def show_report():
    st.subheader("Performance Report")

    if not file_exists(REPORT_FILE):
        st.warning("No report found. Run the full bot test first.")
        return

    with open(REPORT_FILE, "r") as file:
        report = file.read()

    st.text(report)


def show_chart():
    st.subheader("Backtest Chart")

    if not file_exists(CHART_FILE):
        st.warning("No chart found. Run the full bot test first.")
        return

    st.image(CHART_FILE, caption="Backtest Chart")


def show_trades_table(trades):
    st.subheader("Trade History")

    if trades is None or trades.empty:
        st.warning("No trade history found.")
        return

    st.dataframe(trades, use_container_width=True)


def show_strategy_comparison():
    st.subheader("Strategy Comparison")

    comparison = load_csv(COMPARISON_FILE)

    if comparison is None or comparison.empty:
        st.warning("No strategy comparison found. Run the full bot test first.")
        return

    st.dataframe(comparison, use_container_width=True)

    best_strategy = comparison.sort_values(
        by="total_profit_loss",
        ascending=False
    ).iloc[0]

    st.success(
        f"Best strategy: {best_strategy['strategy']} "
        f"with profit/loss ${best_strategy['total_profit_loss']}"
    )

def show_multi_pair_results():
    st.subheader("Multi-Pair Results")

    multi_pair = load_csv(MULTI_PAIR_FILE)

    if multi_pair is None or multi_pair.empty:
        st.warning("No multi-pair results found. Run the multi-pair test first.")
        return

    st.dataframe(multi_pair, use_container_width=True)

    best_result = multi_pair.sort_values(
        by="total_profit_loss",
        ascending=False
    ).iloc[0]

    st.success(
        f"Best result: {best_result['pair']} using {best_result['strategy']} | "
        f"Profit/Loss: ${best_result['total_profit_loss']} | "
        f"Win Rate: {best_result['win_rate']}%"
    )


def show_optimization_results():
    st.subheader("Optimization Results")

    optimization = load_csv(OPTIMIZATION_FILE)

    if optimization is None or optimization.empty:
        st.warning("No optimization results found. Run the full bot test first.")
        return

    st.dataframe(optimization, use_container_width=True)

    best_settings = optimization.sort_values(
        by="total_profit_loss",
        ascending=False
    ).iloc[0]

    st.success(
        f"Best settings: {best_settings['strategy']} | "
        f"{best_settings['settings']} | "
        f"Profit/Loss: ${best_settings['total_profit_loss']}"
    )


def show_market_data():
    st.subheader("Downloaded Market Data")

    data = load_csv(DATA_FILE)

    if data is None or data.empty:
        st.warning("No market data found. Run the full bot test first.")
        return

    st.dataframe(data.tail(100), use_container_width=True)

def show_equity_curve(trades):
    st.subheader("Equity Curve and Drawdown")

    if trades is None or trades.empty:
        st.warning("No trades found. Run the full bot test first.")
        return

    if "exit_time" not in trades.columns or "balance" not in trades.columns:
        st.warning("Trades file does not have exit_time or balance columns.")
        return

    equity = trades[["exit_time", "balance"]].copy()
    equity["exit_time"] = pd.to_datetime(equity["exit_time"])
    equity = equity.sort_values("exit_time")
    equity = equity.set_index("exit_time")

    highest_balance = equity["balance"].cummax()
    drawdown = equity["balance"] - highest_balance

    max_drawdown = drawdown.min()
    final_balance = equity["balance"].iloc[-1]
    highest_account_balance = equity["balance"].max()
    lowest_account_balance = equity["balance"].min()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Final Balance", f"${round(final_balance, 2)}")

    with col2:
        st.metric("Highest Balance", f"${round(highest_account_balance, 2)}")

    with col3:
        st.metric("Max Drawdown", f"${round(max_drawdown, 2)}")

    st.write("### Equity Curve")
    st.line_chart(equity["balance"])

    drawdown_df = pd.DataFrame({
        "drawdown": drawdown
    })

    st.write("### Drawdown")
    st.line_chart(drawdown_df)

    st.write(
        "The equity curve shows account balance after each closed trade. "
        "The drawdown chart shows how much the account dropped from its previous highest balance."
    )
    
def show_walk_forward_results():
    st.subheader("Walk-Forward Results")

    walk_forward = load_csv(WALK_FORWARD_FILE)

    if walk_forward is None or walk_forward.empty:
        st.warning("No walk-forward results found. Run the walk-forward test first.")
        return

    st.dataframe(walk_forward, use_container_width=True)

    result = walk_forward.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Best Strategy", result["best_strategy"])

    with col2:
        st.metric("Training Profit", f"${result['training_profit_loss']}")

    with col3:
        st.metric("Testing Profit", f"${result['testing_profit_loss']}")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Training Win Rate", f"{result['training_win_rate']}%")

    with col5:
        st.metric("Testing Win Rate", f"{result['testing_win_rate']}%")

    with col6:
        st.metric("Testing Profit Factor", result["testing_profit_factor"])

    st.write("### Meaning")

    training_profit = float(result["training_profit_loss"])
    testing_profit = float(result["testing_profit_loss"])

    if testing_profit > 0 and testing_profit >= training_profit * 0.5:
        st.success(
            "The strategy looks more stable because it still performed reasonably on unseen data."
        )

    elif testing_profit > 0:
        st.warning(
            "The strategy made profit on unseen data, but testing performance is much weaker than training performance."
        )

    else:
        st.error(
            "The strategy failed on unseen data. This may indicate overfitting."
        )

    st.info(
        "Walk-forward testing checks if optimized settings still work on future data that the optimizer did not see."
    )

def show_readiness_report():
    st.subheader("Bot Readiness Report")

    if not file_exists(READINESS_FILE):
        st.warning("No readiness report found. Run the readiness check first.")
        return

    with open(READINESS_FILE, "r") as file:
        readiness_report = file.read()

    if "READY FOR DEMO SIGNAL TESTING" in readiness_report:
        st.success("Status: READY FOR DEMO SIGNAL TESTING")
    elif "CAUTION" in readiness_report:
        st.warning("Status: CAUTION")
    elif "NOT READY" in readiness_report:
        st.error("Status: NOT READY")
    else:
        st.info("Status found in report below.")

    st.text(readiness_report)

    st.info(
        "This readiness report does not mean the bot is guaranteed to be profitable. "
        "It only checks whether the strategy is safe enough for demo signal testing."
    )

def main():
    add_custom_css()
    show_sidebar_controls()

    st.markdown(
        "<h1 class='main-title'>📈 Forex Bot Dashboard</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='sub-title'>Backtesting dashboard for your Python forex bot</p>",
        unsafe_allow_html=True
    )

    trades = load_csv(TRADES_FILE)

    show_project_settings()

    st.divider()

    show_trade_summary(trades)

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "Report",
    "Chart",
    "Equity Curve",
    "Trades",
    "Strategy Comparison",
    "Optimization",
    "Multi-Pair",
    "Walk-Forward",
    "Readiness",
    "Market Data"
   ])

    with tab1:
        show_report()

    with tab2:
        show_chart()

    with tab3:
        show_equity_curve(trades)

    with tab4:
        show_trades_table(trades)

    with tab5:
        show_strategy_comparison()

    with tab6:
        show_optimization_results()

    with tab7:
        show_multi_pair_results()

    with tab8:
        show_walk_forward_results()

    with tab9:
        show_readiness_report()

    with tab10:
        show_market_data()


if __name__ == "__main__":
    main()