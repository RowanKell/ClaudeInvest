"""
Machine Learning Prediction System for Stock Trading
Uses Random Forest, XGBoost, and Gradient Boosting for price prediction
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    print("XGBoost not available, using only RandomForest and GradientBoosting")
    XGBOOST_AVAILABLE = False

from config import ML_CONFIG as CONFIG


class FeatureEngineer:
    """Engineer features from stock price data"""

    @staticmethod
    def calculate_technical_indicators(data):
        """Calculate all technical indicators as features"""
        df = data.copy()

        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))

        # Moving averages
        for window in [5, 10, 20, 50]:
            df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'EMA_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()

        # Price relative to moving averages
        df['Price_to_SMA20'] = df['Close'] / df['SMA_20']
        df['Price_to_SMA50'] = df['Close'] / df['SMA_50']

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        sma_20 = df['Close'].rolling(window=20).mean()
        std_20 = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = sma_20 + (std_20 * 2)
        df['BB_Lower'] = sma_20 - (std_20 * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / sma_20
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        df['ATR'] = df[['High', 'Low', 'Close']].apply(
            lambda x: max(x['High'] - x['Low'], abs(x['High'] - x['Close']), abs(x['Low'] - x['Close'])),
            axis=1
        ).rolling(window=14).mean()

        # Volume features
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']

        # Momentum
        df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
        df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
        df['ROC'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100

        # Price channels
        df['High_20'] = df['High'].rolling(window=20).max()
        df['Low_20'] = df['Low'].rolling(window=20).min()
        df['Channel_Position'] = (df['Close'] - df['Low_20']) / (df['High_20'] - df['Low_20'])

        return df

    @staticmethod
    def create_target(data, horizon=1):
        """
        Create target variable: 1 if price goes up tomorrow, 0 otherwise
        horizon: number of days to look ahead
        """
        df = data.copy()
        df['Future_Return'] = df['Close'].shift(-horizon) / df['Close'] - 1
        df['Target'] = (df['Future_Return'] > 0).astype(int)
        return df


class MLTradingSystem:
    """Machine Learning based trading system"""

    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []

    def prepare_data(self, data):
        """Prepare features and target for training"""
        # Engineer features
        df = FeatureEngineer.calculate_technical_indicators(data)
        df = FeatureEngineer.create_target(df, horizon=1)

        # Drop rows with NaN values (from rolling calculations)
        df = df.dropna()

        # Select feature columns (exclude target and non-feature columns)
        exclude_cols = ['Target', 'Future_Return', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]

        X = df[self.feature_columns]
        y = df['Target']

        return X, y, df

    def train_models(self, X_train, y_train):
        """Train multiple ML models"""
        print("\nTraining models...")

        # Random Forest
        print("  Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        self.models['RandomForest'] = rf_model

        # Gradient Boosting
        print("  Training Gradient Boosting...")
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42
        )
        gb_model.fit(X_train, y_train)
        self.models['GradientBoosting'] = gb_model

        # XGBoost (if available)
        if XGBOOST_AVAILABLE:
            print("  Training XGBoost...")
            xgb_model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
            xgb_model.fit(X_train, y_train)
            self.models['XGBoost'] = xgb_model

        print(f"Trained {len(self.models)} models successfully!")

    def evaluate_models(self, X_test, y_test):
        """Evaluate model performance"""
        results = {}

        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            # Predict probabilities for more nuanced predictions
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            else:
                y_pred_proba = y_pred

            results[name] = {
                'accuracy': accuracy,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }

        return results

    def ensemble_predict(self, X):
        """Make ensemble predictions using all models"""
        if not self.models:
            raise ValueError("Models not trained yet!")

        predictions = []
        probabilities = []

        for name, model in self.models.items():
            pred = model.predict(X)
            predictions.append(pred)

            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(X)[:, 1]
            else:
                prob = pred

            probabilities.append(prob)

        # Soft voting: average probabilities
        ensemble_prob = np.mean(probabilities, axis=0)
        ensemble_pred = (ensemble_prob > 0.5).astype(int)

        return ensemble_pred, ensemble_prob

    def backtest_strategy(self, data, predictions, probabilities, initial_capital=10000):
        """Backtest trading strategy based on ML predictions"""
        capital = initial_capital
        position = 0
        shares = 0
        trades = []

        # Start from where we have predictions
        prices = data['Close'].values
        dates = data.index

        for i in range(len(predictions)):
            current_price = prices[i]
            pred = predictions[i]
            prob = probabilities[i]

            # Buy signal: prediction is UP with high confidence
            if pred == 1 and prob > 0.6 and position == 0:
                shares = capital / current_price
                entry_price = current_price
                trades.append({
                    'date': dates[i],
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'confidence': prob,
                    'pnl': 0,
                    'pnl_pct': 0
                })
                position = 1

            # Sell signal: prediction is DOWN or low confidence
            elif (pred == 0 or prob < 0.4) and position == 1:
                capital = shares * current_price
                pnl = capital - initial_capital
                pnl_pct = (current_price - entry_price) / entry_price * 100

                trades.append({
                    'date': dates[i],
                    'type': 'SELL',
                    'price': current_price,
                    'shares': shares,
                    'confidence': 1 - prob,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                position = 0
                shares = 0

        # Close position at end if still holding
        if position == 1:
            capital = shares * prices[-1]
            pnl = capital - initial_capital
            pnl_pct = (prices[-1] - entry_price) / entry_price * 100

            trades.append({
                'date': dates[-1],
                'type': 'SELL (Final)',
                'price': prices[-1],
                'shares': shares,
                'confidence': 0.5,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })

        return {
            'trades': trades,
            'final_capital': capital,
            'total_return': ((capital - initial_capital) / initial_capital) * 100
        }


def analyze_stock_ml(ticker, data, config):
    """Analyze a stock using ML models"""
    print(f"\n{'='*60}")
    print(f"ML Analysis for {ticker}")
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

    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

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
    print(f"Buy & Hold Return: {((test_data.iloc[-1]['Close'] - test_data.iloc[0]['Close']) / test_data.iloc[0]['Close'] * 100):.2f}%")
    print(f"\nML Strategy Performance:")
    print(f"Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"Final Capital: ${backtest_results['final_capital']:,.2f}")
    print(f"Total Return: {backtest_results['total_return']:.2f}%")
    print(f"Number of Trades: {len(backtest_results['trades'])}")

    if len(backtest_results['trades']) > 0:
        trades_df = pd.DataFrame(backtest_results['trades'])
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        if len(winning_trades) > 0:
            print(f"Winning Trades: {len(winning_trades)} (Avg: {winning_trades['pnl_pct'].mean():.2f}%)")
        if len(losing_trades) > 0:
            print(f"Losing Trades: {len(losing_trades)} (Avg: {losing_trades['pnl_pct'].mean():.2f}%)")

        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        print(f"Win Rate: {win_rate:.1f}%")

        # Show sample trades
        print(f"\nFirst 3 Trades:")
        print(trades_df.head(3)[['date', 'type', 'price', 'confidence', 'pnl_pct']].to_string(index=False))

        if len(trades_df) > 3:
            print(f"\nLast 3 Trades:")
            print(trades_df.tail(3)[['date', 'type', 'price', 'confidence', 'pnl_pct']].to_string(index=False))

    return backtest_results, ensemble_accuracy


def main():
    """Main function for ML prediction system demo"""
    print("="*60)
    print("MACHINE LEARNING PREDICTION SYSTEM - DEMO MODE")
    print("="*60)
    print("Using simulated stock data with ML models")
    print(f"Initial Capital: ${CONFIG['initial_capital']:,.2f}")

    # Import sample data generator
    from demo_with_sample_data import generate_sample_stock_data

    sample_stocks = {
        'AAPL': {'start_price': 170, 'trend': 'up', 'volatility': 0.025},
        'MSFT': {'start_price': 350, 'trend': 'up', 'volatility': 0.020},
        'GOOGL': {'start_price': 140, 'trend': 'sideways', 'volatility': 0.028},
        'AMZN': {'start_price': 145, 'trend': 'up', 'volatility': 0.030},
        'TSLA': {'start_price': 180, 'trend': 'sideways', 'volatility': 0.045},
    }

    all_results = {}

    for ticker in CONFIG['watchlist']:
        if ticker in sample_stocks:
            params = sample_stocks[ticker]
            data = generate_sample_stock_data(
                ticker,
                days=500,
                start_price=params['start_price'],
                trend=params['trend'],
                volatility=params['volatility']
            )

            try:
                results, accuracy = analyze_stock_ml(ticker, data, CONFIG)
                all_results[ticker] = {'results': results, 'accuracy': accuracy}
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                continue

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - ML Strategy (DEMO DATA)")
    print(f"{'='*60}")
    print(f"{'Ticker':<10} {'Accuracy':<12} {'Final Capital':<15} {'Return %':<12} {'Trades':<10}")
    print("-"*60)

    for ticker, data in all_results.items():
        results = data['results']
        accuracy = data['accuracy']
        print(f"{ticker:<10} {accuracy:<11.1%} ${results['final_capital']:<14,.2f} {results['total_return']:<11.2f}% {len(results['trades']):<10}")

    if all_results:
        avg_return = np.mean([r['results']['total_return'] for r in all_results.values()])
        avg_accuracy = np.mean([r['accuracy'] for r in all_results.values()])
        total_final = np.sum([r['results']['final_capital'] for r in all_results.values()])
        total_initial = CONFIG['initial_capital'] * len(all_results)
        portfolio_return = ((total_final - total_initial) / total_initial) * 100

        print("-"*60)
        print(f"Average Model Accuracy: {avg_accuracy:.1%}")
        print(f"Average Return per Stock: {avg_return:.2f}%")
        print(f"Total Portfolio: ${total_final:,.2f} (from ${total_initial:,.2f})")
        print(f"Overall Portfolio Return: {portfolio_return:.2f}%")

    print("\n" + "="*60)
    print("NOTE: This is a demonstration with simulated data.")
    print("ML models require careful tuning and ongoing retraining.")
    print("="*60)


if __name__ == "__main__":
    main()
