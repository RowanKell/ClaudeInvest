"""
Multi-source Stock Data Provider
Supports multiple data sources with automatic fallback and caching
"""

import pandas as pd
import numpy as np
import requests
import time
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class DataProviderBase:
    """Base class for all data providers"""

    def __init__(self, cache_dir='data_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_path(self, ticker, start_date, end_date):
        """Generate cache file path"""
        cache_file = f"{ticker}_{start_date}_{end_date}.csv"
        return self.cache_dir / cache_file

    def load_from_cache(self, ticker, start_date, end_date):
        """Load data from cache if available and recent"""
        cache_path = self.get_cache_path(ticker, start_date, end_date)

        if cache_path.exists():
            # Check if cache is less than 24 hours old
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age < 86400:  # 24 hours in seconds
                try:
                    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                    print(f"  ✓ Loaded {ticker} from cache")
                    return df
                except Exception as e:
                    print(f"  ⚠ Cache read error: {e}")
        return None

    def save_to_cache(self, ticker, start_date, end_date, data):
        """Save data to cache"""
        try:
            cache_path = self.get_cache_path(ticker, start_date, end_date)
            data.to_csv(cache_path)
        except Exception as e:
            print(f"  ⚠ Cache save error: {e}")

    def fetch_data(self, ticker, start_date, end_date):
        """Fetch data - to be implemented by subclasses"""
        raise NotImplementedError


class AlphaVantageProvider(DataProviderBase):
    """Alpha Vantage data provider - Free tier: 500 calls/day"""

    def __init__(self, api_key=None, cache_dir='data_cache'):
        super().__init__(cache_dir)
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
        self.rate_limit_delay = 12  # 5 calls per minute = 12 seconds between calls
        self.last_call_time = 0

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call_time = time.time()

    def fetch_data(self, ticker, start_date, end_date):
        """Fetch historical data from Alpha Vantage"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not set. Get one free at https://www.alphavantage.co/support/#api-key")

        # Check cache first
        cached = self.load_from_cache(ticker, start_date, end_date)
        if cached is not None:
            return cached

        print(f"  ⟳ Fetching {ticker} from Alpha Vantage...")
        self._wait_for_rate_limit()

        # Alpha Vantage provides full historical data
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'outputsize': 'full',
            'apikey': self.api_key,
            'datatype': 'json'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Check for error messages
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage error: {data['Error Message']}")

            if 'Note' in data:
                raise ValueError(f"Alpha Vantage rate limit: {data['Note']}")

            # Parse the time series data
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                raise ValueError(f"No data returned for {ticker}")

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()

            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume', 'Dividend', 'Split']

            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Filter by date range
            df = df.loc[start_date:end_date]

            # Keep only essential columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

            if len(df) == 0:
                raise ValueError(f"No data available for {ticker} in date range {start_date} to {end_date}")

            # Save to cache
            self.save_to_cache(ticker, start_date, end_date, df)

            print(f"  ✓ Fetched {len(df)} days of data for {ticker}")
            return df

        except Exception as e:
            raise Exception(f"Alpha Vantage fetch failed for {ticker}: {e}")


class YahooFinanceProvider(DataProviderBase):
    """Yahoo Finance data provider - Free, no API key needed"""

    def __init__(self, cache_dir='data_cache'):
        super().__init__(cache_dir)

    def fetch_data(self, ticker, start_date, end_date):
        """Fetch data from Yahoo Finance"""
        # Check cache first
        cached = self.load_from_cache(ticker, start_date, end_date)
        if cached is not None:
            return cached

        print(f"  ⟳ Fetching {ticker} from Yahoo Finance...")

        try:
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

            # Try multiple methods to avoid blocks
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'period1': start_ts,
                'period2': end_ts,
                'interval': '1d',
                'events': 'history'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = requests.get(url, params=params, headers=headers, timeout=30)

            if response.status_code == 403:
                # Try alternative CSV endpoint
                url_csv = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
                params_csv = {
                    'period1': start_ts,
                    'period2': end_ts,
                    'interval': '1d',
                    'events': 'history'
                }
                response = requests.get(url_csv, params=params_csv, headers=headers, timeout=30)

                if response.status_code == 200:
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                    df.columns = [col.replace('Adj Close', 'Adj_Close') for col in df.columns]
                else:
                    raise Exception(f"Yahoo Finance returned {response.status_code}")
            else:
                response.raise_for_status()
                data = response.json()

                # Parse JSON response
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]

                df = pd.DataFrame({
                    'Open': quotes['open'],
                    'High': quotes['high'],
                    'Low': quotes['low'],
                    'Close': quotes['close'],
                    'Volume': quotes['volume']
                })

                df.index = pd.to_datetime(timestamps, unit='s')

            # Clean up data
            df = df.dropna(how='all')

            if len(df) == 0:
                raise ValueError(f"No data available for {ticker}")

            # Save to cache
            self.save_to_cache(ticker, start_date, end_date, df)

            print(f"  ✓ Fetched {len(df)} days of data for {ticker}")
            return df

        except Exception as e:
            raise Exception(f"Yahoo Finance fetch failed for {ticker}: {e}")


class MultiSourceDataProvider:
    """
    Multi-source data provider with automatic fallback
    Tries providers in order until one succeeds
    """

    def __init__(self, alpha_vantage_key=None, cache_dir='data_cache'):
        self.providers = []

        # Add Alpha Vantage if API key is available
        if alpha_vantage_key or os.getenv('ALPHA_VANTAGE_API_KEY'):
            try:
                self.providers.append(('Alpha Vantage', AlphaVantageProvider(alpha_vantage_key, cache_dir)))
                print("✓ Alpha Vantage provider initialized")
            except Exception as e:
                print(f"⚠ Alpha Vantage initialization failed: {e}")

        # Always add Yahoo Finance as fallback
        self.providers.append(('Yahoo Finance', YahooFinanceProvider(cache_dir)))
        print("✓ Yahoo Finance provider initialized")

    def fetch_data(self, ticker, start_date, end_date):
        """
        Fetch data trying each provider until one succeeds
        """
        errors = []

        for provider_name, provider in self.providers:
            try:
                print(f"\nTrying {provider_name} for {ticker}...")
                data = provider.fetch_data(ticker, start_date, end_date)
                print(f"✓ Successfully fetched {ticker} using {provider_name}")
                return data
            except Exception as e:
                error_msg = f"{provider_name}: {str(e)}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
                continue

        # All providers failed
        raise Exception(f"All data providers failed for {ticker}:\n" + "\n".join(errors))

    def fetch_multiple(self, tickers, start_date, end_date):
        """Fetch data for multiple tickers"""
        results = {}

        for ticker in tickers:
            try:
                data = self.fetch_data(ticker, start_date, end_date)
                results[ticker] = data
            except Exception as e:
                print(f"⚠ Failed to fetch {ticker}: {e}")
                results[ticker] = None

        return results


def get_data_provider(alpha_vantage_key=None):
    """
    Factory function to create a data provider
    """
    return MultiSourceDataProvider(alpha_vantage_key)


if __name__ == "__main__":
    # Test the data provider
    print("="*60)
    print("TESTING MULTI-SOURCE DATA PROVIDER")
    print("="*60)

    # Initialize provider
    provider = get_data_provider()

    # Test fetching data
    test_ticker = 'AAPL'
    start = '2024-01-01'
    end = '2024-12-31'

    print(f"\nTest: Fetching {test_ticker} from {start} to {end}")

    try:
        data = provider.fetch_data(test_ticker, start, end)
        print(f"\n✓ SUCCESS! Retrieved {len(data)} days of data")
        print(f"\nFirst 5 rows:")
        print(data.head())
        print(f"\nLast 5 rows:")
        print(data.tail())
        print(f"\nData summary:")
        print(data.describe())
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
