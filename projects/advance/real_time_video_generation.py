import numpy as np
import matplotlib.pyplot as plt

class RealTimeVideoGeneration:
    def __init__(self):
        pass

    def generate_video(self, n_frames=10):
        # Dummy video generation for demo
        video = [np.random.rand(64, 64) for _ in range(n_frames)]
        print("Generated video frames.")
        return video

    def demo(self):
        video = self.generate_video()
        for i, frame in enumerate(video):
            plt.imshow(frame, cmap='gray')
            plt.title(f'Frame {i+1}')
            plt.savefig("real_time_video_generation.png", dpi=120, bbox_inches="tight")
            print("saved real_time_video_generation.png")
            plt.show()

if __name__ == "__main__":
    print("Real-Time Video Generation Demo")
    generator = RealTimeVideoGeneration()
    generator.demo()
