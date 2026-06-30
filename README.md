# Forex Bot Project

This is a beginner forex trading bot project built with Python.

The bot is currently for **backtesting and learning only**. It does not place real trades.

## Important Warning

This project is for educational purposes only.

Do not use this bot with real money until it has been properly tested on historical data and a demo account.

Forex trading is risky and can lead to financial loss.

## Features

The bot can:

* Download historical forex data
* Generate buy, sell, or no trade signals
* Backtest a moving average crossover strategy
* Backtest an RSI strategy
* Compare different strategies
* Apply basic risk management
* Use stop loss and take profit
* Include spread and commission
* Limit trades per day
* Stop trading after a daily loss limit
* Save trades to a CSV file
* Generate a performance report
* Create a chart showing price, moving averages, entries, and exits
* Save logs for debugging

## Project Structure

```text
forex_bot/
│
├── results/
│   ├── data.csv
│   ├── trades.csv
│   ├── report.txt
│   ├── backtest_chart.png
    ├── optimization_results.csv
│   └── strategy_comparison.csv
│
├── logs/
│
├── main.py
├── strategy.py
├── backtester.py
├── risk_manager.py
├── performance_report.py
├── download_data.py
├── chart.py
├── strategy_comparison.py
├── run_all.py
├── bot_logger.py
├── config.py
├── optimizer.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Files Explained

### main.py

Runs the signal bot and prints the latest trading signal.

It shows:

* Latest candle time
* Close price
* Fast moving average
* Slow moving average
* RSI, if the RSI strategy is selected
* Bot signal

### strategy.py

Contains the trading strategies.

The current strategies are:

* Moving Average crossover strategy
* RSI strategy

For the Moving Average strategy, a buy signal happens when the fast moving average crosses above the slow moving average.

A sell signal happens when the fast moving average crosses below the slow moving average.

For the RSI strategy, a buy signal happens when RSI moves back above the oversold level.

A sell signal happens when RSI moves back below the overbought level.

### backtester.py

Tests the selected strategy using historical price data.

It checks:

* Entry signals
* Stop loss
* Take profit
* Spread
* Commission
* Daily trade limits
* Daily loss limits
* Profit and loss

It saves closed trades to:

```text
results/trades.csv
```

### risk_manager.py

Calculates risk and lot size.

It uses:

* Account balance
* Risk percentage
* Stop loss size
* Pip value

### performance_report.py

Reads the trades file and prints a trading performance report.

It shows:

* Total trades
* Winning trades
* Losing trades
* Win rate
* Average win
* Average loss
* Profit factor
* Best trade
* Worst trade
* Maximum drawdown
* Final balance

The report is saved to:

```text
results/report.txt
```

### download_data.py

Downloads historical forex data using `yfinance`.

The data is saved to:

```text
results/data.csv
```

### chart.py

Creates a chart showing:

* Close price
* Fast moving average
* Slow moving average
* Buy entries
* Sell entries
* Trade exits

The chart is saved to:

```text
results/backtest_chart.png
```

### strategy_comparison.py

Compares different trading strategies using the same historical data.

It currently compares:

* Moving Average strategy
* RSI strategy

The comparison is saved to:

```text
results/strategy_comparison.csv
```

### run_all.py

Runs the full system in one command.

It runs:

```text
download_data.py
backtester.py
performance_report.py
chart.py
strategy_comparison.py
```

It creates or updates files inside the `results/` folder.

### bot_logger.py

Creates log files for the bot.

Logs are saved inside:

```text
logs/
```

### config.py

Controls the main settings of the bot.

You can change:

* Currency pair
* Timeframe
* Data period
* Selected strategy
* Moving average periods
* RSI settings
* Account balance
* Risk percentage
* Stop loss
* Take profit
* Spread
* Commission
* Maximum trades per day
* Daily loss limit

### optimizer.py

Tests different strategy settings to find which settings performed best during backtesting.

It tests settings for:

- Moving Average strategy
- RSI strategy

The optimization results are saved to:

```text
results/optimization_results.csv

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## Requirements

The `requirements.txt` file should contain:

```txt
pandas
yfinance
matplotlib
```

## How to Run the Full Bot Test

Run:

```bash
python run_all.py
```

