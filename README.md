# LLM Crypto Trading Bot

An automated cryptocurrency trading system powered by Qwen3 Max LLM.

## Features

- Real-time cryptocurrency price tracking via Binance API
- Simulated trading with support for long/short positions and leverage
- LLM-driven decision making based on technical analysis and market data
- Token-efficient design with conditional LLM calls
- Comprehensive P/L tracking and logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the trading bot:
```bash
python main.py
```

## Configuration

- `INITIAL_CAPITAL`: Starting capital in USD (default: 1000)
- `MAX_LEVERAGE`: Maximum leverage allowed (default: 10)
- `DECISION_INTERVAL`: Seconds between LLM decisions (default: 300)

## Architecture

- `crypto_api.py`: Cryptocurrency price data fetching
- `trading_simulator.py`: Trading engine with position management
- `llm_agent.py`: LLM integration and decision making
- `technical_analysis.py`: Technical indicators and market analysis
- `main.py`: Main control loop

## Token Optimization

To minimize API costs, the system:
- Uses time-based intervals instead of continuous LLM queries
- Only calls LLM when price volatility exceeds threshold
- Compresses historical data into concise summaries
- Batches analysis for multiple cryptocurrencies

