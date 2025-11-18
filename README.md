# ClaudeInvest - Stock Trading Systems

This repository contains two different stock trading systems with support for both **simulated** and **real market data**.

## 🚀 Quick Start

### Option 1: Demo with Simulated Data (No API Key)
```bash
pip install -r requirements.txt
python demo_with_sample_data.py
```

### Option 2: Test with Real Market Data (Requires Free API Key)

**Get a free Alpha Vantage API key** (takes 30 seconds):
1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter your email → Get your key instantly
3. Set the environment variable:
   ```bash
   export ALPHA_VANTAGE_API_KEY="your_key_here"
   ```

4. Run tests with real data:
   ```bash
   python test_technical_with_real_data.py
   python test_ml_with_real_data.py
   ```

📖 **Full setup guide**: See [REAL_DATA_SETUP.md](REAL_DATA_SETUP.md)

---

## 📊 Trading Systems

### Option 1: Technical Analysis Trading Bot

**Branch**: `claude/stock-trading-research-01McCmTTgkYWpDaJuEvTE1Bc`

A rule-based trading system using technical indicators to identify entry and exit points.

**Strategy**:
- RSI (Relative Strength Index) for overbought/oversold conditions
- MACD (Moving Average Convergence Divergence) for trend direction
- Bollinger Bands for volatility and price extremes
- Stop-loss and take-profit risk management

**Demo Results** (simulated data):
- Portfolio Return: -0.56%
- Very conservative (few trades)

**Usage**:
```bash
# With simulated data
python demo_with_sample_data.py

# With real data (requires API key)
python test_technical_with_real_data.py
```

### Option 2: Machine Learning Prediction System

**Branch**: `claude/ml-prediction-01McCmTTgkYWpDaJuEvTE1Bc`

ML-based system using ensemble models to predict price movements.

**Features**:
- Multiple ML models (Random Forest, XGBoost, Gradient Boosting)
- 30+ engineered features from technical indicators
- Ensemble voting for robust predictions
- Confidence-based trading (only trades with >60% confidence)

**Demo Results** (simulated data):
- Portfolio Return: +30.40%
- Average accuracy: 52%
- Active trading strategy

**Usage**:
```bash
# With simulated data
python ml_prediction_system.py

# With real data (requires API key)
python test_ml_with_real_data.py
```

---

## 📈 Performance Comparison

See [COMPARISON_RESULTS.md](COMPARISON_RESULTS.md) for detailed analysis.

| System | Return | Trades | Complexity | Winner |
|--------|--------|--------|------------|--------|
| Technical Analysis | -0.56% | 2 | Low | |
| ML Prediction | +30.40% | 68 | High | ✓ |

**Note**: Both systems tested on simulated data. Real market performance may differ significantly.

---

## 💾 Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/RowanKell/ClaudeInvest.git
   cd ClaudeInvest
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional)** Set up Alpha Vantage for real data:
   ```bash
   # Get free API key: https://www.alphavantage.co/support/#api-key
   export ALPHA_VANTAGE_API_KEY="your_key_here"
   ```

---

## 📁 Project Structure

```
ClaudeInvest/
├── technical_analysis_bot.py      # Option 1: Technical analysis system
├── ml_prediction_system.py        # Option 2: ML prediction system
├── demo_with_sample_data.py       # Demo with simulated data
├── real_data_provider.py          # Multi-source real data fetcher
├── test_technical_with_real_data.py   # Test Option 1 with real data
├── test_ml_with_real_data.py      # Test Option 2 with real data
├── config.py                      # Configuration for both systems
├── data_fetcher.py                # Yahoo Finance data fetcher
├── COMPARISON_RESULTS.md          # Detailed performance analysis
├── REAL_DATA_SETUP.md             # Setup guide for real data sources
└── requirements.txt               # Python dependencies
```

---

## ⚠️ Important Disclaimers

**Educational Purpose Only**: These trading systems are for learning and research purposes.

**Not Financial Advice**: This is not investment advice. Do not use real money without extensive testing.

**Risk Warning**:
- Past performance does not guarantee future results
- Both systems need significant improvements for real trading
- Always use proper risk management
- Start with paper trading for 3-6 months minimum

**Testing Recommendations**:
1. Test with simulated data first
2. Test with real historical data (backtesting)
3. Paper trade (no real money) for 3-6 months
4. Only use real money after proven consistent performance
5. Never risk more than you can afford to lose

---

## 🔧 Configuration

Edit `config.py` to adjust:
- Watchlist (stocks to trade)
- Technical indicator parameters (RSI periods, MACD settings, etc.)
- Risk management (stop-loss %, take-profit %)
- ML model parameters
- Initial capital for backtesting

---

## 📚 Learn More

- **Setup Real Data**: [REAL_DATA_SETUP.md](REAL_DATA_SETUP.md)
- **Performance Analysis**: [COMPARISON_RESULTS.md](COMPARISON_RESULTS.md)
- **Alpha Vantage API**: https://www.alphavantage.co/documentation/

---

## 🤝 Contributing

This is a research/educational project. Feel free to:
- Test with different parameters
- Add new strategies
- Improve ML models
- Add more data sources
- Share results (with disclaimers!)

---

## 📄 License

Educational use only. Use at your own risk.

---

## 💡 Next Steps

1. **Get API Key**: https://www.alphavantage.co/support/#api-key (free, instant)
2. **Test with Real Data**: Run `python test_technical_with_real_data.py`
3. **Compare Results**: Check simulated vs real performance
4. **Iterate**: Adjust parameters, test different stocks
5. **Paper Trade**: Test without real money for months
6. **Learn**: Study why certain trades work/fail

**Remember**: Consistent profitability in stock markets is extremely difficult. These systems are starting points for learning, not ready-to-use trading bots.
