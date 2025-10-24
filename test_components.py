"""
Test script to verify all components are working
"""

import sys
import os
from typing import Dict

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')


def test_crypto_api():
    """Test cryptocurrency API connection"""
    print("\n" + "="*60)
    print("Testing Crypto API Connection...")
    print("="*60)
    
    try:
        from crypto_api import CryptoAPI
        
        api = CryptoAPI()
        
        # Test single price fetch
        print("\n1. Testing single price fetch (BTCUSDT)...")
        btc_price = api.get_price('BTCUSDT')
        if btc_price:
            print(f"   ✓ Success! BTC Price: ${btc_price:,.2f}")
        else:
            print("   ✗ Failed to fetch BTC price")
            return False
        
        # Test multiple prices
        print("\n2. Testing multiple prices fetch...")
        prices = api.get_multiple_prices(['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
        if prices:
            print(f"   ✓ Success! Fetched {len(prices)} prices:")
            for symbol, price in prices.items():
                print(f"      {symbol}: ${price:,.2f}")
        else:
            print("   ✗ Failed to fetch multiple prices")
            return False
        
        # Test klines
        print("\n3. Testing klines/candlestick data...")
        klines = api.get_klines('BTCUSDT', interval='1h', limit=10)
        if klines:
            print(f"   ✓ Success! Fetched {len(klines)} klines")
            print(f"      Latest close: ${klines[-1]['close']:,.2f}")
        else:
            print("   ✗ Failed to fetch klines")
            return False
        
        # Test 24h stats
        print("\n4. Testing 24h statistics...")
        stats = api.get_24h_stats('BTCUSDT')
        if stats:
            print(f"   ✓ Success!")
            print(f"      24h Change: {stats['price_change_percent']:+.2f}%")
            print(f"      24h High: ${stats['high']:,.2f}")
            print(f"      24h Low: ${stats['low']:,.2f}")
        else:
            print("   ✗ Failed to fetch 24h stats")
            return False
        
        print("\n✓ Crypto API: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Crypto API Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technical_analysis():
    """Test technical analysis module"""
    print("\n" + "="*60)
    print("Testing Technical Analysis...")
    print("="*60)
    
    try:
        from crypto_api import CryptoAPI
        from technical_analysis import analyze_market
        
        api = CryptoAPI()
        
        print("\n1. Fetching market data...")
        klines = api.get_klines('BTCUSDT', interval='1h', limit=100)
        
        if not klines:
            print("   ✗ Failed to fetch klines")
            return False
        
        print(f"   ✓ Fetched {len(klines)} klines")
        
        print("\n2. Running technical analysis...")
        analysis = analyze_market(klines)
        
        if analysis:
            print("   ✓ Analysis complete!")
            print(f"      Current Price: ${analysis['current_price']:,.2f}")
            print(f"      Price Change: {analysis['price_change_percent']:+.2f}%")
            print(f"      Trend: {analysis['trend']}")
            print(f"      RSI: {analysis['rsi']:.2f} ({analysis['rsi_signal']})")
            print(f"      Volume Trend: {analysis['volume_trend']}")
        else:
            print("   ✗ Analysis failed")
            return False
        
        print("\n✓ Technical Analysis: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Technical Analysis Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_simulator():
    """Test trading simulator"""
    print("\n" + "="*60)
    print("Testing Trading Simulator...")
    print("="*60)
    
    try:
        from trading_simulator import TradingSimulator
        
        simulator = TradingSimulator(initial_capital=1000, max_leverage=10)
        
        print("\n1. Testing initial state...")
        print(f"   Initial Capital: ${simulator.initial_capital:,.2f}")
        print(f"   Max Leverage: {simulator.max_leverage}x")
        print(f"   ✓ Simulator initialized")
        
        print("\n2. Testing long position...")
        position = simulator.open_position(
            symbol='BTCUSDT',
            position_type='long',
            size=200,
            current_price=67500,
            leverage=2
        )
        
        if position:
            print(f"   ✓ Opened long position")
            print(f"      Remaining capital: ${simulator.capital:.2f}")
        else:
            print("   ✗ Failed to open position")
            return False
        
        print("\n3. Testing P&L calculation...")
        current_prices = {'BTCUSDT': 68500}  # Simulate price increase
        pnl = position.calculate_pnl(68500)
        print(f"   Entry: $67,500 → Current: $68,500")
        print(f"   ✓ P&L: ${pnl:+.2f}")
        
        print("\n4. Testing position close...")
        realized_pnl = simulator.close_position(position, 68500)
        print(f"   ✓ Position closed")
        print(f"      Realized P&L: ${realized_pnl:+.2f}")
        print(f"      Final capital: ${simulator.capital:.2f}")
        
        print("\n5. Testing statistics...")
        stats = simulator.get_statistics(current_prices)
        print(f"   ✓ Statistics calculated")
        print(f"      Total Value: ${stats['total_value']:.2f}")
        print(f"      Total P&L: ${stats['total_pnl']:+.2f}")
        print(f"      ROI: {stats['roi_percent']:+.2f}%")
        
        print("\n✓ Trading Simulator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Trading Simulator Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_agent():
    """Test LLM agent (requires API key)"""
    print("\n" + "="*60)
    print("Testing LLM Agent...")
    print("="*60)
    
    try:
        from config import DASHSCOPE_API_KEY
        from llm_agent import TradingAgent
        
        if not DASHSCOPE_API_KEY:
            print("\n⚠️  DASHSCOPE_API_KEY not set")
            print("   Skipping LLM tests (this is optional)")
            print("   Set DASHSCOPE_API_KEY in .env to test LLM integration")
            return True
        
        print("\n1. Initializing agent...")
        agent = TradingAgent()
        print("   ✓ Agent initialized")
        
        print("\n2. Creating mock market summary...")
        mock_summary = """=== MARKET SUMMARY ===

Portfolio Status:
- Total Value: $1000.00
- Available Capital: $1000.00
- Total P&L: $0.00 (0.00%)

Market Analysis:

BTCUSDT:
  Price: $67500.00 (+2.50% change)
  Trend: strong_uptrend
  RSI: 65.00 (neutral)
"""
        print("   ✓ Mock summary created")
        
        print("\n3. Requesting LLM decision (this may take a few seconds)...")
        decision = agent.make_decision(mock_summary, 200.0)
        
        if decision and 'actions' in decision:
            print("   ✓ Decision received!")
            print(f"      Analysis: {decision.get('analysis', 'N/A')[:100]}...")
            print(f"      Actions proposed: {len(decision.get('actions', []))}")
        else:
            print("   ✗ Invalid decision format")
            return False
        
        print("\n✓ LLM Agent: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ LLM Agent Test Failed: {e}")
        print("\nThis is often due to:")
        print("  - Missing or invalid API key")
        print("  - Network connectivity issues")
        print("  - API rate limits")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """Test logging module"""
    print("\n" + "="*60)
    print("Testing Logger...")
    print("="*60)
    
    try:
        from logger import TradingLogger
        from datetime import datetime
        
        print("\n1. Initializing logger...")
        logger = TradingLogger(log_dir="test_logs")
        print(f"   ✓ Logger initialized (session: {logger.session_id})")
        
        print("\n2. Testing general logging...")
        logger.log("Test log message")
        print("   ✓ Log written")
        
        print("\n3. Testing trade logging...")
        test_trade = {
            'timestamp': datetime.now().isoformat(),
            'action': 'open',
            'symbol': 'BTCUSDT',
            'type': 'long',
            'size': 100,
            'entry_price': 67500,
            'leverage': 2,
            'pnl': 0
        }
        logger.log_trade(test_trade)
        print("   ✓ Trade logged")
        
        print("\n4. Testing statistics logging...")
        test_stats = {
            'total_value': 1050,
            'total_pnl': 50,
            'roi_percent': 5.0,
            'initial_capital': 1000,
            'current_capital': 950,
            'open_positions': 1,
            'closed_positions': 5,
            'winning_trades': 3,
            'losing_trades': 2,
            'win_rate': 60.0
        }
        logger.log_statistics(test_stats)
        print("   ✓ Statistics logged")
        
        print(f"\n✓ Logger: ALL TESTS PASSED")
        print(f"   Test logs created in: {logger.log_dir}/")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Logger Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════╗
║         Component Test Suite                               ║
║         LLM Crypto Trading Bot                             ║
╚════════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # Run tests
    results['Crypto API'] = test_crypto_api()
    results['Technical Analysis'] = test_technical_analysis()
    results['Trading Simulator'] = test_trading_simulator()
    results['LLM Agent'] = test_llm_agent()
    results['Logger'] = test_logger()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{component:.<40} {status}")
    
    print("="*60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("  1. Set your DASHSCOPE_API_KEY in .env file")
        print("  2. Run: python main.py")
        print("  3. Check the logs/ directory for trading results")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Network connectivity problems")
        print("  - Missing dependencies (run: pip install -r requirements.txt)")
        print("  - API key not configured")
        return 1


if __name__ == "__main__":
    sys.exit(main())

