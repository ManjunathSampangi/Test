"""
Risk Management Module
Handles position sizing, stop-loss, take-profit, and risk limits
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskManagement:
    def __init__(self, config: Dict, scalping_config: Dict = None):
        """
        Initialize Risk Management module
        
        Args:
            config: Configuration dictionary with risk parameters
            scalping_config: Scalping-specific configuration
        """
        self.config = config
        self.scalping_config = scalping_config or {}
        
        # Use scalping config if available, otherwise use regular config
        if self.scalping_config.get('enabled', False):
            self.max_positions = self.scalping_config.get('max_positions', 10)
            self.max_position_size = self.scalping_config.get('max_position_size', 5000)
            self.stop_loss_percentage = self.scalping_config.get('stop_loss_percentage', 0.3)
            self.take_profit_percentage = self.scalping_config.get('take_profit_percentage', 0.5)
            self.trailing_stop_percentage = self.scalping_config.get('trailing_stop_percentage', 0.2)
            self.risk_per_trade = self.scalping_config.get('risk_per_trade', 0.01)
            self.max_holding_time = self.scalping_config.get('max_holding_time_seconds', 300)
            self.quick_exit_threshold = self.scalping_config.get('quick_exit_threshold', 0.15)
        else:
            self.max_positions = config.get('max_positions', 5)
            self.max_position_size = config.get('max_position_size', 10000)
            self.stop_loss_percentage = config.get('stop_loss_percentage', 2.0)
            self.take_profit_percentage = config.get('take_profit_percentage', 3.0)
            self.trailing_stop_percentage = None
            self.risk_per_trade = config.get('risk_per_trade', 0.02)
            self.max_holding_time = None
            self.quick_exit_threshold = None
        
    def calculate_position_size(self, account_value: float, entry_price: float,
                               stop_loss_price: float, risk_amount: Optional[float] = None) -> int:
        """
        Calculate position size based on risk
        
        Args:
            account_value: Total account value
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_amount: Risk amount (optional, uses risk_per_trade if not provided)
            
        Returns:
            Position size (quantity)
        """
        if risk_amount is None:
            risk_amount = account_value * self.risk_per_trade
        
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            logger.warning("Price risk is zero, using default position size")
            return 1
        
        position_size = int(risk_amount / price_risk)
        
        # Cap position size
        max_size_by_capital = int((account_value * 0.1) / entry_price)  # Max 10% of capital
        position_size = min(position_size, max_size_by_capital, 
                          int(self.max_position_size / entry_price))
        
        return max(1, position_size)  # At least 1 unit
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
            
        Returns:
            Stop loss price
        """
        if side == 'BUY':
            return entry_price * (1 - self.stop_loss_percentage / 100)
        else:  # SELL
            return entry_price * (1 + self.stop_loss_percentage / 100)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
            
        Returns:
            Take profit price
        """
        if side == 'BUY':
            return entry_price * (1 + self.take_profit_percentage / 100)
        else:  # SELL
            return entry_price * (1 - self.take_profit_percentage / 100)
    
    def check_max_positions(self, current_positions: int) -> bool:
        """
        Check if maximum positions limit is reached
        
        Args:
            current_positions: Current number of open positions
            
        Returns:
            True if can open new position, False otherwise
        """
        can_open = current_positions < self.max_positions
        if not can_open:
            logger.warning(f"Maximum positions limit reached: {current_positions}/{self.max_positions}")
        return can_open
    
    def check_position_size_limit(self, position_value: float) -> bool:
        """
        Check if position size is within limits
        
        Args:
            position_value: Value of the position
            
        Returns:
            True if within limits, False otherwise
        """
        within_limit = position_value <= self.max_position_size
        if not within_limit:
            logger.warning(f"Position size exceeds limit: {position_value} > {self.max_position_size}")
        return within_limit
    
    def check_risk_limits(self, account_value: float, total_risk: float) -> bool:
        """
        Check if total risk is within acceptable limits
        
        Args:
            account_value: Total account value
            total_risk: Total risk amount
            
        Returns:
            True if within limits, False otherwise
        """
        risk_percentage = (total_risk / account_value) * 100
        max_risk_percentage = 10.0  # Maximum 10% total risk
        
        within_limit = risk_percentage <= max_risk_percentage
        if not within_limit:
            logger.warning(f"Total risk exceeds limit: {risk_percentage:.2f}% > {max_risk_percentage}%")
        return within_limit
    
    def should_exit_position(self, entry_price: float, current_price: float,
                           side: str, position_type: str = 'LONG') -> Dict[str, any]:
        """
        Determine if position should be exited based on stop-loss or take-profit
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            side: 'BUY' or 'SELL' (original side)
            position_type: 'LONG' or 'SHORT'
            
        Returns:
            Dictionary with exit decision and reason
        """
        stop_loss = self.calculate_stop_loss(entry_price, side)
        take_profit = self.calculate_take_profit(entry_price, side)
        
        if position_type == 'LONG':
            if current_price <= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'trigger_price': stop_loss,
                    'current_price': current_price
                }
            elif current_price >= take_profit:
                return {
                    'should_exit': True,
                    'reason': 'TAKE_PROFIT',
                    'trigger_price': take_profit,
                    'current_price': current_price
                }
        else:  # SHORT
            if current_price >= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'trigger_price': stop_loss,
                    'current_price': current_price
                }
            elif current_price <= take_profit:
                return {
                    'should_exit': True,
                    'reason': 'TAKE_PROFIT',
                    'trigger_price': take_profit,
                    'current_price': current_price
                }
        
        return {
            'should_exit': False,
            'reason': 'HOLD',
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'current_price': current_price
        }
    
    def validate_trade(self, account_value: float, entry_price: float,
                      quantity: int, current_positions: int) -> Dict[str, any]:
        """
        Validate if a trade meets risk management criteria
        
        Args:
            account_value: Total account value
            entry_price: Entry price
            quantity: Quantity to trade
            current_positions: Current number of positions
            
        Returns:
            Validation result dictionary
        """
        position_value = entry_price * quantity
        
        checks = {
            'max_positions': self.check_max_positions(current_positions),
            'position_size': self.check_position_size_limit(position_value),
            'position_value': position_value,
            'quantity': quantity
        }
        
        is_valid = checks['max_positions'] and checks['position_size']
        
        return {
            'valid': is_valid,
            'checks': checks,
            'message': 'Trade validated' if is_valid else 'Trade failed risk checks'
        }
    
    def should_exit_scalping_position(self, entry_price: float, current_price: float,
                                     side: str, entry_time: datetime, 
                                     highest_price: float = None, 
                                     lowest_price: float = None) -> Dict[str, any]:
        """
        Determine if scalping position should be exited (with trailing stop and time-based exit)
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            side: 'BUY' or 'SELL'
            entry_time: Entry timestamp
            highest_price: Highest price since entry (for trailing stop)
            lowest_price: Lowest price since entry (for trailing stop)
            
        Returns:
            Dictionary with exit decision and reason
        """
        from datetime import datetime, timedelta
        
        # Check max holding time
        if self.max_holding_time:
            holding_time = (datetime.now() - entry_time).total_seconds()
            if holding_time >= self.max_holding_time:
                return {
                    'should_exit': True,
                    'reason': 'MAX_HOLDING_TIME',
                    'holding_time': holding_time,
                    'current_price': current_price
                }
        
        # Quick exit threshold (small profit, exit quickly)
        if self.quick_exit_threshold:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if side == 'SELL':
                profit_pct = -profit_pct
            
            if profit_pct >= self.quick_exit_threshold:
                return {
                    'should_exit': True,
                    'reason': 'QUICK_EXIT',
                    'profit_pct': profit_pct,
                    'current_price': current_price
                }
        
        # Regular stop loss and take profit
        stop_loss = self.calculate_stop_loss(entry_price, side)
        take_profit = self.calculate_take_profit(entry_price, side)
        
        if side == 'BUY':
            if current_price <= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'trigger_price': stop_loss,
                    'current_price': current_price
                }
            elif current_price >= take_profit:
                return {
                    'should_exit': True,
                    'reason': 'TAKE_PROFIT',
                    'trigger_price': take_profit,
                    'current_price': current_price
                }
            
            # Trailing stop for long positions
            if self.trailing_stop_percentage and highest_price:
                trailing_stop = highest_price * (1 - self.trailing_stop_percentage / 100)
                if current_price <= trailing_stop and current_price < highest_price:
                    return {
                        'should_exit': True,
                        'reason': 'TRAILING_STOP',
                        'trigger_price': trailing_stop,
                        'current_price': current_price,
                        'highest_price': highest_price
                    }
        else:  # SELL
            if current_price >= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'STOP_LOSS',
                    'trigger_price': stop_loss,
                    'current_price': current_price
                }
            elif current_price <= take_profit:
                return {
                    'should_exit': True,
                    'reason': 'TAKE_PROFIT',
                    'trigger_price': take_profit,
                    'current_price': current_price
                }
            
            # Trailing stop for short positions
            if self.trailing_stop_percentage and lowest_price:
                trailing_stop = lowest_price * (1 + self.trailing_stop_percentage / 100)
                if current_price >= trailing_stop and current_price > lowest_price:
                    return {
                        'should_exit': True,
                        'reason': 'TRAILING_STOP',
                        'trigger_price': trailing_stop,
                        'current_price': current_price,
                        'lowest_price': lowest_price
                    }
        
        return {
            'should_exit': False,
            'reason': 'HOLD',
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'current_price': current_price
        }
