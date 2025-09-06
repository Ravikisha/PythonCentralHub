import cv2
import numpy as np

class VideoProcessingTool:
    def __init__(self):
        pass

    def process_video(self, frames):
        print("Processing video frames...")
        return [cv2.GaussianBlur(frame, (5,5), 0) for frame in frames]

    def demo(self):
        frames = [np.random.rand(64, 64, 3).astype(np.float32) for _ in range(3)]
        processed = self.process_video(frames)
        for i, frame in enumerate(processed):
            print(f"Processed frame {i+1} shape: {frame.shape}")

if __name__ == "__main__":
    print("Video Processing Tool Demo")
    tool = VideoProcessingTool()
    tool.demo()
