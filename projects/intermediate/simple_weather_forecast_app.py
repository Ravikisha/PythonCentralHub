"""
Simple Weather Forecast App

A Python application that fetches and displays weather forecast data. Features include:
- Fetching weather data from an API.
- Displaying the forecast in a user-friendly format.
"""

import requests
from tkinter import Tk, Label, Entry, Button, messagebox

API_KEY = "your_openweathermap_api_key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


class WeatherForecastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Weather Forecast App")

        Label(root, text="Enter City Name:").grid(row=0, column=0, padx=10, pady=10)
        self.city_entry = Entry(root, width=30)
        self.city_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(root, text="Get Weather", command=self.get_weather).grid(row=1, column=0, columnspan=2, pady=10)

        self.result_label = Label(root, text="", wraplength=400, justify="left")
        self.result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def get_weather(self):
        """Fetch weather data for the entered city."""
        city = self.city_entry.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        params = {"q": city, "appid": API_KEY, "units": "metric"}
        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if response.status_code == 200:
                weather = data["weather"][0]["description"].capitalize()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]

                result = (
                    f"Weather in {city}:\n"
                    f"Condition: {weather}\n"
                    f"Temperature: {temp}°C\n"
                    f"Feels Like: {feels_like}°C\n"
                    f"Humidity: {humidity}%"
                )
                self.result_label.config(text=result)
            else:
                messagebox.showerror("Error", data.get("message", "Failed to fetch weather data."))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


def main():
    root = Tk()
    app = WeatherForecastApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
