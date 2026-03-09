import cv2
import numpy as np

class RealTimeFaceMaskDetection:
    def __init__(self):
        pass

    def detect_mask(self, image):
        # Dummy mask detection for demo
        print("Detecting face mask in image...")
        return True

    def demo(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = self.detect_mask(img)
        print(f"Face mask detected: {result}")
        cv2.imshow('Face Mask Detection', img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Real-Time Face Mask Detection Demo")
    detector = RealTimeFaceMaskDetection()
    detector.demo()
