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
        show_or_save('Object Detection', img)
        wait_or_skip(1000)
        cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None

def wait_or_skip(delay=0):
    """cv2.waitKey needs a window; without one it raises. Skip it instead."""
    import sys

    if "--show" in sys.argv:
        return cv2.waitKey(delay)
    return -1


def show_or_save(title, image, _counter=[0]):
    """Display the frame, or write it to a file when no window is available.

    Headless OpenCV has no GUI at all, and even a full build cannot open a
    window over SSH or inside a container. Falling back to a file keeps the
    project runnable everywhere and leaves something to look at afterwards.
    """
    import os
    import re as _re

    if "--show" in __import__("sys").argv:
        cv2.imshow(title, image)
        return None
    _counter[0] += 1
    stem = _re.sub(r"\W+", "_", title).strip("_").lower() or "frame"
    name = f"{stem}.png" if _counter[0] == 1 else f"{stem}_{_counter[0]}.png"
    cv2.imwrite(name, image)
    print(f"saved {name}  ({os.path.getsize(name):,} bytes)")
    return name


if __name__ == "__main__":
    print("Object Detection System Demo")
    detector = ObjectDetectionSystem()
    detector.demo()
