"""
Flask web server for trading bot dashboard
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
from typing import Dict, List

app = Flask(__name__)
CORS(app)

# Global state to store trading data
trading_state = {
    'prices': {},
    'price_history': {},
    'value_history': [],
    'positions': [],
    'trades': [],
    'stats': {},
    'last_update': None,
    'running': False,
    'llm_conversations': []  # Store LLM decision history
}


def update_llm_conversation(summary: str, user_prompt: str, chain_of_thought: Dict, actions: List):
    """Add LLM conversation to history"""
    global trading_state
    
    conversation = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'user_prompt': user_prompt,
        'chain_of_thought': chain_of_thought,
        'actions': actions
    }
    
    trading_state['llm_conversations'].append(conversation)
    
    # Keep only last 50 conversations
    if len(trading_state['llm_conversations']) > 50:
        trading_state['llm_conversations'] = trading_state['llm_conversations'][-50:]


def update_trading_data(prices: Dict, positions: List, stats: Dict, 
                       closed_positions: List = None):
    """Update the global trading state"""
    global trading_state
    
    timestamp = datetime.now().isoformat()
    trading_state['last_update'] = timestamp
    trading_state['prices'] = prices
    trading_state['positions'] = positions
    trading_state['stats'] = stats
    
    # Update price history
    for symbol, price in prices.items():
        if symbol not in trading_state['price_history']:
            trading_state['price_history'][symbol] = []
        
        trading_state['price_history'][symbol].append({
            'timestamp': timestamp,
            'price': price
        })
        
        # Keep only last 100 data points
        if len(trading_state['price_history'][symbol]) > 100:
            trading_state['price_history'][symbol] = trading_state['price_history'][symbol][-100:]
    
    # Update value history
    trading_state['value_history'].append({
        'timestamp': timestamp,
        'value': stats.get('total_value', 0)
    })
    
    if len(trading_state['value_history']) > 100:
        trading_state['value_history'] = trading_state['value_history'][-100:]
    
    # Update closed trades
    if closed_positions:
        trading_state['trades'] = closed_positions


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    # Check if advanced dashboard exists, use it, otherwise use basic
    try:
        return render_template('dashboard_with_chat.html')
    except:
        return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current trading status"""
    return jsonify({
        'running': trading_state['running'],
        'last_update': trading_state['last_update']
    })


@app.route('/api/prices')
def get_prices():
    """Get current prices"""
    return jsonify(trading_state['prices'])


@app.route('/api/price_history')
def get_price_history():
    """Get price history for all symbols"""
    return jsonify(trading_state['price_history'])


@app.route('/api/value_history')
def get_value_history():
    """Get account value history"""
    return jsonify(trading_state['value_history'])


@app.route('/api/positions')
def get_positions():
    """Get current open positions"""
    return jsonify(trading_state['positions'])


@app.route('/api/trades')
def get_trades():
    """Get completed trades"""
    return jsonify(trading_state['trades'])


@app.route('/api/stats')
def get_stats():
    """Get portfolio statistics"""
    return jsonify(trading_state['stats'])


@app.route('/api/llm_conversations')
def get_llm_conversations():
    """Get LLM conversation history"""
    return jsonify(trading_state['llm_conversations'])


@app.route('/api/all')
def get_all_data():
    """Get all data at once"""
    return jsonify(trading_state)


def run_server(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask server"""
    trading_state['running'] = True
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    print("Starting web dashboard on http://127.0.0.1:5000")
    run_server(debug=True)

