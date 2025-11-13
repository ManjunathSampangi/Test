"""
Intelligent Autonomous Trading Bot
Enhanced version with multiple strategies, ML analysis, and intelligent opportunity finding
"""

import os
import json
import time
import logging
import pandas as pd
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional
from dotenv import load_dotenv

from fyers_auth import FyersAuth
from market_data import MarketData
from technical_analysis import TechnicalAnalysis
from trading_execution import TradingExecution
from risk_management import RiskManagement
from profit_tracker import ProfitTracker
from advanced_strategies import AdvancedStrategies
from intelligent_opportunity_finder import IntelligentOpportunityFinder
from ml_analysis import MLAnalysis
from market_regime_detector import MarketRegimeDetector

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IntelligentTradingBot:
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize Intelligent Trading Bot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize components
        self.auth = FyersAuth()
        self.session = None
        self.market_data = None
        self.technical_analysis = TechnicalAnalysis(self.config.get('analysis', {}))
        self.trading_execution = None
        
        # Advanced components
        self.advanced_strategies = AdvancedStrategies(self.config.get('strategies', {}))
        self.opportunity_finder = IntelligentOpportunityFinder(self.config.get('opportunity_finder', {}))
        self.ml_analysis = MLAnalysis(self.config.get('ml_analysis', {}))
        self.regime_detector = MarketRegimeDetector(self.config.get('regime_detector', {}))
        
        # Risk management
        scalping_config = self.config.get('scalping', {}) if self.config.get('scalping', {}).get('enabled', False) else None
        self.risk_management = RiskManagement(self.config['trading'], scalping_config)
        
        # Profit tracker
        self.profit_tracker = ProfitTracker(self.config)
        
        # Trading state
        self.active_positions = {}
        self.trade_history = []
        self.is_running = False
        self.current_regime = None
        self.recent_performance = {
            'recent_loss': 0.0,
            'consecutive_losses': 0,
            'win_rate': 0.5
        }
        
        # Symbols to trade
        self.symbols_to_trade = (
            self.config['symbols'].get('high_liquidity_symbols', []) +
            self.config['symbols'].get('nifty_options', []) +
            self.config['symbols'].get('stock_options', [])
        )
        
        # Remove duplicates
        self.symbols_to_trade = list(set(self.symbols_to_trade))
        
    def initialize(self) -> bool:
        """
        Initialize bot components and authenticate
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Intelligent Trading Bot...")
            
            # Create Fyers session
            self.session = self.auth.create_session()
            if not self.session:
                logger.error("Failed to create Fyers session")
                return False
            
            # Verify authentication
            if not self.auth.is_authenticated():
                logger.error("Authentication failed. Please check your credentials.")
                return False
            
            logger.info("Authentication successful")
            
            # Initialize market data
            self.market_data = MarketData(self.session)
            
            # Initialize trading execution
            self.trading_execution = TradingExecution(self.session)
            
            # Train ML models if enough historical data available
            logger.info("Training ML models...")
            self._train_ml_models()
            
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            return False
    
    def _train_ml_models(self):
        """Train ML models on historical data"""
        try:
            # Try to get historical data for training
            training_symbols = self.symbols_to_trade[:3]  # Use first 3 symbols
            
            all_data = []
            for symbol in training_symbols:
                try:
                    df = self.market_data.get_historical_data(
                        symbol, 
                        resolution='15',
                        range_from=None,
                        range_to=None
                    )
                    if not df.empty and len(df) > 100:
                        all_data.append(df)
                except:
                    continue
            
            if all_data:
                # Combine data
                combined_df = pd.concat(all_data, ignore_index=True) if len(all_data) > 1 else all_data[0]
                self.ml_analysis.train_models(combined_df)
                logger.info("ML models trained successfully")
            else:
                logger.warning("Insufficient data for ML training, using rule-based predictions")
        except Exception as e:
            logger.warning(f"Could not train ML models: {str(e)}, using rule-based predictions")
    
    def get_account_value(self) -> float:
        """Get total account value"""
        try:
            profile = self.auth.get_profile()
            if profile and profile.get('s') == 'ok':
                fund_data = profile.get('fund_limit', [])
                if fund_data:
                    return float(fund_data[0].get('equityAmount', 50000))
            return 50000.0  # Default fallback
        except Exception as e:
            logger.error(f"Error getting account value: {str(e)}")
            return 50000.0
    
    def analyze_symbol_intelligently(self, symbol: str) -> Dict:
        """
        Analyze symbol using all available methods
        
        Args:
            symbol: Symbol to analyze
            
        Returns:
            Comprehensive analysis result
        """
        try:
            # Get historical data
            resolution = self.config.get('analysis', {}).get('timeframe', '1')
            df = self.market_data.get_historical_data(
                symbol, 
                resolution=resolution,
                range_from=None,
                range_to=None
            )
            
            if df.empty or len(df) < 20:
                return {
                    'symbol': symbol,
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'error': 'Insufficient data'
                }
            
            # Detect market regime
            regime_info = self.regime_detector.detect_regime(df)
            self.current_regime = regime_info['regime']
            
            # Update strategy weights based on regime
            if regime_info.get('strategy_weights'):
                self.advanced_strategies.strategy_weights = regime_info['strategy_weights']
            
            # Analyze with advanced strategies
            strategy_analysis = self.advanced_strategies.analyze_with_all_strategies(df)
            
            # ML prediction
            ml_prediction = self.ml_analysis.predict(df)
            
            # Technical analysis
            features_df = self.technical_analysis.generate_features(df)
            technical_signal = self.technical_analysis.generate_signal(features_df)
            
            # Combine all analyses
            combined_signal = self._combine_signals(
                strategy_analysis,
                ml_prediction,
                technical_signal,
                regime_info
            )
            
            return {
                'symbol': symbol,
                'signal': combined_signal['signal'],
                'confidence': combined_signal['confidence'],
                'price': df['close'].iloc[-1],
                'regime': regime_info['regime'],
                'regime_confidence': regime_info['confidence'],
                'strategy_analysis': strategy_analysis,
                'ml_prediction': ml_prediction,
                'technical_signal': technical_signal,
                'recommended_strategies': regime_info.get('recommended_strategies', []),
                'details': combined_signal.get('details', '')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _combine_signals(self, strategy_analysis: Dict, ml_prediction: Dict,
                         technical_signal: Dict, regime_info: Dict) -> Dict:
        """Combine signals from multiple sources"""
        signals = []
        confidences = []
        weights = []
        
        # Strategy analysis (weight: 0.4)
        if strategy_analysis['signal'] != 'HOLD':
            signals.append(strategy_analysis['signal'])
            confidences.append(strategy_analysis['confidence'])
            weights.append(0.4)
        
        # ML prediction (weight: 0.3)
        if ml_prediction['prediction'] != 'HOLD':
            signals.append(ml_prediction['prediction'])
            confidences.append(ml_prediction['confidence'])
            weights.append(0.3)
        
        # Technical analysis (weight: 0.3)
        if technical_signal['signal'] != 'HOLD':
            signals.append(technical_signal['signal'])
            confidences.append(technical_signal['confidence'])
            weights.append(0.3)
        
        if not signals:
            return {'signal': 'HOLD', 'confidence': 0.0, 'details': 'No signals'}
        
        # Weighted voting
        buy_score = 0.0
        sell_score = 0.0
        total_weight = sum(weights)
        
        for signal, confidence, weight in zip(signals, confidences, weights):
            weighted_conf = confidence * weight
            if signal == 'BUY':
                buy_score += weighted_conf
            elif signal == 'SELL':
                sell_score += weighted_conf
        
        # Normalize
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine final signal
        min_confidence = 0.6  # Minimum confidence threshold
        
        if buy_score > sell_score and buy_score >= min_confidence:
            signal = 'BUY'
            confidence = buy_score
        elif sell_score > buy_score and sell_score >= min_confidence:
            signal = 'SELL'
            confidence = sell_score
        else:
            signal = 'HOLD'
            confidence = max(buy_score, sell_score)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'details': f"Buy: {buy_score:.2f}, Sell: {sell_score:.2f}, Regime: {regime_info['regime']}"
        }
    
    def find_trading_opportunities(self) -> List[Dict]:
        """Find trading opportunities intelligently"""
        # Update recent performance
        recent_trades = self.profit_tracker.trades[-10:] if len(self.profit_tracker.trades) >= 10 else self.profit_tracker.trades
        self.recent_performance = {
            'recent_loss': sum(t.get('pnl', 0) for t in recent_trades if t.get('pnl', 0) < 0),
            'consecutive_losses': self._count_consecutive_losses(recent_trades),
            'win_rate': self._calculate_win_rate(recent_trades)
        }
        
        # Use intelligent opportunity finder
        if self.recent_performance['recent_loss'] < 0:
            # After loss, use recovery mode
            opportunities = self.opportunity_finder.find_opportunities_after_loss(
                symbols=self.symbols_to_trade,
                market_data_func=lambda s: self.market_data.get_historical_data(s, resolution='1'),
                analysis_func=lambda df: self.advanced_strategies.analyze_with_all_strategies(df),
                loss_amount=abs(self.recent_performance['recent_loss']),
                recent_trades=recent_trades
            )
        else:
            # Normal mode
            opportunities = self.opportunity_finder.find_opportunities(
                symbols=self.symbols_to_trade,
                market_data_func=lambda s: self.market_data.get_historical_data(s, resolution='1'),
                analysis_func=lambda df: self.advanced_strategies.analyze_with_all_strategies(df),
                recent_performance=self.recent_performance
            )
        
        logger.info(f"Found {len(opportunities)} opportunities")
        return opportunities
    
    def execute_trade(self, opportunity: Dict) -> bool:
        """Execute a trade based on opportunity"""
        try:
            symbol = opportunity['symbol']
            signal = opportunity['signal']
            price = opportunity['price']
            
            # Get account value
            account_value = self.get_account_value()
            
            # Get current positions
            positions = self.trading_execution.get_positions()
            current_position_count = len([p for p in positions if float(p.get('qty', 0)) != 0])
            
            # Calculate stop loss
            stop_loss = self.risk_management.calculate_stop_loss(price, signal)
            
            # Calculate position size
            quantity = self.risk_management.calculate_position_size(
                account_value, price, stop_loss
            )
            
            # Validate trade
            validation = self.risk_management.validate_trade(
                account_value, price, quantity, current_position_count
            )
            
            if not validation['valid']:
                logger.warning(f"Trade validation failed for {symbol}: {validation['message']}")
                return False
            
            # Place order
            logger.info(f"Executing {signal} order for {symbol}: {quantity} units at {price}")
            logger.info(f"Regime: {opportunity.get('regime', 'UNKNOWN')}, "
                       f"Confidence: {opportunity.get('confidence', 0):.2f}")
            
            order_result = self.trading_execution.place_option_order(
                option_symbol=symbol,
                side=signal,
                quantity=quantity,
                order_type='MARKET'
            )
            
            if order_result['success']:
                # Track position
                self.active_positions[symbol] = {
                    'entry_price': price,
                    'quantity': quantity,
                    'side': signal,
                    'stop_loss': stop_loss,
                    'take_profit': self.risk_management.calculate_take_profit(price, signal),
                    'entry_time': datetime.now(),
                    'order_id': order_result.get('order_id'),
                    'regime': opportunity.get('regime'),
                    'confidence': opportunity.get('confidence')
                }
                
                self.trade_history.append({
                    'symbol': symbol,
                    'side': signal,
                    'quantity': quantity,
                    'entry_price': price,
                    'time': datetime.now(),
                    'order_id': order_result.get('order_id')
                })
                
                logger.info(f"Trade executed successfully: {symbol}")
                return True
            else:
                logger.error(f"Trade execution failed: {order_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return False
    
    def monitor_positions(self):
        """Monitor active positions and exit if needed"""
        try:
            positions = self.trading_execution.get_positions()
            
            for symbol, position_info in list(self.active_positions.items()):
                # Get current price
                current_price = self.market_data.get_latest_price(symbol)
                
                if current_price == 0:
                    continue
                
                # Update highest/lowest price for trailing stop
                if 'highest_price' not in position_info:
                    position_info['highest_price'] = current_price
                    position_info['lowest_price'] = current_price
                else:
                    position_info['highest_price'] = max(position_info['highest_price'], current_price)
                    position_info['lowest_price'] = min(position_info['lowest_price'], current_price)
                
                # Check if should exit
                scalping_config = self.config.get('scalping', {})
                if scalping_config.get('enabled', False):
                    exit_decision = self.risk_management.should_exit_scalping_position(
                        entry_price=position_info['entry_price'],
                        current_price=current_price,
                        side=position_info['side'],
                        entry_time=position_info['entry_time'],
                        highest_price=position_info.get('highest_price'),
                        lowest_price=position_info.get('lowest_price')
                    )
                else:
                    exit_decision = self.risk_management.should_exit_position(
                        entry_price=position_info['entry_price'],
                        current_price=current_price,
                        side=position_info['side'],
                        position_type='LONG' if position_info['side'] == 'BUY' else 'SHORT'
                    )
                
                if exit_decision['should_exit']:
                    logger.info(f"Exiting position {symbol}: {exit_decision['reason']}")
                    
                    # Exit position
                    exit_result = self.trading_execution.exit_position(
                        symbol=symbol,
                        quantity=position_info['quantity']
                    )
                    
                    if exit_result['success']:
                        # Calculate P&L
                        pnl = (current_price - position_info['entry_price']) * position_info['quantity']
                        if position_info['side'] == 'SELL':
                            pnl = -pnl
                        
                        logger.info(f"Position closed: {symbol}, P&L: ₹{pnl:.2f}, Reason: {exit_decision['reason']}")
                        
                        # Record trade
                        self.profit_tracker.record_trade(
                            symbol=symbol,
                            side=position_info['side'],
                            entry_price=position_info['entry_price'],
                            exit_price=current_price,
                            quantity=position_info['quantity'],
                            entry_time=position_info['entry_time'],
                            exit_time=datetime.now(),
                            pnl=pnl
                        )
                        
                        # Remove from active positions
                        del self.active_positions[symbol]
                    else:
                        logger.error(f"Failed to exit position {symbol}")
                        
        except Exception as e:
            logger.error(f"Error monitoring positions: {str(e)}")
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        now = datetime.now()
        current_time = now.time()
        
        trading_start = dt_time(9, 15)
        trading_end = dt_time(15, 30)
        
        is_weekday = now.weekday() < 5
        
        return is_weekday and trading_start <= current_time <= trading_end
    
    def run_cycle(self):
        """Run one trading cycle"""
        try:
            if not self.is_trading_hours():
                logger.info("Outside trading hours, waiting...")
                return
            
            # Check if should continue trading
            continue_check = self.profit_tracker.should_continue_trading()
            if not continue_check['should_continue']:
                logger.warning(f"Stopping trading: {', '.join(continue_check['reasons'])}")
                logger.info(f"Daily P&L: ₹{continue_check['daily_profit']:.2f}")
                self.is_running = False
                return
            
            logger.info("=" * 60)
            logger.info("Starting Intelligent Trading Cycle")
            logger.info("=" * 60)
            
            # Show performance summary
            perf_summary = self.profit_tracker.get_performance_summary()
            logger.info(f"Today's Performance: Trades: {perf_summary['total_trades']}, "
                       f"P&L: ₹{perf_summary['profit']:.2f}, "
                       f"Win Rate: {perf_summary['win_rate']:.2%}")
            
            # Monitor existing positions
            self.monitor_positions()
            
            # Detect market regime
            if self.symbols_to_trade:
                try:
                    sample_df = self.market_data.get_historical_data(
                        self.symbols_to_trade[0], 
                        resolution='15'
                    )
                    if not sample_df.empty:
                        regime_info = self.regime_detector.detect_regime(sample_df)
                        logger.info(f"Market Regime: {regime_info['regime']} "
                                  f"(confidence: {regime_info['confidence']:.2f})")
                        self.current_regime = regime_info['regime']
                except:
                    pass
            
            # Find new opportunities
            opportunities = self.find_trading_opportunities()
            
            # Execute trades for top opportunities
            max_positions = self.config.get('scalping', {}).get('max_positions', 10) if \
                self.config.get('scalping', {}).get('enabled', False) else \
                self.config['trading']['max_positions']
            
            max_new_positions = max_positions - len(self.active_positions)
            
            executed = 0
            for opportunity in opportunities[:max_new_positions]:
                if opportunity['symbol'] not in self.active_positions:
                    if self.execute_trade(opportunity):
                        executed += 1
                        time.sleep(0.5)  # Small delay between trades
            
            logger.info(f"Executed {executed} new trades")
            logger.info(f"Active positions: {len(self.active_positions)}/{max_positions}")
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
    
    def run(self, cycle_interval: int = None):
        """Run the bot autonomously"""
        if not self.initialize():
            logger.error("Failed to initialize bot. Exiting.")
            return
        
        if cycle_interval is None:
            cycle_interval = self.config.get('scalping', {}).get('cycle_interval_seconds', 30) if \
                self.config.get('scalping', {}).get('enabled', False) else 60
        
        self.is_running = True
        logger.info("=" * 60)
        logger.info("Intelligent Trading Bot Started")
        logger.info("=" * 60)
        logger.info(f"Daily Profit Target: ₹{self.profit_tracker.daily_profit_target}")
        logger.info(f"Daily Loss Limit: ₹{self.profit_tracker.daily_loss_limit}")
        logger.info(f"Cycle Interval: {cycle_interval} seconds")
        logger.info("=" * 60)
        
        try:
            while self.is_running:
                self.run_cycle()
                
                if self.is_running:
                    logger.info(f"Waiting {cycle_interval} seconds until next cycle...")
                    time.sleep(cycle_interval)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.is_running = False
            self._show_final_summary()
        except Exception as e:
            logger.error(f"Fatal error in bot: {str(e)}")
            self.is_running = False
    
    def _show_final_summary(self):
        """Show final performance summary"""
        perf_summary = self.profit_tracker.get_performance_summary()
        logger.info("=" * 60)
        logger.info("FINAL PERFORMANCE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {perf_summary['total_trades']}")
        logger.info(f"Wins: {perf_summary['wins']}, Losses: {perf_summary['losses']}")
        logger.info(f"Win Rate: {perf_summary['win_rate']:.2%}")
        logger.info(f"Total P&L: ₹{perf_summary['profit']:.2f}")
        logger.info(f"Profit Factor: {perf_summary['profit_factor']:.2f}")
        logger.info("=" * 60)
    
    def _count_consecutive_losses(self, recent_trades: List[Dict]) -> int:
        """Count consecutive losses"""
        count = 0
        for trade in reversed(recent_trades):
            if trade.get('pnl', 0) < 0:
                count += 1
            else:
                break
        return count
    
    def _calculate_win_rate(self, recent_trades: List[Dict]) -> float:
        """Calculate win rate"""
        if not recent_trades:
            return 0.5
        wins = sum(1 for t in recent_trades if t.get('pnl', 0) > 0)
        return wins / len(recent_trades)


def main():
    """Main entry point"""
    bot = IntelligentTradingBot()
    bot.run()


if __name__ == "__main__":
    main()
