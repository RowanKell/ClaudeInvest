"""
Test ML Prediction System with Real Market Data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

from ml_prediction_system import MLTradingSystem, FeatureEngineer
from real_data_provider import get_data_provider
from config import ML_CONFIG as CONFIG


def analyze_stock_ml_real(ticker, data, config):
    """Analyze stock using ML with real data"""
    print(f"\n{'='*60}")
    print(f"ML Analysis for {ticker} - REAL DATA")
    print(f"{'='*60}")

    # Initialize system
    ml_system = MLTradingSystem(config)

    # Prepare data
    print("Preparing data and engineering features...")
    X, y, df = ml_system.prepare_data(data)

    print(f"Dataset size: {len(X)} samples")
    print(f"Number of features: {len(ml_system.feature_columns)}")
    print(f"Class distribution: Up={y.sum()} ({y.sum()/len(y)*100:.1f}%), Down={len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")

    # Split data: Train on first 80%, test on last 20%
    split_idx = int(len(X) * config['train_test_split'])
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Training set: {len(X_train)} samples ({X_train.index[0].strftime('%Y-%m-%d')} to {X_train.index[-1].strftime('%Y-%m-%d')})")
    print(f"Test set: {len(X_test)} samples ({X_test.index[0].strftime('%Y-%m-%d')} to {X_test.index[-1].strftime('%Y-%m-%d')})")

    # Scale features
    X_train_scaled = ml_system.scaler.fit_transform(X_train)
    X_test_scaled = ml_system.scaler.transform(X_test)

    # Train models
    ml_system.train_models(X_train_scaled, y_train)

    # Evaluate models
    print("\nEvaluating models on test set...")
    results = ml_system.evaluate_models(X_test_scaled, y_test)

    for name, result in results.items():
        print(f"  {name}: Accuracy = {result['accuracy']:.2%}")

    # Ensemble prediction
    from sklearn.metrics import accuracy_score
    ensemble_pred, ensemble_prob = ml_system.ensemble_predict(X_test_scaled)
    ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
    print(f"  Ensemble: Accuracy = {ensemble_accuracy:.2%}")

    # Backtest strategy
    print("\nBacktesting ML strategy...")
    test_data = df.iloc[split_idx:].copy()
    backtest_results = ml_system.backtest_strategy(
        test_data,
        ensemble_pred,
        ensemble_prob,
        config['initial_capital']
    )

    # Print results
    print(f"\nBacktest Results:")
    print(f"Period: {test_data.index[0].strftime('%Y-%m-%d')} to {test_data.index[-1].strftime('%Y-%m-%d')}")
    print(f"Initial Price: ${test_data.iloc[0]['Close']:.2f}")
    print(f"Final Price: ${test_data.iloc[-1]['Close']:.2f}")

    buy_hold_return = ((test_data.iloc[-1]['Close'] - test_data.iloc[0]['Close']) / test_data.iloc[0]['Close'] * 100)
    print(f"Buy & Hold Return: {buy_hold_return:.2f}%")

    print(f"\nML Strategy Performance:")
    print(f"Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"Final Capital: ${backtest_results['final_capital']:,.2f}")
    print(f"Total Return: {backtest_results['total_return']:.2f}%")
    print(f"Number of Trades: {len(backtest_results['trades'])}")

    # Performance vs Buy & Hold
    outperformance = backtest_results['total_return'] - buy_hold_return
    print(f"Outperformance vs Buy & Hold: {outperformance:+.2f}%")

    if len(backtest_results['trades']) > 0:
        trades_df = pd.DataFrame(backtest_results['trades'])
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        if len(winning_trades) > 0:
            print(f"\nWinning Trades: {len(winning_trades)} (Avg: {winning_trades['pnl_pct'].mean():.2f}%)")
        if len(losing_trades) > 0:
            print(f"Losing Trades: {len(losing_trades)} (Avg: {losing_trades['pnl_pct'].mean():.2f}%)")

        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        print(f"Win Rate: {win_rate:.1f}%")

        # Show sample trades
        print(f"\nRecent Trades (last 5):")
        print(trades_df.tail(5)[['date', 'type', 'price', 'confidence', 'pnl_pct']].to_string(index=False))

    return backtest_results, ensemble_accuracy, buy_hold_return


def main():
    """Main function for ML testing with real data"""
    print("="*60)
    print("ML PREDICTION SYSTEM - REAL DATA TEST")
    print("="*60)

    # Initialize data provider
    print("\nInitializing data provider...")
    data_provider = get_data_provider()

    # Test configuration
    test_tickers = ['AAPL', 'MSFT', 'TSLA']  # Start with 3 stocks
    start_date = '2023-01-01'  # Need more data for ML (2 years)
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"\nTest Configuration:")
    print(f"  Tickers: {', '.join(test_tickers)}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Initial Capital: ${CONFIG['initial_capital']:,.2f} per stock")
    print(f"  ML Models: Random Forest, XGBoost, Gradient Boosting")

    # Fetch data
    print(f"\n{'='*60}")
    print("Fetching Real Market Data...")
    print(f"{'='*60}")

    stock_data = {}
    for ticker in test_tickers:
        try:
            data = data_provider.fetch_data(ticker, start_date, end_date)
            if len(data) < 200:  # ML needs sufficient data
                print(f"⚠ {ticker}: Insufficient data ({len(data)} days), skipping")
                continue
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
    print("Training ML Models and Running Backtests...")
    print(f"{'='*60}")

    all_results = {}
    accuracies = {}
    buy_hold_returns = {}

    for ticker, data in stock_data.items():
        try:
            results, accuracy, buy_hold = analyze_stock_ml_real(ticker, data, CONFIG)
            all_results[ticker] = results
            accuracies[ticker] = accuracy
            buy_hold_returns[ticker] = buy_hold
        except Exception as e:
            print(f"\n⚠ Error analyzing {ticker}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Summary
    if all_results:
        print(f"\n{'='*60}")
        print("SUMMARY - ML Strategy with REAL DATA")
        print(f"{'='*60}")
        print(f"{'Ticker':<10} {'Accuracy':<12} {'Final $':<15} {'Return %':<12} {'vs B&H':<12} {'Trades':<10}")
        print("-"*60)

        for ticker in all_results.keys():
            results = all_results[ticker]
            accuracy = accuracies[ticker]
            buy_hold = buy_hold_returns[ticker]
            outperformance = results['total_return'] - buy_hold

            symbol = "🟢" if outperformance > 0 else ("🔴" if outperformance < 0 else "⚪")

            print(f"{ticker:<10} {accuracy:<11.1%} ${results['final_capital']:<14,.2f} "
                  f"{results['total_return']:<11.2f}% {symbol} {outperformance:<10.2f}% {len(results['trades']):<10}")

        # Aggregate statistics
        avg_accuracy = np.mean(list(accuracies.values()))
        avg_return = np.mean([r['total_return'] for r in all_results.values()])
        avg_buy_hold = np.mean(list(buy_hold_returns.values()))
        total_final = np.sum([r['final_capital'] for r in all_results.values()])
        total_initial = CONFIG['initial_capital'] * len(all_results)
        portfolio_return = ((total_final - total_initial) / total_initial) * 100

        print("-"*60)
        print(f"Average Model Accuracy: {avg_accuracy:.1%}")
        print(f"Average Strategy Return: {avg_return:.2f}%")
        print(f"Average Buy & Hold Return: {avg_buy_hold:.2f}%")
        print(f"Strategy Outperformance: {avg_return - avg_buy_hold:+.2f}%")
        print(f"\nTotal Portfolio Value: ${total_final:,.2f} (from ${total_initial:,.2f})")
        print(f"Overall Portfolio Return: {portfolio_return:.2f}%")

        # Count stocks that beat buy & hold
        beat_bh = sum(1 for ticker in all_results.keys() if all_results[ticker]['total_return'] > buy_hold_returns[ticker])
        print(f"\nStocks that beat Buy & Hold: {beat_bh}/{len(all_results)}")

        # Analysis
        print(f"\n{'='*60}")
        print("ANALYSIS")
        print(f"{'='*60}")

        if avg_accuracy > 0.55:
            print("✓ Model accuracy is above random (>55%) - showing predictive power")
        elif avg_accuracy > 0.52:
            print("⚠ Model accuracy is slightly above random - marginal predictive power")
        else:
            print("✗ Model accuracy near random - consider more features or different approach")

        if portfolio_return > avg_buy_hold:
            print("✓ ML strategy outperformed buy & hold overall")
        else:
            print("✗ ML strategy underperformed buy & hold - needs improvement")

        if beat_bh > len(all_results) / 2:
            print(f"✓ ML strategy beat buy & hold on majority of stocks ({beat_bh}/{len(all_results)})")
        else:
            print(f"✗ ML strategy underperformed on most stocks ({len(all_results) - beat_bh}/{len(all_results)})")

    print("\n" + "="*60)
    print("Real data test complete!")
    print("="*60)


if __name__ == "__main__":
    main()
