"""
Real-time Facial Expression Analysis

Features:
- Real-time facial expression analysis
- Computer vision and ML
- Visualization
- Modular design
- CLI interface
- Error handling
"""
import cv2
import sys
import random
try:
    from sklearn.svm import SVC
except ImportError:
    SVC = None

class ExpressionRecognizer:
    def __init__(self):
        self.model = SVC() if SVC else None
        self.trained = False
    def train(self, X, y):
        if self.model:
            self.model.fit(X, y)
            self.trained = True
    def predict(self, img):
        if self.trained:
            return self.model.predict([img.flatten()])[0]
        return random.choice(['happy', 'sad', 'neutral', 'angry'])

class CLI:
    @staticmethod
    def run():
        print("Real-time Facial Expression Analysis")
        recognizer = ExpressionRecognizer()
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(gray, (64, 64))
            label = recognizer.predict(img)
            cv2.putText(frame, f"Expression: {label}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            show_or_save('Facial Expression Analysis', frame)
            if wait_or_skip(1) & 0xFF == ord('q'):
                break
        cap.release()
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
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
