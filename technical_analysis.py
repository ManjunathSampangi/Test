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
    def __init__(self, config: Dict = None):
        """
        Initialize Technical Analysis module
        
        Args:
            config: Configuration dictionary for scalping parameters
        """
        self.scaler = StandardScaler()
        self.model = None
        self.config = config or {}
        
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
        Generate technical indicators as features (optimized for scalping)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features
        """
        features_df = df.copy()
        
        # Get scalping parameters from config
        rsi_period = self.config.get('rsi_period', 9)
        macd_fast = self.config.get('macd_fast', 8)
        macd_slow = self.config.get('macd_slow', 21)
        macd_signal = self.config.get('macd_signal', 5)
        bb_period = self.config.get('bb_period', 10)
        bb_std = self.config.get('bb_std', 1.5)
        ema_fast = self.config.get('ema_fast', 5)
        ema_slow = self.config.get('ema_slow', 13)
        
        # RSI (faster for scalping)
        features_df['rsi'] = self.calculate_rsi(df, period=rsi_period)
        
        # MACD (optimized for scalping)
        macd_data = self.calculate_macd(df, fast=macd_fast, slow=macd_slow, signal=macd_signal)
        features_df['macd'] = macd_data['macd']
        features_df['macd_signal'] = macd_data['signal']
        features_df['macd_histogram'] = macd_data['histogram']
        
        # Bollinger Bands (tighter for scalping)
        bb_data = self.calculate_bollinger_bands(df, period=bb_period, std_dev=bb_std)
        features_df['bb_upper'] = bb_data['upper']
        features_df['bb_middle'] = bb_data['middle']
        features_df['bb_lower'] = bb_data['lower']
        features_df['bb_width'] = (bb_data['upper'] - bb_data['lower']) / bb_data['middle']
        features_df['bb_position'] = (df['close'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower'])
        
        # ATR (for volatility)
        features_df['atr'] = self.calculate_atr(df, period=9)
        
        # Fast EMAs for scalping
        features_df['ema_fast'] = self.calculate_ema(df, ema_fast)
        features_df['ema_slow'] = self.calculate_ema(df, ema_slow)
        
        # Price momentum (critical for scalping)
        features_df['price_change'] = df['close'].pct_change()
        features_df['price_change_3'] = df['close'].pct_change(periods=3)
        features_df['momentum'] = df['close'].diff(3) / df['close'].shift(3)
        
        # Volume analysis (important for scalping)
        features_df['volume_change'] = df['volume'].pct_change()
        features_df['volume_ma'] = df['volume'].rolling(window=10).mean()
        features_df['volume_ratio'] = df['volume'] / features_df['volume_ma']
        
        # Volatility (short-term)
        features_df['volatility'] = df['close'].rolling(window=10).std()
        features_df['volatility_pct'] = features_df['volatility'] / df['close']
        
        # Price position in recent range
        features_df['high_5'] = df['high'].rolling(window=5).max()
        features_df['low_5'] = df['low'].rolling(window=5).min()
        features_df['range_position'] = (df['close'] - features_df['low_5']) / (features_df['high_5'] - features_df['low_5'])
        
        return features_df
    
    def generate_scalping_signal(self, df: pd.DataFrame, volume_threshold: float = 1.5,
                                 min_volume: int = 10000, momentum_threshold: float = 0.1) -> Dict[str, any]:
        """
        Generate scalping-specific trading signal
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            volume_threshold: Minimum volume ratio threshold
            min_volume: Minimum absolute volume
            momentum_threshold: Minimum momentum threshold
            
        Returns:
            Dictionary with signal, confidence, and details
        """
        if len(df) < 20:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data for scalping'
            }
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Check volume requirement (critical for scalping)
        if latest.get('volume', 0) < min_volume:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': f'Low volume: {latest.get("volume", 0)}'
            }
        
        if latest.get('volume_ratio', 0) < volume_threshold:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': f'Volume below threshold: {latest.get("volume_ratio", 0):.2f}'
            }
        
        signals = []
        confidence_scores = []
        
        # Get thresholds from config
        rsi_oversold = self.config.get('rsi_oversold', 25)
        rsi_overbought = self.config.get('rsi_overbought', 75)
        
        # Strong momentum signals (high priority for scalping)
        if latest.get('momentum', 0) > momentum_threshold:
            signals.append('BUY')
            confidence_scores.append(0.4)
        elif latest.get('momentum', 0) < -momentum_threshold:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # RSI extremes (more sensitive for scalping)
        if latest['rsi'] < rsi_oversold:
            signals.append('BUY')
            confidence_scores.append(0.35)
        elif latest['rsi'] > rsi_overbought:
            signals.append('SELL')
            confidence_scores.append(0.35)
        
        # MACD crossover (faster for scalping)
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals.append('BUY')
            confidence_scores.append(0.4)
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # EMA crossover (fast EMAs for scalping)
        if latest['ema_fast'] > latest['ema_slow'] and prev['ema_fast'] <= prev['ema_slow']:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif latest['ema_fast'] < latest['ema_slow'] and prev['ema_fast'] >= prev['ema_slow']:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Bollinger Bands (tighter bands for scalping)
        if latest['close'] < latest['bb_lower']:
            signals.append('BUY')
            confidence_scores.append(0.25)
        elif latest['close'] > latest['bb_upper']:
            signals.append('SELL')
            confidence_scores.append(0.25)
        
        # Range position (quick reversal signals)
        if latest.get('range_position', 0.5) < 0.2:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif latest.get('range_position', 0.5) > 0.8:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        # Determine final signal
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 2:  # Require at least 2 signals
            signal = 'BUY'
            confidence = min(sum(confidence_scores[:buy_count]) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            signal = 'SELL'
            confidence = min(sum(confidence_scores[:sell_count]) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'momentum': latest.get('momentum', 0),
            'volume_ratio': latest.get('volume_ratio', 0),
            'bb_position': latest['bb_position'],
            'price': latest['close'],
            'volume': latest.get('volume', 0),
            'reason': f'RSI: {latest["rsi"]:.2f}, Momentum: {latest.get("momentum", 0):.3f}, Vol: {latest.get("volume_ratio", 0):.2f}'
        }
    
    def generate_signal(self, df: pd.DataFrame, rsi_oversold: int = 30, 
                       rsi_overbought: int = 70, use_scalping: bool = True) -> Dict[str, any]:
        """
        Generate trading signal based on technical indicators
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            use_scalping: Use scalping-specific signal generation
            
        Returns:
            Dictionary with signal, confidence, and details
        """
        if use_scalping:
            volume_threshold = self.config.get('volume_threshold_multiplier', 1.5)
            min_volume = self.config.get('min_volume', 10000)
            momentum_threshold = self.config.get('momentum_threshold', 0.1)
            return self.generate_scalping_signal(df, volume_threshold, min_volume, momentum_threshold)
        
        # Original signal generation (fallback)
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
        if latest.get('ema_fast', latest.get('ema_12', 0)) > latest.get('ema_slow', latest.get('ema_26', 0)):
            if prev.get('ema_fast', prev.get('ema_12', 0)) <= prev.get('ema_slow', prev.get('ema_26', 0)):
                signals.append('BUY')
                confidence_scores.append(0.2)
        elif latest.get('ema_fast', latest.get('ema_12', 0)) < latest.get('ema_slow', latest.get('ema_26', 0)):
            if prev.get('ema_fast', prev.get('ema_12', 0)) >= prev.get('ema_slow', prev.get('ema_26', 0)):
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
