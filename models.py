from app import db
from datetime import datetime
from sqlalchemy import func

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    strategy = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    exchange_order_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, filled, cancelled, failed
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'amount': self.amount,
            'price': self.price,
            'total': self.total,
            'fee': self.fee,
            'strategy': self.strategy,
            'timestamp': self.timestamp.isoformat(),
            'exchange_order_id': self.exchange_order_id,
            'status': self.status
        }

class PnL(db.Model):
    __tablename__ = 'pnl'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    realized_pnl = db.Column(db.Float, default=0.0)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    avg_win = db.Column(db.Float, default=0.0)
    avg_loss = db.Column(db.Float, default=0.0)
    max_drawdown = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'max_drawdown': self.max_drawdown,
            'timestamp': self.timestamp.isoformat()
        }

class BotStatus(db.Model):
    __tablename__ = 'bot_status'
    
    id = db.Column(db.Integer, primary_key=True)
    is_running = db.Column(db.Boolean, default=False)
    current_strategy = db.Column(db.String(50), default='moving_average')
    total_balance_usd = db.Column(db.Float, default=0.0)
    available_balance_usd = db.Column(db.Float, default=0.0)
    active_positions = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'is_running': self.is_running,
            'current_strategy': self.current_strategy,
            'total_balance_usd': self.total_balance_usd,
            'available_balance_usd': self.available_balance_usd,
            'active_positions': self.active_positions,
            'last_update': self.last_update.isoformat(),
            'error_message': self.error_message
        }

class PortfolioSnapshot(db.Model):
    __tablename__ = 'portfolio_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    initial_deposit_usd = db.Column(db.Float, nullable=False)
    current_portfolio_value_usd = db.Column(db.Float, nullable=False)
    true_profit_usd = db.Column(db.Float, nullable=False)  # current_value - initial_deposit
    profit_percentage = db.Column(db.Float, nullable=False)  # (current_value - initial_deposit) / initial_deposit * 100
    usdt_balance = db.Column(db.Float, default=0.0)
    crypto_holdings_value = db.Column(db.Float, default=0.0)
    total_trades_executed = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'initial_deposit_usd': self.initial_deposit_usd,
            'current_portfolio_value_usd': self.current_portfolio_value_usd,
            'true_profit_usd': self.true_profit_usd,
            'profit_percentage': self.profit_percentage,
            'usdt_balance': self.usdt_balance,
            'crypto_holdings_value': self.crypto_holdings_value,
            'total_trades_executed': self.total_trades_executed,
            'timestamp': self.timestamp.isoformat()
        }

class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, default=0.0)
    change_24h = db.Column(db.Float, default=0.0)
    rsi = db.Column(db.Float)
    ema_short = db.Column(db.Float)
    ema_long = db.Column(db.Float)
    bb_upper = db.Column(db.Float)
    bb_lower = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'price': self.price,
            'volume': self.volume,
            'change_24h': self.change_24h,
            'rsi': self.rsi,
            'ema_short': self.ema_short,
            'ema_long': self.ema_long,
            'bb_upper': self.bb_upper,
            'bb_lower': self.bb_lower,
            'timestamp': self.timestamp.isoformat()
        }
