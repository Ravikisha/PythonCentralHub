# Weather App with GUI (Tkinter)

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import threading

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # API key (you would get this from OpenWeatherMap)
        self.api_key = "your_api_key_here"  # Replace with actual API key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Store weather data
        self.current_weather = None
        self.forecast_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Weather App", 
            font=("Arial", 24, "bold"),
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        title_label.pack(pady=20)
        
        # Search frame
        search_frame = tk.Frame(self.root, bg='#2c3e50')
        search_frame.pack(pady=10)
        
        tk.Label(
            search_frame, 
            text="Enter City:", 
            font=("Arial", 12),
            bg='#2c3e50', 
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        self.city_entry = tk.Entry(
            search_frame, 
            font=("Arial", 12), 
            width=20
        )
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind('<Return>', lambda event: self.get_weather())
        
        self.search_button = tk.Button(
            search_frame, 
            text="Get Weather", 
            command=self.get_weather,
            font=("Arial", 10, "bold"),
            bg='#3498db',
            fg='white',
            padx=10
        )
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # Current weather frame
        self.current_frame = tk.LabelFrame(
            self.root, 
            text="Current Weather", 
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            padx=20,
            pady=15
        )
        self.current_frame.pack(pady=20, padx=20, fill='x')
        
        # Weather info labels
        self.weather_labels = {}
        self.create_weather_labels()
        
        # Forecast frame
        self.forecast_frame = tk.LabelFrame(
            self.root, 
            text="5-Day Forecast", 
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            padx=20,
            pady=15
        )
        self.forecast_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg='#2c3e50')
        buttons_frame.pack(pady=10)
        
        self.refresh_button = tk.Button(
            buttons_frame, 
            text="Refresh", 
            command=self.refresh_weather,
            font=("Arial", 10),
            bg='#27ae60',
            fg='white',
            padx=15
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = tk.Button(
            buttons_frame, 
            text="Save Data", 
            command=self.save_weather_data,
            font=("Arial", 10),
            bg='#e67e22',
            fg='white',
            padx=15
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_weather_labels(self):
        """Create labels for weather information"""
        # City and country
        self.weather_labels['city'] = tk.Label(
            self.current_frame, 
            text="City: -", 
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['city'].grid(row=0, column=0, columnspan=2, pady=5, sticky='w')
        
        # Temperature
        self.weather_labels['temp'] = tk.Label(
            self.current_frame, 
            text="Temperature: -", 
            font=("Arial", 24, "bold"),
            bg='#34495e',
            fg='#e74c3c'
        )
        self.weather_labels['temp'].grid(row=1, column=0, columnspan=2, pady=10)
        
        # Weather description
        self.weather_labels['desc'] = tk.Label(
            self.current_frame, 
            text="Description: -", 
            font=("Arial", 12),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['desc'].grid(row=2, column=0, columnspan=2, pady=5)
        
        # Feels like
        self.weather_labels['feels_like'] = tk.Label(
            self.current_frame, 
            text="Feels like: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['feels_like'].grid(row=3, column=0, pady=5, sticky='w')
        
        # Humidity
        self.weather_labels['humidity'] = tk.Label(
            self.current_frame, 
            text="Humidity: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['humidity'].grid(row=3, column=1, pady=5, sticky='w')
        
        # Pressure
        self.weather_labels['pressure'] = tk.Label(
            self.current_frame, 
            text="Pressure: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['pressure'].grid(row=4, column=0, pady=5, sticky='w')
        
        # Wind speed
        self.weather_labels['wind'] = tk.Label(
            self.current_frame, 
            text="Wind: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['wind'].grid(row=4, column=1, pady=5, sticky='w')
        
        # Visibility
        self.weather_labels['visibility'] = tk.Label(
            self.current_frame, 
            text="Visibility: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['visibility'].grid(row=5, column=0, pady=5, sticky='w')
        
        # UV Index (if available)
        self.weather_labels['uv'] = tk.Label(
            self.current_frame, 
            text="UV Index: -", 
            font=("Arial", 11),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.weather_labels['uv'].grid(row=5, column=1, pady=5, sticky='w')
        
    def get_weather(self):
        """Get weather data for the specified city"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name")
            return
        
        # Show loading status
        self.status_var.set("Loading weather data...")
        self.search_button.config(state='disabled')
        
        # Use threading to prevent UI freezing
        thread = threading.Thread(target=self._fetch_weather_data, args=(city,))
        thread.daemon = True
        thread.start()
        
    def _fetch_weather_data(self, city: str):
        """Fetch weather data in a separate thread"""
        try:
            # Get current weather
            current_url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric"
            
            # For demo purposes, we'll use mock data
            # In real implementation, you would use: response = requests.get(current_url)
            mock_current_data = self.get_mock_current_weather(city)
            
            # Get forecast
            # forecast_url = f"{self.base_url}/forecast?q={city}&appid={self.api_key}&units=metric"
            mock_forecast_data = self.get_mock_forecast_data(city)
            
            # Update UI in main thread
            self.root.after(0, self._update_weather_display, mock_current_data, mock_forecast_data)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error fetching weather data: {str(e)}")
        
    def get_mock_current_weather(self, city: str) -> Dict:
        """Generate mock current weather data for demo"""
        import random
        
        temps = [15, 18, 22, 25, 28, 30, 12, 8, 5, 2]
        conditions = ["Clear", "Cloudy", "Rainy", "Sunny", "Partly Cloudy", "Overcast"]
        
        return {
            "name": city.title(),
            "sys": {"country": "XX"},
            "main": {
                "temp": random.choice(temps),
                "feels_like": random.choice(temps) + random.randint(-3, 3),
                "humidity": random.randint(30, 80),
                "pressure": random.randint(1000, 1030)
            },
            "weather": [{
                "main": random.choice(conditions),
                "description": random.choice(conditions).lower()
            }],
            "wind": {
                "speed": random.randint(5, 25)
            },
            "visibility": random.randint(5000, 10000),
            "dt": int(datetime.now().timestamp())
        }
    
    def get_mock_forecast_data(self, city: str) -> Dict:
        """Generate mock forecast data for demo"""
        import random
        
        forecast_list = []
        for i in range(40):  # 5 days * 8 times per day (3-hour intervals)
            date = datetime.now() + timedelta(hours=i*3)
            temp = random.randint(10, 30)
            
            forecast_list.append({
                "dt": int(date.timestamp()),
                "dt_txt": date.strftime("%Y-%m-%d %H:%M:%S"),
                "main": {
                    "temp": temp,
                    "temp_min": temp - 2,
                    "temp_max": temp + 2
                },
                "weather": [{
                    "main": random.choice(["Clear", "Cloudy", "Rain"]),
                    "description": "demo weather"
                }]
            })
        
        return {"list": forecast_list}
    
    def _update_weather_display(self, current_data: Dict, forecast_data: Dict):
        """Update the weather display with fetched data"""
        try:
            self.current_weather = current_data
            self.forecast_data = forecast_data
            
            # Update current weather
            city_country = f"{current_data['name']}, {current_data['sys']['country']}"
            self.weather_labels['city'].config(text=f"City: {city_country}")
            
            temp = round(current_data['main']['temp'])
            self.weather_labels['temp'].config(text=f"{temp}°C")
            
            desc = current_data['weather'][0]['description'].title()
            self.weather_labels['desc'].config(text=f"Description: {desc}")
            
            feels_like = round(current_data['main']['feels_like'])
            self.weather_labels['feels_like'].config(text=f"Feels like: {feels_like}°C")
            
            humidity = current_data['main']['humidity']
            self.weather_labels['humidity'].config(text=f"Humidity: {humidity}%")
            
            pressure = current_data['main']['pressure']
            self.weather_labels['pressure'].config(text=f"Pressure: {pressure} hPa")
            
            wind_speed = current_data['wind']['speed']
            self.weather_labels['wind'].config(text=f"Wind: {wind_speed} m/s")
            
            visibility = current_data.get('visibility', 0) / 1000
            self.weather_labels['visibility'].config(text=f"Visibility: {visibility:.1f} km")
            
            # Update forecast
            self.update_forecast_display(forecast_data)
            
            # Update status
            self.status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self._show_error(f"Error updating display: {str(e)}")
        
        finally:
            self.search_button.config(state='normal')
    
    def update_forecast_display(self, forecast_data: Dict):
        """Update the forecast display"""
        # Clear existing forecast widgets
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        
        # Group forecast by day
        daily_forecasts = {}
        for item in forecast_data['list'][:40]:  # 5 days
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(item)
        
        # Display daily forecasts
        for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:5]):
            # Calculate daily min/max temperatures
            temps = [f['main']['temp'] for f in forecasts]
            min_temp = round(min(temps))
            max_temp = round(max(temps))
            
            # Get most common weather condition
            conditions = [f['weather'][0]['main'] for f in forecasts]
            most_common = max(set(conditions), key=conditions.count)
            
            # Create forecast frame
            day_frame = tk.Frame(self.forecast_frame, bg='#34495e')
            day_frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            # Configure grid weights
            self.forecast_frame.grid_columnconfigure(i, weight=1)
            
            # Day label
            day_name = date.strftime('%A') if date == datetime.now().date() else date.strftime('%a')
            day_label = tk.Label(
                day_frame, 
                text=day_name,
                font=("Arial", 10, "bold"),
                bg='#34495e',
                fg='#ecf0f1'
            )
            day_label.pack(pady=2)
            
            # Date label
            date_label = tk.Label(
                day_frame, 
                text=date.strftime('%m/%d'),
                font=("Arial", 9),
                bg='#34495e',
                fg='#bdc3c7'
            )
            date_label.pack()
            
            # Weather condition
            condition_label = tk.Label(
                day_frame, 
                text=most_common,
                font=("Arial", 9),
                bg='#34495e',
                fg='#ecf0f1'
            )
            condition_label.pack(pady=2)
            
            # Temperature range
            temp_label = tk.Label(
                day_frame, 
                text=f"{max_temp}°/{min_temp}°",
                font=("Arial", 10, "bold"),
                bg='#34495e',
                fg='#e74c3c'
            )
            temp_label.pack()
    
    def _show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
        self.search_button.config(state='normal')
    
    def refresh_weather(self):
        """Refresh current weather data"""
        city = self.city_entry.get().strip()
        if city:
            self.get_weather()
        else:
            messagebox.showwarning("Warning", "Please enter a city name first")
    
    def save_weather_data(self):
        """Save current weather data to file"""
        if not self.current_weather:
            messagebox.showwarning("Warning", "No weather data to save")
            return
        
        try:
            filename = f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            data_to_save = {
                "current_weather": self.current_weather,
                "forecast": self.forecast_data,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            messagebox.showinfo("Success", f"Weather data saved to {filename}")
            self.status_var.set(f"Data saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

def main():
    """Main function to run the weather app"""
    root = tk.Tk()
    app = WeatherApp(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Show instructions for API key
    messagebox.showinfo(
        "API Key Required", 
        "To use real weather data, please:\n"
        "1. Sign up at https://openweathermap.org/api\n"
        "2. Get your free API key\n"
        "3. Replace 'your_api_key_here' in the code\n\n"
        "For now, the app will show demo data."
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()
