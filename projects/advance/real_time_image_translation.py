import numpy as np

class RealTimeImageTranslation:
    def __init__(self):
        pass

    def translate_image(self, image, shift=(5,5)):
        # Dummy translation for demo
        translated = np.roll(image, shift, axis=(0,1))
        print(f"Translated image by {shift}.")
        return translated

    def demo(self):
        img = np.random.rand(32, 32)
        translated = self.translate_image(img)
        print(f"Original mean: {img.mean():.2f}, Translated mean: {translated.mean():.2f}")

if __name__ == "__main__":
    print("Real-Time Image Translation Demo")
    translator = RealTimeImageTranslation()
    translator.demo()
