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
        
        # Initialize components
        self.auth = FyersAuth()
        self.session = None
        self.market_data = None
        self.technical_analysis = TechnicalAnalysis()
        self.trading_execution = None
        self.risk_management = RiskManagement(self.config['trading'])
        
        # Trading state
        self.active_positions = {}
        self.trade_history = []
        self.is_running = False
        
        # Symbols to trade
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
        Analyze a symbol and generate trading signal
        
        Args:
            symbol: Symbol to analyze
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Get historical data
            df = self.market_data.get_historical_data(symbol, resolution='15', range_from=None, range_to=None)
            
            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                return {
                    'symbol': symbol,
                    'signal': 'HOLD',
                    'confidence': 0.0,
                    'error': 'Insufficient data'
                }
            
            # Generate features
            features_df = self.technical_analysis.generate_features(df)
            
            # Generate signal
            signal_data = self.technical_analysis.generate_signal(
                features_df,
                rsi_oversold=self.config['analysis']['rsi_oversold'],
                rsi_overbought=self.config['analysis']['rsi_overbought']
            )
            
            # Get prediction
            prediction = self.technical_analysis.predict_price_direction(features_df)
            
            return {
                'symbol': symbol,
                'signal': signal_data['signal'],
                'confidence': signal_data['confidence'],
                'price': signal_data['price'],
                'rsi': signal_data['rsi'],
                'macd': signal_data['macd'],
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
        Find trading opportunities across all symbols
        
        Returns:
            List of trading opportunities
        """
        opportunities = []
        
        # Analyze Nifty options
        logger.info("Analyzing Nifty options...")
        for symbol in self.nifty_symbols:
            analysis = self.analyze_symbol(symbol)
            if analysis['signal'] != 'HOLD' and analysis['confidence'] > 0.5:
                opportunities.append({
                    **analysis,
                    'type': 'NIFTY_OPTION'
                })
        
        # Analyze stock options
        logger.info("Analyzing stock options...")
        for symbol in self.stock_symbols:
            analysis = self.analyze_symbol(symbol)
            if analysis['signal'] != 'HOLD' and analysis['confidence'] > 0.5:
                opportunities.append({
                    **analysis,
                    'type': 'STOCK_OPTION'
                })
        
        # Sort by confidence
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
                    'order_id': order_result.get('order_id')
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
        Monitor active positions and exit if stop-loss or take-profit is hit
        """
        try:
            positions = self.trading_execution.get_positions()
            
            for symbol, position_info in list(self.active_positions.items()):
                # Get current price
                current_price = self.market_data.get_latest_price(symbol)
                
                if current_price == 0:
                    continue
                
                # Check if should exit
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
                        
                        logger.info(f"Position closed: {symbol}, P&L: {pnl:.2f}")
                        
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
        Run one trading cycle
        """
        try:
            if not self.is_trading_hours():
                logger.info("Outside trading hours, waiting...")
                return
            
            logger.info("=" * 50)
            logger.info("Starting trading cycle")
            logger.info("=" * 50)
            
            # Monitor existing positions
            self.monitor_positions()
            
            # Find new opportunities
            opportunities = self.find_trading_opportunities()
            
            # Execute trades for top opportunities
            max_new_positions = self.config['trading']['max_positions'] - len(self.active_positions)
            
            for opportunity in opportunities[:max_new_positions]:
                if opportunity['symbol'] not in self.active_positions:
                    self.execute_trade(opportunity)
                    time.sleep(1)  # Small delay between trades
            
            logger.info(f"Active positions: {len(self.active_positions)}")
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
    
    def run(self, cycle_interval: int = 300):
        """
        Run the bot autonomously
        
        Args:
            cycle_interval: Time interval between cycles in seconds (default 5 minutes)
        """
        if not self.initialize():
            logger.error("Failed to initialize bot. Exiting.")
            return
        
        self.is_running = True
        logger.info(f"Bot started. Running cycles every {cycle_interval} seconds.")
        
        try:
            while self.is_running:
                self.run_cycle()
                
                if self.is_running:
                    logger.info(f"Waiting {cycle_interval} seconds until next cycle...")
                    time.sleep(cycle_interval)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.is_running = False
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
