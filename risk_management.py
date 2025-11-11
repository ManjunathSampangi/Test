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
        
        # Zero-loss strategy parameters (read from config or scalping_config)
        source_config = self.scalping_config if self.scalping_config.get('enabled', False) else config
        self.enable_zero_loss = True  # Always enabled for positive profit requirement
        self.min_profit_to_protect = source_config.get('min_profit_to_protect', 0.1)  # Exit on 0.1% profit
        self.breakeven_profit_threshold = source_config.get('breakeven_profit_threshold', 0.2)  # Move to breakeven at 0.2%
        self.min_risk_reward_ratio = source_config.get('min_risk_reward_ratio', 3.0)  # Minimum 1:3 risk/reward
        self.max_loss_before_exit = source_config.get('max_loss_before_exit', 0.05)  # Exit if loss exceeds 0.05%
        
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
        Includes zero-loss strategy for regular trading
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            side: 'BUY' or 'SELL' (original side)
            position_type: 'LONG' or 'SHORT'
            
        Returns:
            Dictionary with exit decision and reason
        """
        # Calculate profit percentage
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        if side == 'SELL':
            profit_pct = -profit_pct
        
        # ZERO-LOSS STRATEGY: Exit immediately on ANY profit (even tiny)
        if self.enable_zero_loss and profit_pct >= self.min_profit_to_protect:
            return {
                'should_exit': True,
                'reason': 'IMMEDIATE_PROFIT_PROTECTION',
                'profit_pct': profit_pct,
                'current_price': current_price,
                'message': f'Exiting with {profit_pct:.2f}% profit to ensure no loss'
            }
        
        # ZERO-LOSS STRATEGY: Exit if loss exceeds maximum allowed
        if self.enable_zero_loss and profit_pct <= -self.max_loss_before_exit:
            return {
                'should_exit': True,
                'reason': 'MAX_LOSS_EXCEEDED',
                'profit_pct': profit_pct,
                'current_price': current_price,
                'message': f'Exiting to prevent larger loss: {profit_pct:.2f}%'
            }
        
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
            'current_price': current_price,
            'profit_pct': profit_pct
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
                                     lowest_price: float = None,
                                     breakeven_activated: bool = False) -> Dict[str, any]:
        """
        Determine if scalping position should be exited (with zero-loss strategy)
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            side: 'BUY' or 'SELL'
            entry_time: Entry timestamp
            highest_price: Highest price since entry (for trailing stop)
            lowest_price: Lowest price since entry (for trailing stop)
            breakeven_activated: Whether breakeven stop has been activated
            
        Returns:
            Dictionary with exit decision and reason
        """
        from datetime import datetime, timedelta
        
        # Calculate profit percentage
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        if side == 'SELL':
            profit_pct = -profit_pct
        
        # ZERO-LOSS STRATEGY: Exit immediately on ANY profit (even tiny)
        if self.enable_zero_loss and profit_pct >= self.min_profit_to_protect:
            return {
                'should_exit': True,
                'reason': 'IMMEDIATE_PROFIT_PROTECTION',
                'profit_pct': profit_pct,
                'current_price': current_price,
                'message': f'Exiting with {profit_pct:.2f}% profit to ensure no loss'
            }
        
        # ZERO-LOSS STRATEGY: Exit if loss exceeds maximum allowed
        if self.enable_zero_loss and profit_pct <= -self.max_loss_before_exit:
            return {
                'should_exit': True,
                'reason': 'MAX_LOSS_EXCEEDED',
                'profit_pct': profit_pct,
                'current_price': current_price,
                'message': f'Exiting to prevent larger loss: {profit_pct:.2f}%'
            }
        
        # Check max holding time
        if self.max_holding_time:
            holding_time = (datetime.now() - entry_time).total_seconds()
            if holding_time >= self.max_holding_time:
                # If in profit, exit; if in loss, exit to prevent further loss
                if profit_pct > 0:
                    return {
                        'should_exit': True,
                        'reason': 'MAX_HOLDING_TIME_PROFIT',
                        'holding_time': holding_time,
                        'profit_pct': profit_pct,
                        'current_price': current_price
                    }
                else:
                    return {
                        'should_exit': True,
                        'reason': 'MAX_HOLDING_TIME_LOSS',
                        'holding_time': holding_time,
                        'profit_pct': profit_pct,
                        'current_price': current_price,
                        'message': 'Exiting at max holding time to prevent loss'
                    }
        
        # Quick exit threshold (small profit, exit quickly)
        if self.quick_exit_threshold:
            if profit_pct >= self.quick_exit_threshold:
                return {
                    'should_exit': True,
                    'reason': 'QUICK_EXIT',
                    'profit_pct': profit_pct,
                    'current_price': current_price
                }
        
        # Calculate dynamic stop loss (breakeven if profit threshold reached)
        if self.enable_zero_loss and profit_pct >= self.breakeven_profit_threshold:
            # Move stop loss to breakeven (entry price)
            stop_loss = entry_price
            breakeven_activated = True
        else:
            stop_loss = self.calculate_stop_loss(entry_price, side)
        
        take_profit = self.calculate_take_profit(entry_price, side)
        
        if side == 'BUY':
            # Exit if price hits breakeven stop (protecting profit)
            if breakeven_activated and current_price <= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'BREAKEVEN_STOP',
                    'trigger_price': stop_loss,
                    'current_price': current_price,
                    'message': 'Exiting at breakeven to protect profit'
                }
            
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
            # Exit if price hits breakeven stop (protecting profit)
            if breakeven_activated and current_price >= stop_loss:
                return {
                    'should_exit': True,
                    'reason': 'BREAKEVEN_STOP',
                    'trigger_price': stop_loss,
                    'current_price': current_price,
                    'message': 'Exiting at breakeven to protect profit'
                }
            
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
            'current_price': current_price,
            'breakeven_activated': breakeven_activated,
            'profit_pct': profit_pct
        }
    
    def validate_risk_reward_ratio(self, entry_price: float, stop_loss_price: float, 
                                   take_profit_price: float, side: str) -> Dict[str, any]:
        """
        Validate that trade has favorable risk/reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            take_profit_price: Take profit price
            side: 'BUY' or 'SELL'
            
        Returns:
            Validation result with risk/reward ratio
        """
        if side == 'BUY':
            risk = abs(entry_price - stop_loss_price)
            reward = abs(take_profit_price - entry_price)
        else:  # SELL
            risk = abs(stop_loss_price - entry_price)
            reward = abs(entry_price - take_profit_price)
        
        if risk == 0:
            return {
                'valid': False,
                'risk_reward_ratio': 0,
                'message': 'Risk is zero, cannot calculate ratio'
            }
        
        risk_reward_ratio = reward / risk
        
        is_valid = risk_reward_ratio >= self.min_risk_reward_ratio
        
        return {
            'valid': is_valid,
            'risk_reward_ratio': risk_reward_ratio,
            'risk': risk,
            'reward': reward,
            'message': f'Risk/Reward: {risk_reward_ratio:.2f} (min: {self.min_risk_reward_ratio:.2f})' if is_valid else f'Risk/Reward too low: {risk_reward_ratio:.2f} < {self.min_risk_reward_ratio:.2f}'
        }
