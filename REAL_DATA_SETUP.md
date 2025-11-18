# Real Data Setup Guide

This guide will help you set up free data sources to test the trading systems with real market data.

## Quick Start (No API Key Required)

The system works out-of-the-box with **Yahoo Finance** (no API key needed):

```bash
python real_data_provider.py
```

This will test fetching AAPL stock data using Yahoo Finance as a fallback.

---

## Recommended: Alpha Vantage Setup (500 free calls/day)

Alpha Vantage is recommended for better reliability and higher rate limits.

### Step 1: Get a Free API Key

1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter your email and click "GET FREE API KEY"
3. You'll receive your API key immediately (no email verification needed)
4. **Free tier limits**: 500 API calls per day, 5 calls per minute

### Step 2: Set Your API Key

**Option A: Environment Variable (Recommended)**

Linux/Mac:
```bash
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
```

Windows (PowerShell):
```powershell
$env:ALPHA_VANTAGE_API_KEY="your_api_key_here"
```

Windows (Command Prompt):
```cmd
set ALPHA_VANTAGE_API_KEY=your_api_key_here
```

**Option B: .env File**

Create a file named `.env` in the project root:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

The system will automatically load this.

**Option C: Pass Directly to Code**

```python
from real_data_provider import get_data_provider

provider = get_data_provider(alpha_vantage_key="your_api_key_here")
```

### Step 3: Test It Works

```bash
python real_data_provider.py
```

You should see:
```
✓ Alpha Vantage provider initialized
✓ Yahoo Finance provider initialized
Trying Alpha Vantage for AAPL...
✓ Successfully fetched AAPL using Alpha Vantage
```

---

## Alternative: Polygon.io (Limited Free Tier)

Polygon.io offers a limited free tier but requires more setup.

### Free Tier Limits
- **5 API calls per minute**
- **2 years of historical data**
- US stocks only

### Setup

1. Sign up at: https://polygon.io/
2. Get your API key from the dashboard
3. Set environment variable:
   ```bash
   export POLYGON_API_KEY="your_api_key_here"
   ```

**Note**: The current system prioritizes Alpha Vantage and Yahoo Finance. Polygon support can be added if needed.

---

## Data Provider Features

### Multi-Source with Automatic Fallback

The system tries providers in this order:
1. **Alpha Vantage** (if API key available) - Most reliable
2. **Yahoo Finance** (always available) - Fallback

### Automatic Caching

- Downloaded data is cached locally in `data_cache/` folder
- Cache expires after 24 hours
- Saves API calls and speeds up repeated runs
- Delete `data_cache/` folder to force fresh downloads

### Rate Limiting Protection

- Automatically waits between API calls
- Alpha Vantage: 12 seconds between calls (5 per minute limit)
- Prevents exceeding free tier limits

---

## Testing the Trading Systems with Real Data

### Option 1: Technical Analysis Bot

```bash
# Set your API key (or skip for Yahoo Finance only)
export ALPHA_VANTAGE_API_KEY="your_key"

# Run with real data
python test_technical_with_real_data.py
```

### Option 2: ML Prediction System

```bash
# Set your API key
export ALPHA_VANTAGE_API_KEY="your_key"

# Run with real data
python test_ml_with_real_data.py
```

---

## Rate Limits Summary

| Provider | Free Tier Limit | API Key Required | Historical Data |
|----------|----------------|------------------|-----------------|
| **Alpha Vantage** | 500 calls/day, 5/min | ✓ Yes (free) | 20+ years |
| **Yahoo Finance** | Varies (can be blocked) | ✗ No | 5+ years |
| **Polygon.io** | 5 calls/min | ✓ Yes (free) | 2 years |

---

## Troubleshooting

### "Alpha Vantage API key not set"

Solution: Set the environment variable or pass the key directly:
```bash
export ALPHA_VANTAGE_API_KEY="your_key"
```

### "All data providers failed"

Possible causes:
1. **Rate limit exceeded**: Wait a few minutes and try again
2. **Invalid ticker**: Check the stock symbol is correct (e.g., 'AAPL' not 'Apple')
3. **Network issues**: Check your internet connection
4. **Date range too old**: Try a more recent date range

### "Yahoo Finance returned 403"

Yahoo Finance occasionally blocks automated requests. Solutions:
1. Use Alpha Vantage instead (get free API key)
2. Wait a few minutes and retry
3. Clear cache: `rm -rf data_cache/`

### Cache not working

Check permissions on `data_cache/` folder:
```bash
ls -la data_cache/
```

Clear cache if needed:
```bash
rm -rf data_cache/
```

---

## API Cost Comparison (if you need more than free tier)

| Provider | Price/Month | Requests | Real-time |
|----------|-------------|----------|-----------|
| Alpha Vantage Premium | $29.99 | 75/min | No |
| Polygon.io Starter | $199 | Unlimited | Yes |
| Alpha Vantage Ultimate | $249.99 | 1200/min | No |

**Recommendation**: Start with free tiers. Only upgrade if you need:
- Real-time data (Polygon)
- High-frequency trading (many API calls)
- Production deployment

---

## Best Practices

### For Development/Learning
- ✓ Use Alpha Vantage free tier (500 calls/day is plenty)
- ✓ Run tests once per day (leverage cache)
- ✓ Test with 2-3 stocks initially
- ✓ Expand to full watchlist once code is working

### For Backtesting
- ✓ Download all data once and cache it
- ✓ Use longer date ranges (1-2 years)
- ✓ Run analysis offline using cached data
- ✓ Refresh cache weekly/monthly

### For Production
- ✗ Don't use free tiers for live trading
- ✓ Upgrade to paid plan with real-time data
- ✓ Implement proper error handling
- ✓ Monitor API usage and costs
- ✓ Have a backup data provider

---

## Next Steps

1. **Get Alpha Vantage API key**: https://www.alphavantage.co/support/#api-key
2. **Test data fetching**: `python real_data_provider.py`
3. **Run backtests with real data**: See test scripts
4. **Compare with simulated results**: Check if patterns hold
5. **Paper trade**: Test live (without real money) for 3-6 months
6. **Iterate and improve**: Refine strategies based on real data

---

## Support

- Alpha Vantage Docs: https://www.alphavantage.co/documentation/
- Polygon.io Docs: https://polygon.io/docs/stocks
- Issues with this code: Check the README or open an issue

Happy trading! 📈
