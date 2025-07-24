#!/usr/bin/env python3
"""
Тестирование циклов Binance бота с проверкой API лимитов и сербского IP
Test Binance bot cycles with API weight limits and Serbian IP verification
"""
import os
import time
import logging
import requests
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_cycles_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BinanceBotTester:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = None
        self.cycle_count = 0
        self.weight_usage = {}
        
        # Торговые пары для мониторинга
        self.trading_pairs = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'BNBUSDT', 'DOTUSDT', 'LINKUSDT'
        ]
        
    def setup_binance_client(self):
        """Инициализация Binance клиента"""
        try:
            if not self.api_key or not self.api_secret:
                logger.error("❌ Binance API ключи не найдены в .env")
                return False
            
            self.client = Client(self.api_key, self.api_secret)
            
            # Тест соединения
            account = self.client.get_account()
            logger.info(f"✅ Binance подключение успешно - Торговля: {account.get('canTrade', False)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Binance: {e}")
            return False
    
    def get_external_ip(self):
        """Получение внешнего IP адреса"""
        try:
            # Проверяем несколько сервисов для определения IP
            services = [
                'https://ifconfig.me',
                'https://ipinfo.io/ip', 
                'https://api.ipify.org'
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=10)
                    ip = response.text.strip()
                    
                    # Проверяем, сербский ли это IP
                    geo_response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=10)
                    geo_data = geo_response.json()
                    
                    country = geo_data.get('country', 'Unknown')
                    city = geo_data.get('city', 'Unknown')
                    org = geo_data.get('org', 'Unknown')
                    
                    logger.info(f"🌍 IP: {ip} | Страна: {country} | Город: {city}")
                    logger.info(f"📡 Провайдер: {org}")
                    
                    if country == 'RS':
                        logger.info("✅ Подтверждён сербский IP")
                    else:
                        logger.warning(f"⚠️ IP не из Сербии (обнаружено: {country})")
                    
                    return ip, country, city, org
                    
                except Exception as e:
                    logger.warning(f"Сервис {service} недоступен: {e}")
                    continue
                    
            return "Unknown", "Unknown", "Unknown", "Unknown"
            
        except Exception as e:
            logger.error(f"Ошибка определения IP: {e}")
            return "Error", "Error", "Error", "Error"
    
    def get_account_balance_with_weights(self):
        """Получение баланса USDT с отслеживанием API weight"""
        try:
            if not self.client:
                return 0.0, {}
            
            # Делаем запрос к аккаунту и получаем заголовки
            response = self.client.get_account()
            
            # Извлекаем заголовки weight из последнего запроса
            # Примечание: python-binance не предоставляет прямой доступ к headers
            # Но мы можем отследить использование через другие методы
            
            usdt_balance = 0.0
            for balance in response['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
                    break
            
            # Логируем информацию о запросе
            logger.info(f"💰 USDT баланс: ${usdt_balance:.2f}")
            
            return usdt_balance, {}
            
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return 0.0, {}
    
    def get_symbol_price_with_weights(self, symbol):
        """Получение цены символа с отслеживанием weight"""
        try:
            if not self.client:
                return 0.0
            
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            # Примечание: каждый запрос цены весит 2 weight units
            self.weight_usage[symbol] = self.weight_usage.get(symbol, 0) + 2
            
            logger.debug(f"📊 {symbol}: ${price:.4f} (weight: +2)")
            
            return price
            
        except Exception as e:
            logger.error(f"Ошибка получения цены {symbol}: {e}")
            return 0.0
    
    def calculate_rsi_with_weights(self, symbol, interval='1h', period=14):
        """Расчёт RSI с отслеживанием weight"""
        try:
            if not self.client:
                return 50
            
            # Запрос исторических данных весит 2 weight units
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=period+1)
            self.weight_usage[f'{symbol}_klines'] = self.weight_usage.get(f'{symbol}_klines', 0) + 2
            
            closes = [float(kline[4]) for kline in klines]
            
            if len(closes) < period + 1:
                return 50
            
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            logger.debug(f"📈 {symbol} RSI: {rsi:.1f} (weight: +2)")
            
            return rsi
            
        except Exception as e:
            logger.error(f"Ошибка расчёта RSI для {symbol}: {e}")
            return 50
    
    def analyze_trading_pair(self, symbol):
        """Анализ торговой пары"""
        try:
            current_price = self.get_symbol_price_with_weights(symbol)
            rsi = self.calculate_rsi_with_weights(symbol)
            
            if current_price == 0:
                return None
            
            # Простая стратегия на основе RSI
            signal = None
            if rsi < 30:
                signal = {
                    'action': 'BUY',
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': rsi,
                    'reason': f'RSI перепродан ({rsi:.1f})'
                }
            elif rsi > 70:
                signal = {
                    'action': 'SELL', 
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': rsi,
                    'reason': f'RSI перекуплен ({rsi:.1f})'
                }
            
            logger.info(f"📊 {symbol}: ${current_price:.4f} | RSI: {rsi:.1f} | {signal['action'] if signal else 'HOLD'}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Ошибка анализа {symbol}: {e}")
            return None
    
    def trading_cycle(self):
        """Основной торговый цикл"""
        self.cycle_count += 1
        cycle_start = time.time()
        
        logger.info(f"🔄 === ЦИКЛ #{self.cycle_count} НАЧАЛСЯ ===")
        
        try:
            # Сброс счётчика weight для этого цикла
            self.weight_usage = {}
            
            # Получение баланса
            balance, balance_weights = self.get_account_balance_with_weights()
            
            signals_generated = 0
            total_weight = 4  # Начальный weight от запроса аккаунта (4 units)
            
            # Анализ каждой торговой пары
            for symbol in self.trading_pairs:
                signal = self.analyze_trading_pair(symbol)
                
                if signal:
                    signals_generated += 1
                    logger.info(f"🎯 Сигнал: {signal['action']} {symbol} - {signal['reason']}")
                
                # Пауза между запросами для соблюдения лимитов
                time.sleep(0.5)
            
            # Подсчёт общего использования weight
            for key, weight in self.weight_usage.items():
                total_weight += weight
            
            cycle_duration = time.time() - cycle_start
            
            # Логирование результатов цикла
            logger.info(f"📈 Результаты цикла #{self.cycle_count}:")
            logger.info(f"   💰 Баланс: ${balance:.2f}")
            logger.info(f"   🎯 Сигналов: {signals_generated}")
            logger.info(f"   ⚖️ Общий API Weight: {total_weight}")
            logger.info(f"   ⏱️ Длительность: {cycle_duration:.1f}с")
            
            # Предупреждение о превышении лимитов
            if total_weight > 100:  # Безопасный лимит в минуту
                logger.warning(f"⚠️ Высокое использование API weight: {total_weight}")
            
            logger.info(f"🔄 === ЦИКЛ #{self.cycle_count} ЗАВЕРШЁН ===\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле #{self.cycle_count}: {e}")
            return False
    
    def run_test_cycles(self, num_cycles=5):
        """Запуск тестовых циклов"""
        logger.info("🚀 НАЧАЛО ТЕСТИРОВАНИЯ NEXUS AI BINANCE BOT")
        logger.info("=" * 60)
        
        # Проверка IP и геолокации
        ip, country, city, org = self.get_external_ip()
        
        # Инициализация Binance клиента
        if not self.setup_binance_client():
            logger.error("❌ Не удалось подключиться к Binance API")
            return False
        
        logger.info(f"📊 Торговые пары: {', '.join(self.trading_pairs)}")
        logger.info(f"🔄 Планируется циклов: {num_cycles}")
        logger.info(f"⏱️ Интервал между циклами: 30 секунд")
        logger.info("=" * 60)
        
        successful_cycles = 0
        
        for i in range(num_cycles):
            try:
                # Выполнение цикла
                success = self.trading_cycle()
                
                if success:
                    successful_cycles += 1
                    logger.info(f"✅ Цикл #{i+1} выполнен успешно")
                else:
                    logger.error(f"❌ Цикл #{i+1} завершился с ошибкой")
                
                # Пауза между циклами (кроме последнего)
                if i < num_cycles - 1:
                    logger.info("⏱️ Ожидание 30 секунд до следующего цикла...")
                    time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Тестирование остановлено пользователем")
                break
            except Exception as e:
                logger.error(f"❌ Критическая ошибка в цикле {i+1}: {e}")
        
        # Итоговый отчёт
        logger.info("=" * 60)
        logger.info("📋 ИТОГОВЫЙ ОТЧЁТ ТЕСТИРОВАНИЯ")
        logger.info(f"🎯 Успешных циклов: {successful_cycles}/{num_cycles}")
        logger.info(f"📊 Процент успеха: {(successful_cycles/num_cycles)*100:.1f}%")
        logger.info(f"🌍 IP адрес: {ip} ({country})")
        logger.info(f"🏙️ Местоположение: {city}")
        logger.info(f"📡 Провайдер: {org}")
        
        if country == 'RS':
            logger.info("✅ Подтверждён сербский IP - VPN отключен")
        else:
            logger.warning(f"⚠️ IP не из Сербии - возможно активен VPN")
        
        logger.info("=" * 60)
        
        return successful_cycles == num_cycles

def main():
    """Главная функция"""
    tester = BinanceBotTester()
    
    # Запуск 5 тестовых циклов
    success = tester.run_test_cycles(5)
    
    if success:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        logger.warning("⚠️ Некоторые тесты завершились с ошибками")

if __name__ == "__main__":
    main()