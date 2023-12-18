# Currency Converter

# Importing the required modules
import requests
from bs4 import BeautifulSoup

# URL
url = "https://www.x-rates.com/calculator/?from=%s&to=%s&amount=%s"

# Getting the user input
print("Currency Converter")
print('''
      List of Currencies:
        1. USD - US Dollar
        2. EUR - Euro
        3. GBP - British Pound
        4. INR - Indian Rupee
        5. AUD - Australian Dollar
        6. CAD - Canadian Dollar
        7. SGD - Singapore Dollar
        8. CHF - Swiss Franc
        9. MYR - Malaysian Ringgit
        10. JPY - Japanese Yen
        11. CNY - Chinese Yuan Renminbi
        12. NZD - New Zealand Dollar
        13. THB - Thai Baht
        14. HUF - Hungarian Forint
        15. AED - Emirati Dirham
        16. HKD - Hong Kong Dollar
        17. MXN - Mexican Peso
        18. ZAR - South African Rand
        19. PHP - Philippine Peso
        20. SEK - Swedish Krona
        
        Don't Enter the Number. Enter the currency code.
    ''')
from_currency = input("From Currency: ").upper()
to_currency = input("To Currency: ").upper()
amount = input("Amount: ")

# Requesting the URL
response = requests.get(url % (from_currency, to_currency, amount))
soup = BeautifulSoup(response.text, "html.parser")

# Finding the converted amount
converted_amount = soup.find("span", class_="ccOutputRslt").text

# Printing the converted amount
print(f'{amount} {from_currency} = {converted_amount}')