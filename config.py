"""
Configuration file for trading systems
"""

# Technical Analysis Bot Configuration
TECHNICAL_ANALYSIS_CONFIG = {
    # Watchlist of stocks to monitor
    'watchlist': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY'],

    # Technical Indicator Parameters
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,

    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,

    'bb_period': 20,
    'bb_std': 2,

    'sma_short': 20,
    'sma_long': 50,

    # Risk Management
    'stop_loss_pct': 0.02,  # 2% stop loss
    'take_profit_pct': 0.05,  # 5% take profit
    'max_position_size': 0.1,  # 10% of portfolio per position

    # Backtesting
    'initial_capital': 10000,
    'start_date': '2024-01-01',
    'end_date': '2025-11-17',
}

# ML Prediction System Configuration
ML_CONFIG = {
    'watchlist': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],

    # Data parameters
    'lookback_days': 1825,  # 5 years of historical data
    'train_test_split': 0.8,
    'validation_split': 0.1,

    # Feature engineering
    'technical_indicators': [
        'RSI', 'MACD', 'BB', 'SMA_20', 'SMA_50',
        'Volume_Ratio', 'Price_Change', 'Volatility'
    ],

    # Model parameters
    'models': ['RandomForest', 'XGBoost', 'GradientBoosting'],
    'ensemble_voting': 'soft',  # 'soft' or 'hard'

    # Risk management
    'initial_capital': 10000,
    'stop_loss_pct': 0.02,
}
