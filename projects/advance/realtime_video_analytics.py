"""
Real-Time Video Analytics System

Features:
- Object tracking
- Face detection
- Statistics dashboard
- Modular design
- CLI interface
- Error handling
"""
import cv2
import numpy as np
import sys
import threading
import queue
import time
from collections import defaultdict

class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise ValueError("Cannot open video source")
        self.stopped = False
        self.q = queue.Queue(maxsize=128)
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            if not self.q.full():
                ret, frame = self.stream.read()
                if not ret:
                    self.stop()
                    break
                self.q.put(frame)
            else:
                time.sleep(0.01)

    def read(self):
        return self.q.get()

    def more(self):
        return not self.q.empty()

    def stop(self):
        self.stopped = True
        self.stream.release()

class ObjectTracker:
    def __init__(self):
        self.tracker = cv2.TrackerKCF_create()
        self.bbox = None
        self.initialized = False

    def init(self, frame, bbox):
        self.tracker.init(frame, bbox)
        self.bbox = bbox
        self.initialized = True

    def update(self, frame):
        if not self.initialized:
            return None
        success, bbox = self.tracker.update(frame)
        if success:
            self.bbox = bbox
            return bbox
        return None

class FaceDetector:
    def __init__(self):
        self.cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, 1.3, 5)
        return faces

class StatsDashboard:
    def __init__(self):
        self.stats = defaultdict(int)
        self.start_time = time.time()

    def update(self, faces, objects):
        self.stats['frames'] += 1
        self.stats['faces'] += len(faces)
        if objects:
            self.stats['objects'] += 1

    def report(self):
        elapsed = time.time() - self.start_time
        print(f"Frames: {self.stats['frames']}")
        print(f"Faces detected: {self.stats['faces']}")
        print(f"Objects tracked: {self.stats['objects']}")
        print(f"Elapsed time: {elapsed:.2f}s")

class CLI:
    @staticmethod
    def run():
        print("Starting Real-Time Video Analytics...")
        stream = VideoStream(0)
        tracker = ObjectTracker()
        detector = FaceDetector()
        dashboard = StatsDashboard()
        bbox = None
        while True:
            if stream.more():
                frame = stream.read()
                faces = detector.detect(frame)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                if bbox:
                    tracked = tracker.update(frame)
                    if tracked:
                        p1 = (int(tracked[0]), int(tracked[1]))
                        p2 = (int(tracked[0]+tracked[2]), int(tracked[1]+tracked[3]))
                        cv2.rectangle(frame, p1, p2, (0,255,0), 2)
                dashboard.update(faces, bbox)
                cv2.imshow('Video Analytics', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    bbox = cv2.selectROI('Video Analytics', frame, False)
                    tracker.init(frame, bbox)
            else:
                time.sleep(0.01)
        stream.stop()
        cv2.destroyAllWindows()
        dashboard.report()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
