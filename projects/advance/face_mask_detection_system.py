"""
Face Mask Detection System

Features:
- Face mask detection using computer vision
- ML model training and prediction
- Real-time webcam interface
- Modular design
- CLI interface
- Error handling
"""
import cv2
import numpy as np
import sys
import os
import random
try:
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
except ImportError:
    SVC = None
    train_test_split = None

class MaskDataset:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.images = []
        self.labels = []
    def load(self):
        for label in os.listdir(self.data_dir):
            label_dir = os.path.join(self.data_dir, label)
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                img = cv2.imread(img_path, 0)
                img = cv2.resize(img, (64, 64)).flatten()
                self.images.append(img)
                self.labels.append(label)
        return np.array(self.images), np.array(self.labels)

class MaskDetector:
    def __init__(self):
        self.model = SVC() if SVC else None
        self.trained = False
    def train(self, X, y):
        if self.model:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            self.model.fit(X_train, y_train)
            acc = self.model.score(X_test, y_test)
            print(f"Model accuracy: {acc}")
            self.trained = True
    def predict(self, img):
        if self.trained:
            return self.model.predict([img.flatten()])[0]
        return random.choice(['mask', 'no_mask'])

class CLI:
    @staticmethod
    def run():
        print("Face Mask Detection System")
        print("Commands: train <data_dir>, predict <img_path>, webcam, exit")
        detector = MaskDetector()
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: train <data_dir>")
                    continue
                ds = MaskDataset(parts[1])
                X, y = ds.load()
                detector.train(X, y)
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <img_path>")
                    continue
                img = cv2.imread(parts[1], 0)
                img = cv2.resize(img, (64, 64))
                label = detector.predict(img)
                print(f"Predicted: {label}")
            elif cmd == 'webcam':
                cap = cv2.VideoCapture(0)
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    img = cv2.resize(gray, (64, 64))
                    label = detector.predict(img)
                    cv2.putText(frame, f"Mask: {label}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    show_or_save('Mask Detection', frame)
                    if wait_or_skip(1) & 0xFF == ord('q'):
                        break
                cap.release()
                cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

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
