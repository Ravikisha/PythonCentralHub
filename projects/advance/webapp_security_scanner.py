import requests

class WebAppSecurityScanner:
    def __init__(self):
        pass

    def scan(self, url):
        try:
            response = requests.get(url)
            print(f"Scanned {url}: Status {response.status_code}")
        except Exception as e:
            print(f"Error scanning {url}: {e}")

    def demo(self):
        self.scan('https://www.python.org')

if __name__ == "__main__":
    print("WebApp Security Scanner Demo")
    scanner = WebAppSecurityScanner()
    scanner.demo()
