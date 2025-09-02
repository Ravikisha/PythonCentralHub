# Advanced Web Scraping with BeautifulSoup

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import os
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging

class WebScraper:
    def __init__(self, base_url: str = "", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a web page and return BeautifulSoup object"""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def scrape_articles_from_website(self, base_url: str, max_pages: int = 5) -> List[Dict]:
        """Scrape articles from a news website"""
        articles = []
        
        # Example for scraping a blog/news site
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            soup = self.fetch_page(url)
            
            if not soup:
                continue
            
            # Find article containers (adjust selectors based on target site)
            article_containers = soup.find_all('article') or soup.find_all('div', class_=['post', 'article', 'entry'])
            
            for container in article_containers:
                article_data = self.extract_article_data(container, base_url)
                if article_data:
                    articles.append(article_data)
        
        return articles
    
    def extract_article_data(self, container, base_url: str) -> Optional[Dict]:
        """Extract article data from HTML container"""
        try:
            # Extract title
            title_elem = container.find('h1') or container.find('h2') or container.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Extract link
            link_elem = container.find('a')
            link = urljoin(base_url, link_elem.get('href')) if link_elem else ""
            
            # Extract excerpt/description
            desc_elem = container.find('p') or container.find('div', class_=['excerpt', 'summary'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract author
            author_elem = container.find('span', class_=['author', 'by']) or container.find('div', class_='author')
            author = author_elem.get_text(strip=True) if author_elem else "Unknown"
            
            # Extract date
            date_elem = container.find('time') or container.find('span', class_=['date', 'published'])
            date = date_elem.get_text(strip=True) if date_elem else ""
            
            # Extract tags/categories
            tag_container = container.find('div', class_=['tags', 'categories'])
            tags = []
            if tag_container:
                tag_links = tag_container.find_all('a')
                tags = [tag.get_text(strip=True) for tag in tag_links]
            
            return {
                'title': title,
                'link': link,
                'description': description[:200] + "..." if len(description) > 200 else description,
                'author': author,
                'date': date,
                'tags': tags
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting article data: {e}")
            return None
    
    def scrape_product_listings(self, base_url: str, max_pages: int = 3) -> List[Dict]:
        """Scrape product listings from an e-commerce site"""
        products = []
        
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            soup = self.fetch_page(url)
            
            if not soup:
                continue
            
            # Find product containers
            product_containers = soup.find_all('div', class_=['product', 'item', 'listing'])
            
            for container in product_containers:
                product_data = self.extract_product_data(container, base_url)
                if product_data:
                    products.append(product_data)
        
        return products
    
    def extract_product_data(self, container, base_url: str) -> Optional[Dict]:
        """Extract product data from HTML container"""
        try:
            # Extract product name
            name_elem = container.find('h2') or container.find('h3') or container.find('a')
            name = name_elem.get_text(strip=True) if name_elem else "No name"
            
            # Extract price
            price_elem = container.find('span', class_=['price', 'cost']) or container.find('div', class_='price')
            price = price_elem.get_text(strip=True) if price_elem else "No price"
            
            # Clean price (remove currency symbols, etc.)
            price_match = re.search(r'[\d,]+\.?\d*', price)
            clean_price = price_match.group() if price_match else "0"
            
            # Extract image URL
            img_elem = container.find('img')
            image_url = urljoin(base_url, img_elem.get('src')) if img_elem else ""
            
            # Extract product link
            link_elem = container.find('a')
            product_link = urljoin(base_url, link_elem.get('href')) if link_elem else ""
            
            # Extract rating
            rating_elem = container.find('div', class_=['rating', 'stars'])
            rating = rating_elem.get_text(strip=True) if rating_elem else "No rating"
            
            return {
                'name': name,
                'price': clean_price,
                'original_price': price,
                'image_url': image_url,
                'product_link': product_link,
                'rating': rating
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {e}")
            return None
    
    def scrape_social_media_posts(self, username: str, platform: str = "twitter") -> List[Dict]:
        """Scrape social media posts (demo - be mindful of ToS)"""
        posts = []
        
        # This is a simplified example - real implementation would need
        # proper authentication and API usage
        if platform.lower() == "twitter":
            # Example URL structure (adjust based on actual requirements)
            url = f"https://twitter.com/{username}"
            soup = self.fetch_page(url)
            
            if soup:
                # Find tweet containers (adjust selectors based on current Twitter structure)
                tweet_containers = soup.find_all('div', {'data-testid': 'tweet'})
                
                for container in tweet_containers:
                    post_data = self.extract_social_post_data(container)
                    if post_data:
                        posts.append(post_data)
        
        return posts
    
    def extract_social_post_data(self, container) -> Optional[Dict]:
        """Extract social media post data"""
        try:
            # Extract post text
            text_elem = container.find('div', {'data-testid': 'tweetText'})
            text = text_elem.get_text(strip=True) if text_elem else ""
            
            # Extract timestamp
            time_elem = container.find('time')
            timestamp = time_elem.get('datetime') if time_elem else ""
            
            # Extract engagement metrics
            likes_elem = container.find('div', {'data-testid': 'like'})
            likes = likes_elem.get_text(strip=True) if likes_elem else "0"
            
            retweets_elem = container.find('div', {'data-testid': 'retweet'})
            retweets = retweets_elem.get_text(strip=True) if retweets_elem else "0"
            
            return {
                'text': text,
                'timestamp': timestamp,
                'likes': likes,
                'retweets': retweets
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting social post data: {e}")
            return None
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Save scraped data to CSV file"""
        if not data:
            self.logger.warning("No data to save")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            self.logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
    
    def scrape_quotes(self) -> List[Dict]:
        """Scrape quotes from quotes.toscrape.com (practice site)"""
        base_url = "http://quotes.toscrape.com"
        quotes = []
        page = 1
        
        while True:
            url = f"{base_url}/page/{page}/"
            soup = self.fetch_page(url)
            
            if not soup:
                break
            
            quote_containers = soup.find_all('div', class_='quote')
            
            if not quote_containers:
                break
            
            for quote_div in quote_containers:
                try:
                    text = quote_div.find('span', class_='text').get_text()
                    author = quote_div.find('small', class_='author').get_text()
                    tags = [tag.get_text() for tag in quote_div.find_all('a', class_='tag')]
                    
                    quotes.append({
                        'text': text,
                        'author': author,
                        'tags': tags
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error extracting quote: {e}")
            
            page += 1
        
        return quotes
    
    def scrape_books_info(self) -> List[Dict]:
        """Scrape book information from books.toscrape.com (practice site)"""
        base_url = "http://books.toscrape.com"
        books = []
        page = 1
        
        while True:
            url = f"{base_url}/catalogue/page-{page}.html"
            soup = self.fetch_page(url)
            
            if not soup:
                break
            
            book_containers = soup.find_all('article', class_='product_pod')
            
            if not book_containers:
                break
            
            for book_article in book_containers:
                try:
                    title_elem = book_article.find('h3').find('a')
                    title = title_elem.get('title')
                    
                    price_elem = book_article.find('p', class_='price_color')
                    price = price_elem.get_text()
                    
                    availability_elem = book_article.find('p', class_='instock availability')
                    availability = availability_elem.get_text(strip=True)
                    
                    rating_elem = book_article.find('p', class_='star-rating')
                    rating = rating_elem.get('class')[1] if rating_elem else 'No rating'
                    
                    books.append({
                        'title': title,
                        'price': price,
                        'availability': availability,
                        'rating': rating
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error extracting book info: {e}")
            
            page += 1
            
            # Limit to prevent infinite loop
            if page > 50:
                break
        
        return books

def main():
    """Main function to demonstrate web scraping"""
    scraper = WebScraper(delay=1.0)
    
    while True:
        print("\n=== Advanced Web Scraper ===")
        print("1. Scrape quotes (practice site)")
        print("2. Scrape books (practice site)")
        print("3. Custom article scraping")
        print("4. Custom product scraping")
        print("5. View scraped data files")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                print("Scraping quotes from quotes.toscrape.com...")
                quotes = scraper.scrape_quotes()
                
                if quotes:
                    print(f"Scraped {len(quotes)} quotes!")
                    
                    # Show first few quotes
                    for i, quote in enumerate(quotes[:3], 1):
                        print(f"\nQuote {i}:")
                        print(f"Text: {quote['text'][:100]}...")
                        print(f"Author: {quote['author']}")
                        print(f"Tags: {', '.join(quote['tags'])}")
                    
                    # Save options
                    save_format = input("\nSave as (csv/json/both): ").strip().lower()
                    
                    if save_format in ['csv', 'both']:
                        scraper.save_to_csv(quotes, 'quotes.csv')
                    if save_format in ['json', 'both']:
                        scraper.save_to_json(quotes, 'quotes.json')
                else:
                    print("No quotes found!")
            
            elif choice == '2':
                print("Scraping books from books.toscrape.com...")
                books = scraper.scrape_books_info()
                
                if books:
                    print(f"Scraped {len(books)} books!")
                    
                    # Show first few books
                    for i, book in enumerate(books[:5], 1):
                        print(f"\nBook {i}:")
                        print(f"Title: {book['title'][:50]}...")
                        print(f"Price: {book['price']}")
                        print(f"Rating: {book['rating']}")
                        print(f"Availability: {book['availability']}")
                    
                    # Save options
                    save_format = input("\nSave as (csv/json/both): ").strip().lower()
                    
                    if save_format in ['csv', 'both']:
                        scraper.save_to_csv(books, 'books.csv')
                    if save_format in ['json', 'both']:
                        scraper.save_to_json(books, 'books.json')
                else:
                    print("No books found!")
            
            elif choice == '3':
                base_url = input("Enter base URL for article scraping: ").strip()
                if base_url:
                    max_pages = int(input("Enter max pages to scrape (default 3): ").strip() or "3")
                    
                    print(f"Scraping articles from {base_url}...")
                    articles = scraper.scrape_articles_from_website(base_url, max_pages)
                    
                    if articles:
                        print(f"Scraped {len(articles)} articles!")
                        
                        # Show first few articles
                        for i, article in enumerate(articles[:3], 1):
                            print(f"\nArticle {i}:")
                            print(f"Title: {article['title'][:50]}...")
                            print(f"Author: {article['author']}")
                            print(f"Date: {article['date']}")
                        
                        # Save options
                        save_format = input("\nSave as (csv/json/both): ").strip().lower()
                        
                        if save_format in ['csv', 'both']:
                            scraper.save_to_csv(articles, 'articles.csv')
                        if save_format in ['json', 'both']:
                            scraper.save_to_json(articles, 'articles.json')
                    else:
                        print("No articles found!")
            
            elif choice == '4':
                base_url = input("Enter base URL for product scraping: ").strip()
                if base_url:
                    max_pages = int(input("Enter max pages to scrape (default 3): ").strip() or "3")
                    
                    print(f"Scraping products from {base_url}...")
                    products = scraper.scrape_product_listings(base_url, max_pages)
                    
                    if products:
                        print(f"Scraped {len(products)} products!")
                        
                        # Show first few products
                        for i, product in enumerate(products[:3], 1):
                            print(f"\nProduct {i}:")
                            print(f"Name: {product['name'][:50]}...")
                            print(f"Price: {product['original_price']}")
                            print(f"Rating: {product['rating']}")
                        
                        # Save options
                        save_format = input("\nSave as (csv/json/both): ").strip().lower()
                        
                        if save_format in ['csv', 'both']:
                            scraper.save_to_csv(products, 'products.csv')
                        if save_format in ['json', 'both']:
                            scraper.save_to_json(products, 'products.json')
                    else:
                        print("No products found!")
            
            elif choice == '5':
                print("\nScraped data files:")
                data_files = ['quotes.csv', 'quotes.json', 'books.csv', 'books.json', 
                             'articles.csv', 'articles.json', 'products.csv', 'products.json']
                
                for filename in data_files:
                    if os.path.exists(filename):
                        size = os.path.getsize(filename)
                        print(f"  {filename} ({size} bytes)")
                    else:
                        print(f"  {filename} (not found)")
            
            elif choice == '0':
                print("Thank you for using the Advanced Web Scraper!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
