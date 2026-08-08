import cv2
import pytesseract
import numpy as np

class OpticalCharacterRecognition:
    def __init__(self):
        pass

    def recognize_text(self, image):
        text = pytesseract.image_to_string(image)
        print(f"Recognized text: {text}")
        return text

    def demo(self):
        img = np.zeros((100, 300, 3), dtype=np.uint8)
        cv2.putText(img, 'Python OCR', (5, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
        self.recognize_text(img)
        show_or_save('OCR Demo', img)
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
    print("Optical Character Recognition Demo")
    ocr = OpticalCharacterRecognition()
    ocr.demo()
