# URL Status Checker

import requests
import time
import csv
from datetime import datetime
from urllib.parse import urlparse

class URLStatusChecker:
    def __init__(self):
        self.results = []
        self.timeout = 10
        
    def check_single_url(self, url):
        """Check the status of a single URL"""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'status': 'Online' if response.status_code < 400 else 'Error',
                'response_time': f"{response_time}ms",
                'final_url': response.url if response.url != url else 'No redirect',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': None
            }
            
        except requests.exceptions.Timeout:
            result = {
                'url': url,
                'status_code': 'Timeout',
                'status': 'Timeout',
                'response_time': f'>{self.timeout}s',
                'final_url': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': 'Request timeout'
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                'url': url,
                'status_code': 'Connection Error',
                'status': 'Offline',
                'response_time': 'N/A',
                'final_url': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': 'Connection failed'
            }
            
        except requests.exceptions.RequestException as e:
            result = {
                'url': url,
                'status_code': 'Error',
                'status': 'Error',
                'response_time': 'N/A',
                'final_url': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }
        
        self.results.append(result)
        return result
    
    def check_multiple_urls(self, urls):
        """Check status of multiple URLs"""
        print(f"Checking {len(urls)} URLs...")
        print("-" * 80)
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Checking: {url}")
            result = self.check_single_url(url)
            
            # Display result
            status_color = "✅" if result['status'] == 'Online' else "❌"
            print(f"    {status_color} {result['status']} | {result['status_code']} | {result['response_time']}")
            
            if result['final_url'] != 'No redirect' and result['final_url'] != 'N/A':
                print(f"    🔄 Redirected to: {result['final_url']}")
            
            if result['error']:
                print(f"    ⚠️  Error: {result['error']}")
            
            print()
        
        return self.results
    
    def load_urls_from_file(self, filename):
        """Load URLs from a text file"""
        try:
            with open(filename, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            return urls
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            return []
    
    def save_results_to_csv(self, filename="url_status_results.csv"):
        """Save results to CSV file"""
        if not self.results:
            print("No results to save.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'status_code', 'status', 'response_time', 'final_url', 'timestamp', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        print(f"Results saved to {filename}")
    
    def generate_summary(self):
        """Generate and display summary statistics"""
        if not self.results:
            print("No results to summarize.")
            return
        
        total_urls = len(self.results)
        online_count = sum(1 for r in self.results if r['status'] == 'Online')
        offline_count = sum(1 for r in self.results if r['status'] == 'Offline')
        error_count = sum(1 for r in self.results if r['status'] == 'Error')
        timeout_count = sum(1 for r in self.results if r['status'] == 'Timeout')
        
        print("\n" + "="*50)
        print("URL STATUS CHECK SUMMARY")
        print("="*50)
        print(f"Total URLs checked: {total_urls}")
        print(f"✅ Online: {online_count} ({online_count/total_urls*100:.1f}%)")
        print(f"❌ Offline: {offline_count} ({offline_count/total_urls*100:.1f}%)")
        print(f"⚠️  Errors: {error_count} ({error_count/total_urls*100:.1f}%)")
        print(f"⏱️  Timeouts: {timeout_count} ({timeout_count/total_urls*100:.1f}%)")
        
        # Show problematic URLs
        problems = [r for r in self.results if r['status'] != 'Online']
        if problems:
            print(f"\nProblematic URLs ({len(problems)}):")
            for result in problems:
                print(f"  {result['url']} - {result['status']} ({result['status_code']})")

def main():
    """Main function to run the URL status checker"""
    checker = URLStatusChecker()
    
    while True:
        print("\n" + "="*50)
        print("URL STATUS CHECKER")
        print("="*50)
        print("1. Check single URL")
        print("2. Check multiple URLs (manual entry)")
        print("3. Check URLs from file")
        print("4. View last results summary")
        print("5. Save results to CSV")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            url = input("Enter URL to check: ").strip()
            if url:
                print(f"\nChecking: {url}")
                result = checker.check_single_url(url)
                
                print(f"\nResults:")
                print(f"URL: {result['url']}")
                print(f"Status: {result['status']} ({result['status_code']})")
                print(f"Response Time: {result['response_time']}")
                if result['final_url'] != 'No redirect' and result['final_url'] != 'N/A':
                    print(f"Redirected to: {result['final_url']}")
                if result['error']:
                    print(f"Error: {result['error']}")
        
        elif choice == '2':
            urls = []
            print("Enter URLs (one per line, empty line to finish):")
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                checker.check_multiple_urls(urls)
                checker.generate_summary()
        
        elif choice == '3':
            filename = input("Enter filename (default: urls.txt): ").strip()
            if not filename:
                filename = "urls.txt"
            
            urls = checker.load_urls_from_file(filename)
            if urls:
                checker.check_multiple_urls(urls)
                checker.generate_summary()
        
        elif choice == '4':
            checker.generate_summary()
        
        elif choice == '5':
            filename = input("Enter CSV filename (default: url_status_results.csv): ").strip()
            if not filename:
                filename = "url_status_results.csv"
            checker.save_results_to_csv(filename)
        
        elif choice == '6':
            print("Thank you for using URL Status Checker!")
            break
        
        else:
            print("Invalid choice! Please select 1-6.")

if __name__ == "__main__":
    main()
