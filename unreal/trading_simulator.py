"""
Trading simulator with support for long/short positions and leverage
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class PositionType(Enum):
    LONG = "long"
    SHORT = "short"


class Position:
    """Represents a trading position"""
    
    def __init__(self, symbol: str, position_type: PositionType, size: float, 
                 entry_price: float, leverage: float, timestamp: datetime,
                 target_price: float = None, stop_loss: float = None):
        self.symbol = symbol
        self.position_type = position_type
        self.size = size  # Amount in USD
        self.entry_price = entry_price
        self.leverage = leverage
        self.timestamp = timestamp
        self.exit_price = None
        self.exit_timestamp = None
        self.pnl = 0.0
        # LLM-defined targets
        self.target_price = target_price  # Take profit target
        self.stop_loss = stop_loss        # Stop loss level
        
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current P&L for the position"""
        if self.position_type == PositionType.LONG:
            price_change_pct = (current_price - self.entry_price) / self.entry_price
        else:  # SHORT
            price_change_pct = (self.entry_price - current_price) / self.entry_price
        
        # Apply leverage to P&L
        pnl = self.size * price_change_pct * self.leverage
        return pnl
    
    def to_dict(self) -> Dict:
        """Convert position to dictionary"""
        return {
            'symbol': self.symbol,
            'type': self.position_type.value,
            'size': self.size,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'leverage': self.leverage,
            'pnl': self.pnl,
            'timestamp': self.timestamp.isoformat(),
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss
        }
    
    def check_targets(self, current_price: float) -> str:
        """Check if price hit target or stop loss"""
        if self.target_price and self.stop_loss:
            if self.position_type == PositionType.LONG:
                if current_price >= self.target_price:
                    return "target_reached"
                elif current_price <= self.stop_loss:
                    return "stop_loss_hit"
            else:  # SHORT
                if current_price <= self.target_price:
                    return "target_reached"
                elif current_price >= self.stop_loss:
                    return "stop_loss_hit"
        return "none"


class TradingSimulator:
    """Simulates cryptocurrency trading with leverage"""
    
    def __init__(self, initial_capital: float, max_leverage: float = 10):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.max_leverage = max_leverage
        self.open_positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.trade_history: List[Dict] = []
        
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total account value including open positions"""
        total = self.capital
        
        # Add back margin locked in positions
        for position in self.open_positions:
            margin = position.size / position.leverage
            total += margin
            
            # Add unrealized P&L
            if position.symbol in current_prices:
                pnl = position.calculate_pnl(current_prices[position.symbol])
                total += pnl
        
        return total
    
    def get_available_capital(self) -> float:
        """Get capital available for new positions"""
        # Capital available is already adjusted when positions are opened
        return self.capital
    
    def open_position(self, symbol: str, position_type: str, size: float, 
                     current_price: float, leverage: float = 1.0,
                     target_price: float = None, stop_loss: float = None) -> Optional[Position]:
        """
        Open a new trading position
        
        Args:
            symbol: Trading pair symbol
            position_type: 'long' or 'short'
            size: Position size in USD
            current_price: Current market price
            leverage: Leverage multiplier (1-max_leverage)
            target_price: LLM-defined take profit target
            stop_loss: LLM-defined stop loss level
            
        Returns:
            Position object if successful, None otherwise
        """
        # Validate inputs
        if leverage > self.max_leverage:
            print(f"Leverage {leverage} exceeds maximum {self.max_leverage}")
            return None
        
        if leverage < 1:
            print(f"Leverage must be at least 1")
            return None
        
        # Check if we have enough capital
        margin_required = size / leverage
        if margin_required > self.get_available_capital():
            print(f"Insufficient capital. Required: ${margin_required:.2f}, Available: ${self.get_available_capital():.2f}")
            return None
        
        # Create position
        pos_type = PositionType.LONG if position_type.lower() == 'long' else PositionType.SHORT
        position = Position(
            symbol=symbol,
            position_type=pos_type,
            size=size,
            entry_price=current_price,
            leverage=leverage,
            timestamp=datetime.now(),
            target_price=target_price,
            stop_loss=stop_loss
        )
        
        self.open_positions.append(position)
        self.capital -= margin_required
        
        # Record trade
        self.trade_history.append({
            'action': 'open',
            'symbol': symbol,
            'type': position_type,
            'size': size,
            'price': current_price,
            'leverage': leverage,
            'timestamp': position.timestamp.isoformat()
        })
        
        print(f"Opened {position_type.upper()} position: {symbol} ${size:.2f} @ ${current_price:.2f} (Leverage: {leverage}x)")
        return position
    
    def close_position(self, position: Position, current_price: float) -> float:
        """
        Close an existing position
        
        Args:
            position: Position to close
            current_price: Current market price
            
        Returns:
            Realized P&L
        """
        if position not in self.open_positions:
            print("Position not found in open positions")
            return 0.0
        
        # Calculate P&L
        pnl = position.calculate_pnl(current_price)
        position.pnl = pnl
        position.exit_price = current_price
        position.exit_timestamp = datetime.now()
        
        # Return margin and add/subtract P&L
        margin = position.size / position.leverage
        self.capital += margin + pnl
        
        # Move position to closed
        self.open_positions.remove(position)
        self.closed_positions.append(position)
        
        # Record trade
        self.trade_history.append({
            'action': 'close',
            'symbol': position.symbol,
            'type': position.position_type.value,
            'size': position.size,
            'entry_price': position.entry_price,
            'exit_price': current_price,
            'leverage': position.leverage,
            'pnl': pnl,
            'timestamp': position.exit_timestamp.isoformat()
        })
        
        print(f"Closed {position.position_type.value.upper()} position: {position.symbol} P&L: ${pnl:.2f}")
        return pnl
    
    def close_all_positions(self, current_prices: Dict[str, float]):
        """Close all open positions"""
        for position in self.open_positions.copy():
            if position.symbol in current_prices:
                self.close_position(position, current_prices[position.symbol])
    
    def get_statistics(self, current_prices: Dict[str, float]) -> Dict:
        """Get trading statistics"""
        total_value = self.get_total_value(current_prices)
        total_pnl = total_value - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        winning_trades = [p for p in self.closed_positions if p.pnl > 0]
        losing_trades = [p for p in self.closed_positions if p.pnl <= 0]
        
        win_rate = len(winning_trades) / len(self.closed_positions) * 100 if self.closed_positions else 0
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.capital,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'roi_percent': roi,
            'open_positions': len(self.open_positions),
            'closed_positions': len(self.closed_positions),
            'total_trades': len(self.closed_positions),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
        }
    
    def get_open_positions_summary(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Get summary of open positions with current P&L"""
        summary = []
        for position in self.open_positions:
            if position.symbol in current_prices:
                current_pnl = position.calculate_pnl(current_prices[position.symbol])
                summary.append({
                    'symbol': position.symbol,
                    'type': position.position_type.value,
                    'size': position.size,
                    'entry_price': position.entry_price,
                    'current_price': current_prices[position.symbol],
                    'leverage': position.leverage,
                    'current_pnl': current_pnl,
                    'pnl_percent': (current_pnl / position.size) * 100
                })
        return summary

