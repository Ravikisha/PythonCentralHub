import re

class RealTimeTextExtraction:
    def __init__(self):
        pass

    def extract_emails(self, text):
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        print(f"Extracted emails: {emails}")
        return emails

    def demo(self):
        text = "Contact us at info@example.com or support@domain.com."
        self.extract_emails(text)

if __name__ == "__main__":
    print("Real-Time Text Extraction Demo")
    extractor = RealTimeTextExtraction()
    extractor.demo()
