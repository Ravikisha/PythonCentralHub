"""
Weather App with Voice Commands

A Python application that fetches weather information based on voice commands. Features include:
- Voice recognition to capture user queries.
- Fetching weather data from an API.
- Displaying weather information in a user-friendly format.
"""

import speech_recognition as sr
import requests
from tkinter import Tk, Label, Button, messagebox

API_KEY = "your_openweathermap_api_key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App with Voice Commands")

        self.label = Label(root, text="Click the button and say a city name:")
        self.label.pack(pady=10)

        self.voice_button = Button(root, text="Speak", command=self.get_weather_by_voice)
        self.voice_button.pack(pady=5)

        self.result_label = Label(root, text="", wraplength=400, justify="left")
        self.result_label.pack(pady=10)

    def get_weather_by_voice(self):
        """Capture voice input and fetch weather information."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.label.config(text="Listening...")
                audio = recognizer.listen(source)
                city = recognizer.recognize_google(audio)
                self.label.config(text=f"You said: {city}")
                self.fetch_weather(city)
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Sorry, I could not understand the audio.")
            except sr.RequestError:
                messagebox.showerror("Error", "Could not request results, please check your internet connection.")

    def fetch_weather(self, city):
        """Fetch weather data from the OpenWeatherMap API."""
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
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
