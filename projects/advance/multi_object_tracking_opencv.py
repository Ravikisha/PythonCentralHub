"""
Multi-object Tracking with OpenCV

Features:
- Multi-object tracking
- Visualization
- Modular design
- CLI interface
- Error handling
"""
import cv2
import sys
import random

class MultiObjectTracker:
    def __init__(self):
        self.trackers = cv2.MultiTracker_create()
    def add_tracker(self, frame, bbox):
        tracker = cv2.TrackerKCF_create()
        self.trackers.add(tracker, frame, bbox)
    def update(self, frame):
        success, boxes = self.trackers.update(frame)
        return success, boxes

class CLI:
    @staticmethod
    def run():
        print("Multi-object Tracking with OpenCV")
        cap = cv2.VideoCapture(0)
        mot = MultiObjectTracker()
        bboxes = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if len(bboxes) == 0:
                bboxes = cv2.selectROIs('Multi-object Tracking', frame, False)
                for bbox in bboxes:
                    mot.add_tracker(frame, tuple(bbox))
            success, boxes = mot.update(frame)
            for i, box in enumerate(boxes):
                p1 = (int(box[0]), int(box[1]))
                p2 = (int(box[0]+box[2]), int(box[1]+box[3]))
                cv2.rectangle(frame, p1, p2, (0,255,0), 2)
                cv2.putText(frame, f"Obj {i}", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
            show_or_save('Multi-object Tracking', frame)
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
