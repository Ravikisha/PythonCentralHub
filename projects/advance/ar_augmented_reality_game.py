"""
AR (Augmented Reality) Game

Features:
- Marker detection
- Interactive gameplay
- Modular design
- GUI (OpenCV)
- Error handling
"""
import cv2
import numpy as np
import sys
import random

class ARGame:
    def __init__(self):
        self.marker_color = (0,255,0)
        self.score = 0
    def detect_marker(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([40, 40, 40])
        upper = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            return (x, y, w, h)
        return None
    def play(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            marker = self.detect_marker(frame)
            if marker:
                x, y, w, h = marker
                cv2.rectangle(frame, (x, y), (x+w, y+h), self.marker_color, 2)
                self.score += 1
                cv2.putText(frame, f"Score: {self.score}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            show_or_save('AR Game', frame)
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
        game = ARGame()
        game.play()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
