# URL Shorter

import pyshorteners # pip install pyshorteners



url = input("Enter URL: ")
# TinyURL
shortener = pyshorteners.Shortener()
shortURL = shortener.tinyurl.short(url)

# Bitly
# bitlyShortener = pyshorteners.Shortener(api_key='01b6c587cskek4kdfijsjce4cf27ce2') # Change API Key with your own API Key
# shortURL = bitlyShortener.bitly.short(url) # bitly
print("Short URL: ", shortURL)