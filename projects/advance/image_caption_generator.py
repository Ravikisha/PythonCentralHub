import numpy as np
import matplotlib.pyplot as plt

class ImageCaptionGenerator:
    def __init__(self):
        pass

    def generate_caption(self, image):
        # Dummy caption for demo
        return "A sample caption for the image."

    def demo(self):
        img = np.random.rand(64, 64)
        plt.imshow(img, cmap='gray')
        plt.title(self.generate_caption(img))
        plt.show()

if __name__ == "__main__":
    print("Image Caption Generator Demo")
    generator = ImageCaptionGenerator()
    generator.demo()