This will:

1. Download forex data
2. Run the backtest
3. Save trades to `results/trades.csv`
4. Generate a performance report
5. Save the report to `results/report.txt`
6. Create a chart
7. Save the chart to `results/backtest_chart.png`
8. Compare strategies
9. Save the strategy comparison to `results/strategy_comparison.csv`
10. Save logs inside the `logs/` folder

## How to Run Individual Files

Download data:

```bash
python download_data.py
```

Run the signal bot:

```bash
python main.py
```

Run the backtester:

```bash
python backtester.py
```

Generate performance report:

```bash
python performance_report.py
```

Generate chart:

```bash
python chart.py
```

Compare strategies:

```bash
python strategy_comparison.py
```

## Current Strategies

The bot currently supports two strategies:

```text
MOVING_AVERAGE
RSI
```

You can change the selected strategy in `config.py`.

Example:

```python
STRATEGY_NAME = "MOVING_AVERAGE"
```

or:

```python
STRATEGY_NAME = "RSI"
```

## Moving Average Strategy

Default settings:

```python
FAST_MA_PERIOD = 5
SLOW_MA_PERIOD = 10
```

Buy rule:

```text
Fast moving average crosses above slow moving average
```

Sell rule:

```text
Fast moving average crosses below slow moving average
```

## RSI Strategy

Default settings:

```python
RSI_PERIOD = 14
RSI_BUY_LEVEL = 30
RSI_SELL_LEVEL = 70
```

Buy rule:

```text
RSI crosses back above the oversold level
```

Sell rule:

```text
RSI crosses back below the overbought level
```

## Risk Settings

Default risk settings:

```python
ACCOUNT_BALANCE = 1000
RISK_PERCENT = 1

STOP_LOSS_PIPS = 20
TAKE_PROFIT_PIPS = 40

SPREAD_PIPS = 2
COMMISSION_PER_TRADE = 0

MAX_TRADES_PER_DAY = 3
DAILY_LOSS_LIMIT_PERCENT = 3
```

This means:

* Starting balance is $1000
* Risk per trade is 1%
* Stop loss is 20 pips
* Take profit is 40 pips
* Spread is 2 pips
* Maximum trades per day is 3
* Bot stops trading for the day after losing 3%

## Changing the Currency Pair

Open `config.py`.

To test EUR/USD:

```python
SYMBOL = "EURUSD=X"
```

To test GBP/USD:

```python
SYMBOL = "GBPUSD=X"
```

To test AUD/USD:

```python
SYMBOL = "AUDUSD=X"
```

To test USD/JPY:

```python
SYMBOL = "JPY=X"
```

After changing the symbol, run:

```bash
python run_all.py
```

## Generated Results

The bot saves generated output files inside the `results/` folder.

```text
results/data.csv
```

Stores downloaded forex price data.

```text
results/trades.csv
```

Stores all closed backtest trades.

```text
results/report.txt
```

Stores the performance report.

```text
results/backtest_chart.png
```

Stores the backtest chart.

```text
results/strategy_comparison.csv
```

Stores the comparison between different strategies.

These files are generated automatically and should not be uploaded to GitHub.

## Logs

The bot saves activity and error messages inside the `logs/` folder.

Example:

```text
logs/bot_2026-06-19.log
```

The `logs/` folder should not be uploaded to GitHub.

## GitHub Upload Notes

Upload the source code and documentation only.

Upload these files:

```text
main.py
strategy.py
backtester.py
risk_manager.py
performance_report.py
download_data.py
chart.py
strategy_comparison.py
run_all.py
bot_logger.py
config.py
requirements.txt
README.md
.gitignore
```

Do not upload:

```text
.venv/
results/
logs/
__pycache__/
.env
```

These files and folders should be ignored by `.gitignore`.

## Current Status

Current version:

```text
Backtesting only
No real trades
No broker connection
Safe for learning
```

## Future Improvements

Possible future improvements:

* Add breakout strategy
* Add support and resistance strategy
* Add trailing stop loss
* Add multiple currency pairs
* Add better chart labels
* Add Telegram alerts
* Connect to MetaTrader 5 demo account
* Add live demo trading
* Add database logging
* Add a simple dashboard
