import os

class DocumentSearchEngine:
    def __init__(self, directory):
        self.directory = directory

    def search(self, keyword):
        results = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.txt'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if keyword in content:
                            results.append(path)
        print(f"Found {len(results)} documents containing '{keyword}'.")
        return results

if __name__ == "__main__":
    print("Document Search Engine Demo")
    engine = DocumentSearchEngine("documents")
    # engine.search("Python")
