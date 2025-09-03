# Basic Web Crawler

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import csv
from collections import deque

class WebCrawler:
    def __init__(self, start_url, max_pages=10, delay=1):
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls = set()
        self.to_visit = deque([start_url])
        self.crawled_data = []
        
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    def get_page_content(self, url):
        """Fetch and parse page content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, html, base_url):
        """Extract all links from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if self.is_valid_url(full_url):
                links.append(full_url)
        
        return links
    
    def extract_page_data(self, html, url):
        """Extract useful data from the page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract headings
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            headings.append(heading.get_text().strip())
        
        # Extract text content (first 200 chars)
        text_content = soup.get_text()
        clean_text = ' '.join(text_content.split())[:200] + '...'
        
        return {
            'url': url,
            'title': title_text,
            'description': description,
            'headings': headings[:5],  # First 5 headings
            'content_preview': clean_text,
            'links_count': len(self.extract_links(html, url))
        }
    
    def crawl(self):
        """Main crawling function"""
        print(f"Starting crawl from: {self.start_url}")
        print(f"Max pages: {self.max_pages}")
        print("-" * 50)
        
        pages_crawled = 0
        
        while self.to_visit and pages_crawled < self.max_pages:
            current_url = self.to_visit.popleft()
            
            if current_url in self.visited_urls:
                continue
            
            print(f"Crawling: {current_url}")
            
            # Fetch page content
            html = self.get_page_content(current_url)
            if html is None:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Extract page data
            page_data = self.extract_page_data(html, current_url)
            self.crawled_data.append(page_data)
            
            print(f"  Title: {page_data['title']}")
            print(f"  Links found: {page_data['links_count']}")
            
            # Extract and queue new links
            links = self.extract_links(html, current_url)
            for link in links:
                if link not in self.visited_urls:
                    # Only crawl within the same domain
                    if urlparse(link).netloc == urlparse(self.start_url).netloc:
                        self.to_visit.append(link)
            
            pages_crawled += 1
            
            # Be respectful - add delay
            time.sleep(self.delay)
        
        print(f"\nCrawling completed! Visited {pages_crawled} pages.")
        return self.crawled_data
    
    def save_to_csv(self, filename="crawl_results.csv"):
        """Save crawled data to CSV file"""
        if not self.crawled_data:
            print("No data to save.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'description', 'headings', 'content_preview', 'links_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for data in self.crawled_data:
                # Convert headings list to string
                data_copy = data.copy()
                data_copy['headings'] = '; '.join(data['headings'])
                writer.writerow(data_copy)
        
        print(f"Results saved to {filename}")
    
    def print_summary(self):
        """Print crawling summary"""
        if not self.crawled_data:
            print("No data crawled.")
            return
        
        print(f"\nCRAWL SUMMARY")
        print("=" * 50)
        print(f"Total pages crawled: {len(self.crawled_data)}")
        print(f"Total unique URLs visited: {len(self.visited_urls)}")
        
        print(f"\nPages found:")
        for i, data in enumerate(self.crawled_data, 1):
            print(f"{i:2d}. {data['title'][:50]}...")
            print(f"     {data['url']}")

def main():
    # Example usage
    start_url = input("Enter the starting URL to crawl: ").strip()
    if not start_url:
        start_url = "https://example.com"
    
    try:
        max_pages = int(input("Enter maximum pages to crawl (default 5): ") or "5")
    except ValueError:
        max_pages = 5
    
    print(f"\nStarting web crawler...")
    crawler = WebCrawler(start_url, max_pages=max_pages, delay=1)
    
    try:
        crawled_data = crawler.crawl()
        crawler.print_summary()
        
        save_choice = input("\nSave results to CSV? (y/n): ").lower()
        if save_choice == 'y':
            crawler.save_to_csv()
    
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user.")
    except Exception as e:
        print(f"Error during crawling: {e}")

if __name__ == "__main__":
    main()
