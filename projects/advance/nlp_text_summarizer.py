from gensim.summarization import summarize

class NLPTextSummarizer:
    def __init__(self):
        pass

    def summarize_text(self, text):
        summary = summarize(text)
        print(f"Summary:\n{summary}")
        return summary

    def demo(self):
        text = """Natural language processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to enable computers to understand, interpret, and generate human language in a way that is both meaningful and useful."""
        self.summarize_text(text)

if __name__ == "__main__":
    print("NLP Text Summarizer Demo")
    summarizer = NLPTextSummarizer()
    summarizer.demo()
