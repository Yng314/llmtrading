"""
Real-time value monitoring - compares what's shown on web vs actual calculation
"""

import requests
import time

def monitor():
    print("=" * 80)
    print("Real-time Value Monitoring")
    print("=" * 80)
    print()
    
    while True:
        try:
            response = requests.get('http://127.0.0.1:5000/api/all')
            data = response.json()
            
            stats = data.get('stats', {})
            positions = data.get('positions', [])
            prices = data.get('prices', {})
            
            print(f"\n[{time.strftime('%H:%M:%S')}] Current State:")
            print("-" * 80)
            
            # Stats from backend
            print(f"Backend Stats:")
            print(f"  Initial Capital: ${stats.get('initial_capital', 0):.2f}")
            print(f"  Current Capital: ${stats.get('current_capital', 0):.2f}")
            print(f"  Total Value:     ${stats.get('total_value', 0):.2f}")
            print(f"  Total P&L:       ${stats.get('total_pnl', 0):+.2f}")
            print(f"  ROI:             {stats.get('roi_percent', 0):+.2f}%")
            print()
            
            # Manual calculation from positions
            if positions:
                print(f"Open Positions ({len(positions)}):")
                total_margin = 0
                total_unrealized_pnl = 0
                
                for pos in positions:
                    margin = pos['size'] / pos['leverage']
                    pnl = pos['current_pnl']
                    total_margin += margin
                    total_unrealized_pnl += pnl
                    
                    print(f"  {pos['symbol']} {pos['type'].upper()}:")
                    print(f"    Size: ${pos['size']:.2f}, Leverage: {pos['leverage']}x")
                    print(f"    Margin: ${margin:.2f}")
                    print(f"    Entry: ${pos['entry_price']:.4f}, Current: ${pos['current_price']:.4f}")
                    print(f"    P&L: ${pnl:+.2f} ({pos['pnl_percent']:+.2f}%)")
                
                print()
                print(f"Summary:")
                print(f"  Total Margin Locked:     ${total_margin:.2f}")
                print(f"  Total Unrealized P&L:    ${total_unrealized_pnl:+.2f}")
                print(f"  Current Capital (cash):  ${stats.get('current_capital', 0):.2f}")
                print()
                
                # Manual total value calculation
                manual_total = stats.get('current_capital', 0) + total_margin + total_unrealized_pnl
                backend_total = stats.get('total_value', 0)
                
                print(f"Value Calculation:")
                print(f"  Manual:  ${stats.get('current_capital', 0):.2f} (capital) + ${total_margin:.2f} (margin) + ${total_unrealized_pnl:+.2f} (P&L) = ${manual_total:.2f}")
                print(f"  Backend: ${backend_total:.2f}")
                print(f"  Difference: ${manual_total - backend_total:+.2f}")
                
                if abs(manual_total - backend_total) > 0.01:
                    print("  ⚠️ MISMATCH!")
                else:
                    print("  ✓ Match")
            
            print()
            input("Press Enter for next update (or Ctrl+C to quit)...")
            
        except KeyboardInterrupt:
            print("\n\nStopped monitoring.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    print("Connecting to http://127.0.0.1:5000...")
    print("Make sure the trading bot is running!")
    print()
    monitor()

