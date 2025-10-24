"""
Logging and statistics tracking module
"""

import json
import csv
from datetime import datetime
from typing import Dict, List
import os


class TradingLogger:
    """Logs trading activities and statistics"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Log files
        self.general_log = os.path.join(log_dir, f"trading_{self.session_id}.log")
        self.trades_log = os.path.join(log_dir, f"trades_{self.session_id}.csv")
        self.stats_log = os.path.join(log_dir, f"stats_{self.session_id}.json")
        self.decisions_log = os.path.join(log_dir, f"decisions_{self.session_id}.json")
        
        # Initialize files
        self._init_logs()
        
        # In-memory stats
        self.stats_history = []
        self.decisions_history = []
    
    def _init_logs(self):
        """Initialize log files"""
        # General log
        self.log("=== Trading Session Started ===")
        
        # Trades CSV
        with open(self.trades_log, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'action', 'symbol', 'type', 'size', 
                'entry_price', 'exit_price', 'leverage', 'pnl'
            ])
    
    def log(self, message: str):
        """Write message to general log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        with open(self.general_log, 'a', encoding='utf-8') as f:
            f.write(log_message)
        
        print(message)
    
    def log_trade(self, trade: Dict):
        """Log a trade to CSV"""
        with open(self.trades_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade.get('timestamp', ''),
                trade.get('action', ''),
                trade.get('symbol', ''),
                trade.get('type', ''),
                trade.get('size', 0),
                trade.get('entry_price', 0),
                trade.get('exit_price', 0),
                trade.get('leverage', 1),
                trade.get('pnl', 0)
            ])
    
    def log_statistics(self, stats: Dict):
        """Log portfolio statistics"""
        stats['timestamp'] = datetime.now().isoformat()
        self.stats_history.append(stats)
        
        # Write all stats history to file
        with open(self.stats_log, 'w', encoding='utf-8') as f:
            json.dump(self.stats_history, f, indent=2)
    
    def log_decision(self, decision: Dict, market_summary: str):
        """Log LLM decision"""
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'market_summary': market_summary
        }
        self.decisions_history.append(decision_record)
        
        # Write all decisions history to file
        with open(self.decisions_log, 'w', encoding='utf-8') as f:
            json.dump(self.decisions_history, f, indent=2)
    
    def print_summary(self, stats: Dict, current_prices: Dict[str, float]):
        """Print formatted summary to console and log"""
        summary = f"\n{'='*60}\n"
        summary += f"TRADING SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Initial Capital:    ${stats['initial_capital']:,.2f}\n"
        summary += f"Current Value:      ${stats['total_value']:,.2f}\n"
        summary += f"Total P&L:          ${stats['total_pnl']:+,.2f}\n"
        summary += f"ROI:                {stats['roi_percent']:+.2f}%\n"
        summary += f"{'='*60}\n"
        summary += f"Open Positions:     {stats['open_positions']}\n"
        summary += f"Closed Trades:      {stats['closed_positions']}\n"
        summary += f"Winning Trades:     {stats['winning_trades']}\n"
        summary += f"Losing Trades:      {stats['losing_trades']}\n"
        summary += f"Win Rate:           {stats['win_rate']:.2f}%\n"
        summary += f"{'='*60}\n"
        
        self.log(summary)
    
    def create_final_report(self, simulator, current_prices: Dict[str, float]):
        """Create final trading report"""
        stats = simulator.get_statistics(current_prices)
        
        report = f"\n{'='*60}\n"
        report += f"FINAL TRADING REPORT - Session {self.session_id}\n"
        report += f"{'='*60}\n\n"
        
        report += f"PERFORMANCE METRICS:\n"
        report += f"  Initial Capital:     ${stats['initial_capital']:,.2f}\n"
        report += f"  Final Value:         ${stats['total_value']:,.2f}\n"
        report += f"  Total P&L:           ${stats['total_pnl']:+,.2f}\n"
        report += f"  ROI:                 {stats['roi_percent']:+.2f}%\n\n"
        
        report += f"TRADING STATISTICS:\n"
        report += f"  Total Trades:        {stats['total_trades']}\n"
        report += f"  Winning Trades:      {stats['winning_trades']}\n"
        report += f"  Losing Trades:       {stats['losing_trades']}\n"
        report += f"  Win Rate:            {stats['win_rate']:.2f}%\n\n"
        
        if simulator.closed_positions:
            report += f"TRADE HISTORY:\n"
            for i, pos in enumerate(simulator.closed_positions[-10:], 1):  # Last 10 trades
                report += f"  {i}. {pos.symbol} {pos.position_type.value.upper()}: "
                report += f"${pos.size:.2f} @ ${pos.entry_price:.2f} -> ${pos.exit_price:.2f} "
                report += f"(P&L: ${pos.pnl:+.2f})\n"
        
        report += f"\n{'='*60}\n"
        
        self.log(report)
        
        # Save report to separate file
        report_file = os.path.join(self.log_dir, f"report_{self.session_id}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


if __name__ == "__main__":
    # Test logger
    logger = TradingLogger()
    
    logger.log("Testing logger functionality")
    
    test_trade = {
        'timestamp': datetime.now().isoformat(),
        'action': 'open',
        'symbol': 'BTCUSDT',
        'type': 'long',
        'size': 100,
        'entry_price': 67500,
        'exit_price': 0,
        'leverage': 2,
        'pnl': 0
    }
    
    logger.log_trade(test_trade)
    
    test_stats = {
        'total_value': 1050,
        'total_pnl': 50,
        'roi_percent': 5.0,
        'open_positions': 1,
        'closed_positions': 5,
        'winning_trades': 3,
        'losing_trades': 2,
        'win_rate': 60.0
    }
    
    logger.log_statistics(test_stats)
    
    print(f"\nLogs created in: {logger.log_dir}")
    print(f"Session ID: {logger.session_id}")

