import numpy as np
import matplotlib.pyplot as plt

class RealTimeImageGeneration:
    def __init__(self):
        pass

    def generate_image(self):
        # Dummy image generation for demo
        img = np.random.rand(64, 64)
        print("Generated image.")
        return img

    def demo(self):
        img = self.generate_image()
        plt.imshow(img, cmap='gray')
        plt.title('Real-Time Image Generation')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Image Generation Demo")
    generator = RealTimeImageGeneration()
    generator.demo()
