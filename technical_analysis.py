"""
Technical analysis module for cryptocurrency data
"""

import numpy as np
from typing import List, Dict


def calculate_sma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return 0.0
    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int) -> float:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices: List[float]) -> Dict[str, float]:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    if len(prices) < 26:
        return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    macd = ema_12 - ema_26
    
    # For simplicity, using a basic signal line calculation
    signal = macd * 0.9  # Simplified signal line
    histogram = macd - signal
    
    return {
        'macd': macd,
        'signal': signal,
        'histogram': histogram
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        current_price = prices[-1] if prices else 0
        return {
            'upper': current_price,
            'middle': current_price,
            'lower': current_price
        }
    
    recent_prices = prices[-period:]
    sma = sum(recent_prices) / period
    variance = sum((p - sma) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    return {
        'upper': sma + (std * std_dev),
        'middle': sma,
        'lower': sma - (std * std_dev)
    }


def analyze_market(klines: List[Dict]) -> Dict:
    """
    Perform comprehensive technical analysis on market data
    
    Args:
        klines: List of kline/candlestick data
        
    Returns:
        Dictionary with technical indicators and analysis
    """
    if not klines:
        return {}
    
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    volumes = [k['volume'] for k in klines]
    timestamps = [k['timestamp'] for k in klines]
    
    current_price = closes[-1]
    price_change = ((current_price - closes[0]) / closes[0]) * 100 if closes[0] > 0 else 0
    
    # Calculate indicators
    sma_20 = calculate_sma(closes, 20)
    sma_50 = calculate_sma(closes, 50)
    ema_12 = calculate_ema(closes, 12)
    ema_20 = calculate_ema(closes, 20)
    rsi_7 = calculate_rsi(closes, 7)
    rsi_14 = calculate_rsi(closes, 14)
    macd = calculate_macd(closes)
    bb = calculate_bollinger_bands(closes)
    
    # Get recent series (last 10 points for intraday)
    recent_count = min(10, len(closes))
    recent_prices = closes[-recent_count:]
    recent_ema20 = [calculate_ema(closes[:i+1], 20) for i in range(len(closes)-recent_count, len(closes))]
    recent_rsi7 = [calculate_rsi(closes[:i+1], 7) for i in range(len(closes)-recent_count, len(closes))]
    recent_rsi14 = [calculate_rsi(closes[:i+1], 14) for i in range(len(closes)-recent_count, len(closes))]
    
    # Calculate MACD series
    recent_macd = []
    for i in range(len(closes)-recent_count, len(closes)):
        m = calculate_macd(closes[:i+1])
        recent_macd.append(m['macd'])
    
    # Volume analysis
    avg_volume = sum(volumes[-20:]) / min(20, len(volumes))
    volume_trend = "high" if volumes[-1] > avg_volume * 1.2 else "normal" if volumes[-1] > avg_volume * 0.8 else "low"
    
    # Trend detection
    trend = "neutral"
    if sma_20 > 0 and sma_50 > 0:
        if current_price > sma_20 > sma_50:
            trend = "strong_uptrend"
        elif current_price > sma_20 and sma_20 < sma_50:
            trend = "weak_uptrend"
        elif current_price < sma_20 < sma_50:
            trend = "strong_downtrend"
        elif current_price < sma_20 and sma_20 > sma_50:
            trend = "weak_downtrend"
    
    # RSI signals
    rsi_signal = "neutral"
    if rsi_14 > 70:
        rsi_signal = "overbought"
    elif rsi_14 < 30:
        rsi_signal = "oversold"
    
    # Bollinger Bands signals
    bb_signal = "neutral"
    if current_price > bb['upper']:
        bb_signal = "above_upper_band"
    elif current_price < bb['lower']:
        bb_signal = "below_lower_band"
    
    return {
        'current_price': current_price,
        'price_change_percent': price_change,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'ema_12': ema_12,
        'ema_20': ema_20,
        'rsi_7': rsi_7,
        'rsi_14': rsi_14,
        'rsi_signal': rsi_signal,
        'macd': macd,
        'bollinger_bands': bb,
        'bb_signal': bb_signal,
        'trend': trend,
        'volume_trend': volume_trend,
        'avg_volume': avg_volume,
        'current_volume': volumes[-1],
        # Time series data (oldest → newest)
        'series': {
            'prices': recent_prices,
            'ema_20': recent_ema20,
            'rsi_7': recent_rsi7,
            'rsi_14': recent_rsi14,
            'macd': recent_macd,
            'volumes': volumes[-recent_count:],
        }
    }

