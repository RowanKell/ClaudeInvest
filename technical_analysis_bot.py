"""
Technical Analysis Trading Bot
Uses RSI, MACD, and Bollinger Bands to generate trading signals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from config import TECHNICAL_ANALYSIS_CONFIG as CONFIG
from data_fetcher import fetch_yahoo_data


class TechnicalIndicators:
    """Calculate technical indicators for stock analysis"""

    @staticmethod
    def calculate_rsi(data, period=14):
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow, adjust=False).mean()

        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return upper_band, sma, lower_band

    @staticmethod
    def calculate_sma(data, period):
        """Calculate Simple Moving Average"""
        return data['Close'].rolling(window=period).mean()


class TradingSignals:
    """Generate trading signals based on technical indicators"""

    def __init__(self, config):
        self.config = config

    def generate_signals(self, data):
        """Generate buy/sell signals based on technical indicators"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['signal'] = 0  # 0 = hold, 1 = buy, -1 = sell

        # Calculate indicators
        rsi = TechnicalIndicators.calculate_rsi(data, self.config['rsi_period'])
        macd, signal_line, histogram = TechnicalIndicators.calculate_macd(
            data,
            self.config['macd_fast'],
            self.config['macd_slow'],
            self.config['macd_signal']
        )
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(
            data,
            self.config['bb_period'],
            self.config['bb_std']
        )
        sma_short = TechnicalIndicators.calculate_sma(data, self.config['sma_short'])
        sma_long = TechnicalIndicators.calculate_sma(data, self.config['sma_long'])

        # Store indicators in signals dataframe
        signals['rsi'] = rsi
        signals['macd'] = macd
        signals['macd_signal'] = signal_line
        signals['bb_upper'] = bb_upper
        signals['bb_lower'] = bb_lower
        signals['bb_middle'] = bb_middle
        signals['sma_short'] = sma_short
        signals['sma_long'] = sma_long

        # Generate BUY signals
        buy_conditions = (
            (rsi < self.config['rsi_oversold']) &  # RSI oversold
            (macd > signal_line) &  # MACD crossover
            (data['Close'] < bb_lower)  # Price below lower Bollinger Band
        )

        # Generate SELL signals
        sell_conditions = (
            (rsi > self.config['rsi_overbought']) |  # RSI overbought
            (macd < signal_line)  # MACD crossunder
        )

        signals.loc[buy_conditions, 'signal'] = 1
        signals.loc[sell_conditions, 'signal'] = -1

        return signals


class Backtester:
    """Backtest trading strategy on historical data"""

    def __init__(self, initial_capital, stop_loss_pct=0.02, take_profit_pct=0.05):
        self.initial_capital = initial_capital
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def run_backtest(self, signals):
        """Run backtest on signals"""
        capital = self.initial_capital
        position = 0  # 0 = no position, 1 = holding
        entry_price = 0
        shares = 0

        trades = []
        portfolio_value = []

        for i in range(len(signals)):
            current_price = signals.iloc[i]['price']
            signal = signals.iloc[i]['signal']

            # Check stop loss and take profit if holding position
            if position == 1:
                price_change = (current_price - entry_price) / entry_price

                # Stop loss hit
                if price_change <= -self.stop_loss_pct:
                    capital = shares * current_price
                    trades.append({
                        'date': signals.index[i],
                        'type': 'SELL (Stop Loss)',
                        'price': current_price,
                        'shares': shares,
                        'pnl': capital - self.initial_capital,
                        'pnl_pct': price_change * 100
                    })
                    position = 0
                    shares = 0

                # Take profit hit
                elif price_change >= self.take_profit_pct:
                    capital = shares * current_price
                    trades.append({
                        'date': signals.index[i],
                        'type': 'SELL (Take Profit)',
                        'price': current_price,
                        'shares': shares,
                        'pnl': capital - self.initial_capital,
                        'pnl_pct': price_change * 100
                    })
                    position = 0
                    shares = 0

                # Normal sell signal
                elif signal == -1:
                    capital = shares * current_price
                    trades.append({
                        'date': signals.index[i],
                        'type': 'SELL (Signal)',
                        'price': current_price,
                        'shares': shares,
                        'pnl': capital - self.initial_capital,
                        'pnl_pct': price_change * 100
                    })
                    position = 0
                    shares = 0

            # Buy signal and no position
            elif signal == 1 and position == 0:
                shares = capital / current_price
                entry_price = current_price
                trades.append({
                    'date': signals.index[i],
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'pnl': 0,
                    'pnl_pct': 0
                })
                position = 1

            # Calculate current portfolio value
            if position == 1:
                portfolio_value.append(shares * current_price)
            else:
                portfolio_value.append(capital)

        # Close any open position at the end
        if position == 1:
            final_price = signals.iloc[-1]['price']
            capital = shares * final_price
            price_change = (final_price - entry_price) / entry_price
            trades.append({
                'date': signals.index[-1],
                'type': 'SELL (Final)',
                'price': final_price,
                'shares': shares,
                'pnl': capital - self.initial_capital,
                'pnl_pct': price_change * 100
            })

        return {
            'trades': trades,
            'portfolio_value': portfolio_value,
            'final_capital': capital,
            'total_return': ((capital - self.initial_capital) / self.initial_capital) * 100
        }


def fetch_stock_data(ticker, start_date, end_date):
    """Fetch historical stock data"""
    return fetch_yahoo_data(ticker, start_date, end_date)


def analyze_stock(ticker, config):
    """Analyze a single stock and generate trading signals"""
    print(f"\n{'='*60}")
    print(f"Analyzing {ticker}")
    print(f"{'='*60}")

    # Fetch data
    data = fetch_stock_data(ticker, config['start_date'], config['end_date'])
    if data is None:
        return None

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

        # Show recent trades
        print(f"\nRecent Trades:")
        print(trades_df.tail(5).to_string(index=False))

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
    """Main function to run the technical analysis bot"""
    print("="*60)
    print("TECHNICAL ANALYSIS TRADING BOT")
    print("="*60)
    print(f"Testing Period: {CONFIG['start_date']} to {CONFIG['end_date']}")
    print(f"Watchlist: {', '.join(CONFIG['watchlist'])}")
    print(f"Initial Capital: ${CONFIG['initial_capital']:,.2f}")

    all_results = {}

    for ticker in CONFIG['watchlist']:
        results = analyze_stock(ticker, CONFIG)
        if results:
            all_results[ticker] = results

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY - All Stocks")
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

        print("-"*60)
        print(f"Average Return: {avg_return:.2f}%")
        print(f"Total Portfolio: ${total_final:,.2f} (from ${total_initial:,.2f})")


if __name__ == "__main__":
    main()
