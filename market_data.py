"""
Market Data Module
Fetches real-time and historical market data for options and Nifty
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketData:
    def __init__(self, fyers_session):
        """
        Initialize Market Data fetcher
        
        Args:
            fyers_session: Authenticated Fyers session object
        """
        self.session = fyers_session
        self.base_url = "https://api.fyers.in/v2"
        
    def get_quote(self, symbols: List[str]) -> Dict:
        """
        Get real-time quotes for symbols
        
        Args:
            symbols: List of symbols (e.g., ['NSE:NIFTY50-INDEX'])
            
        Returns:
            Quote data dictionary
        """
        try:
            data = {
                "symbols": ",".join(symbols)
            }
            quote = self.session.quotes(data=data)
            
            if quote.get('s') == 'ok':
                logger.info(f"Quote fetched for {len(symbols)} symbols")
                return quote.get('d', [])
            else:
                logger.error(f"Error fetching quotes: {quote}")
                return []
        except Exception as e:
            logger.error(f"Exception fetching quotes: {str(e)}")
            return []
    
    def get_historical_data(self, symbol: str, resolution: str = '1', 
                           date_format: int = 1, range_from: str = None, 
                           range_to: str = None, cont_flag: str = '1') -> pd.DataFrame:
        """
        Get historical data for a symbol
        
        Args:
            symbol: Symbol (e.g., 'NSE:NIFTY50-INDEX')
            resolution: Time resolution ('1', '5', '15', '30', '60', 'D')
            date_format: Date format (1 for epoch, 0 for date)
            range_from: Start date (YYYY-MM-DD)
            range_to: End date (YYYY-MM-DD)
            cont_flag: Continuous flag
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not range_from:
                range_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not range_to:
                range_to = datetime.now().strftime('%Y-%m-%d')
            
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": date_format,
                "range_from": range_from,
                "range_to": range_to,
                "cont_flag": cont_flag
            }
            
            historical = self.session.history(data=data)
            
            if historical.get('s') == 'ok':
                df = pd.DataFrame(historical['candles'])
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
                df.drop('timestamp', axis=1, inplace=True)
                logger.info(f"Historical data fetched for {symbol}: {len(df)} candles")
                return df
            else:
                logger.error(f"Error fetching historical data: {historical}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Exception fetching historical data: {str(e)}")
            return pd.DataFrame()
    
    def get_option_chain(self, underlying_symbol: str) -> List[Dict]:
        """
        Get option chain for underlying symbol
        
        Args:
            underlying_symbol: Underlying symbol (e.g., 'NSE:NIFTY50-INDEX')
            
        Returns:
            List of option contracts
        """
        try:
            # Note: Fyers API structure may vary. This is a template.
            # You may need to adjust based on actual Fyers API documentation
            data = {
                "symbol": underlying_symbol
            }
            
            # This is a placeholder - adjust based on actual Fyers API
            option_chain = self.session.option_chain(data=data)
            
            if option_chain.get('s') == 'ok':
                logger.info(f"Option chain fetched for {underlying_symbol}")
                return option_chain.get('data', [])
            else:
                logger.error(f"Error fetching option chain: {option_chain}")
                return []
        except Exception as e:
            logger.error(f"Exception fetching option chain: {str(e)}")
            return []
    
    def get_nifty_options(self, expiry_date: str = None) -> List[Dict]:
        """
        Get Nifty options contracts
        
        Args:
            expiry_date: Expiry date (YYYY-MM-DD), None for all expiries
            
        Returns:
            List of Nifty option contracts
        """
        return self.get_option_chain('NSE:NIFTY50-INDEX')
    
    def get_stock_options(self, stock_symbol: str, expiry_date: str = None) -> List[Dict]:
        """
        Get stock options contracts
        
        Args:
            stock_symbol: Stock symbol (e.g., 'NSE:RELIANCE-EQ')
            expiry_date: Expiry date (YYYY-MM-DD), None for all expiries
            
        Returns:
            List of stock option contracts
        """
        return self.get_option_chain(stock_symbol)
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Symbol to get price for
            
        Returns:
            Latest price (float)
        """
        quotes = self.get_quote([symbol])
        if quotes and len(quotes) > 0:
            quote_data = quotes[0].get('n', {})
            return quote_data.get('lp', 0.0)  # Last price
        return 0.0
    
    def get_volume(self, symbol: str) -> int:
        """
        Get volume for a symbol
        
        Args:
            symbol: Symbol to get volume for
            
        Returns:
            Volume (int)
        """
        quotes = self.get_quote([symbol])
        if quotes and len(quotes) > 0:
            quote_data = quotes[0].get('n', {})
            return quote_data.get('v', 0)  # Volume
        return 0
