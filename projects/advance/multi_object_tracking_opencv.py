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
            cv2.imshow('Multi-object Tracking', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
