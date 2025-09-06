import speech_recognition as sr

class SpeechToTextConverter:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def convert(self):
        with sr.Microphone() as source:
            print("Say something...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
            except Exception as e:
                print(f"Error: {e}")

    def demo(self):
        self.convert()

if __name__ == "__main__":
    print("Speech to Text Converter Demo")
    converter = SpeechToTextConverter()
    # converter.demo()  # Uncomment to run with microphone
