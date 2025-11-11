"""
Profit Tracking Module
Tracks performance metrics and ensures profitability
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfitTracker:
    def __init__(self, config: Dict):
        """
        Initialize Profit Tracker
        
        Args:
            config: Configuration dictionary with profit tracking parameters
        """
        self.config = config.get('profit_tracking', {})
        self.daily_profit_target = self.config.get('daily_profit_target', 5000)
        self.daily_loss_limit = self.config.get('daily_loss_limit', -3000)
        self.min_win_rate = self.config.get('min_win_rate', 0.55)
        self.min_profit_factor = self.config.get('min_profit_factor', 1.5)
        
        # Performance tracking
        self.trades = []
        self.daily_stats = defaultdict(lambda: {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0.0,
            'total_profit': 0.0,
            'total_loss': 0.0
        })
        
        # Load historical data if exists
        self.load_stats()
    
    def record_trade(self, symbol: str, side: str, entry_price: float, 
                    exit_price: float, quantity: int, entry_time: datetime,
                    exit_time: datetime, pnl: float):
        """
        Record a completed trade
        
        Args:
            symbol: Symbol traded
            side: 'BUY' or 'SELL'
            entry_price: Entry price
            exit_price: Exit price
            quantity: Quantity traded
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            pnl: Profit/Loss amount
        """
        trade = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'pnl': pnl,
            'date': exit_time.date()
        }
        
        self.trades.append(trade)
        
        # Update daily stats
        trade_date = exit_time.date()
        self.daily_stats[trade_date]['trades'] += 1
        self.daily_stats[trade_date]['profit'] += pnl
        
        if pnl > 0:
            self.daily_stats[trade_date]['wins'] += 1
            self.daily_stats[trade_date]['total_profit'] += pnl
        else:
            self.daily_stats[trade_date]['losses'] += 1
            self.daily_stats[trade_date]['total_loss'] += abs(pnl)
        
        logger.info(f"Trade recorded: {symbol} {side} | P&L: {pnl:.2f}")
        
        # Save stats
        self.save_stats()
    
    def get_daily_profit(self, trade_date: date = None) -> float:
        """
        Get profit for a specific date
        
        Args:
            trade_date: Date to check (default: today)
            
        Returns:
            Daily profit amount
        """
        if trade_date is None:
            trade_date = date.today()
        
        return self.daily_stats[trade_date]['profit']
    
    def get_win_rate(self, trade_date: date = None) -> float:
        """
        Get win rate for a specific date
        
        Args:
            trade_date: Date to check (default: today)
            
        Returns:
            Win rate (0-1)
        """
        if trade_date is None:
            trade_date = date.today()
        
        stats = self.daily_stats[trade_date]
        total_trades = stats['trades']
        
        if total_trades == 0:
            return 0.0
        
        return stats['wins'] / total_trades
    
    def get_profit_factor(self, trade_date: date = None) -> float:
        """
        Get profit factor for a specific date
        
        Args:
            trade_date: Date to check (default: today)
            
        Returns:
            Profit factor (total_profit / total_loss)
        """
        if trade_date is None:
            trade_date = date.today()
        
        stats = self.daily_stats[trade_date]
        total_loss = stats['total_loss']
        
        if total_loss == 0:
            return float('inf') if stats['total_profit'] > 0 else 0.0
        
        return stats['total_profit'] / total_loss
    
    def should_continue_trading(self) -> Dict[str, any]:
        """
        Check if bot should continue trading based on performance
        
        Returns:
            Dictionary with decision and reasons
        """
        today = date.today()
        daily_profit = self.get_daily_profit(today)
        win_rate = self.get_win_rate(today)
        profit_factor = self.get_profit_factor(today)
        
        reasons = []
        should_continue = True
        
        # Check daily loss limit
        if daily_profit <= self.daily_loss_limit:
            should_continue = False
            reasons.append(f"Daily loss limit reached: {daily_profit:.2f} <= {self.daily_loss_limit}")
        
        # Check daily profit target
        if daily_profit >= self.daily_profit_target:
            should_continue = False
            reasons.append(f"Daily profit target achieved: {daily_profit:.2f} >= {self.daily_profit_target}")
        
        # Check win rate (if enough trades)
        stats = self.daily_stats[today]
        if stats['trades'] >= 10 and win_rate < self.min_win_rate:
            reasons.append(f"Low win rate: {win_rate:.2%} < {self.min_win_rate:.2%}")
            # Don't stop, but log warning
        
        # Check profit factor
        if stats['trades'] >= 10 and profit_factor < self.min_profit_factor:
            reasons.append(f"Low profit factor: {profit_factor:.2f} < {self.min_profit_factor}")
            # Don't stop, but log warning
        
        return {
            'should_continue': should_continue,
            'daily_profit': daily_profit,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'reasons': reasons
        }
    
    def get_performance_summary(self, trade_date: date = None) -> Dict:
        """
        Get performance summary for a date
        
        Args:
            trade_date: Date to summarize (default: today)
            
        Returns:
            Performance summary dictionary
        """
        if trade_date is None:
            trade_date = date.today()
        
        stats = self.daily_stats[trade_date]
        win_rate = self.get_win_rate(trade_date)
        profit_factor = self.get_profit_factor(trade_date)
        
        return {
            'date': trade_date.isoformat(),
            'total_trades': stats['trades'],
            'wins': stats['wins'],
            'losses': stats['losses'],
            'win_rate': win_rate,
            'profit': stats['profit'],
            'total_profit': stats['total_profit'],
            'total_loss': stats['total_loss'],
            'profit_factor': profit_factor,
            'avg_win': stats['total_profit'] / stats['wins'] if stats['wins'] > 0 else 0,
            'avg_loss': stats['total_loss'] / stats['losses'] if stats['losses'] > 0 else 0
        }
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            stats_data = {
                'trades': [
                    {
                        **trade,
                        'entry_time': trade['entry_time'].isoformat(),
                        'exit_time': trade['exit_time'].isoformat(),
                        'date': trade['date'].isoformat()
                    }
                    for trade in self.trades
                ],
                'daily_stats': {
                    str(date): stats
                    for date, stats in self.daily_stats.items()
                }
            }
            
            with open('profit_stats.json', 'w') as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {str(e)}")
    
    def load_stats(self):
        """Load statistics from file"""
        try:
            with open('profit_stats.json', 'r') as f:
                stats_data = json.load(f)
                
            # Load trades
            self.trades = []
            for trade in stats_data.get('trades', []):
                trade['entry_time'] = datetime.fromisoformat(trade['entry_time'])
                trade['exit_time'] = datetime.fromisoformat(trade['exit_time'])
                trade['date'] = date.fromisoformat(trade['date'])
                self.trades.append(trade)
            
            # Load daily stats
            self.daily_stats = defaultdict(lambda: {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'profit': 0.0,
                'total_profit': 0.0,
                'total_loss': 0.0
            })
            
            for date_str, stats in stats_data.get('daily_stats', {}).items():
                self.daily_stats[date.fromisoformat(date_str)] = stats
                
            logger.info(f"Loaded {len(self.trades)} historical trades")
        except FileNotFoundError:
            logger.info("No existing stats file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading stats: {str(e)}")
