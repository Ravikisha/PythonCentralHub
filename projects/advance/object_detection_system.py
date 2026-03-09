import cv2
import numpy as np

class ObjectDetectionSystem:
    def __init__(self):
        pass

    def detect_objects(self, image):
        # Dummy detection for demo
        print("Detecting objects in image...")
        return [(10, 10, 50, 50)]

    def demo(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        boxes = self.detect_objects(img)
        for (x, y, w, h) in boxes:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.imshow('Object Detection', img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Object Detection System Demo")
    detector = ObjectDetectionSystem()
    detector.demo()
