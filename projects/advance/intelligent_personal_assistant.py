import datetime
import webbrowser

class IntelligentPersonalAssistant:
    def __init__(self):
        pass

    def tell_time(self):
        now = datetime.datetime.now()
        print(f"Current time: {now.strftime('%H:%M:%S')}")

    def open_website(self, url):
        webbrowser.open(url)
        print(f"Opened website: {url}")

    def demo(self):
        self.tell_time()
        self.open_website('https://www.python.org')

if __name__ == "__main__":
    print("Intelligent Personal Assistant Demo")
    assistant = IntelligentPersonalAssistant()
    assistant.demo()
