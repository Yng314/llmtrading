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

# File to persist LLM conversations
LLM_CONVERSATIONS_FILE = 'llm_conversations.json'

def load_llm_conversations():
    """Load LLM conversations from file on startup"""
    global trading_state
    if os.path.exists(LLM_CONVERSATIONS_FILE):
        try:
            with open(LLM_CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                trading_state['llm_conversations'] = json.load(f)
            print(f"✅ Loaded {len(trading_state['llm_conversations'])} LLM conversations")
        except Exception as e:
            print(f"⚠️  Failed to load LLM conversations: {e}")
            trading_state['llm_conversations'] = []

def save_llm_conversations():
    """Save LLM conversations to file"""
    try:
        with open(LLM_CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(trading_state['llm_conversations'], f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to save LLM conversations: {e}")


def update_llm_conversation(decision: Dict):
    """Add LLM conversation to history"""
    global trading_state
    
    conversation = {
        'timestamp': datetime.now().isoformat(),
        'summary': decision.get('summary', ''),
        'user_prompt': decision.get('user_prompt', ''),
        'chain_of_thought': decision.get('chain_of_thought', {}),
        'actions': decision.get('actions', [])
    }
    
    trading_state['llm_conversations'].append(conversation)
    
    # Keep only last 50 conversations
    if len(trading_state['llm_conversations']) > 50:
        trading_state['llm_conversations'] = trading_state['llm_conversations'][-50:]
    
    # Persist to file
    save_llm_conversations()


def update_trading_data(prices: Dict, positions: List, stats: Dict, 
                       closed_positions: List = None,
                       value_history: List = None,
                       price_history: Dict = None):
    """Update the global trading state"""
    global trading_state
    
    # Use provided history if available, otherwise maintain our own
    if value_history is not None:
        trading_state['value_history'] = value_history
    if price_history is not None:
        trading_state['price_history'] = price_history
    
    timestamp = datetime.now().isoformat()
    trading_state['last_update'] = timestamp
    trading_state['prices'] = prices
    trading_state['positions'] = positions
    trading_state['stats'] = stats
    
    # Update price history (only if not provided from bot)
    if price_history is None:
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
    
    # Update value history (only if not provided from bot)
    if value_history is None:
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
    # Load saved conversations on startup
    load_llm_conversations()
    
    trading_state['running'] = True
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == '__main__':
    print("Starting web dashboard on http://127.0.0.1:5000")
    run_server(debug=True)

