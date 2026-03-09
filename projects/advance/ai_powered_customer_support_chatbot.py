"""
AI-powered Customer Support Chatbot

Features:
- NLP-based chatbot
- Intent recognition
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    import nltk
    from nltk.chat.util import Chat, reflections
except ImportError:
    nltk = None
    Chat = None
    reflections = None

class CustomerSupportChatbot:
    def __init__(self):
        self.pairs = [
            [r"(hi|hello|hey)", ["Hello! How can I help you today?"]],
            [r"(problem|issue)", ["Can you describe your problem in detail?"]],
            [r"(refund)", ["Refunds are processed within 5 business days."]],
            [r"(bye|exit)", ["Goodbye! Have a nice day."]],
        ]
        self.chat = Chat(self.pairs, reflections) if Chat else None
    def respond(self, text):
        if self.chat:
            return self.chat.respond(text)
        return "Chatbot library not available."

class CLI:
    @staticmethod
    def run():
        print("AI-powered Customer Support Chatbot")
        bot = CustomerSupportChatbot()
        while True:
            cmd = input('> ')
            if cmd == 'exit':
                print("Goodbye!")
                break
            response = bot.respond(cmd)
            print(response)

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
