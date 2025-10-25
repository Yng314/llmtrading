"""
Real Trading Executor - 真实交易执行器
替换原来的 TradingSimulator，连接真实的Binance账户
"""

from typing import Dict, List, Optional
from datetime import datetime
from binance_real_trader import BinanceRealTrader, calculate_quantity_from_usdt, round_quantity


class RealTradingExecutor:
    """
    真实交易执行器
    
    功能：
    - 连接Binance合约账户
    - 执行真实的开仓、平仓操作
    - 查询真实的余额和持仓
    - 计算真实的盈亏
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, initial_capital: float = None):
        """
        初始化真实交易执行器
        
        Args:
            api_key: Binance API Key
            api_secret: Binance API Secret  
            testnet: 是否使用测试网（强烈建议先用测试网）
            initial_capital: 初始资金（如果不提供，从config读取）
        """
        self.trader = BinanceRealTrader(api_key, api_secret, testnet=testnet)
        
        # 从config读取初始资金，而不是从币安账户读取
        # 因为账户余额会随着盈亏变化，不适合作为initial_capital
        if initial_capital is not None:
            self.initial_capital = initial_capital
        else:
            from config import INITIAL_CAPITAL
            self.initial_capital = INITIAL_CAPITAL
        
        # 记录本地交易历史（因为API可能有限制）
        self.trade_history: List[Dict] = []
        self.trade_history_file = 'real_trade_history.json'
        
        # 加载历史交易记录
        self._load_trade_history()
        
        print(f"✅ 初始资金设置: ${self.initial_capital:.2f} USDT")
        print(f"💡 如需修改，请在 .env 文件中设置: INITIAL_CAPITAL=5000")
    
    def _load_trade_history(self):
        """加载历史交易记录"""
        import os
        if os.path.exists(self.trade_history_file):
            try:
                import json
                with open(self.trade_history_file, 'r', encoding='utf-8') as f:
                    self.trade_history = json.load(f)
                print(f"✅ 加载了 {len(self.trade_history)} 条历史交易记录")
            except Exception as e:
                print(f"⚠️  加载交易历史失败: {e}")
                self.trade_history = []
    
    def _save_trade_history(self):
        """保存交易历史到文件"""
        try:
            import json
            with open(self.trade_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.trade_history, f, indent=2)
        except Exception as e:
            print(f"⚠️  保存交易历史失败: {e}")
    
    def _update_initial_capital(self):
        """已弃用：不再从币安账户读取初始资金"""
        pass
    
    # ===== 账户信息 =====
    
    def get_total_value(self, current_prices: Dict[str, float] = None) -> float:
        """
        获取账户总价值
        
        Returns:
            账户总价值（包括持仓和未实现盈亏）
        """
        account = self.trader.get_account_info()
        if not account:
            return 0.0
        
        # 使用 totalMarginBalance = 钱包余额 + 未实现盈亏
        # totalWalletBalance 只包含钱包余额，不包含未实现盈亏
        total_margin = float(account.get('totalMarginBalance', 0))
        
        # 如果没有 totalMarginBalance，手动计算
        if total_margin == 0:
            wallet = float(account.get('totalWalletBalance', 0))
            unrealized = float(account.get('totalUnrealizedProfit', 0))
            total_margin = wallet + unrealized
        
        return total_margin
    
    def get_available_capital(self) -> float:
        """获取可用资金"""
        balance = self.trader.get_available_balance()
        return balance if balance is not None else 0.0
    
    def get_statistics(self, current_prices: Dict[str, float]) -> Dict:
        """
        获取交易统计
        
        Returns:
            {
                'initial_capital': 初始资金,
                'current_capital': 可用资金,
                'total_value': 总价值,
                'total_pnl': 总盈亏,
                'roi_percent': 收益率,
                'open_positions': 持仓数量,
                'total_trades': 总交易次数,
                ...
            }
        """
        account = self.trader.get_account_info()
        if not account:
            return self._empty_stats()
        
        # 使用 totalMarginBalance (包含未实现盈亏) 而不是 totalWalletBalance
        total_value = float(account.get('totalMarginBalance', 0))
        if total_value == 0:  # 如果没有这个字段，手动计算
            wallet = float(account.get('totalWalletBalance', 0))
            unrealized = float(account.get('totalUnrealizedProfit', 0))
            total_value = wallet + unrealized
        
        available = float(account.get('availableBalance', 0))
        
        # 计算持仓
        positions = self.trader.get_positions()
        num_positions = len(positions) if positions else 0
        
        # 计算盈亏
        total_pnl = total_value - self.initial_capital if self.initial_capital else 0
        roi = (total_pnl / self.initial_capital * 100) if self.initial_capital else 0
        
        # 统计交易记录
        winning_trades = len([t for t in self.trade_history if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in self.trade_history if t.get('pnl', 0) <= 0])
        total_closed = winning_trades + losing_trades
        win_rate = (winning_trades / total_closed * 100) if total_closed > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': available,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'roi_percent': roi,
            'open_positions': num_positions,
            'closed_positions': total_closed,
            'total_trades': total_closed,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
        }
    
    def _empty_stats(self) -> Dict:
        """返回空的统计数据"""
        return {
            'initial_capital': self.initial_capital or 0,
            'current_capital': 0,
            'total_value': 0,
            'total_pnl': 0,
            'roi_percent': 0,
            'open_positions': 0,
            'closed_positions': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
        }
    
    # ===== 持仓管理 =====
    
    def get_open_positions_summary(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        获取持仓摘要
        
        Returns:
            [
                {
                    'symbol': 'BTCUSDT',
                    'type': 'long',
                    'size': 200.0,  # USDT价值
                    'entry_price': 50000,
                    'current_price': 51000,
                    'leverage': 10,
                    'current_pnl': 20.0,
                    'pnl_percent': 10.0
                }
            ]
        """
        positions = self.trader.get_positions()
        if not positions:
            return []
        
        summary = []
        for pos in positions:
            symbol = pos.get('symbol', '')
            position_amt = float(pos.get('positionAmt', 0))
            entry_price = float(pos.get('entryPrice', 0))
            leverage = int(pos.get('leverage', 1))
            
            # Binance API可能返回不同格式的键名，尝试多种可能
            unrealized_pnl = float(pos.get('unRealizedProfit', 
                                   pos.get('unrealizedProfit', 
                                   pos.get('unrealized_profit', 0))))
            
            # 判断多空
            position_type = 'long' if position_amt > 0 else 'short'
            
            # 计算USDT价值
            current_price = current_prices.get(symbol, entry_price)
            size = abs(position_amt) * entry_price / leverage  # 保证金
            
            # 盈亏百分比
            pnl_percent = (unrealized_pnl / size * 100) if size > 0 else 0
            
            summary.append({
                'symbol': symbol,
                'type': position_type,
                'size': size,
                'entry_price': entry_price,
                'current_price': current_price,
                'leverage': leverage,
                'current_pnl': unrealized_pnl,
                'pnl_percent': pnl_percent,
                'quantity': abs(position_amt),  # 币的数量
            })
        
        return summary
    
    # ===== 交易操作 =====
    
    def open_position(self, symbol: str, position_type: str, size: float,
                     current_price: float, leverage: float = 1.0,
                     target_price: float = None, stop_loss: float = None) -> Optional[Dict]:
        """
        开仓
        
        Args:
            symbol: 交易对
            position_type: 'long' 或 'short'
            size: 持仓大小（USDT金额）
            current_price: 当前价格
            leverage: 杠杆倍数
            target_price: 目标价（暂不使用）
            stop_loss: 止损价（暂不使用）
        
        Returns:
            持仓信息或None
        """
        # 设置最小开仓金额（防止数量为0）
        MIN_POSITION_SIZE = 10.0  # 最小$10
        if size < MIN_POSITION_SIZE:
            print(f"⚠️  开仓金额太小 (${size:.2f} < ${MIN_POSITION_SIZE}), 已跳过")
            return None
        
        # 检查资金
        available = self.get_available_capital()
        margin_required = size / leverage
        
        if margin_required > available:
            print(f"❌ 资金不足: 需要 ${margin_required:.2f}, 可用 ${available:.2f}")
            return None
        
        # 计算币的数量
        quantity = calculate_quantity_from_usdt(size, current_price, leverage)
        quantity = round_quantity(symbol, quantity)
        
        if quantity <= 0:
            print(f"❌ 数量计算错误: {quantity}")
            return None
        
        # 确定买卖方向
        side = 'BUY' if position_type.lower() == 'long' else 'SELL'
        
        print(f"📤 发送开仓订单: {symbol} {side} {quantity} @ ${current_price:.2f} ({leverage}x)")
        
        # 执行开仓
        order = self.trader.open_position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            leverage=int(leverage),
            order_type='MARKET'
        )
        
        if not order:
            print(f"❌ 开仓失败")
            return None
        
        # 从币安API获取实际成交价格
        # 市价单成交后，从持仓信息中获取真实的入场价格
        actual_entry_price = current_price  # 默认使用预估价
        actual_quantity = quantity  # 默认使用预估数量
        
        # 等待订单成交，获取持仓信息
        import time
        time.sleep(0.5)  # 给币安API一点时间更新持仓
        
        positions = self.trader.get_positions()
        if positions:
            for pos in positions:
                if pos['symbol'] == symbol:
                    pos_amt = float(pos['positionAmt'])
                    # 找到刚刚开的仓
                    if (position_type.lower() == 'long' and pos_amt > 0) or \
                       (position_type.lower() == 'short' and pos_amt < 0):
                        actual_entry_price = float(pos.get('entryPrice', current_price))
                        actual_quantity = abs(pos_amt)
                        print(f"✅ 实际成交价: ${actual_entry_price:.2f}, 数量: {actual_quantity}")
                        break
        
        # 记录交易（使用实际成交价）
        trade_record = {
            'action': 'open',
            'symbol': symbol,
            'type': position_type,
            'size': size,
            'price': actual_entry_price,  # ✅ 使用实际成交价
            'leverage': leverage,
            'quantity': actual_quantity,  # ✅ 使用实际成交数量
            'timestamp': datetime.now().isoformat(),
            'order_id': order.get('orderId'),
        }
        self.trade_history.append(trade_record)
        self._save_trade_history()  # ✅ 保存到文件
        
        print(f"✅ 开仓成功: Order ID {order.get('orderId')}")
        
        # 返回持仓信息（使用实际成交价）
        return {
            'symbol': symbol,
            'type': position_type,
            'size': size,
            'entry_price': actual_entry_price,  # ✅ 使用实际成交价
            'leverage': leverage,
            'target_price': target_price,
            'stop_loss': stop_loss,
        }
    
    def close_position(self, symbol: str, position_type: str, current_price: float = None) -> bool:
        """
        平仓
        
        Args:
            symbol: 交易对
            position_type: 'long' 或 'short'
            current_price: 当前价格（用于计算盈亏）
        
        Returns:
            是否成功
        """
        position_side = 'LONG' if position_type.lower() == 'long' else 'SHORT'
        
        print(f"📤 发送平仓订单: {symbol} {position_side}")
        
        # 获取持仓信息（用于记录完整的交易数据）
        positions = self.trader.get_positions()
        target_position = None
        if positions:
            for pos in positions:
                if pos['symbol'] == symbol:
                    pos_amt = float(pos['positionAmt'])
                    if position_side == 'LONG' and pos_amt > 0:
                        target_position = pos
                        break
                    elif position_side == 'SHORT' and pos_amt < 0:
                        target_position = pos
                        break
        
        # 提取持仓信息用于记录
        entry_price = float(target_position.get('entryPrice', 0)) if target_position else 0
        leverage = int(target_position.get('leverage', 1)) if target_position else 1
        position_amt = float(target_position.get('positionAmt', 0)) if target_position else 0
        
        # 执行平仓
        result = self.trader.close_position(symbol, position_side)
        
        if not result:
            print(f"❌ 平仓失败")
            return False
        
        # 等待平仓完成，获取实际退出价格
        import time
        time.sleep(0.5)
        
        # 从币安API获取实际平仓价格（从新的持仓信息或者用当前价）
        actual_exit_price = current_price if current_price else entry_price
        
        # 记录交易（完整信息）
        pnl = 0
        if target_position:
            pnl = float(target_position.get('unRealizedProfit', 
                       target_position.get('unrealizedProfit',
                       target_position.get('unrealized_profit', 0))))
        
        # 计算仓位大小（USDT价值）
        size = abs(position_amt) * entry_price / leverage if entry_price and leverage else 0
        
        trade_record = {
            'action': 'close',
            'symbol': symbol,
            'type': position_type,
            'entry_price': entry_price,  # ✅ 添加开仓价
            'exit_price': actual_exit_price,  # ✅ 实际平仓价
            'size': size,  # ✅ 添加仓位大小
            'leverage': leverage,  # ✅ 添加杠杆
            'pnl': pnl,
            'timestamp': datetime.now().isoformat(),
            'order_id': result.get('orderId'),
        }
        self.trade_history.append(trade_record)
        self._save_trade_history()  # ✅ 保存到文件
        
        print(f"✅ 平仓成功: Order ID {result.get('orderId')}, 盈亏: ${pnl:.2f}")
        
        return True
    
    def close_all_positions(self, current_prices: Dict[str, float]):
        """平掉所有持仓"""
        positions = self.trader.get_positions()
        if not positions:
            print("ℹ️  当前无持仓")
            return
        
        for pos in positions:
            symbol = pos['symbol']
            pos_amt = float(pos['positionAmt'])
            position_side = 'LONG' if pos_amt > 0 else 'SHORT'
            current_price = current_prices.get(symbol)
            
            self.close_position(symbol, position_side.lower(), current_price)
    
    # ===== 持仓属性（用于兼容原接口） =====
    
    @property
    def open_positions(self) -> List:
        """返回持仓列表（用于兼容）"""
        positions = self.trader.get_positions()
        return positions if positions else []
    
    @property
    def closed_positions(self) -> List:
        """返回已平仓列表（从trade_history提取完整信息）"""
        closed = []
        for trade in self.trade_history:
            if trade.get('action') == 'close':
                # 构造完整的交易信息供Web显示
                closed.append({
                    'symbol': trade['symbol'],
                    'type': trade['type'],
                    'entry_price': trade.get('entry_price', 0),  # ✅ 开仓价
                    'exit_price': trade.get('exit_price', 0),    # ✅ 平仓价
                    'size': trade.get('size', 0),                # ✅ 仓位大小
                    'leverage': trade.get('leverage', 1),        # ✅ 杠杆
                    'pnl': trade.get('pnl', 0),                  # ✅ 盈亏
                    'timestamp': trade['timestamp'],
                })
        return closed


