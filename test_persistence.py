"""
Test data persistence functionality
"""

import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

from data_persistence import DataPersistence
from trading_simulator import TradingSimulator

def test_persistence():
    """Test save and load functionality"""
    print("="*60)
    print("Testing Data Persistence")
    print("="*60)
    
    # Create persistence instance
    dp = DataPersistence("test_trading_data.json")
    
    # Create a simulator with some data
    print("\n1. Creating simulator with test data...")
    sim = TradingSimulator(initial_capital=1000, max_leverage=20)
    
    # Open some positions
    sim.open_position('BTCUSDT', 'long', 100, 100000, 10)
    sim.open_position('ETHUSDT', 'short', 150, 4000, 15)
    
    print(f"   Capital: ${sim.capital:.2f}")
    print(f"   Open Positions: {len(sim.open_positions)}")
    
    # Create some dummy history
    value_history = [
        {'timestamp': '2025-10-24T10:00:00', 'value': 1000},
        {'timestamp': '2025-10-24T10:05:00', 'value': 1010},
        {'timestamp': '2025-10-24T10:10:00', 'value': 1005}
    ]
    
    price_history = {
        'BTCUSDT': [
            {'timestamp': '2025-10-24T10:00:00', 'price': 100000},
            {'timestamp': '2025-10-24T10:05:00', 'price': 101000}
        ]
    }
    
    iteration_count = 42
    
    # Save state
    print("\n2. Saving state...")
    success = dp.save_state(sim, value_history, price_history, iteration_count)
    if success:
        print("   ✅ State saved successfully")
    else:
        print("   ❌ Failed to save state")
        return False
    
    # Load state
    print("\n3. Loading state...")
    loaded_state = dp.load_state()
    if loaded_state:
        print("   ✅ State loaded successfully")
    else:
        print("   ❌ Failed to load state")
        return False
    
    # Verify loaded data
    print("\n4. Verifying loaded data...")
    assert loaded_state['iteration_count'] == 42, "Iteration count mismatch"
    assert loaded_state['simulator']['capital'] == sim.capital, "Capital mismatch"
    assert len(loaded_state['simulator']['open_positions']) == 2, "Position count mismatch"
    assert len(loaded_state['value_history']) == 3, "Value history length mismatch"
    print("   ✅ All assertions passed")
    
    # Restore simulator
    print("\n5. Restoring simulator...")
    restored_sim = dp.restore_simulator(loaded_state)
    print(f"   Capital: ${restored_sim.capital:.2f}")
    print(f"   Open Positions: {len(restored_sim.open_positions)}")
    print(f"   Position 1: {restored_sim.open_positions[0].symbol} {restored_sim.open_positions[0].position_type}")
    print(f"   Position 2: {restored_sim.open_positions[1].symbol} {restored_sim.open_positions[1].position_type}")
    
    # Clean up
    print("\n6. Cleaning up test file...")
    dp.delete_state()
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        test_persistence()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

