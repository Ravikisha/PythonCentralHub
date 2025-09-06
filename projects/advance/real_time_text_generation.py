import random

class RealTimeTextGeneration:
    def __init__(self):
        self.words = ['Python', 'AI', 'data', 'science', 'project', 'code', 'automation']

    def generate_sentence(self):
        sentence = ' '.join(random.choices(self.words, k=7))
        print(f"Generated sentence: {sentence}")
        return sentence

    def demo(self):
        for _ in range(3):
            self.generate_sentence()

if __name__ == "__main__":
    print("Real-Time Text Generation Demo")
    generator = RealTimeTextGeneration()
    generator.demo()
