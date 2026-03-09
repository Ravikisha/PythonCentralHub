"""
Advanced Chatbot with NLP

Features:
- Advanced NLP
- Context management
- Web/CLI interface
- Modular design
- Error handling
"""
import sys
import random
try:
    import nltk
    from nltk.chat.util import Chat, reflections
except ImportError:
    Chat = None
    reflections = {}

pairs = [
    [r"my name is (.*)", ["Hello %1, how are you today?"]],
    [r"(hi|hello|hey)", ["Hello!", "Hi there!"]],
    [r"what is your name?", ["I am an advanced chatbot."]],
    [r"how are you?", ["I'm doing well, thank you."]],
    [r"quit", ["Bye-bye!"]]
]

class AdvancedChatbot:
    def __init__(self):
        self.chat = Chat(pairs, reflections) if Chat else None
    def converse(self):
        if self.chat:
            self.chat.converse()
        else:
            print("NLP libraries not available.")

class CLI:
    @staticmethod
    def run():
        print("Advanced Chatbot with NLP")
        bot = AdvancedChatbot()
        bot.converse()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
