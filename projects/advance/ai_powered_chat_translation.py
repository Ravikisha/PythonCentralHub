"""
AI-powered Chat Translation

Features:
- Real-time chat translation
- Multi-language support
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    from googletrans import Translator
except ImportError:
    Translator = None

class ChatTranslator:
    def __init__(self):
        self.translator = Translator() if Translator else None
    def translate(self, text, dest='en'):
        if self.translator:
            return self.translator.translate(text, dest=dest).text
        return "Translation library not available."

class CLI:
    @staticmethod
    def run():
        print("AI-powered Chat Translation")
        translator = ChatTranslator()
        while True:
            cmd = input('> ')
            if cmd.startswith('translate'):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: translate <text> <lang>")
                    continue
                text = parts[1]
                lang = parts[2]
                result = translator.translate(text, dest=lang)
                print(f"Translated: {result}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'translate <text> <lang>' or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