# ===== 测试代码 =====

if __name__ == "__main__":
    """测试真实交易执行器"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ 请在 .env 文件中设置 BINANCE_API_KEY 和 BINANCE_API_SECRET")
        exit(1)
    
    # 创建执行器（测试网）
    executor = RealTradingExecutor(api_key, api_secret, testnet=True)
    
    print("\n=== 测试真实交易执行器 ===\n")
    
    # 1. 查询统计
    print("1. 查询账户统计...")
    stats = executor.get_statistics({})
    print(f"   总价值: ${stats['total_value']:.2f}")
    print(f"   可用资金: ${stats['current_capital']:.2f}")
    print(f"   盈亏: ${stats['total_pnl']:.2f} ({stats['roi_percent']:.2f}%)")
    print(f"   持仓: {stats['open_positions']}个")
    
    # 2. 查询持仓
    print("\n2. 查询持仓...")
    from crypto_api import CryptoAPI
    crypto_api = CryptoAPI()
    prices = crypto_api.get_multiple_prices(['BTCUSDT', 'ETHUSDT'])
    
    positions = executor.get_open_positions_summary(prices)
    if positions:
        for pos in positions:
            print(f"   {pos['symbol']} {pos['type'].upper()}: "
                  f"${pos['size']:.2f} @ ${pos['entry_price']:.2f}, "
                  f"盈亏: ${pos['current_pnl']:.2f} ({pos['pnl_percent']:.2f}%)")
    else:
        print("   无持仓")
    
    print("\n=== 测试完成 ===")

