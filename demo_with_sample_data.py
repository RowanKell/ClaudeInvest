"""
Demo of both trading systems using sample data
This demonstrates how the systems work with realistic price movements
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from technical_analysis_bot import TechnicalIndicators, TradingSignals, Backtester
from config import TECHNICAL_ANALYSIS_CONFIG as CONFIG


def generate_sample_stock_data(ticker, days=365, start_price=100, trend='up', volatility=0.02):
    """
    Generate realistic sample stock data with cyclical patterns
    ticker: stock symbol
    days: number of trading days
    start_price: initial stock price
    trend: 'up', 'down', or 'sideways'
    volatility: daily volatility (0.02 = 2%)
    """
    np.random.seed(hash(ticker) % 10000)  # Reproducible but different per ticker

    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    prices = [start_price]

    # Trend parameters
    if trend == 'up':
        drift = 0.001  # 0.1% daily upward drift
    elif trend == 'down':
        drift = -0.001
    else:
        drift = 0

    for i in range(1, days):
        # Add cyclical component to create more realistic patterns
        cycle = 0.003 * np.sin(i / 30)  # ~30-day cycle
        # Generate price movement with trend, cycle, and noise
        change = drift + cycle + np.random.normal(0, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)

    # Create OHLCV data
    df = pd.DataFrame(index=dates)
    df['Close'] = prices
    df['Open'] = df['Close'] * (1 + np.random.uniform(-0.01, 0.01, days))
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, days))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, days))
    df['Volume'] = np.random.randint(1000000, 10000000, days)

    return df


def analyze_sample_stock(ticker, data, config):
    """Analyze sample stock data"""
    print(f"\n{'='*60}")
    print(f"Analyzing {ticker}")
    print(f"{'='*60}")

    # Generate signals
    signal_generator = TradingSignals(config)
    signals = signal_generator.generate_signals(data)

    # Run backtest
    backtester = Backtester(
        config['initial_capital'],
        config['stop_loss_pct'],
        config['take_profit_pct']
    )
    results = backtester.run_backtest(signals)

    # Print results
    print(f"\nBacktest Results for {ticker}:")
    print(f"Period: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"Initial Price: ${data.iloc[0]['Close']:.2f}")
    print(f"Final Price: ${data.iloc[-1]['Close']:.2f}")
    print(f"Buy & Hold Return: {((data.iloc[-1]['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close'] * 100):.2f}%")
    print(f"\nStrategy Performance:")
    print(f"Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"Final Capital: ${results['final_capital']:,.2f}")
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Number of Trades: {len(results['trades'])}")

    if len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        if len(winning_trades) > 0:
            print(f"Winning Trades: {len(winning_trades)} (Avg: {winning_trades['pnl_pct'].mean():.2f}%)")
        if len(losing_trades) > 0:
            print(f"Losing Trades: {len(losing_trades)} (Avg: {losing_trades['pnl_pct'].mean():.2f}%)")

        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        print(f"Win Rate: {win_rate:.1f}%")

        # Show first and last few trades
        print(f"\nFirst 3 Trades:")
        print(trades_df.head(3).to_string(index=False))

        print(f"\nLast 3 Trades:")
        print(trades_df.tail(3).to_string(index=False))

        # Current signals (last day)
        last_signal = signals.iloc[-1]
        print(f"\nCurrent Status (as of {signals.index[-1].strftime('%Y-%m-%d')}):")
        print(f"  Price: ${last_signal['price']:.2f}")
        print(f"  RSI: {last_signal['rsi']:.2f}")
        print(f"  MACD: {last_signal['macd']:.2f} | Signal: {last_signal['macd_signal']:.2f}")
        print(f"  BB Upper: ${last_signal['bb_upper']:.2f} | Middle: ${last_signal['bb_middle']:.2f} | Lower: ${last_signal['bb_lower']:.2f}")

        if last_signal['signal'] == 1:
            print(f"  🟢 SIGNAL: BUY")
        elif last_signal['signal'] == -1:
            print(f"  🔴 SIGNAL: SELL")
        else:
            print(f"  ⚪ SIGNAL: HOLD")

    return results


def main():
    """Main demo function"""
    print("="*60)
    print("TECHNICAL ANALYSIS TRADING BOT - DEMO MODE")
    print("="*60)
    print("Using simulated stock data to demonstrate system capabilities")
    print(f"Testing Period: ~1 year of daily data")
    print(f"Initial Capital: ${CONFIG['initial_capital']:,.2f}")

    # Create sample data for different stocks with different characteristics
    sample_stocks = {
        'AAPL': {'start_price': 170, 'trend': 'up', 'volatility': 0.025},
        'MSFT': {'start_price': 350, 'trend': 'up', 'volatility': 0.020},
        'GOOGL': {'start_price': 140, 'trend': 'sideways', 'volatility': 0.028},
        'AMZN': {'start_price': 145, 'trend': 'up', 'volatility': 0.030},
        'TSLA': {'start_price': 180, 'trend': 'sideways', 'volatility': 0.045},
        'NVDA': {'start_price': 450, 'trend': 'up', 'volatility': 0.038},
        'META': {'start_price': 320, 'trend': 'up', 'volatility': 0.032},
        'SPY': {'start_price': 440, 'trend': 'up', 'volatility': 0.015},
    }

    all_results = {}

    for ticker in CONFIG['watchlist']:
        if ticker in sample_stocks:
            params = sample_stocks[ticker]
            data = generate_sample_stock_data(
                ticker,
                days=500,  # More days for better pattern demonstration
                start_price=params['start_price'],
                trend=params['trend'],
                volatility=params['volatility']
            )
            results = analyze_sample_stock(ticker, data, CONFIG)
            if results:
                all_results[ticker] = results

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - All Stocks (DEMO DATA)")
    print(f"{'='*60}")
    print(f"{'Ticker':<10} {'Final Capital':<15} {'Return %':<12} {'Trades':<10}")
    print("-"*60)

    for ticker, results in all_results.items():
        print(f"{ticker:<10} ${results['final_capital']:<14,.2f} {results['total_return']:<11.2f}% {len(results['trades']):<10}")

    # Calculate average performance
    if all_results:
        avg_return = np.mean([r['total_return'] for r in all_results.values()])
        total_final = np.sum([r['final_capital'] for r in all_results.values()])
        total_initial = CONFIG['initial_capital'] * len(all_results)
        portfolio_return = ((total_final - total_initial) / total_initial) * 100

        print("-"*60)
        print(f"Average Return per Stock: {avg_return:.2f}%")
        print(f"Total Portfolio Value: ${total_final:,.2f} (from ${total_initial:,.2f})")
        print(f"Overall Portfolio Return: {portfolio_return:.2f}%")

    print("\n" + "="*60)
    print("NOTE: This is a demonstration with simulated data.")
    print("Real market results will vary and depend on many factors.")
    print("="*60)


if __name__ == "__main__":
    main()
