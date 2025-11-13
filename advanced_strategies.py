"""
Advanced Trading Strategies Module
Implements multiple world-class trading strategies:
- Momentum Trading
- Mean Reversion
- Breakout Trading
- Trend Following
- Pairs Trading/Arbitrage
- Volume Profile Analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedStrategies:
    def __init__(self, config: Dict = None):
        """
        Initialize Advanced Strategies module
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.strategy_weights = {
            'momentum': 0.25,
            'mean_reversion': 0.20,
            'breakout': 0.20,
            'trend_following': 0.15,
            'volume_profile': 0.10,
            'arbitrage': 0.10
        }
        
    def momentum_strategy(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Momentum Strategy - Buy strong trends, sell weak trends
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period for momentum calculation
            
        Returns:
            Strategy signal dictionary
        """
        if len(df) < lookback + 10:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'momentum'}
        
        # Calculate momentum indicators
        df['returns'] = df['close'].pct_change()
        df['momentum'] = df['close'].pct_change(lookback)
        # ROC calculation with division by zero protection
        shifted_close = df['close'].shift(lookback)
        df['roc'] = np.where(
            shifted_close != 0,
            (df['close'] - shifted_close) / shifted_close * 100,
            0
        )
        
        # Volume-weighted momentum
        df['volume_momentum'] = (df['volume'] * df['returns']).rolling(lookback).sum()
        
        # Price acceleration
        df['acceleration'] = df['momentum'].diff()
        
        # Relative strength vs market (if available)
        df['price_strength'] = df['close'].rolling(lookback).apply(
            lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.5
        )
        
        if len(df) < 2:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'momentum'}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Fill NaN values
        latest = latest.fillna(0)
        prev = prev.fillna(0)
        
        signals = []
        confidence_scores = []
        
        # Strong momentum signals
        momentum_val = latest.get('momentum', 0) if pd.notna(latest.get('momentum', 0)) else 0
        roc_val = latest.get('roc', 0) if pd.notna(latest.get('roc', 0)) else 0
        
        if momentum_val > 0.05 and roc_val > 2:
            signals.append('BUY')
            confidence_scores.append(0.4)
        elif momentum_val < -0.05 and roc_val < -2:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # Volume confirmation
        volume_momentum = latest.get('volume_momentum', 0) if pd.notna(latest.get('volume_momentum', 0)) else 0
        if volume_momentum > 0 and momentum_val > 0:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif volume_momentum < 0 and momentum_val < 0:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Acceleration signals
        acceleration = latest.get('acceleration', 0) if pd.notna(latest.get('acceleration', 0)) else 0
        if acceleration > 0 and momentum_val > 0:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif acceleration < 0 and momentum_val < 0:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        # Price strength
        price_strength = latest.get('price_strength', 0.5) if pd.notna(latest.get('price_strength', 0.5)) else 0.5
        if price_strength > 0.7:
            signals.append('BUY')
            confidence_scores.append(0.1)
        elif price_strength < 0.3:
            signals.append('SELL')
            confidence_scores.append(0.1)
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 2:
            signal = 'BUY'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'BUY']) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            signal = 'SELL'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'SELL']) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'momentum',
            'momentum': momentum_val,
            'roc': roc_val,
            'details': f"Momentum: {momentum_val:.3f}, ROC: {roc_val:.2f}%"
        }
    
    def mean_reversion_strategy(self, df: pd.DataFrame, lookback: int = 20, 
                               std_dev: float = 2.0) -> Dict:
        """
        Mean Reversion Strategy - Buy oversold, sell overbought
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period
            std_dev: Standard deviation threshold
            
        Returns:
            Strategy signal dictionary
        """
        if len(df) < lookback + 10:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'mean_reversion'}
        
        # Calculate mean and std
        df['sma'] = df['close'].rolling(lookback).mean()
        df['std'] = df['close'].rolling(lookback).std()
        # Z-score with division by zero protection
        df['z_score'] = np.where(
            df['std'] != 0,
            (df['close'] - df['sma']) / df['std'],
            0
        )
        
        # Bollinger Bands
        df['bb_upper'] = df['sma'] + (df['std'] * std_dev)
        df['bb_lower'] = df['sma'] - (df['std'] * std_dev)
        # BB position with division by zero protection
        bb_range = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = np.where(
            bb_range != 0,
            (df['close'] - df['bb_lower']) / bb_range,
            0.5
        )
        
        # RSI for mean reversion
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        # RSI with division by zero protection
        rs = np.where(loss != 0, gain / loss, 0)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Distance from mean with division by zero protection
        df['distance_from_mean'] = np.where(
            df['sma'] != 0,
            (df['close'] - df['sma']) / df['sma'] * 100,
            0
        )
        
        if len(df) < 1:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'mean_reversion'}
        
        latest = df.iloc[-1]
        latest = latest.fillna(0)
        
        signals = []
        confidence_scores = []
        
        # Get values safely
        z_score_val = latest.get('z_score', 0) if pd.notna(latest.get('z_score', 0)) else 0
        close_val = latest.get('close', 0) if pd.notna(latest.get('close', 0)) else 0
        bb_lower_val = latest.get('bb_lower', 0) if pd.notna(latest.get('bb_lower', 0)) else 0
        bb_upper_val = latest.get('bb_upper', 0) if pd.notna(latest.get('bb_upper', 0)) else 0
        rsi_val = latest.get('rsi', 50) if pd.notna(latest.get('rsi', 50)) else 50
        distance_val = latest.get('distance_from_mean', 0) if pd.notna(latest.get('distance_from_mean', 0)) else 0
        
        # Z-score extremes
        if z_score_val < -std_dev:
            signals.append('BUY')
            confidence_scores.append(0.4)
        elif z_score_val > std_dev:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # Bollinger Band extremes
        if close_val < bb_lower_val:
            signals.append('BUY')
            confidence_scores.append(0.35)
        elif close_val > bb_upper_val:
            signals.append('SELL')
            confidence_scores.append(0.35)
        
        # RSI extremes
        if rsi_val < 30:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif rsi_val > 70:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Distance from mean
        if distance_val < -2:
            signals.append('BUY')
            confidence_scores.append(0.25)
        elif distance_val > 2:
            signals.append('SELL')
            confidence_scores.append(0.25)
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 2:
            signal = 'BUY'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'BUY']) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            signal = 'SELL'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'SELL']) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        bb_position_val = latest.get('bb_position', 0.5) if pd.notna(latest.get('bb_position', 0.5)) else 0.5
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'mean_reversion',
            'z_score': z_score_val,
            'rsi': rsi_val,
            'bb_position': bb_position_val,
            'details': f"Z-score: {z_score_val:.2f}, RSI: {rsi_val:.2f}"
        }
    
    def breakout_strategy(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Breakout Strategy - Buy breakouts above resistance, sell below support
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period for support/resistance
            
        Returns:
            Strategy signal dictionary
        """
        if len(df) < lookback + 10:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'breakout'}
        
        # Calculate support and resistance
        df['high_20'] = df['high'].rolling(lookback).max()
        df['low_20'] = df['low'].rolling(lookback).min()
        df['range'] = df['high_20'] - df['low_20']
        
        # Volume confirmation
        df['volume_ma'] = df['volume'].rolling(lookback).mean()
        # Volume ratio with division by zero protection
        df['volume_ratio'] = np.where(
            df['volume_ma'] != 0,
            df['volume'] / df['volume_ma'],
            1.0
        )
        
        # Price position in range with division by zero protection
        df['range_position'] = np.where(
            df['range'] != 0,
            (df['close'] - df['low_20']) / df['range'],
            0.5
        )
        
        # Breakout detection
        df['breakout_up'] = (df['close'] > df['high_20'].shift(1)).astype(int)
        df['breakout_down'] = (df['close'] < df['low_20'].shift(1)).astype(int)
        
        # Volatility expansion
        df['atr'] = self._calculate_atr(df)
        df['atr_ma'] = df['atr'].rolling(lookback).mean()
        # Volatility expansion with division by zero protection
        df['volatility_expansion'] = np.where(
            df['atr_ma'] != 0,
            df['atr'] / df['atr_ma'],
            1.0
        )
        
        if len(df) < 2:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'breakout'}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Fill NaN values
        latest = latest.fillna(0)
        prev = prev.fillna(0)
        
        signals = []
        confidence_scores = []
        
        # Get values safely
        breakout_up = latest.get('breakout_up', 0) if pd.notna(latest.get('breakout_up', 0)) else 0
        breakout_down = latest.get('breakout_down', 0) if pd.notna(latest.get('breakout_down', 0)) else 0
        volume_ratio = latest.get('volume_ratio', 1.0) if pd.notna(latest.get('volume_ratio', 1.0)) else 1.0
        range_position = latest.get('range_position', 0.5) if pd.notna(latest.get('range_position', 0.5)) else 0.5
        volatility_expansion = latest.get('volatility_expansion', 1.0) if pd.notna(latest.get('volatility_expansion', 1.0)) else 1.0
        close_val = latest.get('close', 0) if pd.notna(latest.get('close', 0)) else 0
        prev_high = prev.get('high', 0) if pd.notna(prev.get('high', 0)) else 0
        prev_low = prev.get('low', 0) if pd.notna(prev.get('low', 0)) else 0
        
        # Upward breakout with volume
        if breakout_up == 1 and volume_ratio > 1.5:
            signals.append('BUY')
            confidence_scores.append(0.5)
        # Downward breakout with volume
        elif breakout_down == 1 and volume_ratio > 1.5:
            signals.append('SELL')
            confidence_scores.append(0.5)
        
        # Near resistance with volume
        if range_position > 0.9 and volume_ratio > 1.3:
            signals.append('BUY')
            confidence_scores.append(0.3)
        # Near support with volume
        elif range_position < 0.1 and volume_ratio > 1.3:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Volatility expansion breakout
        if volatility_expansion > 1.2 and close_val > prev_high:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif volatility_expansion > 1.2 and close_val < prev_low:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 1:
            signal = 'BUY'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'BUY']) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 1:
            signal = 'SELL'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'SELL']) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'breakout',
            'range_position': range_position,
            'volume_ratio': volume_ratio,
            'volatility_expansion': volatility_expansion,
            'details': f"Range pos: {range_position:.2f}, Vol ratio: {volume_ratio:.2f}"
        }
    
    def trend_following_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Trend Following Strategy - Follow the trend
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Strategy signal dictionary
        """
        if len(df) < 50:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'trend_following'}
        
        # Multiple EMAs
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['sma_200'] = df['close'].rolling(200).mean() if len(df) >= 200 else df['close'].rolling(len(df)).mean()
        
        # ADX for trend strength
        df['adx'] = self._calculate_adx(df)
        
        # MACD
        macd_data = self._calculate_macd(df)
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']
        
        if len(df) < 2:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'trend_following'}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Fill NaN values
        latest = latest.fillna(0)
        prev = prev.fillna(0)
        
        signals = []
        confidence_scores = []
        
        # Get values safely
        ema_9 = latest.get('ema_9', 0) if pd.notna(latest.get('ema_9', 0)) else 0
        ema_21 = latest.get('ema_21', 0) if pd.notna(latest.get('ema_21', 0)) else 0
        ema_50 = latest.get('ema_50', 0) if pd.notna(latest.get('ema_50', 0)) else 0
        sma_200 = latest.get('sma_200', 0) if pd.notna(latest.get('sma_200', 0)) else 0
        close_val = latest.get('close', 0) if pd.notna(latest.get('close', 0)) else 0
        macd = latest.get('macd', 0) if pd.notna(latest.get('macd', 0)) else 0
        macd_signal = latest.get('macd_signal', 0) if pd.notna(latest.get('macd_signal', 0)) else 0
        prev_macd = prev.get('macd', 0) if pd.notna(prev.get('macd', 0)) else 0
        prev_macd_signal = prev.get('macd_signal', 0) if pd.notna(prev.get('macd_signal', 0)) else 0
        adx = latest.get('adx', 0) if pd.notna(latest.get('adx', 0)) else 0
        
        # EMA alignment (bullish)
        if ema_9 > ema_21 > ema_50:
            signals.append('BUY')
            confidence_scores.append(0.4)
        # EMA alignment (bearish)
        elif ema_9 < ema_21 < ema_50:
            signals.append('SELL')
            confidence_scores.append(0.4)
        
        # Price above/below SMA 200
        if close_val > sma_200:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif close_val < sma_200:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        # MACD crossover
        if macd > macd_signal and prev_macd <= prev_macd_signal:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif macd < macd_signal and prev_macd >= prev_macd_signal:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # ADX trend strength
        if adx > 25:  # Strong trend
            if ema_9 > ema_21:
                signals.append('BUY')
                confidence_scores.append(0.1)
            elif ema_9 < ema_21:
                signals.append('SELL')
                confidence_scores.append(0.1)
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 2:
            signal = 'BUY'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'BUY']) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            signal = 'SELL'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'SELL']) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'trend_following',
            'adx': adx,
            'ema_alignment': 'BULLISH' if ema_9 > ema_21 > ema_50 else 'BEARISH',
            'details': f"ADX: {adx:.2f}, EMA alignment: {ema_9 > ema_21 > ema_50}"
        }
    
    def volume_profile_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Volume Profile Strategy - Trade based on volume analysis
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Strategy signal dictionary
        """
        if len(df) < 30:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'volume_profile'}
        
        # Volume moving averages
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        df['volume_ma_20'] = df['volume'].rolling(20).mean()
        
        # Volume-price trend
        df['vpt'] = (df['close'].pct_change() * df['volume']).cumsum()
        df['vpt_ma'] = df['vpt'].rolling(20).mean()
        
        # On Balance Volume
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        df['obv_ma'] = df['obv'].rolling(20).mean()
        
        # Volume-weighted average price with division by zero protection
        volume_cumsum = df['volume'].cumsum()
        df['vwap'] = np.where(
            volume_cumsum != 0,
            (df['close'] * df['volume']).cumsum() / volume_cumsum,
            df['close']
        )
        
        # Accumulation/Distribution with division by zero protection
        hl_range = df['high'] - df['low']
        df['ad'] = np.where(
            hl_range != 0,
            ((df['close'] - df['low']) - (df['high'] - df['close'])) / hl_range * df['volume'],
            0
        )
        df['ad'] = df['ad'].fillna(0).cumsum()
        
        if len(df) < 2:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'volume_profile'}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Fill NaN values
        latest = latest.fillna(0)
        prev = prev.fillna(0)
        
        signals = []
        confidence_scores = []
        
        # Get values safely
        volume = latest.get('volume', 0) if pd.notna(latest.get('volume', 0)) else 0
        volume_ma_20 = latest.get('volume_ma_20', 0) if pd.notna(latest.get('volume_ma_20', 0)) else 0
        close_val = latest.get('close', 0) if pd.notna(latest.get('close', 0)) else 0
        prev_close = prev.get('close', 0) if pd.notna(prev.get('close', 0)) else 0
        vpt = latest.get('vpt', 0) if pd.notna(latest.get('vpt', 0)) else 0
        vpt_ma = latest.get('vpt_ma', 0) if pd.notna(latest.get('vpt_ma', 0)) else 0
        prev_vpt = prev.get('vpt', 0) if pd.notna(prev.get('vpt', 0)) else 0
        prev_vpt_ma = prev.get('vpt_ma', 0) if pd.notna(prev.get('vpt_ma', 0)) else 0
        obv = latest.get('obv', 0) if pd.notna(latest.get('obv', 0)) else 0
        obv_ma = latest.get('obv_ma', 0) if pd.notna(latest.get('obv_ma', 0)) else 0
        prev_obv = prev.get('obv', 0) if pd.notna(prev.get('obv', 0)) else 0
        prev_obv_ma = prev.get('obv_ma', 0) if pd.notna(prev.get('obv_ma', 0)) else 0
        vwap = latest.get('vwap', 0) if pd.notna(latest.get('vwap', 0)) else 0
        
        # Volume spike with price movement
        if volume_ma_20 > 0 and volume > volume_ma_20 * 1.5:
            if close_val > prev_close:
                signals.append('BUY')
                confidence_scores.append(0.4)
            elif close_val < prev_close:
                signals.append('SELL')
                confidence_scores.append(0.4)
        
        # VPT crossover
        if vpt > vpt_ma and prev_vpt <= prev_vpt_ma:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif vpt < vpt_ma and prev_vpt >= prev_vpt_ma:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # OBV crossover
        if obv > obv_ma and prev_obv <= prev_obv_ma:
            signals.append('BUY')
            confidence_scores.append(0.3)
        elif obv < obv_ma and prev_obv >= prev_obv_ma:
            signals.append('SELL')
            confidence_scores.append(0.3)
        
        # Price vs VWAP
        if close_val > vwap:
            signals.append('BUY')
            confidence_scores.append(0.2)
        elif close_val < vwap:
            signals.append('SELL')
            confidence_scores.append(0.2)
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count and buy_count >= 2:
            signal = 'BUY'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'BUY']) / buy_count, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            signal = 'SELL'
            confidence = min(sum([s for i, s in enumerate(confidence_scores) if signals[i] == 'SELL']) / sell_count, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        volume_ratio_val = volume / volume_ma_20 if volume_ma_20 > 0 else 0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': 'volume_profile',
            'volume_ratio': volume_ratio_val,
            'vpt_trend': 'UP' if vpt > vpt_ma else 'DOWN',
            'details': f"Vol ratio: {volume_ratio_val:.2f}, VPT: {vpt:.0f}"
        }
    
    def arbitrage_strategy(self, df: pd.DataFrame, market_data: List[Dict] = None) -> Dict:
        """
        Arbitrage Strategy - Find price discrepancies (simplified version)
        
        Args:
            df: DataFrame with OHLCV data
            market_data: Additional market data for comparison
            
        Returns:
            Strategy signal dictionary
        """
        # This is a simplified arbitrage - in real implementation,
        # you would compare prices across different exchanges/markets
        if len(df) < 20:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'arbitrage'}
        
        # Calculate fair value based on historical patterns
        df['fair_value'] = df['close'].rolling(20).mean()
        # Price deviation with division by zero protection
        df['price_deviation'] = np.where(
            df['fair_value'] != 0,
            (df['close'] - df['fair_value']) / df['fair_value'] * 100,
            0
        )
        
        if len(df) < 1:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategy': 'arbitrage'}
        
        latest = df.iloc[-1]
        latest = latest.fillna(0)
        
        price_deviation = latest.get('price_deviation', 0) if pd.notna(latest.get('price_deviation', 0)) else 0
        
        # Simple mean reversion arbitrage
        if price_deviation < -1.0:  # Price below fair value
            return {
                'signal': 'BUY',
                'confidence': 0.3,
                'strategy': 'arbitrage',
                'price_deviation': price_deviation,
                'details': f"Price deviation: {price_deviation:.2f}%"
            }
        elif price_deviation > 1.0:  # Price above fair value
            return {
                'signal': 'SELL',
                'confidence': 0.3,
                'strategy': 'arbitrage',
                'price_deviation': price_deviation,
                'details': f"Price deviation: {price_deviation:.2f}%"
            }
        
        return {
            'signal': 'HOLD',
            'confidence': 0.0,
            'strategy': 'arbitrage',
            'price_deviation': price_deviation,
            'details': f"Price deviation: {price_deviation:.2f}%"
        }
    
    def analyze_with_all_strategies(self, df: pd.DataFrame) -> Dict:
        """
        Analyze using all strategies and combine results
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Combined analysis result
        """
        strategies = [
            self.momentum_strategy(df),
            self.mean_reversion_strategy(df),
            self.breakout_strategy(df),
            self.trend_following_strategy(df),
            self.volume_profile_strategy(df),
            self.arbitrage_strategy(df)
        ]
        
        # Filter out HOLD signals
        active_strategies = [s for s in strategies if s['signal'] != 'HOLD']
        
        if not active_strategies:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'strategies': {},
                'details': 'No active strategy signals'
            }
        
        # Weight signals by strategy weights and confidence
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        
        strategy_details = {}
        
        for strategy_result in active_strategies:
            strategy_name = strategy_result['strategy']
            weight = self.strategy_weights.get(strategy_name, 0.1)
            confidence = strategy_result['confidence']
            
            weighted_score = weight * confidence
            total_weight += weight
            
            strategy_details[strategy_name] = {
                'signal': strategy_result['signal'],
                'confidence': confidence,
                'weight': weight
            }
            
            if strategy_result['signal'] == 'BUY':
                buy_score += weighted_score
            elif strategy_result['signal'] == 'SELL':
                sell_score += weighted_score
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine final signal
        if buy_score > sell_score and buy_score > 0.3:
            signal = 'BUY'
            confidence = min(buy_score, 1.0)
        elif sell_score > buy_score and sell_score > 0.3:
            signal = 'SELL'
            confidence = min(sell_score, 1.0)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'strategies': strategy_details,
            'active_strategies': len(active_strategies),
            'details': f"Buy: {buy_score:.2f}, Sell: {sell_score:.2f}, Active: {len(active_strategies)}"
        }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return {'macd': macd, 'signal': signal_line, 'histogram': histogram}
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        # Simplified ADX calculation
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        tr = self._calculate_atr(df, period)
        
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        
        return adx.fillna(0)
