"""
AI-powered Document Search

Features:
- Semantic document search
- NLP-based ranking
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None

class DocumentSearch:
    def __init__(self):
        self.vectorizer = TfidfVectorizer() if TfidfVectorizer else None
        self.documents = []
        self.vectors = None
    def add_documents(self, docs):
        self.documents.extend(docs)
        if self.vectorizer:
            self.vectors = self.vectorizer.fit_transform(self.documents)
    def search(self, query):
        if self.vectorizer and self.vectors is not None:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.vectors).flatten()
            ranked = sorted(zip(self.documents, scores), key=lambda x: x[1], reverse=True)
            return ranked[:5]
        return []

class CLI:
    @staticmethod
    def run():
        print("AI-powered Document Search")
        searcher = DocumentSearch()
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: add <doc1|doc2|...>")
                    continue
                docs = parts[1].split('|')
                searcher.add_documents(docs)
                print(f"Added {len(docs)} documents.")
            elif cmd.startswith('search'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: search <query>")
                    continue
                query = parts[1]
                results = searcher.search(query)
                for doc, score in results:
                    print(f"Score: {score:.2f} | Doc: {doc}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
