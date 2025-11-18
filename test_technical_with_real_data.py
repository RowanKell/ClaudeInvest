"""
Test Technical Analysis Trading Bot with Real Market Data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

from technical_analysis_bot import TradingSignals, Backtester
from real_data_provider import get_data_provider
from config import TECHNICAL_ANALYSIS_CONFIG as CONFIG


def analyze_stock_real_data(ticker, data, config):
    """Analyze a single stock using real data"""
    print(f"\n{'='*60}")
    print(f"Analyzing {ticker} - REAL DATA")
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
    print(f"Trading Days: {len(data)}")
    print(f"Initial Price: ${data.iloc[0]['Close']:.2f}")
    print(f"Final Price: ${data.iloc[-1]['Close']:.2f}")

    buy_hold_return = ((data.iloc[-1]['Close'] - data.iloc[0]['Close']) / data.iloc[0]['Close'] * 100)
    print(f"Buy & Hold Return: {buy_hold_return:.2f}%")

    print(f"\nStrategy Performance:")
    print(f"Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"Final Capital: ${results['final_capital']:,.2f}")
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Number of Trades: {len(results['trades'])}")

    # Performance vs Buy & Hold
    outperformance = results['total_return'] - buy_hold_return
    print(f"Outperformance vs Buy & Hold: {outperformance:+.2f}%")

    if len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        if len(winning_trades) > 0:
            print(f"\nWinning Trades: {len(winning_trades)} (Avg: {winning_trades['pnl_pct'].mean():.2f}%)")
        if len(losing_trades) > 0:
            print(f"Losing Trades: {len(losing_trades)} (Avg: {losing_trades['pnl_pct'].mean():.2f}%)")

        if len(trades_df) > 0:
            win_rate = len(winning_trades) / len(trades_df) * 100
            print(f"Win Rate: {win_rate:.1f}%")

        # Show recent trades
        print(f"\nRecent Trades (last 5):")
        print(trades_df.tail(5)[['date', 'type', 'price', 'pnl_pct']].to_string(index=False))

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
    else:
        print(f"\n⚠ No trades generated - strategy conditions not met")
        print(f"   Try adjusting parameters in config.py for more signals")

    return results, buy_hold_return


def main():
    """Main function to test with real data"""
    print("="*60)
    print("TECHNICAL ANALYSIS BOT - REAL DATA TEST")
    print("="*60)

    # Initialize data provider
    print("\nInitializing data provider...")
    data_provider = get_data_provider()

    # Test configuration
    # Use shorter watchlist for initial testing to save API calls
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']  # Expand to full watchlist once working
    start_date = '2024-01-01'
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday

    print(f"\nTest Configuration:")
    print(f"  Tickers: {', '.join(test_tickers)}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Initial Capital: ${CONFIG['initial_capital']:,.2f} per stock")

    # Fetch data for all tickers
    print(f"\n{'='*60}")
    print("Fetching Real Market Data...")
    print(f"{'='*60}")

    stock_data = {}
    for ticker in test_tickers:
        try:
            data = data_provider.fetch_data(ticker, start_date, end_date)
            stock_data[ticker] = data
        except Exception as e:
            print(f"⚠ Failed to fetch {ticker}: {e}")

    if not stock_data:
        print("\n✗ No data fetched. Please check:")
        print("  1. Your internet connection")
        print("  2. API key is set (for Alpha Vantage)")
        print("  3. Ticker symbols are valid")
        sys.exit(1)

    # Analyze each stock
    print(f"\n{'='*60}")
    print("Running Backtests on Real Data...")
    print(f"{'='*60}")

    all_results = {}
    buy_hold_returns = {}

    for ticker, data in stock_data.items():
        try:
            results, buy_hold = analyze_stock_real_data(ticker, data, CONFIG)
            all_results[ticker] = results
            buy_hold_returns[ticker] = buy_hold
        except Exception as e:
            print(f"\n⚠ Error analyzing {ticker}: {e}")
            continue

    # Summary
    if all_results:
        print(f"\n{'='*60}")
        print("SUMMARY - Technical Analysis with REAL DATA")
        print(f"{'='*60}")
        print(f"{'Ticker':<10} {'Final Capital':<15} {'Return %':<12} {'vs B&H':<12} {'Trades':<10}")
        print("-"*60)

        for ticker in all_results.keys():
            results = all_results[ticker]
            buy_hold = buy_hold_returns[ticker]
            outperformance = results['total_return'] - buy_hold

            symbol = "🟢" if outperformance > 0 else ("🔴" if outperformance < 0 else "⚪")

            print(f"{ticker:<10} ${results['final_capital']:<14,.2f} {results['total_return']:<11.2f}% "
                  f"{symbol} {outperformance:<10.2f}% {len(results['trades']):<10}")

        # Calculate aggregate statistics
        avg_return = np.mean([r['total_return'] for r in all_results.values()])
        avg_buy_hold = np.mean(list(buy_hold_returns.values()))
        total_final = np.sum([r['final_capital'] for r in all_results.values()])
        total_initial = CONFIG['initial_capital'] * len(all_results)
        portfolio_return = ((total_final - total_initial) / total_initial) * 100

        print("-"*60)
        print(f"Average Strategy Return: {avg_return:.2f}%")
        print(f"Average Buy & Hold Return: {avg_buy_hold:.2f}%")
        print(f"Strategy Outperformance: {avg_return - avg_buy_hold:+.2f}%")
        print(f"\nTotal Portfolio Value: ${total_final:,.2f} (from ${total_initial:,.2f})")
        print(f"Overall Portfolio Return: {portfolio_return:.2f}%")

        # Count stocks that beat buy & hold
        beat_bh = sum(1 for ticker in all_results.keys() if all_results[ticker]['total_return'] > buy_hold_returns[ticker])
        print(f"\nStocks that beat Buy & Hold: {beat_bh}/{len(all_results)}")

    print("\n" + "="*60)
    print("Test Complete! Check COMPARISON_RESULTS.md for analysis.")
    print("="*60)


if __name__ == "__main__":
    main()
