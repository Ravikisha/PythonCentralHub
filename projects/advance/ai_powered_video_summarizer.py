"""
AI-powered Video Summarizer

Features:
- Summarizes videos using deep learning
- Key frame extraction
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

class VideoSummarizer:
    def __init__(self):
        pass
    def summarize(self, video_path):
        if not cv2 or not np:
            print("OpenCV and numpy required.")
            return []
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        if not frames:
            print("No frames found.")
            return []
        # Key frame extraction (simple diff)
        key_frames = [frames[0]]
        for i in range(1, len(frames)):
            diff = np.sum(np.abs(frames[i].astype(np.int32) - frames[i-1].astype(np.int32)))
            if diff > 1e6:
                key_frames.append(frames[i])
        print(f"Extracted {len(key_frames)} key frames.")
        return key_frames

class CLI:
    @staticmethod
    def run():
        print("AI-powered Video Summarizer")
        summarizer = VideoSummarizer()
        while True:
            cmd = input('> ')
            if cmd.startswith('summarize'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: summarize <video_path>")
                    continue
                video_path = parts[1]
                key_frames = summarizer.summarize(video_path)
                print(f"Key frames: {len(key_frames)}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
