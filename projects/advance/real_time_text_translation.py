from googletrans import Translator

class RealTimeTextTranslation:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, dest='es'):
        result = self.translator.translate(text, dest=dest)
        print(f"Original: {text}\nTranslated: {result.text}")
        return result.text

    def demo(self):
        self.translate('Python is awesome!', 'fr')

if __name__ == "__main__":
    print("Real-Time Text Translation Demo")
    translator = RealTimeTextTranslation()
    translator.demo()
