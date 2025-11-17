# ClaudeInvest - Stock Trading Systems

This repository contains two different stock trading systems:

## Option 1: Technical Analysis Trading Bot

A rule-based trading system using technical indicators to identify entry and exit points.

**Features:**
- RSI (Relative Strength Index) for overbought/oversold conditions
- MACD (Moving Average Convergence Divergence) for trend direction
- Bollinger Bands for volatility and price extremes
- Backtesting framework to evaluate historical performance
- Paper trading mode for risk-free testing

**Usage:**
```bash
python technical_analysis_bot.py
```

## Option 2: Machine Learning Prediction System

A machine learning-based system that predicts stock price movements using historical data.

**Features:**
- Multiple ML models (Random Forest, XGBoost, Gradient Boosting)
- Feature engineering from technical indicators
- Ensemble voting for robust predictions
- Performance metrics and evaluation

**Usage:**
```bash
python ml_prediction_system.py
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Disclaimer

These trading systems are for educational purposes only. Past performance does not guarantee future results. Always practice proper risk management and never invest more than you can afford to lose.
