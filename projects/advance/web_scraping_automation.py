import requests
from bs4 import BeautifulSoup

class WebScrapingAutomation:
    def __init__(self):
        pass

    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Title of {url}: {soup.title.string}")
        return soup.title.string

    def demo(self):
        self.scrape('https://www.python.org')

if __name__ == "__main__":
    print("Web Scraping Automation Demo")
    scraper = WebScrapingAutomation()
    scraper.demo()
