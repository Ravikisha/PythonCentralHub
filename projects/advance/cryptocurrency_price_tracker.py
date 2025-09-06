"""
Cryptocurrency Price Tracker

Features:
- API integration
- Data visualization
- Modular design
- CLI interface
- Error handling
"""
import requests
import sys
import time
import matplotlib.pyplot as plt

class CryptoAPI:
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

class PriceTracker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.prices = []
        self.timestamps = []
        self.api = CryptoAPI()
    def track(self, duration=60):
        print(f"Tracking {self.symbol} for {duration} seconds...")
        for _ in range(duration):
            try:
                price = self.api.get_price(self.symbol)
                self.prices.append(price)
                self.timestamps.append(time.time())
                print(f"{self.symbol}: ${price}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)
    def plot(self):
        plt.plot(self.timestamps, self.prices, label=self.symbol)
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.title(f'{self.symbol} Price Over Time')
        plt.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python cryptocurrency_price_tracker.py <symbol>")
            sys.exit(1)
        symbol = sys.argv[1]
        tracker = PriceTracker(symbol)
        tracker.track(60)
        tracker.plot()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
