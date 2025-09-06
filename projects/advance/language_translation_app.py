from googletrans import Translator

class LanguageTranslationApp:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, dest='es'):
        result = self.translator.translate(text, dest=dest)
        print(f"Original: {text}\nTranslated: {result.text}")
        return result.text

    def demo(self):
        self.translate('Hello, world!', 'fr')

if __name__ == "__main__":
    print("Language Translation App Demo")
    app = LanguageTranslationApp()
    app.demo()
