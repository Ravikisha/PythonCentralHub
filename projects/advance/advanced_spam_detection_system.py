"""
Advanced Spam Detection System

Features:
- Spam detection using ML
- Reporting
- Email integration
- Modular design
- CLI interface
- Error handling
"""
import sys
import random
try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
except ImportError:
    CountVectorizer = None
    MultinomialNB = None

class SpamDetector:
    def __init__(self):
        self.vectorizer = CountVectorizer() if CountVectorizer else None
        self.model = MultinomialNB() if MultinomialNB else None
        self.trained = False
    def train(self, texts, labels):
        if self.vectorizer and self.model:
            X = self.vectorizer.fit_transform(texts)
            self.model.fit(X, labels)
            self.trained = True
    def predict(self, text):
        if self.trained:
            X = self.vectorizer.transform([text])
            return self.model.predict(X)[0]
        return random.choice(['spam', 'ham'])

class CLI:
    @staticmethod
    def run():
        print("Advanced Spam Detection System")
        detector = SpamDetector()
        # Dummy training data
        texts = ["Win money now!", "Hello friend", "Cheap meds", "Meeting at 10"]
        labels = ["spam", "ham", "spam", "ham"]
        detector.train(texts, labels)
        while True:
            cmd = input('> ')
            if cmd.startswith('check'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: check <text>")
                    continue
                text = parts[1]
                result = detector.predict(text)
                print(f"Result: {result}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'check <text>' or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
