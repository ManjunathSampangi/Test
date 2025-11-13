"""
Intelligent Opportunity Finder
Finds trading opportunities intelligently, especially after losses
Uses multiple filters and adaptive criteria
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentOpportunityFinder:
    def __init__(self, config: Dict = None):
        """
        Initialize Intelligent Opportunity Finder
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.recent_losses = []
        self.successful_patterns = []
        
    def find_opportunities(self, symbols: List[str], market_data_func, 
                          analysis_func, recent_performance: Dict) -> List[Dict]:
        """
        Find trading opportunities with intelligent filtering
        
        Args:
            symbols: List of symbols to analyze
            market_data_func: Function to get market data for a symbol
            analysis_func: Function to analyze a symbol
            recent_performance: Recent performance metrics
            
        Returns:
            List of opportunities sorted by quality
        """
        opportunities = []
        
        # Adjust criteria based on recent performance
        min_confidence = self._calculate_min_confidence(recent_performance)
        volume_multiplier = self._calculate_volume_multiplier(recent_performance)
        
        logger.info(f"Finding opportunities with min_confidence={min_confidence:.2f}, "
                   f"volume_multiplier={volume_multiplier:.2f}")
        
        for symbol in symbols:
            try:
                # Get market data
                df = market_data_func(symbol)
                if df.empty or len(df) < 20:
                    continue
                
                # Analyze symbol
                analysis = analysis_func(df)
                
                if analysis['signal'] == 'HOLD':
                    continue
                
                # Apply intelligent filters
                if self._passes_filters(df, analysis, min_confidence, volume_multiplier, recent_performance):
                    opportunity = {
                        'symbol': symbol,
                        'signal': analysis['signal'],
                        'confidence': analysis['confidence'],
                        'price': analysis.get('price', df['close'].iloc[-1]),
                        'analysis': analysis,
                        'quality_score': self._calculate_quality_score(df, analysis, recent_performance),
                        'risk_reward': self._calculate_risk_reward(df, analysis),
                        'market_conditions': self._analyze_market_conditions(df)
                    }
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                continue
        
        # Sort by quality score
        opportunities.sort(key=lambda x: x['quality_score'], reverse=True)
        
        logger.info(f"Found {len(opportunities)} high-quality opportunities")
        return opportunities
    
    def find_opportunities_after_loss(self, symbols: List[str], market_data_func,
                                      analysis_func, loss_amount: float,
                                      recent_trades: List[Dict]) -> List[Dict]:
        """
        Find opportunities specifically after a loss - more conservative approach
        
        Args:
            symbols: List of symbols to analyze
            market_data_func: Function to get market data
            analysis_func: Function to analyze symbol
            loss_amount: Amount of recent loss
            recent_trades: Recent trade history
            
        Returns:
            List of high-quality opportunities
        """
        # After loss, be more selective
        recent_performance = {
            'recent_loss': loss_amount,
            'consecutive_losses': self._count_consecutive_losses(recent_trades),
            'win_rate': self._calculate_recent_win_rate(recent_trades)
        }
        
        # Increase minimum confidence after losses
        base_min_confidence = 0.6
        if recent_performance['consecutive_losses'] >= 2:
            base_min_confidence = 0.75  # Very selective after 2+ losses
        elif recent_performance['consecutive_losses'] == 1:
            base_min_confidence = 0.65  # More selective after 1 loss
        
        # Find opportunities with stricter criteria
        opportunities = []
        
        for symbol in symbols:
            try:
                df = market_data_func(symbol)
                if df.empty or len(df) < 30:  # Require more data after loss
                    continue
                
                analysis = analysis_func(df)
                
                if analysis['signal'] == 'HOLD':
                    continue
                
                # Stricter filters after loss
                if analysis['confidence'] < base_min_confidence:
                    continue
                
                # Check for high-probability setups only
                if not self._is_high_probability_setup(df, analysis):
                    continue
                
                # Calculate quality score (higher threshold after loss)
                quality_score = self._calculate_quality_score(df, analysis, recent_performance)
                if quality_score < 0.7:  # Higher threshold
                    continue
                
                opportunity = {
                    'symbol': symbol,
                    'signal': analysis['signal'],
                    'confidence': analysis['confidence'],
                    'price': analysis.get('price', df['close'].iloc[-1]),
                    'analysis': analysis,
                    'quality_score': quality_score,
                    'risk_reward': self._calculate_risk_reward(df, analysis),
                    'market_conditions': self._analyze_market_conditions(df),
                    'recovery_potential': self._estimate_recovery_potential(df, analysis, loss_amount)
                }
                opportunities.append(opportunity)
                
            except Exception as e:
                logger.error(f"Error finding opportunity for {symbol} after loss: {str(e)}")
                continue
        
        # Sort by recovery potential and quality
        opportunities.sort(key=lambda x: (x.get('recovery_potential', 0) * x['quality_score']), reverse=True)
        
        logger.info(f"Found {len(opportunities)} high-quality recovery opportunities after loss")
        return opportunities
    
    def _passes_filters(self, df: pd.DataFrame, analysis: Dict, min_confidence: float,
                       volume_multiplier: float, recent_performance: Dict) -> bool:
        """Check if opportunity passes all filters"""
        # Confidence filter
        if analysis['confidence'] < min_confidence:
            return False
        
        # Volume filter
        if 'volume_ratio' in analysis:
            if analysis['volume_ratio'] < volume_multiplier:
                return False
        else:
            # Calculate volume ratio
            volume_ma = df['volume'].rolling(20).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            if current_volume / volume_ma < volume_multiplier:
                return False
        
        # Price action filter
        if not self._has_good_price_action(df):
            return False
        
        # Volatility filter (avoid extreme volatility)
        volatility = df['close'].pct_change().rolling(10).std().iloc[-1]
        if volatility > 0.05:  # Too volatile
            return False
        
        return True
    
    def _has_good_price_action(self, df: pd.DataFrame) -> bool:
        """Check if price action is favorable"""
        # Check for consistent trend or clear reversal
        recent_returns = df['close'].pct_change().tail(5)
        
        # Avoid choppy markets
        if recent_returns.std() > recent_returns.mean() * 2:
            return False
        
        return True
    
    def _is_high_probability_setup(self, df: pd.DataFrame, analysis: Dict) -> bool:
        """Check if this is a high-probability setup"""
        # Multiple confirmations required
        confirmations = 0
        
        # Volume confirmation
        volume_ma = df['volume'].rolling(20).mean().iloc[-1]
        if df['volume'].iloc[-1] > volume_ma * 1.5:
            confirmations += 1
        
        # Price momentum confirmation
        momentum = df['close'].pct_change(5).iloc[-1]
        if abs(momentum) > 0.02:
            confirmations += 1
        
        # Technical indicator alignment
        if analysis['confidence'] > 0.7:
            confirmations += 1
        
        # Multiple strategy agreement (if available)
        if 'strategies' in analysis:
            active_strategies = len([s for s in analysis['strategies'].values() if s['signal'] != 'HOLD'])
            if active_strategies >= 3:
                confirmations += 1
        
        return confirmations >= 2
    
    def _calculate_quality_score(self, df: pd.DataFrame, analysis: Dict,
                                 recent_performance: Dict) -> float:
        """Calculate overall quality score for opportunity"""
        score = 0.0
        
        # Base confidence score (40%)
        score += analysis['confidence'] * 0.4
        
        # Volume quality (20%)
        volume_ma = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = df['volume'].iloc[-1] / volume_ma if volume_ma > 0 else 1.0
        volume_score = min(volume_ratio / 2.0, 1.0)  # Cap at 2x average
        score += volume_score * 0.2
        
        # Price momentum (15%)
        momentum = abs(df['close'].pct_change(5).iloc[-1])
        momentum_score = min(momentum / 0.05, 1.0)  # Normalize to 5% move
        score += momentum_score * 0.15
        
        # Risk-reward ratio (15%)
        risk_reward = self._calculate_risk_reward(df, analysis)
        rr_score = min(risk_reward / 3.0, 1.0)  # Cap at 3:1 RR
        score += rr_score * 0.15
        
        # Market conditions (10%)
        market_score = self._analyze_market_conditions_score(df)
        score += market_score * 0.1
        
        return min(score, 1.0)
    
    def _calculate_risk_reward(self, df: pd.DataFrame, analysis: Dict) -> float:
        """Calculate risk-reward ratio"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Estimate stop loss (2% default)
            stop_loss_pct = 0.02
            stop_loss = current_price * (1 - stop_loss_pct)
            
            # Estimate take profit based on analysis confidence
            take_profit_pct = analysis['confidence'] * 0.03  # Up to 3% based on confidence
            take_profit = current_price * (1 + take_profit_pct)
            
            risk = current_price - stop_loss
            reward = take_profit - current_price
            
            if risk > 0:
                return reward / risk
            return 1.0
        except:
            return 1.5  # Default
    
    def _analyze_market_conditions(self, df: pd.DataFrame) -> Dict:
        """Analyze current market conditions"""
        volatility = df['close'].pct_change().rolling(20).std().iloc[-1]
        trend = 'UP' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'DOWN'
        volume_trend = 'INCREASING' if df['volume'].iloc[-5:].mean() > df['volume'].iloc[-20:-5].mean() else 'DECREASING'
        
        return {
            'volatility': volatility,
            'trend': trend,
            'volume_trend': volume_trend,
            'condition': 'TRENDING' if volatility < 0.02 else 'VOLATILE'
        }
    
    def _analyze_market_conditions_score(self, df: pd.DataFrame) -> float:
        """Score market conditions (0-1)"""
        volatility = df['close'].pct_change().rolling(20).std().iloc[-1]
        
        # Prefer moderate volatility (not too low, not too high)
        if 0.01 < volatility < 0.03:
            return 1.0
        elif 0.005 < volatility < 0.04:
            return 0.7
        else:
            return 0.4
    
    def _calculate_min_confidence(self, recent_performance: Dict) -> float:
        """Calculate minimum confidence based on recent performance"""
        base_confidence = 0.6
        
        # Increase confidence requirement after losses
        if recent_performance.get('recent_loss', 0) > 0:
            base_confidence += 0.1
        
        # Increase if win rate is low
        win_rate = recent_performance.get('win_rate', 0.5)
        if win_rate < 0.4:
            base_confidence += 0.1
        
        return min(base_confidence, 0.8)
    
    def _calculate_volume_multiplier(self, recent_performance: Dict) -> float:
        """Calculate required volume multiplier"""
        base_multiplier = 1.5
        
        # Require higher volume after losses
        if recent_performance.get('recent_loss', 0) > 0:
            base_multiplier += 0.3
        
        return base_multiplier
    
    def _count_consecutive_losses(self, recent_trades: List[Dict]) -> int:
        """Count consecutive losses"""
        count = 0
        for trade in reversed(recent_trades):
            if trade.get('pnl', 0) < 0:
                count += 1
            else:
                break
        return count
    
    def _calculate_recent_win_rate(self, recent_trades: List[Dict], window: int = 10) -> float:
        """Calculate recent win rate"""
        if not recent_trades:
            return 0.5
        
        recent = recent_trades[-window:]
        wins = sum(1 for t in recent if t.get('pnl', 0) > 0)
        return wins / len(recent) if recent else 0.5
    
    def _estimate_recovery_potential(self, df: pd.DataFrame, analysis: Dict,
                                    loss_amount: float) -> float:
        """Estimate potential to recover from loss"""
        if loss_amount <= 0:
            return 1.0
        
        # Estimate potential profit
        current_price = df['close'].iloc[-1]
        potential_profit_pct = analysis['confidence'] * 0.03  # Up to 3%
        potential_profit = current_price * potential_profit_pct
        
        # Estimate position size needed
        # Assuming we risk 1% per trade
        account_value = 50000  # Default
        risk_per_trade = account_value * 0.01
        position_size = risk_per_trade / (current_price * 0.02)  # 2% stop loss
        
        potential_recovery = potential_profit * position_size
        
        # Recovery ratio
        if loss_amount > 0:
            recovery_ratio = min(potential_recovery / loss_amount, 2.0)  # Cap at 2x
            return recovery_ratio
        
        return 1.0
