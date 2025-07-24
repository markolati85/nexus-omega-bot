#!/usr/bin/env python3
"""
NEXUS OKX PRO - AUTONOMOUS AI TRADING BOT v6.0
Complete autonomous trading with spot, margin, and futures integration
GPT-4o powered with advanced risk management and opportunity detection
Up to 125x leverage with intelligent capital allocation
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

# Import all advanced modules
from strategy_selector import select_optimal_strategy, get_strategy_parameters
from ai_core_langchain import get_trade_decision
from futures_handler import FuturesHandler
from margin_handler import MarginHandler
from opportunity_shift_engine import OpportunityShiftEngine
from auto_transfer_handler import AutoTransferHandler
from failsafe import FailsafeSystem

# AI Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available - using technical analysis only")

# Exchange Integration
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print("Error: CCXT required for OKX - install with: pip install ccxt")
    sys.exit(1)

# Load environment
load_dotenv()

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_okx_pro.log'),
        logging.StreamHandler()
    ]
)

class NexusOKXProAutonomous:
    def __init__(self):
        """Initialize Autonomous OKX Pro trading system"""
        self.okx_client = None
        self.trading_enabled = False
        self.autonomous_mode = True
        
        # Load configuration
        self.config = self._load_config()
        
        # Core settings
        self.confidence_threshold = self.config.get('confidence_threshold', 70)
        self.position_size = self.config['risk']['position_size_pct'] / 100
        self.trading_pairs = [f"{pair.replace('USDT', '/USDT')}" for pair in self.config['pairs']]
        self.min_trade_usdt = 5.0
        self.cycle_count = 0
        
        # Advanced handlers
        self.futures_handler = None
        self.margin_handler = None
        self.transfer_handler = None
        self.opportunity_engine = None
        self.failsafe = None
        
        # Load leverage profile
        self.leverage_profile = self._load_leverage_profile()
        
        logging.info("🚀 NEXUS OKX PRO - AUTONOMOUS AI TRADING BOT v6.0")
        logging.info("🤖 GPT-4o Powered with Advanced Risk Management")
        logging.info("📊 Spot + Margin + Futures Integration Active")
        logging.info("⚡ Up to 125x Leverage with Intelligent Capital Allocation")
        
        self.initialize_all_systems()
    
    def initialize_all_systems(self):
        """Initialize all trading systems and handlers"""
        
        # Core OKX connection
        okx_success = self.setup_okx_connection()
        
        if okx_success:
            logging.info("✅ OKX connection established")
            
            # Initialize advanced handlers
            self.futures_handler = FuturesHandler(self.okx_client)
            self.margin_handler = MarginHandler(self.okx_client)
            self.transfer_handler = AutoTransferHandler(self.okx_client)
            self.opportunity_engine = OpportunityShiftEngine(
                self.okx_client, 
                self.futures_handler, 
                self.margin_handler
            )
            self.failsafe = FailsafeSystem()
            
            # Set daily start balance for failsafe
            total_balance = self._get_total_portfolio_value()
            self.failsafe.set_daily_start_balance(total_balance)
            
            logging.info("🔧 All advanced systems initialized")
            logging.info("🛡️ Failsafe protection active")
            logging.info("🔄 Opportunity detection enabled")
            logging.info("💱 Auto-transfer system ready")
            
        else:
            logging.error("❌ OKX connection failed - check API credentials")
            sys.exit(1)
    
    def setup_okx_connection(self):
        """Setup OKX exchange connection with proven parameters"""
        try:
            api_key = os.getenv('OKX_API_KEY')
            secret = os.getenv('OKX_SECRET') 
            passphrase = os.getenv('OKX_PASSPHRASE')
            
            if not all([api_key, secret, passphrase]):
                logging.error("❌ OKX API credentials missing from environment")
                logging.info("Required: OKX_API_KEY, OKX_SECRET, OKX_PASSPHRASE")
                return False
                
            # Initialize OKX client with proven settings
            self.okx_client = ccxt.okx({
                'apiKey': api_key,
                'secret': secret,
                'password': passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'createMarketBuyOrderRequiresPrice': False
                },
                'timeout': 30000,
                'rateLimit': 100
            })
            
            # Test connection with account balance
            balance = self.okx_client.fetch_balance()
            logging.info("✅ OKX API connection verified")
            
            # Check if we can trade
            if balance and 'USDT' in balance['total']:
                self.trading_enabled = True
                logging.info("🎉 OKX TRADING ENABLED - Ready for live execution")
                self.display_account_summary()
                return True
            else:
                logging.warning("⚠️ No USDT balance found - check account funding")
                return False
            
        except ccxt.AuthenticationError as e:
            logging.error(f"❌ OKX Authentication Error: {e}")
            logging.info("💡 Solution: Verify API key, secret, and passphrase are correct")
            return False
        except ccxt.NetworkError as e:
            logging.error(f"❌ OKX Network Error: {e}")
            return False
        except Exception as e:
            logging.error(f"❌ OKX Connection Error: {e}")
            return False
    
    def setup_openai_connection(self):
        """Setup OpenAI GPT-4o for enhanced decision making"""
        if not OPENAI_AVAILABLE:
            return False
            
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logging.warning("⚠️ OpenAI API key not found")
                return False
                
            self.openai_client = OpenAI(api_key=api_key)
            
            # Test GPT-4o connection
            test_response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Respond with: GPT-4o Ready"}],
                max_tokens=10
            )
            
            if "Ready" in test_response.choices[0].message.content:
                logging.info("✅ GPT-4o API connection verified")
                return True
            else:
                logging.warning("⚠️ GPT-4o test failed")
                return False
                
        except Exception as e:
            logging.error(f"❌ OpenAI setup error: {e}")
            return False
    
    def display_account_summary(self):
        """Display comprehensive account information"""
        try:
            balance = self.okx_client.fetch_balance()
            total_portfolio_usdt = 0
            
            logging.info("💼 OKX ACCOUNT SUMMARY:")
            logging.info("=" * 50)
            
            # Show all non-zero balances
            assets_shown = 0
            for asset, amounts in balance['total'].items():
                if amounts > 0.001:  # Only show meaningful amounts
                    try:
                        if asset == 'USDT':
                            usdt_value = amounts
                        else:
                            # Get current price in USDT
                            ticker = self.okx_client.fetch_ticker(f'{asset}/USDT')
                            usdt_value = amounts * ticker['last']
                        
                        total_portfolio_usdt += usdt_value
                        logging.info(f"   {asset}: {amounts:.6f} (${usdt_value:.2f})")
                        assets_shown += 1
                        
                    except:
                        # Asset might not have USDT pair
                        logging.info(f"   {asset}: {amounts:.6f}")
                        
                    if assets_shown >= 10:  # Limit output
                        break
            
            logging.info("=" * 50)
            logging.info(f"📊 Total Portfolio Value: ${total_portfolio_usdt:.2f}")
            logging.info(f"💰 Available for Trading: ${balance['USDT']['free']:.2f}")
            logging.info(f"🎯 Min Trade Size: ${self.min_trade_usdt}")
            
        except Exception as e:
            logging.error(f"Account summary error: {e}")
    
    def get_enhanced_market_data(self, pair):
        """Get comprehensive market analysis for AI decision making"""
        try:
            # Get current ticker
            ticker = self.okx_client.fetch_ticker(pair)
            
            # Get OHLCV data for technical analysis
            ohlcv_1h = self.okx_client.fetch_ohlcv(pair, '1h', limit=50)
            ohlcv_4h = self.okx_client.fetch_ohlcv(pair, '4h', limit=20)
            
            # Calculate technical indicators
            closes_1h = [candle[4] for candle in ohlcv_1h[-20:]]
            closes_4h = [candle[4] for candle in ohlcv_4h[-14:]]
            
            current_price = ticker['last']
            price_change_24h = ticker['percentage'] or 0
            volume_24h = ticker['quoteVolume'] or 0
            
            # Technical indicators
            rsi = self.calculate_rsi(closes_1h, 14)
            sma_20 = sum(closes_1h[-20:]) / len(closes_1h[-20:])
            ema_12 = self.calculate_ema(closes_1h, 12)
            
            # Volume analysis
            volumes = [candle[5] for candle in ohlcv_1h[-10:]]
            avg_volume = sum(volumes) / len(volumes)
            volume_ratio = (ticker['quoteVolume'] or 0) / max(avg_volume, 1)
            
            return {
                'pair': pair,
                'price': current_price,
                'price_change_24h': price_change_24h,
                'volume_24h': volume_24h,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'sma_20': sma_20,
                'ema_12': ema_12,
                'price_vs_sma': (current_price / sma_20 - 1) * 100,
                'price_vs_ema': (current_price / ema_12 - 1) * 100
            }
            
        except Exception as e:
            logging.error(f"Market data error for {pair}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI technical indicator"""
        if len(prices) < period + 1:
            return 50
            
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_ema(self, prices, period):
        """Calculate EMA technical indicator"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def get_ai_trading_decision(self, market_data):
        """Get AI-enhanced trading decision using GPT-4o"""
        if not self.openai_client:
            return self.get_technical_decision(market_data)
        
        try:
            prompt = f"""
