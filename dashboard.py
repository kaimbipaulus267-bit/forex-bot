import os
import pandas as pd
import streamlit as st

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
)


st.set_page_config(
    page_title="Forex Bot Dashboard",
    page_icon="📈",
    layout="wide"
)


def file_exists(file_path):
    return os.path.exists(file_path)


def load_csv(file_path):
    if file_exists(file_path):
        return pd.read_csv(file_path)

    return None


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
        st.warning("No trades found. Run python run_all.py first.")
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
        st.warning("No report found. Run python run_all.py first.")
        return

    with open(REPORT_FILE, "r") as file:
        report = file.read()

    st.text(report)


def show_chart():
    st.subheader("Backtest Chart")

    if not file_exists(CHART_FILE):
        st.warning("No chart found. Run python run_all.py first.")
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
        st.warning("No strategy comparison found. Run python run_all.py first.")
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


def show_optimization_results():
    st.subheader("Optimization Results")

    optimization = load_csv(OPTIMIZATION_FILE)

    if optimization is None or optimization.empty:
        st.warning("No optimization results found. Run python run_all.py first.")
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
        st.warning("No market data found. Run python run_all.py first.")
        return

    st.dataframe(data.tail(100), use_container_width=True)


def main():
    st.title("📈 Forex Bot Dashboard")
    st.write("Backtesting dashboard for the Python forex bot.")

    trades = load_csv(TRADES_FILE)

    show_project_settings()

    st.divider()

    show_trade_summary(trades)

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Report",
        "Chart",
        "Trades",
        "Strategy Comparison",
        "Optimization",
        "Market Data"
    ])

    with tab1:
        show_report()

    with tab2:
        show_chart()

    with tab3:
        show_trades_table(trades)

    with tab4:
        show_strategy_comparison()

    with tab5:
        show_optimization_results()

    with tab6:
        show_market_data()


if __name__ == "__main__":
    main()