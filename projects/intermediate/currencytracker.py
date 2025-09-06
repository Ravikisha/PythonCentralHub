#!/usr/bin/env python3
"""
Currency Exchange Rate Tracker
A comprehensive application for tracking real-time currency exchange rates.

Features:
- Real-time exchange rates from API
- Multiple currency pairs
- Historical data and trends
- Rate alerts and notifications
- Conversion calculator
- Data visualization with charts
- Currency favorites
- Offline mode with cached data

Requirements:
- requests
- tkinter (built-in)
- matplotlib
- json (built-in)
- datetime (built-in)

Author: Python Central Hub
Date: 2025-09-06
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json
import datetime
import threading
import time
from pathlib import Path
import os

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib not available. Chart features will be disabled.")


class CurrencyTracker:
    """Main currency exchange rate tracker application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Currency Exchange Rate Tracker")
        self.root.geometry("1000x700")
        
        # API configuration
        self.api_key = "demo"  # Use demo key or get free key from exchangerate-api.com
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        
        # Data storage
        self.rates_data = {}
        self.historical_data = {}
        self.favorites = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        self.alerts = []
        self.auto_refresh = True
        self.refresh_interval = 300  # 5 minutes
        
        # Data file for offline mode
        self.data_file = Path("currency_data.json")
        self.load_cached_data()
        
        # Setup GUI
        self.setup_gui()
        self.load_initial_data()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_rates_tab()
        self.create_converter_tab()
        self.create_charts_tab()
        self.create_alerts_tab()
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_rates_tab(self):
        """Create the exchange rates display tab."""
        self.rates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rates_frame, text="📈 Exchange Rates")
        
        # Control frame
        control_frame = ttk.Frame(self.rates_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Base currency selection
        ttk.Label(control_frame, text="Base Currency:").pack(side=tk.LEFT, padx=5)
        self.base_currency_var = tk.StringVar(value="USD")
        self.base_currency_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.base_currency_var,
            values=self.get_currency_list(),
            state="readonly",
            width=10
        )
        self.base_currency_combo.pack(side=tk.LEFT, padx=5)
        self.base_currency_combo.bind('<<ComboboxSelected>>', self.on_base_currency_change)
        
        # Refresh button
        ttk.Button(
            control_frame, text="🔄 Refresh", 
            command=self.refresh_rates
        ).pack(side=tk.LEFT, padx=10)
        
        # Add to favorites button
        ttk.Button(
            control_frame, text="⭐ Add Favorite", 
            command=self.add_favorite
        ).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=15)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace('w', self.filter_rates)
        
        # Rates display frame
        rates_display_frame = ttk.LabelFrame(self.rates_frame, text="Current Exchange Rates")
        rates_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for rates
        columns = ("Currency", "Rate", "Change", "Last Updated")
        self.rates_tree = ttk.Treeview(rates_display_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.rates_tree.heading("Currency", text="Currency")
        self.rates_tree.heading("Rate", text="Exchange Rate")
        self.rates_tree.heading("Change", text="24h Change")
        self.rates_tree.heading("Last Updated", text="Last Updated")
        
        self.rates_tree.column("Currency", width=100)
        self.rates_tree.column("Rate", width=150)
        self.rates_tree.column("Change", width=100)
        self.rates_tree.column("Last Updated", width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(rates_display_frame, orient=tk.VERTICAL, command=self.rates_tree.yview)
        self.rates_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.rates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu for rates tree
        self.rates_tree.bind("<Button-3>", self.show_rates_context_menu)
    
    def create_converter_tab(self):
        """Create the currency converter tab."""
        self.converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_frame, text="💱 Converter")
        
        # Main converter frame
        main_frame = ttk.LabelFrame(self.converter_frame, text="Currency Converter")
        main_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # From currency
        from_frame = ttk.Frame(main_frame)
        from_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(from_frame, text="From:").pack(side=tk.LEFT)
        self.from_currency_var = tk.StringVar(value="USD")
        self.from_currency_combo = ttk.Combobox(
            from_frame,
            textvariable=self.from_currency_var,
            values=self.get_currency_list(),
            state="readonly",
            width=15
        )
        self.from_currency_combo.pack(side=tk.LEFT, padx=10)
        
        self.amount_var = tk.StringVar(value="1.00")
        self.amount_entry = ttk.Entry(from_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.pack(side=tk.LEFT, padx=10)
        self.amount_var.trace('w', self.on_amount_change)
        
        # To currency
        to_frame = ttk.Frame(main_frame)
        to_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(to_frame, text="To:").pack(side=tk.LEFT)
        self.to_currency_var = tk.StringVar(value="EUR")
        self.to_currency_combo = ttk.Combobox(
            to_frame,
            textvariable=self.to_currency_var,
            values=self.get_currency_list(),
            state="readonly",
            width=15
        )
        self.to_currency_combo.pack(side=tk.LEFT, padx=10)
        
        self.result_var = tk.StringVar(value="0.00")
        self.result_entry = ttk.Entry(to_frame, textvariable=self.result_var, width=15, state="readonly")
        self.result_entry.pack(side=tk.LEFT, padx=10)
        
        # Convert button
        ttk.Button(
            main_frame, text="🔄 Convert", 
            command=self.convert_currency
        ).pack(pady=10)
        
        # Bind currency selection changes
        self.from_currency_combo.bind('<<ComboboxSelected>>', self.convert_currency)
        self.to_currency_combo.bind('<<ComboboxSelected>>', self.convert_currency)
        
        # Conversion history
        history_frame = ttk.LabelFrame(self.converter_frame, text="Conversion History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # History listbox
        self.history_listbox = tk.Listbox(history_frame, height=10)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear history button
        ttk.Button(
            history_frame, text="Clear History", 
            command=self.clear_conversion_history
        ).pack(pady=5)
    
    def create_charts_tab(self):
        """Create the charts and trends tab."""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="📊 Charts")
        
        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(
                self.charts_frame,
                text="Charts feature requires matplotlib.\nInstall with: pip install matplotlib",
                font=("Arial", 12),
                justify=tk.CENTER
            ).pack(expand=True)
            return
        
        # Chart controls
        control_frame = ttk.Frame(self.charts_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Currency Pair:").pack(side=tk.LEFT, padx=5)
        self.chart_currency_var = tk.StringVar(value="EUR")
        self.chart_currency_combo = ttk.Combobox(
            control_frame,
            textvariable=self.chart_currency_var,
            values=self.get_currency_list(),
            state="readonly",
            width=10
        )
        self.chart_currency_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame, text="📊 Update Chart", 
            command=self.update_chart
        ).pack(side=tk.LEFT, padx=10)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize chart
        self.setup_chart()
    
    def create_alerts_tab(self):
        """Create the rate alerts tab."""
        self.alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alerts_frame, text="🔔 Alerts")
        
        # Add alert frame
        add_frame = ttk.LabelFrame(self.alerts_frame, text="Add Rate Alert")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Alert form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(padx=10, pady=10)
        
        ttk.Label(form_frame, text="Currency:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.alert_currency_var = tk.StringVar(value="EUR")
        alert_currency_combo = ttk.Combobox(
            form_frame,
            textvariable=self.alert_currency_var,
            values=self.get_currency_list(),
            state="readonly",
            width=10
        )
        alert_currency_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Condition:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.alert_condition_var = tk.StringVar(value="Above")
        alert_condition_combo = ttk.Combobox(
            form_frame,
            textvariable=self.alert_condition_var,
            values=["Above", "Below"],
            state="readonly",
            width=10
        )
        alert_condition_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Rate:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.alert_rate_var = tk.StringVar()
        alert_rate_entry = ttk.Entry(form_frame, textvariable=self.alert_rate_var, width=15)
        alert_rate_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(
            form_frame, text="Add Alert", 
            command=self.add_alert
        ).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Alerts list
        alerts_list_frame = ttk.LabelFrame(self.alerts_frame, text="Active Alerts")
        alerts_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Alerts treeview
        alert_columns = ("Currency", "Condition", "Target Rate", "Current Rate", "Status")
        self.alerts_tree = ttk.Treeview(alerts_list_frame, columns=alert_columns, show="headings", height=10)
        
        for col in alert_columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=120)
        
        self.alerts_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Remove alert button
        ttk.Button(
            alerts_list_frame, text="Remove Selected Alert", 
            command=self.remove_alert
        ).pack(pady=5)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        
        # Auto-refresh settings
        refresh_frame = ttk.LabelFrame(self.settings_frame, text="Auto-Refresh Settings")
        refresh_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        ttk.Checkbutton(
            refresh_frame, 
            text="Enable auto-refresh",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        interval_frame = ttk.Frame(refresh_frame)
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interval_frame, text="Refresh interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=str(self.refresh_interval))
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            interval_frame, text="Apply", 
            command=self.apply_refresh_interval
        ).pack(side=tk.LEFT, padx=10)
        
        # Favorites management
        favorites_frame = ttk.LabelFrame(self.settings_frame, text="Favorite Currencies")
        favorites_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.favorites_listbox = tk.Listbox(favorites_frame, height=8)
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fav_buttons_frame = ttk.Frame(favorites_frame)
        fav_buttons_frame.pack(pady=5)
        
        ttk.Button(
            fav_buttons_frame, text="Remove Selected", 
            command=self.remove_favorite
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            fav_buttons_frame, text="Clear All", 
            command=self.clear_favorites
        ).pack(side=tk.LEFT, padx=5)
        
        # Update favorites display
        self.update_favorites_display()
        
        # Data management
        data_frame = ttk.LabelFrame(self.settings_frame, text="Data Management")
        data_frame.pack(fill=tk.X, padx=20, pady=20)
        
        data_buttons_frame = ttk.Frame(data_frame)
        data_buttons_frame.pack(pady=10)
        
        ttk.Button(
            data_buttons_frame, text="Export Data", 
            command=self.export_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            data_buttons_frame, text="Clear Cache", 
            command=self.clear_cache
        ).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        """Create status bar at bottom of window."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.last_update_label = ttk.Label(self.status_frame, text="Last update: Never", relief=tk.SUNKEN)
        self.last_update_label.pack(side=tk.RIGHT)
    
    def get_currency_list(self):
        """Get list of available currencies."""
        default_currencies = [
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD',
            'MXN', 'SGD', 'HKD', 'NOK', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR', 'KRW'
        ]
        
        if self.rates_data:
            return sorted(list(self.rates_data.keys()))
        return default_currencies
    
    def load_cached_data(self):
        """Load cached data from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.rates_data = data.get('rates', {})
                    self.historical_data = data.get('historical', {})
                    self.favorites = data.get('favorites', self.favorites)
                    self.alerts = data.get('alerts', [])
        except Exception as e:
            print(f"Error loading cached data: {e}")
    
    def save_cached_data(self):
        """Save data to cache file."""
        try:
            data = {
                'rates': self.rates_data,
                'historical': self.historical_data,
                'favorites': self.favorites,
                'alerts': self.alerts,
                'last_update': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cached data: {e}")
    
    def load_initial_data(self):
        """Load initial exchange rate data."""
        self.update_status("Loading exchange rates...")
        
        def load_data():
            self.fetch_exchange_rates()
            self.root.after(0, self.update_rates_display)
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def fetch_exchange_rates(self):
        """Fetch current exchange rates from API."""
        try:
            base = self.base_currency_var.get()
            url = f"{self.base_url}/{base}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.rates_data = data.get('rates', {})
            
            # Store historical data point
            timestamp = datetime.datetime.now().isoformat()
            if base not in self.historical_data:
                self.historical_data[base] = {}
            
            for currency, rate in self.rates_data.items():
                if currency not in self.historical_data[base]:
                    self.historical_data[base][currency] = []
                
                # Keep only last 30 data points
                if len(self.historical_data[base][currency]) >= 30:
                    self.historical_data[base][currency].pop(0)
                
                self.historical_data[base][currency].append({
                    'timestamp': timestamp,
                    'rate': rate
                })
            
            self.save_cached_data()
            self.update_status("Exchange rates updated successfully")
            self.last_update_label.config(text=f"Last update: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except requests.RequestException as e:
            self.update_status(f"Network error: {e}")
            if not self.rates_data:
                messagebox.showerror("Error", "Failed to load exchange rates and no cached data available.")
        except Exception as e:
            self.update_status(f"Error: {e}")
    
    def update_rates_display(self):
        """Update the rates display in the treeview."""
        # Clear existing items
        for item in self.rates_tree.get_children():
            self.rates_tree.delete(item)
        
        # Filter rates based on search
        search_term = self.search_var.get().upper()
        
        # Sort currencies - favorites first, then alphabetically
        currencies = list(self.rates_data.keys())
        favorites_sorted = [c for c in self.favorites if c in currencies]
        others_sorted = sorted([c for c in currencies if c not in self.favorites])
        
        for currency in favorites_sorted + others_sorted:
            if search_term and search_term not in currency:
                continue
            
            rate = self.rates_data[currency]
            
            # Calculate 24h change (simplified - using last 2 data points)
            change = "N/A"
            base = self.base_currency_var.get()
            if (base in self.historical_data and 
                currency in self.historical_data[base] and 
                len(self.historical_data[base][currency]) >= 2):
                
                current_rate = self.historical_data[base][currency][-1]['rate']
                previous_rate = self.historical_data[base][currency][-2]['rate']
                change_pct = ((current_rate - previous_rate) / previous_rate) * 100
                change = f"{change_pct:+.2f}%"
            
            # Color coding for favorites
            tags = ()
            if currency in self.favorites:
                tags = ('favorite',)
            
            self.rates_tree.insert(
                '', tk.END,
                values=(currency, f"{rate:.6f}", change, datetime.datetime.now().strftime('%H:%M:%S')),
                tags=tags
            )
        
        # Configure tag colors
        self.rates_tree.tag_configure('favorite', background='#E8F4FD')
        
        # Update converter currency lists
        currencies = self.get_currency_list()
        self.from_currency_combo['values'] = currencies
        self.to_currency_combo['values'] = currencies
        self.chart_currency_combo['values'] = currencies
        
        # Check alerts
        self.check_alerts()
    
    def refresh_rates(self):
        """Manually refresh exchange rates."""
        def refresh():
            self.fetch_exchange_rates()
            self.root.after(0, self.update_rates_display)
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def on_base_currency_change(self, event=None):
        """Handle base currency change."""
        self.refresh_rates()
    
    def filter_rates(self, *args):
        """Filter rates based on search term."""
        self.update_rates_display()
    
    def add_favorite(self):
        """Add selected currency to favorites."""
        selection = self.rates_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a currency first.")
            return
        
        item = self.rates_tree.item(selection[0])
        currency = item['values'][0]
        
        if currency not in self.favorites:
            self.favorites.append(currency)
            self.update_favorites_display()
            self.update_rates_display()
            self.save_cached_data()
    
    def remove_favorite(self):
        """Remove selected favorite currency."""
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a favorite to remove.")
            return
        
        currency = self.favorites_listbox.get(selection[0])
        self.favorites.remove(currency)
        self.update_favorites_display()
        self.update_rates_display()
        self.save_cached_data()
    
    def clear_favorites(self):
        """Clear all favorite currencies."""
        if messagebox.askyesno("Confirm", "Clear all favorite currencies?"):
            self.favorites.clear()
            self.update_favorites_display()
            self.update_rates_display()
            self.save_cached_data()
    
    def update_favorites_display(self):
        """Update the favorites listbox."""
        self.favorites_listbox.delete(0, tk.END)
        for currency in self.favorites:
            self.favorites_listbox.insert(tk.END, currency)
    
    def convert_currency(self, event=None):
        """Convert currency amounts."""
        try:
            amount = float(self.amount_var.get())
            from_currency = self.from_currency_var.get()
            to_currency = self.to_currency_var.get()
            
            if from_currency == to_currency:
                result = amount
            else:
                # Get rates for conversion
                base = self.base_currency_var.get()
                
                if from_currency == base:
                    from_rate = 1.0
                else:
                    from_rate = self.rates_data.get(from_currency, 1.0)
                
                if to_currency == base:
                    to_rate = 1.0
                else:
                    to_rate = self.rates_data.get(to_currency, 1.0)
                
                # Convert: amount -> base -> target
                result = (amount / from_rate) * to_rate
            
            self.result_var.set(f"{result:.6f}")
            
            # Add to conversion history
            history_entry = f"{amount:.2f} {from_currency} = {result:.6f} {to_currency} ({datetime.datetime.now().strftime('%H:%M:%S')})"
            self.history_listbox.insert(0, history_entry)
            
            # Keep only last 20 entries
            if self.history_listbox.size() > 20:
                self.history_listbox.delete(tk.END)
            
        except ValueError:
            self.result_var.set("Invalid amount")
        except Exception as e:
            self.result_var.set("Error")
            self.update_status(f"Conversion error: {e}")
    
    def on_amount_change(self, *args):
        """Handle amount change in converter."""
        self.convert_currency()
    
    def clear_conversion_history(self):
        """Clear conversion history."""
        self.history_listbox.delete(0, tk.END)
    
    def setup_chart(self):
        """Setup the matplotlib chart."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.figure = Figure(figsize=(10, 6), dpi=80)
        self.chart_subplot = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty chart
        self.chart_subplot.set_title("Exchange Rate Trends")
        self.chart_subplot.set_xlabel("Time")
        self.chart_subplot.set_ylabel("Exchange Rate")
        self.canvas.draw()
    
    def update_chart(self):
        """Update the exchange rate chart."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        currency = self.chart_currency_var.get()
        base = self.base_currency_var.get()
        
        if (base not in self.historical_data or 
            currency not in self.historical_data[base] or
            len(self.historical_data[base][currency]) < 2):
            messagebox.showinfo("Info", "Not enough historical data for chart.")
            return
        
        # Get historical data
        data_points = self.historical_data[base][currency]
        timestamps = [datetime.datetime.fromisoformat(point['timestamp']) for point in data_points]
        rates = [point['rate'] for point in data_points]
        
        # Clear and update chart
        self.chart_subplot.clear()
        self.chart_subplot.plot(timestamps, rates, marker='o', linewidth=2, markersize=4)
        self.chart_subplot.set_title(f"{base}/{currency} Exchange Rate Trend")
        self.chart_subplot.set_xlabel("Time")
        self.chart_subplot.set_ylabel("Exchange Rate")
        self.chart_subplot.grid(True, alpha=0.3)
        
        # Format x-axis
        self.figure.autofmt_xdate()
        
        self.canvas.draw()
    
    def add_alert(self):
        """Add a new rate alert."""
        try:
            currency = self.alert_currency_var.get()
            condition = self.alert_condition_var.get()
            target_rate = float(self.alert_rate_var.get())
            
            alert = {
                'currency': currency,
                'condition': condition,
                'target_rate': target_rate,
                'created': datetime.datetime.now().isoformat(),
                'triggered': False
            }
            
            self.alerts.append(alert)
            self.update_alerts_display()
            self.save_cached_data()
            
            # Clear form
            self.alert_rate_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rate.")
    
    def remove_alert(self):
        """Remove selected alert."""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alert to remove.")
            return
        
        item = self.alerts_tree.item(selection[0])
        currency = item['values'][0]
        condition = item['values'][1]
        target_rate = float(item['values'][2])
        
        # Find and remove alert
        for i, alert in enumerate(self.alerts):
            if (alert['currency'] == currency and 
                alert['condition'] == condition and 
                alert['target_rate'] == target_rate):
                del self.alerts[i]
                break
        
        self.update_alerts_display()
        self.save_cached_data()
    
    def update_alerts_display(self):
        """Update alerts display."""
        # Clear existing items
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        # Add alerts
        for alert in self.alerts:
            currency = alert['currency']
            current_rate = self.rates_data.get(currency, "N/A")
            status = "Triggered" if alert['triggered'] else "Active"
            
            self.alerts_tree.insert(
                '', tk.END,
                values=(
                    currency,
                    alert['condition'],
                    f"{alert['target_rate']:.6f}",
                    f"{current_rate:.6f}" if isinstance(current_rate, (int, float)) else current_rate,
                    status
                )
            )
    
    def check_alerts(self):
        """Check if any alerts should be triggered."""
        for alert in self.alerts:
            if alert['triggered']:
                continue
            
            currency = alert['currency']
            current_rate = self.rates_data.get(currency)
            
            if current_rate is None:
                continue
            
            triggered = False
            if alert['condition'] == "Above" and current_rate > alert['target_rate']:
                triggered = True
            elif alert['condition'] == "Below" and current_rate < alert['target_rate']:
                triggered = True
            
            if triggered:
                alert['triggered'] = True
                self.show_alert_notification(alert, current_rate)
        
        self.update_alerts_display()
    
    def show_alert_notification(self, alert, current_rate):
        """Show alert notification."""
        message = (
            f"Rate Alert Triggered!\n\n"
            f"Currency: {alert['currency']}\n"
            f"Condition: {alert['condition']} {alert['target_rate']:.6f}\n"
            f"Current Rate: {current_rate:.6f}"
        )
        messagebox.showinfo("Rate Alert", message)
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        if self.auto_refresh:
            self.refresh_rates()
            self.root.after(self.refresh_interval * 1000, self.start_auto_refresh)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
    
    def apply_refresh_interval(self):
        """Apply new refresh interval."""
        try:
            self.refresh_interval = int(self.interval_var.get())
            self.update_status(f"Refresh interval set to {self.refresh_interval} seconds")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for refresh interval.")
    
    def show_rates_context_menu(self, event):
        """Show context menu for rates tree."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Add to Favorites", command=self.add_favorite)
        context_menu.add_command(label="Set Alert", command=self.set_alert_for_currency)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def set_alert_for_currency(self):
        """Set alert for selected currency."""
        selection = self.rates_tree.selection()
        if not selection:
            return
        
        item = self.rates_tree.item(selection[0])
        currency = item['values'][0]
        
        # Switch to alerts tab and set currency
        self.notebook.select(3)  # Alerts tab
        self.alert_currency_var.set(currency)
    
    def export_data(self):
        """Export data to JSON file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'rates': self.rates_data,
                    'historical': self.historical_data,
                    'favorites': self.favorites,
                    'alerts': self.alerts,
                    'export_date': datetime.datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def clear_cache(self):
        """Clear cached data."""
        if messagebox.askyesno("Confirm", "Clear all cached data?"):
            self.rates_data.clear()
            self.historical_data.clear()
            
            if self.data_file.exists():
                self.data_file.unlink()
            
            self.update_rates_display()
            self.update_status("Cache cleared")
    
    def update_status(self, message):
        """Update status bar message."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main function to run the currency tracker."""
    app = CurrencyTracker()
    app.run()


if __name__ == "__main__":
    main()
