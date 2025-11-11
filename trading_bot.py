"""
Autonomous Trading Bot
Main orchestrator that runs the trading bot autonomously
"""

import os
import json
import time
import logging
from datetime import datetime, time as dt_time
from typing import Dict, List
from dotenv import load_dotenv

from fyers_auth import FyersAuth
from market_data import MarketData
from technical_analysis import TechnicalAnalysis
from trading_execution import TradingExecution
from risk_management import RiskManagement
from profit_tracker import ProfitTracker

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutonomousTradingBot:
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize Autonomous Trading Bot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Check if scalping is enabled
        self.scalping_enabled = self.config.get('scalping', {}).get('enabled', False)
        
        # Initialize components
        self.auth = FyersAuth()
        self.session = None
        self.market_data = None
        self.technical_analysis = TechnicalAnalysis(self.config.get('analysis', {}))
        self.trading_execution = None
        
        # Initialize risk management with scalping config if enabled
        scalping_config = self.config.get('scalping', {}) if self.scalping_enabled else None
        self.risk_management = RiskManagement(self.config['trading'], scalping_config)
        
        # Initialize profit tracker
        self.profit_tracker = ProfitTracker(self.config)
        
        # Trading state
        self.active_positions = {}
        self.trade_history = []
        self.is_running = False
        
        # Symbols to trade (prioritize high liquidity for scalping)
        if self.scalping_enabled:
            self.symbols_to_trade = self.config['symbols'].get('high_liquidity_symbols', [])
            if not self.symbols_to_trade:
                self.symbols_to_trade = (self.config['symbols'].get('nifty_options', []) + 
                                       self.config['symbols'].get('stock_options', []))
        else:
            self.nifty_symbols = self.config['symbols'].get('nifty_options', [])
            self.stock_symbols = self.config['symbols'].get('stock_options', [])
        
    def initialize(self) -> bool:
        """
        Initialize bot components and authenticate
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing trading bot...")
            
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
            
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}")
            return False
    
    def get_account_value(self) -> float:
        """
        Get total account value
        
        Returns:
            Account value (float)
        """
        try:
            profile = self.auth.get_profile()
            if profile and profile.get('s') == 'ok':
                fund_data = profile.get('fund_limit', [])
                if fund_data:
                    return float(fund_data[0].get('equityAmount', 0))
            return 100000.0  # Default fallback
        except Exception as e:
            logger.error(f"Error getting account value: {str(e)}")
            return 100000.0  # Default fallback
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """
        Analyze a symbol and generate trading signal (optimized for scalping)
        
        Args:
            symbol: Symbol to analyze
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Use 1-minute timeframe for scalping, 15-minute for regular trading
            resolution = self.config.get('analysis', {}).get('timeframe', '1') if self.scalping_enabled else '15'
            lookback_period = self.config.get('analysis', {}).get('lookback_period', 50) if self.scalping_enabled else 100
            
            # Get historical data
            df = self.market_data.get_historical_data(symbol, resolution=resolution, range_from=None, range_to=None)
            
            min_data_points = 20 if self.scalping_enabled else 50
            if df.empty or len(df) < min_data_points:
                logger.warning(f"Insufficient data for {symbol}: {len(df)} candles")
                return {
                    'symbol': symbol,
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'error': 'Insufficient data'
                }
            
            # Generate features
            features_df = self.technical_analysis.generate_features(df)
            
            # Generate signal (use scalping mode if enabled)
            signal_data = self.technical_analysis.generate_signal(
                features_df,
                rsi_oversold=self.config['analysis'].get('rsi_oversold', 25),
                rsi_overbought=self.config['analysis'].get('rsi_overbought', 75),
                use_scalping=self.scalping_enabled
            )
            
            # Get prediction
            prediction = self.technical_analysis.predict_price_direction(features_df)
            
            return {
                'symbol': symbol,
                'signal': signal_data['signal'],
                'confidence': signal_data['confidence'],
                'price': signal_data['price'],
                'rsi': signal_data.get('rsi', 0),
                'macd': signal_data.get('macd', 0),
                'momentum': signal_data.get('momentum', 0),
                'volume_ratio': signal_data.get('volume_ratio', 0),
                'prediction': prediction['prediction'],
                'prediction_confidence': prediction['confidence'],
                'details': signal_data['reason']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def find_trading_opportunities(self) -> List[Dict]:
        """
        Find trading opportunities across all symbols (optimized for scalping)
        
        Returns:
            List of trading opportunities
        """
        opportunities = []
        
        # Use high liquidity symbols for scalping
        if self.scalping_enabled:
            symbols_to_analyze = self.symbols_to_trade
            min_confidence = 0.75  # STRICT: Higher confidence threshold for zero-loss strategy
        else:
            symbols_to_analyze = self.nifty_symbols + self.stock_symbols
            min_confidence = 0.70  # STRICT: Higher confidence threshold for zero-loss strategy
        
        logger.info(f"Analyzing {len(symbols_to_analyze)} symbols...")
        for symbol in symbols_to_analyze:
            analysis = self.analyze_symbol(symbol)
            if analysis['signal'] != 'HOLD' and analysis['confidence'] >= min_confidence:
                # Additional filters for scalping
                if self.scalping_enabled:
                    # Check volume requirement
                    if analysis.get('volume_ratio', 0) < 1.2:
                        continue
                    # Check momentum
                    if abs(analysis.get('momentum', 0)) < 0.05:
                        continue
                
                opportunities.append({
                    **analysis,
                    'type': 'SCALPING' if self.scalping_enabled else 'REGULAR'
                })
        
        # Sort by confidence (and momentum for scalping)
        if self.scalping_enabled:
            opportunities.sort(key=lambda x: (x['confidence'], abs(x.get('momentum', 0))), reverse=True)
        else:
            opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"Found {len(opportunities)} trading opportunities")
        return opportunities
    
    def execute_trade(self, opportunity: Dict) -> bool:
        """
        Execute a trade based on opportunity
        
        Args:
            opportunity: Trading opportunity dictionary
            
        Returns:
            True if trade executed successfully, False otherwise
        """
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
            
            # Calculate take profit
            take_profit = self.risk_management.calculate_take_profit(price, signal)
            
            # ZERO-LOSS STRATEGY: Validate risk/reward ratio before entering trade
            risk_reward_validation = self.risk_management.validate_risk_reward_ratio(
                entry_price=price,
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
                side=signal
            )
            
            if not risk_reward_validation['valid']:
                logger.warning(f"Trade rejected for {symbol}: {risk_reward_validation['message']}")
                return False
            
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
            
            logger.info(f"Risk/Reward validated: {risk_reward_validation['risk_reward_ratio']:.2f} for {symbol}")
            
            # Place order
            logger.info(f"Executing {signal} order for {symbol}: {quantity} units at {price}")
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
                    'take_profit': take_profit,
                    'entry_time': datetime.now(),
                    'order_id': order_result.get('order_id'),
                    'breakeven_activated': False  # Track breakeven status for zero-loss strategy
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
        """
        Monitor active positions and exit if stop-loss, take-profit, or scalping conditions are met
        """
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
                
                # Check if should exit (use scalping logic if enabled)
                if self.scalping_enabled:
                    exit_decision = self.risk_management.should_exit_scalping_position(
                        entry_price=position_info['entry_price'],
                        current_price=current_price,
                        side=position_info['side'],
                        entry_time=position_info['entry_time'],
                        highest_price=position_info.get('highest_price'),
                        lowest_price=position_info.get('lowest_price'),
                        breakeven_activated=position_info.get('breakeven_activated', False)
                    )
                    # Update breakeven status
                    if exit_decision.get('breakeven_activated', False):
                        position_info['breakeven_activated'] = True
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
                        
                        # Log with zero-loss strategy message if applicable
                        exit_message = exit_decision.get('message', exit_decision['reason'])
                        logger.info(f"Position closed: {symbol}, P&L: {pnl:.2f}, Reason: {exit_message}")
                        
                        # Warn if loss occurred (shouldn't happen with zero-loss strategy)
                        if pnl < 0:
                            logger.error(f"⚠️ LOSS DETECTED: {symbol} closed with loss of {pnl:.2f}. This violates zero-loss policy!")
                        
                        # Record trade in profit tracker
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
        """
        Check if current time is within trading hours
        
        Returns:
            True if within trading hours, False otherwise
        """
        now = datetime.now()
        current_time = now.time()
        
        trading_start = dt_time(9, 15)  # 9:15 AM
        trading_end = dt_time(15, 30)   # 3:30 PM
        
        # Check if weekday (Monday=0, Sunday=6)
        is_weekday = now.weekday() < 5
        
        return is_weekday and trading_start <= current_time <= trading_end
    
    def run_cycle(self):
        """
        Run one trading cycle (optimized for scalping)
        """
        try:
            if not self.is_trading_hours():
                logger.info("Outside trading hours, waiting...")
                return
            
            # Check if should continue trading based on profit targets
            continue_check = self.profit_tracker.should_continue_trading()
            if not continue_check['should_continue']:
                logger.warning(f"Stopping trading: {', '.join(continue_check['reasons'])}")
                logger.info(f"Daily P&L: {continue_check['daily_profit']:.2f}")
                self.is_running = False
                return
            
            logger.info("=" * 50)
            logger.info("Starting trading cycle" + (" [SCALPING MODE]" if self.scalping_enabled else ""))
            logger.info("=" * 50)
            
            # Show performance summary
            perf_summary = self.profit_tracker.get_performance_summary()
            logger.info(f"Today's Performance: Trades: {perf_summary['total_trades']}, "
                       f"P&L: {perf_summary['profit']:.2f}, "
                       f"Win Rate: {perf_summary['win_rate']:.2%}")
            
            # Monitor existing positions (critical for scalping - check frequently)
            self.monitor_positions()
            
            # Find new opportunities
            opportunities = self.find_trading_opportunities()
            
            # Execute trades for top opportunities
            max_positions = (self.config.get('scalping', {}).get('max_positions', 10) 
                           if self.scalping_enabled 
                           else self.config['trading']['max_positions'])
            max_new_positions = max_positions - len(self.active_positions)
            
            for opportunity in opportunities[:max_new_positions]:
                if opportunity['symbol'] not in self.active_positions:
                    self.execute_trade(opportunity)
                    time.sleep(0.5 if self.scalping_enabled else 1)  # Faster for scalping
            
            logger.info(f"Active positions: {len(self.active_positions)}/{max_positions}")
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
    
    def run(self, cycle_interval: int = None):
        """
        Run the bot autonomously (optimized for scalping)
        
        Args:
            cycle_interval: Time interval between cycles in seconds (uses config if not provided)
        """
        if not self.initialize():
            logger.error("Failed to initialize bot. Exiting.")
            return
        
        # Use scalping cycle interval if scalping is enabled
        if cycle_interval is None:
            if self.scalping_enabled:
                cycle_interval = self.config.get('scalping', {}).get('cycle_interval_seconds', 30)
            else:
                cycle_interval = 300  # 5 minutes default
        
        self.is_running = True
        mode_str = "SCALPING MODE" if self.scalping_enabled else "REGULAR MODE"
        logger.info(f"Bot started in {mode_str}. Running cycles every {cycle_interval} seconds.")
        
        if self.scalping_enabled:
            logger.info("Scalping parameters:")
            logger.info(f"  - Stop Loss: {self.risk_management.stop_loss_percentage}%")
            logger.info(f"  - Take Profit: {self.risk_management.take_profit_percentage}%")
            logger.info(f"  - Max Holding Time: {self.risk_management.max_holding_time}s")
            logger.info(f"  - Quick Exit Threshold: {self.risk_management.quick_exit_threshold}%")
            logger.info(f"  - Daily Profit Target: ₹{self.profit_tracker.daily_profit_target}")
            logger.info(f"  - Daily Loss Limit: ₹{self.profit_tracker.daily_loss_limit}")
        
        try:
            while self.is_running:
                self.run_cycle()
                
                if self.is_running:
                    logger.info(f"Waiting {cycle_interval} seconds until next cycle...")
                    time.sleep(cycle_interval)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.is_running = False
            # Show final performance summary
            perf_summary = self.profit_tracker.get_performance_summary()
            logger.info("=" * 50)
            logger.info("FINAL PERFORMANCE SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Total Trades: {perf_summary['total_trades']}")
            logger.info(f"Wins: {perf_summary['wins']}, Losses: {perf_summary['losses']}")
            logger.info(f"Win Rate: {perf_summary['win_rate']:.2%}")
            logger.info(f"Total P&L: ₹{perf_summary['profit']:.2f}")
            logger.info(f"Profit Factor: {perf_summary['profit_factor']:.2f}")
        except Exception as e:
            logger.error(f"Fatal error in bot: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """
        Stop the bot
        """
        logger.info("Stopping bot...")
        self.is_running = False
        
        # Close all positions if needed (optional)
        # for symbol in list(self.active_positions.keys()):
        #     self.trading_execution.exit_position(symbol)


def main():
    """Main entry point"""
    bot = AutonomousTradingBot()
    bot.run(cycle_interval=300)  # Run every 5 minutes


if __name__ == "__main__":
    main()
