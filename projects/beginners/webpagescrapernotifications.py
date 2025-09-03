# Web Page Scraper with Notifications

import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import hashlib

class WebPageMonitor:
    def __init__(self, url, email_config=None):
        self.url = url
        self.email_config = email_config
        self.previous_content = None
        
    def get_page_content(self):
        """Fetch and parse web page content"""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content (you can modify this to target specific elements)
            content = soup.get_text().strip()
            return content
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def get_content_hash(self, content):
        """Generate hash of content for comparison"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def send_notification_email(self, subject, message):
        """Send email notification when changes are detected"""
        if not self.email_config:
            print("Email configuration not provided")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], self.email_config['to_email'], text)
            server.quit()
            
            print("Notification email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def send_desktop_notification(self, title, message):
        """Send desktop notification (cross-platform)"""
        try:
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                timeout=10
            )
        except ImportError:
            print("Desktop notifications require 'plyer' package")
            print(f"Notification: {title} - {message}")
    
    def check_for_changes(self):
        """Check if page content has changed"""
        print(f"Checking {self.url} for changes...")
        
        current_content = self.get_page_content()
        if current_content is None:
            return
        
        current_hash = self.get_content_hash(current_content)
        
        if self.previous_content is None:
            self.previous_content = current_hash
            print("Initial content captured. Monitoring for changes...")
            return
        
        if current_hash != self.previous_content:
            print("Content change detected!")
            
            # Send notifications
            subject = f"Web Page Change Detected: {self.url}"
            message = f"The webpage {self.url} has been updated!\n\nCheck it out: {self.url}"
            
            self.send_desktop_notification("Page Updated!", f"Changes detected on {self.url}")
            
            if self.email_config:
                self.send_notification_email(subject, message)
            
            self.previous_content = current_hash
        else:
            print("No changes detected.")
    
    def start_monitoring(self, interval_minutes=30):
        """Start monitoring the webpage at specified intervals"""
        print(f"Starting to monitor {self.url} every {interval_minutes} minutes...")
        
        # Schedule the check
        schedule.every(interval_minutes).minutes.do(self.check_for_changes)
        
        # Initial check
        self.check_for_changes()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    # Example usage
    url_to_monitor = "https://example.com"
    
    # Optional email configuration
    email_config = {
        'from_email': 'your_email@gmail.com',
        'to_email': 'recipient@gmail.com',
        'password': 'your_app_password',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587
    }
    
    # Create monitor instance (set email_config to None to disable email notifications)
    monitor = WebPageMonitor(url_to_monitor, email_config=None)
    
    # Start monitoring (checks every 30 minutes)
    try:
        monitor.start_monitoring(interval_minutes=1)  # Check every minute for demo
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()
