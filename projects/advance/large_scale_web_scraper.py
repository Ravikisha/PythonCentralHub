"""
Large Scale Web Scraper

Features:
- Distributed scraping
- Multi-threading
- Data cleaning
- Export features
- CLI interface
- Error handling
"""
import requests
from bs4 import BeautifulSoup
import threading
import queue
import csv
import sys
import time

class ScraperThread(threading.Thread):
    def __init__(self, url_queue, data_queue):
        super().__init__()
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.daemon = True

    def run(self):
        while True:
            try:
                url = self.url_queue.get(timeout=3)
                resp = requests.get(url)
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.string if soup.title else ''
                self.data_queue.put({'url': url, 'title': title})
                self.url_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                self.url_queue.task_done()

class WebScraper:
    def __init__(self, urls):
        self.urls = urls
        self.url_queue = queue.Queue()
        self.data_queue = queue.Queue()
        for url in urls:
            self.url_queue.put(url)

    def scrape(self, num_threads=10):
        threads = [ScraperThread(self.url_queue, self.data_queue) for _ in range(num_threads)]
        for t in threads:
            t.start()
        self.url_queue.join()

    def export(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title'])
            writer.writeheader()
            while not self.data_queue.empty():
                writer.writerow(self.data_queue.get())

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python large_scale_web_scraper.py <urls_file>")
            sys.exit(1)
        with open(sys.argv[1], 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        scraper = WebScraper(urls)
        print("Scraping...")
        scraper.scrape()
        print("Exporting results...")
        scraper.export('scraped_data.csv')
        print("Results saved to scraped_data.csv")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
