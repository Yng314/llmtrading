"""
Data Persistence Module
Saves and loads trading state to/from JSON file
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from trading_simulator import TradingSimulator, Position, PositionType


class DataPersistence:
    """Handle saving and loading trading state"""
    
    def __init__(self, data_file: str = "trading_data.json"):
        self.data_file = data_file
    
    def save_state(self, simulator: TradingSimulator, 
                   value_history: List[Dict], 
                   price_history: Dict[str, List[Dict]],
                   iteration_count: int) -> bool:
        """Save current trading state to file"""
        try:
            # Convert Position objects to dict
            open_positions = [
                {
                    'symbol': pos.symbol,
                    'position_type': pos.position_type.value if hasattr(pos.position_type, 'value') else str(pos.position_type),
                    'entry_price': pos.entry_price,
                    'size': pos.size,
                    'leverage': pos.leverage,
                    'timestamp': pos.timestamp.isoformat(),
                    'target_price': pos.target_price,
                    'stop_loss': pos.stop_loss
                }
                for pos in simulator.open_positions
            ]
            
            # Trade history is already in dict format
            trade_history = simulator.trade_history
            
            state = {
                'timestamp': datetime.now().isoformat(),
                'iteration_count': iteration_count,
                'simulator': {
                    'initial_capital': simulator.initial_capital,
                    'capital': simulator.capital,
                    'open_positions': open_positions,
                    'trade_history': trade_history
                },
                'value_history': value_history,
                'price_history': price_history
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print(f"✅ State saved to {self.data_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def load_state(self) -> Optional[Dict]:
        """Load trading state from file"""
        if not os.path.exists(self.data_file):
            print(f"ℹ️  No saved state found ({self.data_file})")
            return None
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            print(f"✅ State loaded from {self.data_file}")
            print(f"   Saved at: {state['timestamp']}")
            print(f"   Iteration: {state['iteration_count']}")
            print(f"   Capital: ${state['simulator']['capital']:.2f}")
            print(f"   Open Positions: {len(state['simulator']['open_positions'])}")
            print(f"   Trade History: {len(state['simulator']['trade_history'])} trades")
            
            return state
            
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return None
    
    def restore_simulator(self, state: Dict) -> TradingSimulator:
        """Restore TradingSimulator from saved state"""
        sim_data = state['simulator']
        
        # Create simulator with original initial capital
        simulator = TradingSimulator(initial_capital=sim_data['initial_capital'])
        
        # Restore capital
        simulator.capital = sim_data['capital']
        
        # Restore trade history
        simulator.trade_history = sim_data['trade_history']
        
        # Restore open positions
        for pos_data in sim_data['open_positions']:
            # Convert string to PositionType enum
            pos_type_str = pos_data['position_type']
            pos_type = PositionType.LONG if pos_type_str == 'long' else PositionType.SHORT
            
            position = Position(
                symbol=pos_data['symbol'],
                position_type=pos_type,
                size=pos_data['size'],
                entry_price=pos_data['entry_price'],
                leverage=pos_data['leverage'],
                timestamp=datetime.fromisoformat(pos_data['timestamp']),
                target_price=pos_data.get('target_price'),
                stop_loss=pos_data.get('stop_loss')
            )
            simulator.open_positions.append(position)
        
        return simulator
    
    def delete_state(self) -> bool:
        """Delete saved state file"""
        try:
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
                print(f"✅ Deleted saved state: {self.data_file}")
                return True
            else:
                print(f"ℹ️  No saved state to delete")
                return False
        except Exception as e:
            print(f"❌ Error deleting state: {e}")
            return False

