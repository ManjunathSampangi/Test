"""
Market Regime Detector
Detects current market regime and adapts strategy accordingly
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    def __init__(self, config: Dict = None):
        """
        Initialize Market Regime Detector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.regime_history = []
        
    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """
        Detect current market regime
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Regime information dictionary
        """
        if len(df) < 50:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0.0,
                'recommended_strategies': []
            }
        
        # Calculate regime indicators
        volatility = self._calculate_volatility(df)
        trend_strength = self._calculate_trend_strength(df)
        volume_profile = self._analyze_volume_profile(df)
        price_action = self._analyze_price_action(df)
        
        # Determine regime
        regime_scores = {
            'TRENDING': 0.0,
            'RANGING': 0.0,
            'VOLATILE': 0.0,
            'BREAKOUT': 0.0,
            'REVERSAL': 0.0
        }
        
        # Trending regime
        if trend_strength > 0.7:
            regime_scores['TRENDING'] = trend_strength
        elif trend_strength > 0.5:
            regime_scores['TRENDING'] = trend_strength * 0.7
        
        # Ranging regime
        if volatility < 0.015 and trend_strength < 0.3:
            regime_scores['RANGING'] = 0.8
        
        # Volatile regime
        if volatility > 0.03:
            regime_scores['VOLATILE'] = min(volatility / 0.05, 1.0)
        
        # Breakout regime
        if price_action['breakout_probability'] > 0.6:
            regime_scores['BREAKOUT'] = price_action['breakout_probability']
        
        # Reversal regime
        if price_action['reversal_probability'] > 0.6:
            regime_scores['REVERSAL'] = price_action['reversal_probability']
        
        # Find dominant regime
        dominant_regime = max(regime_scores.items(), key=lambda x: x[1])
        regime_name = dominant_regime[0]
        confidence = dominant_regime[1]
        
        # Get recommended strategies for this regime
        recommended_strategies = self._get_recommended_strategies(regime_name)
        
        # Adjust strategy weights based on regime
        strategy_weights = self._get_strategy_weights(regime_name)
        
        result = {
            'regime': regime_name,
            'confidence': confidence,
            'volatility': volatility,
            'trend_strength': trend_strength,
            'volume_profile': volume_profile,
            'price_action': price_action,
            'recommended_strategies': recommended_strategies,
            'strategy_weights': strategy_weights,
            'regime_scores': regime_scores
        }
        
        self.regime_history.append({
            'timestamp': datetime.now(),
            'regime': regime_name,
            'confidence': confidence
        })
        
        # Keep only recent history
        if len(self.regime_history) > 100:
            self.regime_history = self.regime_history[-100:]
        
        return result
    
    def _calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calculate market volatility"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(period).std().iloc[-1]
        return volatility
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength (ADX-like)"""
        # Simplified trend strength calculation
        ema_fast = df['close'].ewm(span=9, adjust=False).mean()
        ema_slow = df['close'].ewm(span=21, adjust=False).mean()
        
        # Trend direction consistency
        trend_direction = (ema_fast > ema_slow).astype(int)
        consistency = trend_direction.rolling(20).mean().iloc[-1]
        
        # Price momentum
        momentum = abs(df['close'].pct_change(20).iloc[-1])
        
        # Combine metrics
        trend_strength = (consistency * 0.6 + min(momentum * 10, 1.0) * 0.4)
        
        return min(trend_strength, 1.0)
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict:
        """Analyze volume profile"""
        volume_ma = df['volume'].rolling(20).mean()
        try:
            current_volume = df['volume'].iloc[-1] if len(df) > 0 else 0
            volume_ma_val = volume_ma.iloc[-1] if len(volume_ma) > 0 and pd.notna(volume_ma.iloc[-1]) else 1.0
            volume_ratio = current_volume / volume_ma_val if volume_ma_val > 0 else 1.0
            if pd.isna(volume_ratio):
                volume_ratio = 1.0
        except (IndexError, KeyError, ZeroDivisionError):
            volume_ratio = 1.0
        
        # Volume trend
        try:
            if len(df) >= 15:
                vol_recent = df['volume'].iloc[-5:].mean() if len(df) >= 5 else 0
                vol_prev = df['volume'].iloc[-15:-5].mean() if len(df) >= 15 else 0
                volume_trend = 'INCREASING' if pd.notna(vol_recent) and pd.notna(vol_prev) and vol_recent > vol_prev else 'DECREASING'
            else:
                volume_trend = 'UNKNOWN'
        except Exception:
            volume_trend = 'UNKNOWN'
        
        return {
            'volume_ratio': volume_ratio,
            'volume_trend': volume_trend,
            'volume_regime': 'HIGH' if volume_ratio > 1.5 else 'NORMAL' if volume_ratio > 0.8 else 'LOW'
        }
    
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """Analyze price action patterns"""
        # Support and resistance levels
        lookback = 20
        high_20 = df['high'].rolling(lookback).max().iloc[-1]
        low_20 = df['low'].rolling(lookback).min().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Breakout probability
        range_size = high_20 - low_20
        distance_to_high = (high_20 - current_price) / range_size if range_size > 0 else 0.5
        distance_to_low = (current_price - low_20) / range_size if range_size > 0 else 0.5
        
        breakout_probability = 0.0
        if distance_to_high < 0.05:  # Near resistance
            breakout_probability = 0.7
        elif distance_to_low < 0.05:  # Near support
            breakout_probability = 0.3
        
        # Reversal probability
        reversal_probability = 0.0
        rsi = self._calculate_rsi(df)
        if rsi > 75:
            reversal_probability = 0.7
        elif rsi < 25:
            reversal_probability = 0.7
        
        # Momentum
        momentum_5 = df['close'].pct_change(5).iloc[-1]
        momentum_10 = df['close'].pct_change(10).iloc[-1]
        
        return {
            'breakout_probability': breakout_probability,
            'reversal_probability': reversal_probability,
            'momentum_5': momentum_5,
            'momentum_10': momentum_10,
            'distance_to_high': distance_to_high,
            'distance_to_low': distance_to_low
        }
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50.0
    
    def _get_recommended_strategies(self, regime: str) -> List[str]:
        """Get recommended strategies for regime"""
        strategy_map = {
            'TRENDING': ['trend_following', 'momentum', 'breakout'],
            'RANGING': ['mean_reversion', 'arbitrage'],
            'VOLATILE': ['breakout', 'momentum'],
            'BREAKOUT': ['breakout', 'momentum', 'volume_profile'],
            'REVERSAL': ['mean_reversion', 'volume_profile']
        }
        return strategy_map.get(regime, ['momentum', 'trend_following'])
    
    def _get_strategy_weights(self, regime: str) -> Dict[str, float]:
        """Get strategy weights adjusted for regime"""
        base_weights = {
            'momentum': 0.20,
            'mean_reversion': 0.20,
            'breakout': 0.20,
            'trend_following': 0.15,
            'volume_profile': 0.15,
            'arbitrage': 0.10
        }
        
        regime_adjustments = {
            'TRENDING': {
                'trend_following': 0.30,
                'momentum': 0.25,
                'breakout': 0.20,
                'mean_reversion': 0.10,
                'volume_profile': 0.10,
                'arbitrage': 0.05
            },
            'RANGING': {
                'mean_reversion': 0.35,
                'arbitrage': 0.25,
                'volume_profile': 0.20,
                'momentum': 0.10,
                'trend_following': 0.05,
                'breakout': 0.05
            },
            'VOLATILE': {
                'breakout': 0.30,
                'momentum': 0.25,
                'volume_profile': 0.20,
                'trend_following': 0.15,
                'mean_reversion': 0.05,
                'arbitrage': 0.05
            },
            'BREAKOUT': {
                'breakout': 0.40,
                'momentum': 0.25,
                'volume_profile': 0.20,
                'trend_following': 0.10,
                'mean_reversion': 0.03,
                'arbitrage': 0.02
            },
            'REVERSAL': {
                'mean_reversion': 0.40,
                'volume_profile': 0.25,
                'momentum': 0.15,
                'trend_following': 0.10,
                'breakout': 0.05,
                'arbitrage': 0.05
            }
        }
        
        return regime_adjustments.get(regime, base_weights)
    
    def get_regime_history(self, periods: int = 10) -> List[Dict]:
        """Get recent regime history"""
        return self.regime_history[-periods:] if len(self.regime_history) > periods else self.regime_history