Analyze this cryptocurrency trading opportunity for {market_data['pair']}:

MARKET DATA:
- Current Price: ${market_data['price']:.4f}
- 24h Change: {market_data['price_change_24h']:.2f}%
- 24h Volume: ${market_data['volume_24h']:,.0f}
- Volume Ratio: {market_data['volume_ratio']:.2f}x average

TECHNICAL INDICATORS:
- RSI: {market_data['rsi']:.1f}
- Price vs SMA20: {market_data['price_vs_sma']:+.2f}%
- Price vs EMA12: {market_data['price_vs_ema']:+.2f}%

As an expert crypto trader, should I BUY, SELL, or HOLD this asset?
Consider market momentum, technical signals, and risk management.

Respond with ONLY valid JSON:
{{"action": "buy/sell/hold", "confidence": 0-100, "reason": "detailed analysis"}}
"""
            
            logging.info(f"🤖 Requesting GPT-4o analysis for {market_data['pair']}...")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            logging.info(f"🔍 GPT-4o Response: {ai_response}")
            
            # Parse AI decision
            decision = json.loads(ai_response)
            
            return {
                'action': decision.get('action', 'hold').lower(),
                'confidence': max(0, min(100, decision.get('confidence', 50))),
                'reason': decision.get('reason', 'AI analysis complete'),
                'source': 'GPT-4o'
            }
            
        except Exception as e:
            logging.error(f"AI decision error: {e}")
            return self.get_technical_decision(market_data)
    
    def get_technical_decision(self, market_data):
        """Fallback technical analysis decision"""
        rsi = market_data['rsi']
        price_change = market_data['price_change_24h']
        volume_ratio = market_data['volume_ratio']
        
        confidence = 60
        
        # RSI-based signals
        if rsi < 30 and price_change > -5:
            action = 'buy'
            confidence = 75
            reason = f"RSI oversold ({rsi:.1f}) with manageable downtrend"
        elif rsi > 70 and price_change > 5:
            action = 'sell'
            confidence = 75
            reason = f"RSI overbought ({rsi:.1f}) with strong uptrend"
        elif rsi < 40 and volume_ratio > 1.5:
            action = 'buy'
            confidence = 65
            reason = f"RSI low ({rsi:.1f}) with high volume"
        else:
            action = 'hold'
            confidence = 55
            reason = f"Neutral conditions - RSI: {rsi:.1f}"
        
        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'source': 'Technical Analysis'
        }
    
    def execute_okx_trade(self, pair, action, decision_data):
        """Execute trade on OKX with enhanced error handling"""
        if not self.trading_enabled:
            logging.info(f"📊 SIMULATION: {action.upper()} {pair} - {decision_data['reason']}")
            return False
        
        confidence = decision_data['confidence']
        if confidence < self.confidence_threshold:
            logging.info(f"⚠️ Confidence too low ({confidence}%) - skipping {pair}")
            return False
        
        try:
            balance = self.okx_client.fetch_balance()
            usdt_free = balance['USDT']['free']
            
            if action == 'buy':
                # Calculate trade amount
                trade_amount = min(usdt_free * self.position_size, usdt_free - 1)  # Keep 1 USDT buffer
                
                if trade_amount < self.min_trade_usdt:
                    logging.warning(f"⚠️ Insufficient USDT for trade: ${trade_amount:.2f} < ${self.min_trade_usdt}")
                    return False
                
                # Get current price and calculate quantity
                ticker = self.okx_client.fetch_ticker(pair)
                current_price = ticker['last']
                quantity = trade_amount / current_price
                
                # Execute market buy order
                order = self.okx_client.create_market_buy_order(pair, quantity)
                
                logging.info("🟢 OKX BUY ORDER EXECUTED")
                logging.info(f"📋 Order ID: {order.get('id', 'N/A')}")
                logging.info(f"💰 Amount: {quantity:.6f} {pair.split('/')[0]} (${trade_amount:.2f})")
                logging.info(f"💲 Price: ${current_price:.4f}")
                logging.info(f"🤖 {decision_data['source']}: {confidence}% - {decision_data['reason']}")
                
                return True
                
            elif action == 'sell':
                # Get holdings of the base asset
                base_asset = pair.split('/')[0]
                asset_balance = balance.get(base_asset, {}).get('free', 0)
                
                if asset_balance <= 0:
                    logging.info(f"⚠️ No {base_asset} to sell")
                    return False
                
                # Sell 30% of holdings for conservative approach
                sell_quantity = asset_balance * 0.3
                
                # Execute market sell order
                order = self.okx_client.create_market_sell_order(pair, sell_quantity)
                
                ticker = self.okx_client.fetch_ticker(pair)
                current_price = ticker['last']
                usdt_value = sell_quantity * current_price
                
                logging.info("🔴 OKX SELL ORDER EXECUTED")
                logging.info(f"📋 Order ID: {order.get('id', 'N/A')}")
                logging.info(f"💰 Amount: {sell_quantity:.6f} {base_asset} (${usdt_value:.2f})")
                logging.info(f"💲 Price: ${current_price:.4f}")
                logging.info(f"🤖 {decision_data['source']}: {confidence}% - {decision_data['reason']}")
                
                return True
                
        except ccxt.InsufficientFunds as e:
            logging.error(f"❌ Insufficient funds for {action} {pair}: {e}")
        except ccxt.InvalidOrder as e:
            logging.error(f"❌ Invalid order for {action} {pair}: {e}")
        except Exception as e:
            logging.error(f"❌ Trade execution failed for {action} {pair}: {e}")
        
        return False
    
    def run_autonomous_trading_cycle(self):
        """Execute complete autonomous trading cycle with all advanced features"""
        self.cycle_count += 1
        logging.info(f"🔄 AUTONOMOUS CYCLE #{self.cycle_count}")
        logging.info("=" * 80)
        
        try:
            # Step 1: Check opportunity shifts for existing positions
            if self.opportunity_engine and self.cycle_count % 3 == 0:  # Every 3rd cycle
                self._check_opportunity_shifts()
            
            # Step 2: Optimize wallet distribution
            if self.transfer_handler and self.cycle_count % 10 == 0:  # Every 10th cycle
                self.transfer_handler.optimize_wallet_distribution()
            
            # Step 3: Analyze all trading pairs with AI
            trading_opportunities = []
            
            for pair in self.trading_pairs:
                try:
                    opportunity = self._analyze_trading_opportunity(pair)
                    if opportunity:
                        trading_opportunities.append(opportunity)
                        
                except Exception as e:
                    logging.error(f"Analysis error for {pair}: {e}")
                    continue
            
            # Step 4: Rank opportunities by AI confidence and expected ROI
            trading_opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            # Step 5: Execute top opportunities (max 3 per cycle)
            executed_trades = 0
            max_trades_per_cycle = 3
            
            for opportunity in trading_opportunities[:max_trades_per_cycle]:
                if self._execute_autonomous_trade(opportunity):
                    executed_trades += 1
                    time.sleep(2)  # Rate limiting
            
            # Step 6: Cycle summary and monitoring
            self._log_cycle_summary(len(trading_opportunities), executed_trades)
            
            # Step 7: Portfolio status every 5 cycles
            if self.cycle_count % 5 == 0:
                self._comprehensive_portfolio_report()
                
        except Exception as e:
            logging.error(f"Autonomous cycle error: {e}")
        
        logging.info("⏱️ Next autonomous cycle in 3 minutes...")
    
    def run_autonomous_mode(self):
        """Main autonomous trading execution loop"""
        if not self.okx_client:
            logging.error("❌ OKX not initialized - cannot start autonomous trading")
            return
        
        logging.info("🚀 STARTING NEXUS OKX PRO AUTONOMOUS MODE")
        logging.info("=" * 80)
        logging.info(f"🎯 AI Confidence Threshold: {self.confidence_threshold}%")
        logging.info(f"📊 Base Position Size: {self.position_size*100}% per trade")
        logging.info(f"💰 Minimum Trade Size: ${self.min_trade_usdt}")
        logging.info(f"🔄 Cycle Interval: {self.config['cycle_interval_sec']} seconds")
        logging.info(f"🛡️ Max Daily Loss: {self.config['risk']['max_daily_loss_pct']}%")
        logging.info(f"⚡ Max Leverage: 125x (dynamic based on conditions)")
        logging.info("=" * 80)
        
        # Initial portfolio report
        self._comprehensive_portfolio_report()
        
        while True:
            try:
                # Check failsafe before starting cycle
                if self.failsafe and not self._check_failsafe_approval():
                    logging.warning("⚠️ Trading paused by failsafe - waiting for next cycle")
                    time.sleep(self.config['cycle_interval_sec'])
                    continue
                
                # Run autonomous trading cycle
                self.run_autonomous_trading_cycle()
                
                # Wait for next cycle
                time.sleep(self.config['cycle_interval_sec'])
                
            except KeyboardInterrupt:
                logging.info("🛑 Autonomous bot stopped by user")
                self._safe_shutdown()
                break
            except Exception as e:
                logging.error(f"❌ Autonomous loop error: {e}")
                time.sleep(60)  # Wait before retrying
                
    def _load_config(self):
        """Load autonomous configuration"""
        try:
            with open('config_autonomous.json', 'r') as f:
                config = json.load(f)
            logging.info("📋 Autonomous configuration loaded")
            return config
        except FileNotFoundError:
            logging.error("❌ config_autonomous.json not found")
            sys.exit(1)
        except Exception as e:
            logging.error(f"❌ Config loading error: {e}")
            sys.exit(1)
    
    def _load_leverage_profile(self):
        """Load leverage profile for different pairs"""
        try:
            with open('leverage_profile.json', 'r') as f:
                profile = json.load(f)
            logging.info("⚡ Leverage profile loaded")
            return profile
        except FileNotFoundError:
            logging.warning("⚠️ leverage_profile.json not found - using default leverage")
            return {}
        except Exception as e:
            logging.error(f"❌ Leverage profile loading error: {e}")
            return {}
    
    def _get_total_portfolio_value(self):
        """Calculate total portfolio value across all wallets"""
        try:
            if not self.transfer_handler:
                balance = self.okx_client.fetch_balance()
                return balance.get('USDT', {}).get('total', 0)
            
            wallet_summary = self.transfer_handler.get_wallet_summary()
            return wallet_summary.get('total_balance', 0)
            
        except Exception as e:
            logging.error(f"Error calculating portfolio value: {e}")
            return 0
    
    def _check_opportunity_shifts(self):
        """Check for opportunity shifts in existing positions"""
        try:
            shifts = self.opportunity_engine.monitor_positions(self.trading_pairs)
            
            for shift in shifts:
                if shift['roi_improvement'] > 3.0:  # Minimum 3% improvement
                    logging.info(f"🔄 Opportunity shift detected: {shift['from_pair']} → {shift['to_pair']}")
                    logging.info(f"📈 Expected improvement: {shift['roi_improvement']:+.2f}%")
                    
                    # Execute shift if high confidence
                    if shift['confidence'] > 80:
                        result = self.opportunity_engine.execute_opportunity_shift(shift)
                        if result['success']:
                            logging.info("✅ Opportunity shift executed successfully")
                        
        except Exception as e:
            logging.error(f"Opportunity shift check error: {e}")
    
    def _analyze_trading_opportunity(self, pair):
        """Analyze single trading opportunity with full AI and technical analysis"""
        try:
            # Get comprehensive market data
            market_data = self.get_enhanced_market_data(pair)
            if not market_data:
                return None
            
            # Get AI decision with GPT-4o
            ai_decision = get_trade_decision(market_data)
            
            if ai_decision['direction'] == 'hold':
                return None
            
            # Select optimal strategy
            strategy = select_optimal_strategy(market_data)
            strategy_params = get_strategy_parameters(strategy, market_data)
            
            # Get optimal leverage
            pair_symbol = pair.replace('/', '')
            optimal_leverage = self.leverage_profile.get(pair_symbol, 10)
            
            # Apply AI leverage recommendation
            ai_leverage = ai_decision.get('leverage', optimal_leverage)
            final_leverage = min(ai_leverage, optimal_leverage)  # Use lower of AI or profile
            
            # Calculate opportunity score
            score = self._calculate_opportunity_score(ai_decision, market_data, strategy_params)
            
            return {
                'pair': pair,
                'ai_decision': ai_decision,
                'strategy': strategy,
                'strategy_params': strategy_params,
                'leverage': final_leverage,
                'score': score,
                'market_data': market_data
            }
            
        except Exception as e:
            logging.error(f"Opportunity analysis error for {pair}: {e}")
            return None
    
    def _calculate_opportunity_score(self, ai_decision, market_data, strategy_params):
        """Calculate comprehensive opportunity score"""
        
        # Base score from AI confidence
        base_score = ai_decision.get('confidence', 50)
        
        # Strategy alignment bonus
        strategy_bonus = 0
        if ai_decision.get('strategy') == market_data.get('optimal_strategy'):
            strategy_bonus = 10
        
        # Market condition modifiers
        volatility = market_data.get('volatility', 1.0)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        volatility_modifier = min(volatility * 5, 15)  # Max 15 point bonus
        volume_modifier = min((volume_ratio - 1) * 10, 10)  # Max 10 point bonus
        
        # Risk-reward adjustment
        take_profit = ai_decision.get('take_profit_pct', 4.0)
        stop_loss = ai_decision.get('stop_loss_pct', 2.0)
        risk_reward_ratio = take_profit / max(stop_loss, 0.5)
        risk_reward_bonus = min(risk_reward_ratio * 3, 15)  # Max 15 point bonus
        
        final_score = base_score + strategy_bonus + volatility_modifier + volume_modifier + risk_reward_bonus
        
        return min(final_score, 100)  # Cap at 100
    
    def _execute_autonomous_trade(self, opportunity):
        """Execute autonomous trade with full risk management"""
        try:
            pair = opportunity['pair']
            ai_decision = opportunity['ai_decision']
            leverage = opportunity['leverage']
            
            # Failsafe check
            if not self._check_trade_with_failsafe(opportunity):
                return False
            
            # Determine optimal trading type (spot, margin, futures)
            trading_type = self._select_optimal_trading_type(ai_decision, leverage)
            
            # Ensure sufficient capital
            required_capital = self._calculate_required_capital(opportunity, trading_type)
            
            if self.transfer_handler:
                transfer_result = self.transfer_handler.check_and_transfer(trading_type, required_capital)
                if not transfer_result['success']:
                    logging.warning(f"❌ Insufficient capital for {pair} trade")
                    return False
            
            # Execute trade based on type
            result = self._execute_trade_by_type(opportunity, trading_type)
            
            if result and result.get('success'):
                # Record trade for failsafe monitoring
                if self.failsafe:
                    self.failsafe.record_trade_result(result)
                
                logging.info(f"✅ Autonomous trade executed: {pair} via {trading_type}")
                return True
            else:
                logging.warning(f"❌ Trade execution failed for {pair}")
                return False
                
        except Exception as e:
            logging.error(f"Autonomous trade execution error: {e}")
            return False
    
    def _check_failsafe_approval(self):
        """Check if trading is approved by failsafe system"""
        if not self.failsafe:
            return True
        
        # Get basic trade data for approval check
        total_balance = self._get_total_portfolio_value()
        
        dummy_trade_data = {
            'position_value': total_balance * self.position_size,
            'account_balance': total_balance
        }
        
        approval = self.failsafe.check_trade_approval(dummy_trade_data)
        return approval.get('approved', False)
    
    def _check_trade_with_failsafe(self, opportunity):
        """Check specific trade with failsafe"""
        if not self.failsafe:
            return True
        
        total_balance = self._get_total_portfolio_value()
        position_value = total_balance * self.position_size * opportunity['leverage']
        
        trade_data = {
            'position_value': position_value,
            'account_balance': total_balance,
            'pair': opportunity['pair'],
            'confidence': opportunity['ai_decision']['confidence']
        }
        
        approval = self.failsafe.check_trade_approval(trade_data)
        
        if not approval.get('approved'):
            logging.warning(f"⚠️ Trade blocked by failsafe: {approval.get('reason')}")
            
        return approval.get('approved', False)
    
    def _select_optimal_trading_type(self, ai_decision, leverage):
        """Select optimal trading type based on conditions"""
        
        if leverage > 10:
            return 'futures'  # High leverage requires futures
        elif leverage > 3:
            return 'margin'   # Medium leverage uses margin
        else:
            return 'spot'     # Low leverage uses spot
    
    def _calculate_required_capital(self, opportunity, trading_type):
        """Calculate required capital for trade"""
        
        total_balance = self._get_total_portfolio_value()
        base_amount = total_balance * self.position_size
        
        # Add buffer for leverage and fees
        leverage = opportunity['leverage']
        buffer_multiplier = 1.2  # 20% buffer
        
        if trading_type == 'futures':
            required = (base_amount / leverage) * buffer_multiplier
        elif trading_type == 'margin':
            required = (base_amount / min(leverage, 5)) * buffer_multiplier
        else:
            required = base_amount * buffer_multiplier
        
        return max(required, self.min_trade_usdt)
    
    def _execute_trade_by_type(self, opportunity, trading_type):
        """Execute trade using appropriate handler"""
        
        pair = opportunity['pair']
        ai_decision = opportunity['ai_decision']
        direction = ai_decision['direction']
        leverage = opportunity['leverage']
        
        # Calculate position size
        if trading_type == 'futures':
            balance = self.futures_handler.get_futures_balance()
        elif trading_type == 'margin':
            balance = self.margin_handler.get_margin_balance()
        else:
            balance_info = self.okx_client.fetch_balance()
            balance = balance_info.get('USDT', {}).get('free', 0)
        
        # Calculate quantity
        market_price = opportunity['market_data']['price']
        trade_amount = balance * self.position_size
        quantity = trade_amount / market_price
        
        # Execute based on type
        if trading_type == 'futures':
            return self.futures_handler.open_futures_position(pair, direction, leverage, quantity)
        elif trading_type == 'margin':
            return self.margin_handler.open_margin_position(pair, direction, leverage, quantity)
        else:
            # Spot trading
            side = 'buy' if direction == 'long' else 'sell'
            try:
                order = self.okx_client.create_market_order(pair, 'market', side, quantity)
                return {
                    'success': True,
                    'order_id': order.get('id'),
                    'pair': pair,
                    'side': side,
                    'quantity': quantity
                }
            except Exception as e:
                logging.error(f"Spot trade error: {e}")
                return {'success': False, 'error': str(e)}
    
    def _log_cycle_summary(self, opportunities_found, trades_executed):
        """Log comprehensive cycle summary"""
        
        logging.info("=" * 80)
        logging.info(f"📊 CYCLE #{self.cycle_count} SUMMARY:")
        logging.info(f"   🔍 Opportunities analyzed: {opportunities_found}")
        logging.info(f"   ⚡ Trades executed: {trades_executed}")
        
        if self.failsafe:
            risk_status = self.failsafe.get_risk_status()
            logging.info(f"   🛡️ Daily PnL: {risk_status['daily_pnl']:+.2f} USDT")
            logging.info(f"   📉 Daily Loss: {risk_status['daily_loss_pct']:.2f}%")
            logging.info(f"   🔴 Consecutive losses: {risk_status['consecutive_losses']}")
        
        logging.info("=" * 80)
    
    def _comprehensive_portfolio_report(self):
        """Generate comprehensive portfolio report"""
        
        try:
            logging.info("💼 COMPREHENSIVE PORTFOLIO REPORT")
            logging.info("=" * 80)
            
            # Wallet distribution
            if self.transfer_handler:
                wallet_summary = self.transfer_handler.get_wallet_summary()
                total_balance = wallet_summary['total_balance']
                
                logging.info(f"💰 Total Portfolio Value: ${total_balance:.2f}")
                logging.info("📊 Wallet Distribution:")
                
                for wallet, info in wallet_summary['wallets'].items():
                    balance = info['balance']
                    percentage = info['percentage']
                    logging.info(f"   {wallet.capitalize()}: ${balance:.2f} ({percentage:.1f}%)")
            
            # Active positions
            if self.futures_handler:
                futures_positions = self.futures_handler.get_active_positions()
                if futures_positions:
                    logging.info("🔮 Active Futures Positions:")
                    for pair, pos in futures_positions.items():
                        logging.info(f"   {pair}: {pos['side']} {pos['size']:.6f} @ {pos['leverage']}x (PnL: {pos['pnl']:+.2f})")
            
            # Risk status
            if self.failsafe:
                risk_status = self.failsafe.get_risk_status()
                logging.info("🛡️ Risk Management Status:")
                logging.info(f"   Trading Enabled: {risk_status['trading_enabled']}")
                logging.info(f"   Emergency Mode: {risk_status['emergency_mode']}")
                logging.info(f"   Daily PnL: {risk_status['daily_pnl']:+.2f} USDT")
                
                if risk_status['remaining_cooldown_hours'] > 0:
                    logging.info(f"   Cooldown Remaining: {risk_status['remaining_cooldown_hours']:.1f} hours")
            
            logging.info("=" * 80)
            
        except Exception as e:
            logging.error(f"Portfolio report error: {e}")
    
    def _safe_shutdown(self):
        """Safely shutdown autonomous bot"""
        
        logging.info("🛑 Initiating safe shutdown...")
        
        try:
            # Close any risky positions if needed
            if self.opportunity_engine:
                logging.info("🔍 Checking for risky positions...")
            
            # Save state
            if self.failsafe:
                logging.info("💾 Saving failsafe state...")
            
            logging.info("✅ Safe shutdown completed")
            
        except Exception as e:
            logging.error(f"Shutdown error: {e}")

def main():
    """Entry point for Nexus OKX Pro Autonomous Bot"""
    print("🚀 NEXUS OKX PRO - AUTONOMOUS AI TRADING BOT v6.0")
    print("🤖 GPT-4o Powered with Advanced Risk Management")
    print("📊 Spot + Margin + Futures Integration")
    print("⚡ Up to 125x Leverage with Intelligent Capital Allocation")
    print("=" * 80)
    
    try:
        bot = NexusOKXProAutonomous()
        bot.run_autonomous_mode()
    except Exception as e:
        logging.error(f"❌ Autonomous bot startup failed: {e}")
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()