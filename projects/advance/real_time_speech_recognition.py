import speech_recognition as sr

class RealTimeSpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize(self):
        with sr.Microphone() as source:
            print("Say something...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
            except Exception as e:
                print(f"Error: {e}")

    def demo(self):
        self.recognize()

if __name__ == "__main__":
    print("Real-Time Speech Recognition Demo")
    recognizer = RealTimeSpeechRecognition()
    # recognizer.demo()  # Uncomment to run with microphone
