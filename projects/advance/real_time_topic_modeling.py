from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

class RealTimeTopicModeling:
    def __init__(self, n_topics=2):
        self.model = LatentDirichletAllocation(n_components=n_topics)

    def fit(self, X):
        self.model.fit(X)
        print(f"Model fitted for {self.model.n_components} topics.")

    def demo(self):
        X = np.random.randint(0, 5, (100, 10))
        self.fit(X)

if __name__ == "__main__":
    print("Real-Time Topic Modeling Demo")
    modeler = RealTimeTopicModeling()
    modeler.demo()
