"""
Simple data fetcher for stock prices using Yahoo Finance API directly
"""

import requests
import pandas as pd
from datetime import datetime
import time


def fetch_yahoo_data(ticker, start_date, end_date):
    """
    Fetch stock data directly from Yahoo Finance
    """
    try:
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

        # Yahoo Finance API endpoint
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
        params = {
            'period1': start_ts,
            'period2': end_ts,
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # Parse CSV data
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # Rename columns to match yfinance format
        df.columns = [col.replace('Adj Close', 'Adj_Close') for col in df.columns]

        return df

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def get_current_price(ticker):
    """Get current/latest price for a ticker"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            'interval': '1d',
            'range': '1d'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return price

    except Exception as e:
        print(f"Error fetching current price for {ticker}: {e}")
        return None
