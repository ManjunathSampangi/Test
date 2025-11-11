"""
Trading Execution Module
Handles order placement, modification, and cancellation
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingExecution:
    def __init__(self, fyers_session):
        """
        Initialize Trading Execution module
        
        Args:
            fyers_session: Authenticated Fyers session object
        """
        self.session = fyers_session
        
    def place_order(self, symbol: str, side: str, quantity: int, 
                   order_type: str = 'MARKET', price: float = 0.0,
                   product_type: str = 'INTRADAY', validity: str = 'DAY') -> Dict:
        """
        Place an order
        
        Args:
            symbol: Symbol to trade (e.g., 'NSE:NIFTY50-INDEX')
            side: 'BUY' or 'SELL'
            quantity: Number of shares/lots
            order_type: 'MARKET', 'LIMIT', 'SL', 'SL-M'
            price: Price for limit orders
            product_type: 'INTRADAY', 'MARGIN', 'CNC'
            validity: 'DAY', 'IOC'
            
        Returns:
            Order response dictionary
        """
        try:
            data = {
                "symbol": symbol,
                "qty": quantity,
                "type": 2 if order_type == 'MARKET' else 1,  # 1=LIMIT, 2=MARKET
                "side": 1 if side == 'BUY' else -1,  # 1=BUY, -1=SELL
                "productType": product_type,
                "limitPrice": price if order_type == 'LIMIT' else 0,
                "stopPrice": 0,
                "validity": validity,
                "disclosedQty": 0,
                "offlineOrder": "False",
                "stopLoss": 0,
                "takeProfit": 0
            }
            
            order_response = self.session.place_order(data=data)
            
            if order_response.get('s') == 'ok':
                logger.info(f"Order placed successfully: {side} {quantity} {symbol}")
                return {
                    'success': True,
                    'order_id': order_response.get('id'),
                    'message': order_response.get('message', 'Order placed'),
                    'data': order_response
                }
            else:
                logger.error(f"Order placement failed: {order_response}")
                return {
                    'success': False,
                    'error': order_response.get('message', 'Unknown error'),
                    'data': order_response
                }
        except Exception as e:
            logger.error(f"Exception placing order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def place_option_order(self, option_symbol: str, side: str, quantity: int,
                          order_type: str = 'MARKET', price: float = 0.0) -> Dict:
        """
        Place an options order
        
        Args:
            option_symbol: Option symbol (e.g., 'NSE:NIFTY50-INDEX-OPT')
            side: 'BUY' or 'SELL'
            quantity: Number of lots
            order_type: 'MARKET' or 'LIMIT'
            price: Price for limit orders
            
        Returns:
            Order response dictionary
        """
        return self.place_order(
            symbol=option_symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            product_type='INTRADAY'
        )
    
    def modify_order(self, order_id: str, quantity: Optional[int] = None,
                    price: Optional[float] = None) -> Dict:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            
        Returns:
            Modification response dictionary
        """
        try:
            data = {
                "id": order_id
            }
            
            if quantity is not None:
                data["qty"] = quantity
            if price is not None:
                data["type"] = 1  # LIMIT order
                data["limitPrice"] = price
            
            modify_response = self.session.modify_order(data=data)
            
            if modify_response.get('s') == 'ok':
                logger.info(f"Order {order_id} modified successfully")
                return {
                    'success': True,
                    'message': modify_response.get('message', 'Order modified'),
                    'data': modify_response
                }
            else:
                logger.error(f"Order modification failed: {modify_response}")
                return {
                    'success': False,
                    'error': modify_response.get('message', 'Unknown error'),
                    'data': modify_response
                }
        except Exception as e:
            logger.error(f"Exception modifying order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response dictionary
        """
        try:
            data = {
                "id": order_id
            }
            
            cancel_response = self.session.cancel_order(data=data)
            
            if cancel_response.get('s') == 'ok':
                logger.info(f"Order {order_id} cancelled successfully")
                return {
                    'success': True,
                    'message': cancel_response.get('message', 'Order cancelled'),
                    'data': cancel_response
                }
            else:
                logger.error(f"Order cancellation failed: {cancel_response}")
                return {
                    'success': False,
                    'error': cancel_response.get('message', 'Unknown error'),
                    'data': cancel_response
                }
        except Exception as e:
            logger.error(f"Exception cancelling order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get order status
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        try:
            data = {
                "id": order_id
            }
            
            status_response = self.session.order_status(data=data)
            
            if status_response.get('s') == 'ok':
                return {
                    'success': True,
                    'status': status_response.get('orderBook', [{}])[0] if status_response.get('orderBook') else {},
                    'data': status_response
                }
            else:
                return {
                    'success': False,
                    'error': status_response.get('message', 'Unknown error'),
                    'data': status_response
                }
        except Exception as e:
            logger.error(f"Exception getting order status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def get_positions(self) -> List[Dict]:
        """
        Get current positions
        
        Returns:
            List of position dictionaries
        """
        try:
            positions_response = self.session.positions()
            
            if positions_response.get('s') == 'ok':
                positions = positions_response.get('netPositions', [])
                logger.info(f"Retrieved {len(positions)} positions")
                return positions
            else:
                logger.error(f"Error fetching positions: {positions_response}")
                return []
        except Exception as e:
            logger.error(f"Exception fetching positions: {str(e)}")
            return []
    
    def get_holdings(self) -> List[Dict]:
        """
        Get current holdings
        
        Returns:
            List of holding dictionaries
        """
        try:
            holdings_response = self.session.holdings()
            
            if holdings_response.get('s') == 'ok':
                holdings = holdings_response.get('holdings', [])
                logger.info(f"Retrieved {len(holdings)} holdings")
                return holdings
            else:
                logger.error(f"Error fetching holdings: {holdings_response}")
                return []
        except Exception as e:
            logger.error(f"Exception fetching holdings: {str(e)}")
            return []
    
    def exit_position(self, symbol: str, quantity: int = None) -> Dict:
        """
        Exit a position (close it)
        
        Args:
            symbol: Symbol to exit
            quantity: Quantity to exit (None for full position)
            
        Returns:
            Exit order response
        """
        positions = self.get_positions()
        
        for position in positions:
            if position.get('symbol') == symbol:
                current_qty = position.get('qty', 0)
                side = 'SELL' if current_qty > 0 else 'BUY'
                qty = quantity if quantity else abs(current_qty)
                
                return self.place_order(
                    symbol=symbol,
                    side=side,
                    quantity=qty,
                    order_type='MARKET'
                )
        
        return {
            'success': False,
            'error': 'Position not found'
        }
