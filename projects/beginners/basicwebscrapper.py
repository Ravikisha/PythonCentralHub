# Basic Web Scrapper

# Importing Libraries
import requests
from bs4 import BeautifulSoup

# URL
url = "https://webscraper.io/test-sites/e-commerce/allinone/phones/touch"

# Requesting the URL
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Finding the phones
phones = soup.find_all("div", class_="card-body")

# Creating a CSV file
open_file = open("phones.csv", "a")
headers = "Name, Price, Description, Reviews, Rating, Image\n"
open_file.write(headers)

# Looping through the phones
skipped = 0
for phone in phones:
    name = phone.find("a", class_="title")
    price = phone.find("h4", class_="price")
    description = phone.find("p", class_="description")
    reviews = phone.find("p", class_="float-end review-count")
    rating = phone.find("p", attrs={"data-rating": True})
    image_tag = phone.find("img", class_="img-responsive")
    image = image_tag["src"] if image_tag else ""

    # A site's markup is not an API. Any of these selectors can stop
    # matching without warning, and `None.text` is the AttributeError that
    # follows -- which is exactly how this file broke. Skipping the row and
    # counting it beats a traceback halfway through the file.
    if not all((name, price, description, reviews, rating)):
        skipped += 1
        continue
    
    # Writing to the CSV file
    open_file.write(f'{name.text}, {price.text}, {description.text}, {reviews.text}, {rating["data-rating"]}, {image}\n')
    print(f'Name: {name.text} \nPrice: {price.text} \nDescription: {description.text} \nReviews: {reviews.text} \nRating: {rating["data-rating"]} \nImage: {image} \n')

print(f"\nwrote {len(phones) - skipped} row(s); "
      f"skipped {skipped} whose markup did not match")
if not phones:
    print("no product cards found at all -- the page layout has changed, "
          "or the request was blocked")

# Closing the CSV file
open_file.close()   
    