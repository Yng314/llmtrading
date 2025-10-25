"""
Binance Real Trading API Integration
支持合约交易（杠杆、做空做多）
"""

import hmac
import hashlib
import time
from typing import Dict, List, Optional
from urllib.parse import urlencode
import requests
from datetime import datetime


class BinanceRealTrader:
    """
    Binance 合约交易（支持杠杆和做空）
    
    使用说明：
    1. 先在测试网测试: https://testnet.binancefuture.com
    2. 获取测试网API密钥
    3. 设置在 .env 文件中
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        初始化Binance交易客户端
        
        Args:
            api_key: Binance API Key
            api_secret: Binance API Secret
            testnet: 是否使用测试网（默认True，强烈建议先测试）
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        if testnet:
            # 测试网地址
            self.base_url = "https://testnet.binancefuture.com"
            print("⚠️  使用测试网模式（虚拟资金）")
        else:
            # 实盘地址
            self.base_url = "https://fapi.binance.com"
            print("🔴 使用实盘模式（真实资金）")
        
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        }
    
    def _generate_signature(self, params: Dict) -> str:
        """生成请求签名"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            return None
    
    # ===== 账户信息 =====
    
    def get_account_info(self) -> Optional[Dict]:
        """
        获取账户信息（余额、持仓等）
        
        Returns:
            {
                'totalWalletBalance': '1000.00',        # 钱包余额（不含未实现盈亏）
                'totalUnrealizedProfit': '50.00',       # 未实现盈亏
                'totalMarginBalance': '1050.00',        # 保证金余额 = 钱包余额 + 未实现盈亏
                'availableBalance': '950.00',           # 可用余额
                'positions': [...],                      # 持仓信息
                ...
            }
        """
        return self._request('GET', '/fapi/v2/account', signed=True)
    
    def get_balance(self) -> Optional[Dict[str, float]]:
        """
        获取账户余额
        
        Returns:
            {'USDT': 1000.00, 'BNB': 0.5, ...}
        """
        account = self.get_account_info()
        if not account:
            return None
        
        balances = {}
        for asset in account.get('assets', []):
            balance = float(asset.get('walletBalance', 0))
            if balance > 0:
                balances[asset['asset']] = balance
        
        return balances
    
    def get_available_balance(self) -> Optional[float]:
        """
        获取可用余额（USDT）
        
        Returns:
            可用USDT余额
        """
        account = self.get_account_info()
        if not account:
            return None
        
        return float(account.get('availableBalance', 0))
    
    # ===== 持仓管理 =====
    
    def get_positions(self) -> Optional[List[Dict]]:
        """
        获取当前持仓
        
        Returns:
            [
                {
                    'symbol': 'BTCUSDT',
                    'positionSide': 'LONG',  # LONG/SHORT
                    'positionAmt': '0.001',  # 持仓数量
                    'entryPrice': '50000',   # 开仓价格
                    'unRealizedProfit': '10', # 未实现盈亏
                    'leverage': '10',         # 杠杆倍数
                    ...
                }
            ]
        """
        account = self.get_account_info()
        if not account:
            return None
        
        # 过滤出有持仓的
        positions = []
        for pos in account.get('positions', []):
            if float(pos.get('positionAmt', 0)) != 0:
                positions.append(pos)
        
        return positions
    
    # ===== 交易操作 =====
    
    def set_leverage(self, symbol: str, leverage: int) -> Optional[Dict]:
        """
        设置杠杆倍数
        
        Args:
            symbol: 交易对，如 'BTCUSDT'
            leverage: 杠杆倍数 (1-125)
        """
        params = {
            'symbol': symbol,
            'leverage': leverage
        }
        return self._request('POST', '/fapi/v1/leverage', params=params, signed=True)
    
    def set_margin_type(self, symbol: str, margin_type: str = 'CROSSED') -> Optional[Dict]:
        """
        设置保证金模式
        
        Args:
            symbol: 交易对
            margin_type: 'ISOLATED' (逐仓) 或 'CROSSED' (全仓)
        """
        params = {
            'symbol': symbol,
            'marginType': margin_type
        }
        return self._request('POST', '/fapi/v1/marginType', params=params, signed=True)
    
    def open_position(self, symbol: str, side: str, quantity: float, 
                     leverage: int = 1, order_type: str = 'MARKET',
                     price: float = None) -> Optional[Dict]:
        """
        开仓（做多或做空）
        
        Args:
            symbol: 交易对，如 'BTCUSDT'
            side: 'BUY' (做多) 或 'SELL' (做空)
            quantity: 数量（币的数量，不是USDT金额）
            leverage: 杠杆倍数
            order_type: 'MARKET' (市价) 或 'LIMIT' (限价)
            price: 限价单的价格
        
        Returns:
            订单信息
        """
        # 先设置杠杆
        self.set_leverage(symbol, leverage)
        
        # 下单参数
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("限价单必须提供价格")
            params['price'] = price
            params['timeInForce'] = 'GTC'  # Good Till Cancel
        
        return self._request('POST', '/fapi/v1/order', params=params, signed=True)
    
    def close_position(self, symbol: str, position_side: str) -> Optional[Dict]:
        """
        平仓（市价全部平仓）
        
        Args:
            symbol: 交易对
            position_side: 'LONG' 或 'SHORT'
        
        Returns:
            订单信息
        """
        # 获取当前持仓数量
        positions = self.get_positions()
        if not positions:
            return None
        
        position = None
        for pos in positions:
            if pos['symbol'] == symbol:
                pos_amt = float(pos['positionAmt'])
                if position_side == 'LONG' and pos_amt > 0:
                    position = pos
                    break
                elif position_side == 'SHORT' and pos_amt < 0:
                    position = pos
                    break
        
        if not position:
            print(f"❌ 未找到持仓: {symbol} {position_side}")
            return None
        
        # 平仓方向与开仓相反
        close_side = 'SELL' if position_side == 'LONG' else 'BUY'
        quantity = abs(float(position['positionAmt']))
        
        params = {
            'symbol': symbol,
            'side': close_side,
            'type': 'MARKET',
            'quantity': quantity,
        }
        
        return self._request('POST', '/fapi/v1/order', params=params, signed=True)
    
    # ===== 价格查询 =====
    
    def get_price(self, symbol: str) -> Optional[float]:
        """获取当前价格"""
        result = self._request('GET', '/fapi/v1/ticker/price', params={'symbol': symbol})
        if result:
            return float(result.get('price', 0))
        return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """获取多个交易对的价格"""
        prices = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            if price:
                prices[symbol] = price
        return prices
    
    # ===== 订单查询 =====
    
    def get_open_orders(self, symbol: str = None) -> Optional[List[Dict]]:
        """
        查询当前挂单
        
        Args:
            symbol: 可选，指定交易对
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._request('GET', '/fapi/v1/openOrders', params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """撤销订单"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._request('DELETE', '/fapi/v1/order', params=params, signed=True)
    
    def cancel_all_orders(self, symbol: str) -> Optional[Dict]:
        """撤销某交易对的所有挂单"""
        params = {'symbol': symbol}
        return self._request('DELETE', '/fapi/v1/allOpenOrders', params=params, signed=True)


