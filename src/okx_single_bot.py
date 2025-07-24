import os
import sys
import time
import json
import logging
from typing import Dict

from dotenv import load_dotenv

try:
    import ccxt
except ImportError:
    raise SystemExit('ccxt is required')

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()

LOG_FILE = 'okx_bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

CONFIG_PATH = os.getenv('OKX_BOT_CONFIG', 'config.json')


def load_config(path: str) -> Dict:
    if not os.path.exists(path):
        return {
            'pair': 'BTC/USDT',
            'cycle_interval': 60,
            'position_size_pct': 50,
            'confidence_threshold': 60,
        }
    with open(path, 'r') as f:
        return json.load(f)


class OKXBot:
    def __init__(self, config: Dict):
        self.config = config
        self.pair = config.get('pair', 'BTC/USDT')
        self.cycle_interval = config.get('cycle_interval', 60)
        self.position_size_pct = config.get('position_size_pct', 50) / 100
        self.confidence_threshold = config.get('confidence_threshold', 60)
        self.client = self._init_okx()
        self.ai_client = self._init_openai()

    def _init_okx(self):
        api_key = os.getenv('OKX_API_KEY')
        secret = os.getenv('OKX_SECRET')
        password = os.getenv('OKX_PASSPHRASE')
        if not all([api_key, secret, password]):
            raise SystemExit('Missing OKX API credentials')
        return ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True,
        })

    def _init_openai(self):
        if not OpenAI:
            logging.warning('OpenAI library missing. Using heuristic decisions.')
            return None
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logging.warning('OPENAI_API_KEY not set. Using heuristic decisions.')
            return None
        return OpenAI(api_key=api_key)

    def ai_decision(self, price: float) -> Dict:
        if not self.ai_client:
            # Simple heuristic: random hold/buy/sell based on price moves
            return {'action': 'hold', 'confidence': 50}
        prompt = f"Current price for {self.pair} is {price:.2f}. Should we buy, sell or hold? Respond in JSON." 
        try:
            resp = self.ai_client.chat.completions.create(
                model='gpt-4o',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=20,
                temperature=0.1,
            )
            data = json.loads(resp.choices[0].message.content.strip())
            return {
                'action': data.get('action', 'hold'),
                'confidence': data.get('confidence', 50)
            }
        except Exception as e:
            logging.error(f'AI decision error: {e}')
            return {'action': 'hold', 'confidence': 50}

    def execute_trade(self, action: str, price: float):
        balance = self.client.fetch_balance()
        usdt = balance['USDT']['free']
        size = usdt * self.position_size_pct
        if action == 'buy' and size > 5:
            amount = size / price
            order = self.client.create_market_buy_order(self.pair, amount)
            logging.info(f'BUY {amount} {self.pair} @ {price} => {order}')
        elif action == 'sell':
            pos = balance.get(self.pair.split('/')[0], {}).get('free', 0)
            if pos * price > 5:
                order = self.client.create_market_sell_order(self.pair, pos)
                logging.info(f'SELL {pos} {self.pair} @ {price} => {order}')

    def cycle(self):
        ticker = self.client.fetch_ticker(self.pair)
        price = ticker['last']
        decision = self.ai_decision(price)
        logging.info(f'DECISION {decision}')
        if decision['confidence'] >= self.confidence_threshold:
            self.execute_trade(decision['action'], price)
        else:
            logging.info('Confidence too low, skipping trade')

    def run(self):
        while True:
            try:
                self.cycle()
            except Exception as e:
                logging.exception(f'Cycle error: {e}')
            time.sleep(self.cycle_interval)


def main():
    config = load_config(CONFIG_PATH)
    bot = OKXBot(config)
    bot.run()


if __name__ == '__main__':
    main()
