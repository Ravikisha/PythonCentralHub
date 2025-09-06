"""
Cryptocurrency Trading Bot

Features:
- Automated trading
- Strategy modules
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import requests
import time
import sys
import random

class ExchangeAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"
    def get_price(self, symbol):
        params = {"ids": symbol, "vs_currencies": "usd"}
        resp = requests.get(self.base_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data[symbol]["usd"]
        else:
            raise ValueError("API error: " + resp.text)

class Strategy:
    def __init__(self):
        self.last_price = None
    def should_buy(self, price):
        if self.last_price is None:
            self.last_price = price
            return False
        decision = price < self.last_price * 0.98
        self.last_price = price
        return decision
    def should_sell(self, price):
        if self.last_price is None:
            self.last_price = price
            return False
        decision = price > self.last_price * 1.02
        self.last_price = price
        return decision

class TradingBot:
    def __init__(self, symbol):
        self.symbol = symbol
        self.api = ExchangeAPI()
        self.strategy = Strategy()
        self.balance = 1000
        self.holdings = 0
        self.history = []
    def run(self, duration=60):
        print(f"Trading {self.symbol} for {duration} seconds...")
        for _ in range(duration):
            try:
                price = self.api.get_price(self.symbol)
                action = None
                if self.strategy.should_buy(price) and self.balance > price:
                    self.holdings += 1
                    self.balance -= price
                    action = 'BUY'
                elif self.strategy.should_sell(price) and self.holdings > 0:
                    self.holdings -= 1
                    self.balance += price
                    action = 'SELL'
                self.history.append({'price': price, 'action': action, 'balance': self.balance, 'holdings': self.holdings})
                print(f"{self.symbol}: ${price} | Action: {action} | Balance: {self.balance} | Holdings: {self.holdings}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)
    def report(self):
        print("Trading History:")
        for h in self.history:
            print(h)

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python cryptocurrency_trading_bot.py <symbol>")
            sys.exit(1)
        symbol = sys.argv[1]
        bot = TradingBot(symbol)
        bot.run(60)
        bot.report()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
