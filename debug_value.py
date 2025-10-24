"""
Debug script to verify value calculation
"""

from trading_simulator import TradingSimulator

# Create simulator with $1000 initial capital
sim = TradingSimulator(1000, max_leverage=20)

print("=" * 60)
print("Initial State")
print("=" * 60)
print(f"Capital: ${sim.capital:.2f}")
print(f"Total Value: ${sim.get_total_value({}):.2f}")
print()

# Simulate the user's positions
print("=" * 60)
print("Opening Positions (matching user's scenario)")
print("=" * 60)

# Position 1: BNB LONG
bnb_pos = sim.open_position('BNBUSDT', 'long', 200, 1111.48, 15)
print(f"After BNB LONG: Capital = ${sim.capital:.2f}")

# Position 2: SOL SHORT
sol_pos = sim.open_position('SOLUSDT', 'short', 190, 190.94, 18)
print(f"After SOL SHORT: Capital = ${sim.capital:.2f}")

# Position 3: ADA LONG
ada_pos = sim.open_position('ADAUSDT', 'long', 188.12, 0.64, 15)
print(f"After ADA LONG: Capital = ${sim.capital:.2f}")

print()

# Simulate closed trades (total P&L: -$6.94)
print("=" * 60)
print("Simulating Closed Trades")
print("=" * 60)

# Create temporary positions for closed trades
eth_pos1 = sim.open_position('ETHUSDT', 'short', 190, 3847.15, 18)
sim.close_position(eth_pos1, 3853.25)  # -$5.42

eth_pos2 = sim.open_position('ETHUSDT', 'short', 188, 3841.70, 18)
sim.close_position(eth_pos2, 3847.45)  # -$5.06

btc_pos = sim.open_position('BTCUSDT', 'short', 200, 109897.29, 15)
sim.close_position(btc_pos, 109974.40)  # -$2.10

ada_pos_temp = sim.open_position('ADAUSDT', 'short', 188, 0.64, 18)
sim.close_position(ada_pos_temp, 0.64)  # Should be +$4.20 but price same?

eth_pos3 = sim.open_position('ETHUSDT', 'short', 190, 3851.60, 15)
sim.close_position(eth_pos3, 3849.65)  # +$1.44

print(f"After closed trades: Capital = ${sim.capital:.2f}")
print()

# Re-open the 3 positions that should be open
print("=" * 60)
print("Re-opening Current Positions")
print("=" * 60)

# Clear positions
sim.open_positions = []

# Re-open current positions
bnb_pos = sim.open_position('BNBUSDT', 'long', 200, 1111.48, 15)
sol_pos = sim.open_position('SOLUSDT', 'short', 190, 190.94, 18)
ada_pos = sim.open_position('ADAUSDT', 'long', 188.12, 0.64, 15)

print(f"Capital after re-opening: ${sim.capital:.2f}")
print()

# Calculate current value with current prices
print("=" * 60)
print("Current State Calculation")
print("=" * 60)

current_prices = {
    'BNBUSDT': 1117.84,
    'SOLUSDT': 190.19,
    'ADAUSDT': 0.64
}

print(f"Current Capital (cash): ${sim.capital:.2f}")
print()

print("Open Positions:")
for pos in sim.open_positions:
    margin = pos.size / pos.leverage
    pnl = pos.calculate_pnl(current_prices[pos.symbol])
    print(f"  {pos.symbol} {pos.position_type.value.upper()}:")
    print(f"    Size: ${pos.size:.2f}, Leverage: {pos.leverage}x")
    print(f"    Margin: ${margin:.2f}")
    print(f"    Entry: ${pos.entry_price:.4f}, Current: ${current_prices[pos.symbol]:.4f}")
    print(f"    P&L: ${pnl:+.2f}")
print()

# Manual calculation
total_margin = sum(pos.size / pos.leverage for pos in sim.open_positions)
total_unrealized_pnl = sum(pos.calculate_pnl(current_prices[pos.symbol]) 
                           for pos in sim.open_positions)

print("Manual Calculation:")
print(f"  Current Capital: ${sim.capital:.2f}")
print(f"  Total Margin Locked: ${total_margin:.2f}")
print(f"  Total Unrealized P&L: ${total_unrealized_pnl:+.2f}")
print(f"  Total Value: ${sim.capital + total_margin + total_unrealized_pnl:.2f}")
print()

# Using built-in function
total_value = sim.get_total_value(current_prices)
stats = sim.get_statistics(current_prices)

print("Using get_total_value():")
print(f"  Total Value: ${total_value:.2f}")
print()

print("Using get_statistics():")
print(f"  Initial Capital: ${stats['initial_capital']:.2f}")
print(f"  Current Capital: ${stats['current_capital']:.2f}")
print(f"  Total Value: ${stats['total_value']:.2f}")
print(f"  Total P&L: ${stats['total_pnl']:+.2f}")
print(f"  ROI: {stats['roi_percent']:+.2f}%")
print()

print("=" * 60)
print("Expected vs Actual")
print("=" * 60)
print(f"Expected Total Value: ~$1021 (with +$28 unrealized, -$7 realized)")
print(f"Actual Total Value: ${stats['total_value']:.2f}")
print(f"Difference: ${stats['total_value'] - 1021:.2f}")

