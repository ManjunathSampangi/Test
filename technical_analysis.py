"""
Technical Analysis Module
Performs technical analysis and generates trading signals
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalysis:
    def __init__(self):
        """Initialize Technical Analysis module"""
        self.scaler = StandardScaler()
        self.model = None
        
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'close' column
            period: RSI period (default 14)
            
        Returns:
            RSI series
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, 
                      slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Dictionary with 'macd', 'signal', 'histogram' series
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, 
                                  std_dev: int = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with 'close' column
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with 'upper', 'middle', 'lower' bands
        """
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period
            
        Returns:
            ATR series
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            df: DataFrame with 'close' column
            period: EMA period
            
        Returns:
            EMA series
        """
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            df: DataFrame with 'close' column
            period: SMA period
            
        Returns:
            SMA series
        """
        return df['close'].rolling(window=period).mean()
    
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate technical indicators as features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features
        """
        features_df = df.copy()
        
        # RSI
        features_df['rsi'] = self.calculate_rsi(df)
        
        # MACD
        macd_data = self.calculate_macd(df)
        features_df['macd'] = macd_data['macd']
        features_df['macd_signal'] = macd_data['signal']
        features_df['macd_histogram'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(df)
        features_df['bb_upper'] = bb_data['upper']
        features_df['bb_middle'] = bb_data['middle']
        features_df['bb_lower'] = bb_data['lower']
        features_df['bb_width'] = (bb_data['upper'] - bb_data['lower']) / bb_data['middle']
        features_df['bb_position'] = (df['close'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower'])
        
        # ATR
        features_df['atr'] = self.calculate_atr(df)
        
        # Moving Averages
        features_df['sma_20'] = self.calculate_sma(df, 20)
        features_df['sma_50'] = self.calculate_sma(df, 50)
        features_df['ema_12'] = self.calculate_ema(df, 12)
        features_df['ema_26'] = self.calculate_ema(df, 26)
        
        # Price changes
        features_df['price_change'] = df['close'].pct_change()
        features_df['volume_change'] = df['volume'].pct_change()
        
        # Volatility
        features_df['volatility'] = df['close'].rolling(window=20).std()
        
        return features_df
    
    def generate_signal(self, df: pd.DataFrame, rsi_oversold: int = 30, 
                       rsi_overbought: int = 70) -> Dict[str, any]:
        """
        Generate trading signal based on technical indicators
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            
        Returns:
            Dictionary with signal, confidence, and details
        """
        if len(df) < 50:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data'
            }
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        confidence_scores = []
        
        # RSI signals
        if latest['rsi'] < rsi_oversold:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif latest['rsi'] > rsi_overbought:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # MACD signals
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals.append('BUY')
            confidence_scores.append(0.4)
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # Bollinger Bands signals
        if latest['close'] < latest['bb_lower']:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif latest['close'] > latest['bb_upper']:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Moving Average crossover
        if latest['ema_12'] > latest['ema_26'] and prev['ema_12'] <= prev['ema_26']:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif latest['ema_12'] < latest['ema_26'] and prev['ema_12'] >= prev['ema_26']:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        # Determine final signal
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            signal = 'BUY'
            confidence = min(sum(confidence_scores[:buy_count]), 1.0)
        elif sell_count > buy_count:
            signal = 'SELL'
            confidence = min(sum(confidence_scores[:sell_count]), 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'bb_position': latest['bb_position'],
            'price': latest['close'],
            'reason': f'RSI: {latest["rsi"]:.2f}, MACD: {latest["macd"]:.2f}, BB: {latest["bb_position"]:.2f}'
        }
    
    def predict_price_direction(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Predict price direction using ML model
        
        Args:
            df: DataFrame with features
            
        Returns:
            Prediction dictionary
        """
        try:
            features_df = self.generate_features(df)
            
            # Prepare features for prediction
            feature_columns = ['rsi', 'macd', 'macd_signal', 'macd_histogram',
                             'bb_width', 'bb_position', 'atr', 'sma_20', 'sma_50',
                             'price_change', 'volume_change', 'volatility']
            
            # Get latest features
            latest_features = features_df[feature_columns].iloc[-1:].values
            
            # Simple rule-based prediction (can be replaced with trained ML model)
            signal_data = self.generate_signal(features_df)
            
            return {
                'prediction': signal_data['signal'],
                'confidence': signal_data['confidence'],
                'expected_move': signal_data.get('expected_move', 0.0),
                'details': signal_data
            }
        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            return {
                'prediction': 'HOLD',
                'confidence': 0.0,
                'expected_move': 0.0,
                'details': {}
            }
