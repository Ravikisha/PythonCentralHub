"""
Real-Time Weather Forecasting System

Features:
- Real-time weather prediction using ML
- Data visualization
- API integration
- Modular design
- CLI interface
- Error handling
"""
import requests
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        resp = requests.get(self.base_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "desc": data["weather"][0]["description"],
                "dt": datetime.fromtimestamp(data["dt"])
            }
        else:
            raise ValueError("API error: " + resp.text)

class WeatherPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.trained = False

    def train(self, df):
        X = df[["humidity", "pressure"]]
        y = df["temp"]
        self.model.fit(X, y)
        self.trained = True

    def predict(self, humidity, pressure):
        if not self.trained:
            raise ValueError("Model not trained")
        return self.model.predict(np.array([[humidity, pressure]]))[0]

class Visualizer:
    @staticmethod
    def plot(df):
        plt.plot(df["dt"], df["temp"], label="Temperature")
        plt.xlabel("Time")
        plt.ylabel("Temperature (C)")
        plt.title("Temperature Over Time")
        plt.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 3:
            print("Usage: python real_time_weather_forecasting.py <API_KEY> <CITY>")
            sys.exit(1)
        api_key = sys.argv[1]
        city = sys.argv[2]
        api = WeatherAPI(api_key)
        predictor = WeatherPredictor()
        records = []
        print(f"Collecting weather data for {city}...")
        for _ in range(10):
            try:
                data = api.get_weather(city)
                records.append(data)
                print(f"{data['dt']}: {data['temp']}C, {data['desc']}")
            except Exception as e:
                print(f"Error: {e}")
            import time; time.sleep(2)
        df = pd.DataFrame(records)
        predictor.train(df)
        print("Model trained. Predicting next hour...")
        pred = predictor.predict(df.iloc[-1]["humidity"], df.iloc[-1]["pressure"])
        print(f"Predicted temperature: {pred:.2f}C")
        Visualizer.plot(df)

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
