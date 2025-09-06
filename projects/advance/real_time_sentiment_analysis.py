from textblob import TextBlob

class RealTimeSentimentAnalysis:
    def __init__(self):
        pass

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        print(f"Sentiment polarity: {blob.sentiment.polarity}")
        return blob.sentiment.polarity

    def demo(self):
        self.analyze_sentiment('Python is awesome!')
        self.analyze_sentiment('This is terrible.')

if __name__ == "__main__":
    print("Real-Time Sentiment Analysis Demo")
    analyzer = RealTimeSentimentAnalysis()
    analyzer.demo()
