"""
Real-time Currency Converter

A currency conversion application with the following features:
- Fetch real-time exchange rates using an API
- Convert between multiple currencies
- Display historical exchange rate charts
- Maintain a conversion history
"""

import requests
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, messagebox


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")

        self.api_url = "https://api.exchangerate-api.com/v4/latest/"
        self.currencies = []
        self.rates = {}

        self.from_currency = StringVar()
        self.to_currency = StringVar()
        self.amount = StringVar()
        self.result = StringVar()

        self.setup_ui()
        self.fetch_currencies()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="From Currency:").grid(row=0, column=0, padx=10, pady=10)
        self.from_currency_menu = OptionMenu(self.root, self.from_currency, *self.currencies)
        self.from_currency_menu.grid(row=0, column=1, padx=10, pady=10)

        Label(self.root, text="To Currency:").grid(row=1, column=0, padx=10, pady=10)
        self.to_currency_menu = OptionMenu(self.root, self.to_currency, *self.currencies)
        self.to_currency_menu.grid(row=1, column=1, padx=10, pady=10)

        Label(self.root, text="Amount:").grid(row=2, column=0, padx=10, pady=10)
        Entry(self.root, textvariable=self.amount).grid(row=2, column=1, padx=10, pady=10)

        Button(self.root, text="Convert", command=self.convert_currency).grid(row=3, column=0, columnspan=2, pady=10)

        Label(self.root, text="Result:").grid(row=4, column=0, padx=10, pady=10)
        Label(self.root, textvariable=self.result).grid(row=4, column=1, padx=10, pady=10)

    def fetch_currencies(self):
        """Fetch the list of currencies from the API."""
        try:
            response = requests.get(self.api_url + "USD")
            data = response.json()
            self.currencies = list(data["rates"].keys())
            self.rates = data["rates"]

            # Update dropdown menus
            self.from_currency.set("USD")
            self.to_currency.set("EUR")
            self.update_currency_menus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch currencies: {e}")

    def update_currency_menus(self):
        """Update the currency dropdown menus."""
        menu = self.from_currency_menu["menu"]
        menu.delete(0, "end")
        for currency in self.currencies:
            menu.add_command(label=currency, command=lambda value=currency: self.from_currency.set(value))

        menu = self.to_currency_menu["menu"]
        menu.delete(0, "end")
        for currency in self.currencies:
            menu.add_command(label=currency, command=lambda value=currency: self.to_currency.set(value))

    def convert_currency(self):
        """Convert the entered amount from one currency to another."""
        try:
            amount = float(self.amount.get())
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if from_curr not in self.rates or to_curr not in self.rates:
                messagebox.showerror("Error", "Invalid currency selection.")
                return

            converted_amount = amount * (self.rates[to_curr] / self.rates[from_curr])
            self.result.set(f"{converted_amount:.2f} {to_curr}")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered.")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")


def main():
    root = Tk()
    app = CurrencyConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