# ===== 辅助函数 =====

def calculate_quantity_from_usdt(usdt_amount: float, price: float, leverage: int) -> float:
    """
    根据USDT金额计算币的数量
    
    Args:
        usdt_amount: 想要开仓的USDT金额（如200 USDT）
        price: 当前币价
        leverage: 杠杆倍数
    
    Returns:
        币的数量（需要根据交易所规则调整精度）
    """
    # 实际购买力 = usdt_amount * leverage
    # 币的数量 = 购买力 / 价格
    quantity = (usdt_amount * leverage) / price
    return quantity


def round_quantity(symbol: str, quantity: float) -> float:
    """
    根据交易对规则调整数量精度
    
    不同币种有不同的数量精度要求：
    - BTC: 3位小数
    - ETH: 3位小数
    - BNB: 2位小数
    - 小币种: 整数
    """
    # 根据Binance合约规则调整精度
    if symbol == 'BTCUSDT':
        return round(quantity, 3)
    elif symbol == 'ETHUSDT':
        return round(quantity, 3)
    elif symbol == 'BNBUSDT':
        return round(quantity, 2)
    elif symbol == 'ADAUSDT':
        return round(quantity, 0)  # 整数
    elif symbol == 'SOLUSDT':
        return round(quantity, 0)  # 整数（修复：从1改为0）
    else:
        return round(quantity, 1)


# ===== 测试代码 =====

if __name__ == "__main__":
    """测试Binance API连接"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 从环境变量读取API密钥
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ 请在 .env 文件中设置 BINANCE_API_KEY 和 BINANCE_API_SECRET")
        print("\n如何获取测试网API密钥：")
        print("1. 访问: https://testnet.binancefuture.com")
        print("2. 用GitHub账号登录")
        print("3. 生成API Key和Secret")
        exit(1)
    
    # 创建交易客户端（默认使用测试网）
    trader = BinanceRealTrader(api_key, api_secret, testnet=True)
    
    print("\n=== 测试Binance API连接 ===\n")
    
    # 1. 查询账户余额
    print("1. 查询账户余额...")
    balance = trader.get_available_balance()
    if balance is not None:
        print(f"   ✅ 可用余额: ${balance:.2f} USDT")
    else:
        print("   ❌ 查询失败")
    
    # 2. 查询当前价格
    print("\n2. 查询BTC价格...")
    btc_price = trader.get_price('BTCUSDT')
    if btc_price:
        print(f"   ✅ BTC价格: ${btc_price:,.2f}")
    else:
        print("   ❌ 查询失败")
    
    # 3. 查询持仓
    print("\n3. 查询当前持仓...")
    positions = trader.get_positions()
    if positions is not None:
        if positions:
            print(f"   ✅ 当前持仓: {len(positions)}个")
            for pos in positions:
                print(f"      {pos['symbol']} {pos['positionSide']}: "
                      f"{pos['positionAmt']} @ ${pos['entryPrice']}, "
                      f"未实现盈亏: ${pos['unRealizedProfit']}")
        else:
            print("   ✅ 当前无持仓")
    else:
        print("   ❌ 查询失败")
    
    # 4. 查询挂单
    print("\n4. 查询挂单...")
    orders = trader.get_open_orders()
    if orders is not None:
        if orders:
            print(f"   ✅ 当前挂单: {len(orders)}个")
        else:
            print("   ✅ 当前无挂单")
    else:
        print("   ❌ 查询失败")
    
    print("\n=== 测试完成 ===")
    print("\n⚠️  提醒：当前使用测试网，资金是虚拟的。")
    print("如需实盘交易，请修改 testnet=False，并充分测试后再使用。")

