from gensim.summarization import summarize

class RealTimeTextSummarization:
    def __init__(self):
        pass

    def summarize_text(self, text):
        summary = summarize(text)
        print(f"Summary:\n{summary}")
        return summary

    def demo(self):
        text = """Python is a powerful programming language. It is widely used in data science, machine learning, and web development. Python's simplicity and readability make it a favorite among developers."""
        self.summarize_text(text)

if __name__ == "__main__":
    print("Real-Time Text Summarization Demo")
    summarizer = RealTimeTextSummarization()
    summarizer.demo()
