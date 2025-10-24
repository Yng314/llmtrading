# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit the `.env` file and add your DashScope API key:

```
DASHSCOPE_API_KEY=your_api_key_here
```

To get a DashScope API key:
1. Visit https://dashscope.aliyun.com/
2. Sign up/Login
3. Navigate to API Keys section
4. Create a new API key

### 3. Run the Bot

```bash
python main.py
```

The bot will:
- Connect to Binance API for real-time prices
- Analyze market data using technical indicators
- Make trading decisions via Qwen3 Max LLM
- Execute simulated trades with your virtual $1000 capital
- Log all activities to the `logs/` directory

### 4. Monitor Progress

The bot prints real-time updates to the console and logs everything to files:

- `logs/trading_YYYYMMDD_HHMMSS.log` - General activity log
- `logs/trades_YYYYMMDD_HHMMSS.csv` - All executed trades
- `logs/stats_YYYYMMDD_HHMMSS.json` - Portfolio statistics over time
- `logs/decisions_YYYYMMDD_HHMMSS.json` - LLM decisions and reasoning
- `logs/report_YYYYMMDD_HHMMSS.txt` - Final trading report

### 5. Stop the Bot

Press `Ctrl+C` to gracefully stop the bot. It will:
- Close all open positions
- Calculate final P&L
- Generate a comprehensive report

## Configuration

Edit `config.py` to customize:

```python
# Initial capital in USD
INITIAL_CAPITAL = 1000

# Maximum leverage allowed
MAX_LEVERAGE = 10

# Seconds between LLM decisions (to save tokens)
DECISION_INTERVAL = 300  # 5 minutes

# Trading pairs to monitor
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

# Volatility threshold for early LLM trigger
VOLATILITY_THRESHOLD = 0.02  # 2% price change
```

## Token Optimization Strategies

The bot implements several strategies to minimize LLM API costs:

### 1. Time-Based Intervals
- Default: Only requests LLM decision every 5 minutes
- Reduces unnecessary calls during stable markets

### 2. Volatility Triggers
- Makes early decisions when price changes exceed 2%
- Catches important market movements

### 3. Batch Analysis
- Analyzes all trading pairs in one LLM call
- More efficient than per-symbol calls

### 4. Compressed Context
- Sends only essential market data to LLM
- Focuses on actionable indicators (RSI, MACD, trends)

## Testing Individual Components

### Test Crypto API
```bash
python crypto_api.py
```

### Test LLM Agent
```bash
python llm_agent.py
```

### Test Logger
```bash
python logger.py
```

## Understanding Trading Actions

The LLM can suggest these actions:

### Open Long Position
- Expects price to go up
- Profit when price increases
- Loss when price decreases

### Open Short Position
- Expects price to go down
- Profit when price decreases
- Loss when price increases

### Close Position
- Exit an existing position
- Lock in profits or cut losses

### Leverage
- Multiplies both gains and losses
- 2x leverage = 2x the profit/loss
- Use cautiously!

## Example Trading Scenario

1. **Initial State**: $1000 capital, no positions
2. **LLM Analysis**: BTC showing strong uptrend, RSI at 65 (neutral)
3. **Decision**: Open LONG BTCUSDT $200 @ $67,500 (2x leverage)
4. **After 1 hour**: BTC rises to $68,500 (+1.48%)
5. **Position P&L**: $200 × 1.48% × 2 = +$5.92
6. **LLM Analysis**: RSI now 72 (overbought)
7. **Decision**: Close position, take profits
8. **Final**: $1000 + $5.92 = $1,005.92

## Risk Management

The LLM is instructed to follow these principles:

- **Position Sizing**: Max 20% of capital per trade
- **Stop Loss**: Close position if P&L drops below -10%
- **Take Profit**: Consider closing at +15-20% gains
- **Leverage Limits**: 1-3x for safer trades, higher only with strong conviction
- **Diversification**: Trade multiple coins to spread risk

## Troubleshooting

### "Server disconnected" Error
If you see connection errors to DashScope API:
- Check your API key is correct
- Ensure you have internet connectivity
- If using VPN, try disabling it (VPNs can interfere with localhost/API connections)

### No Prices Fetched
- Binance API might be rate-limited
- Check your internet connection
- Try again in a few seconds

### Bot Makes No Trades
This is normal! The LLM is conservative and waits for good opportunities. If markets are stable or unclear, it may recommend no action.

## Advanced Usage

### Run for Limited Time
Edit `main.py`:
```python
bot.run(iterations=50, sleep_seconds=30)  # Run for 50 iterations
```

### Adjust Decision Frequency
For more aggressive trading:
```python
DECISION_INTERVAL = 60  # Check every minute
```

### Modify Trading Pairs
Focus on specific coins:
```python
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT']  # Only BTC and ETH
```

## Safety Reminders

⚠️ **This is a SIMULATION**
- No real money is at risk
- Uses Binance prices but doesn't execute real trades
- Perfect for learning and testing strategies

⚠️ **Before Real Trading**
- Test thoroughly with simulation
- Understand risks of leverage and crypto volatility
- Never invest more than you can afford to lose
- Consider consulting with financial advisors

## Getting Help

Common questions:

**Q: How much does it cost to run?**
A: Only API costs for Qwen3 Max. With optimizations, expect ~$0.01-0.05 per hour depending on market volatility.

**Q: Can I use a different LLM?**
A: Yes! Modify `llm_agent.py` to use OpenAI, Claude, or other providers.

**Q: Can I add more indicators?**
A: Absolutely! Edit `technical_analysis.py` to add more indicators to the analysis.

**Q: How do I transition to real trading?**
A: You'd need to integrate with an exchange's trading API (Binance, Coinbase, etc.) and add order execution logic. Start with small amounts!

