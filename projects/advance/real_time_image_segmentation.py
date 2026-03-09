import numpy as np
import matplotlib.pyplot as plt

class RealTimeImageSegmentation:
    def __init__(self):
        pass

    def segment_image(self, image):
        # Dummy segmentation for demo
        mask = image > 0.5
        print("Segmented image.")
        return mask

    def demo(self):
        img = np.random.rand(64, 64)
        mask = self.segment_image(img)
        plt.imshow(mask, cmap='gray')
        plt.title('Real-Time Image Segmentation')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Image Segmentation Demo")
    segmenter = RealTimeImageSegmentation()
    segmenter.demo()
