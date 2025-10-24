import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')

# Trading Configuration
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '1000'))
MAX_LEVERAGE = float(os.getenv('MAX_LEVERAGE', '20'))  # Increased for aggressive trading
DECISION_INTERVAL = int(os.getenv('DECISION_INTERVAL', '300'))  # seconds

# Trading pairs to monitor
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']

# LLM Configuration
LLM_MODEL = 'qwen3-max'
LLM_TEMPERATURE = 0.7

# Token optimization settings
VOLATILITY_THRESHOLD = 0.02  # 2% price change triggers LLM call
MAX_HISTORY_ITEMS = 20  # Maximum historical data points to keep

