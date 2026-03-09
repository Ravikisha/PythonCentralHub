import numpy as np

class RealTimeImageExtraction:
    def __init__(self):
        pass

    def extract_features(self, image):
        # Dummy feature extraction for demo
        print("Extracting features from image...")
        return np.mean(image)

    def demo(self):
        img = np.random.rand(64, 64)
        features = self.extract_features(img)
        print(f"Extracted feature value: {features}")

if __name__ == "__main__":
    print("Real-Time Image Extraction Demo")
    extractor = RealTimeImageExtraction()
    extractor.demo()
