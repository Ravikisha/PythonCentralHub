"""
Real-time Object Detection (Webcam)

Features:
- Real-time object detection from webcam
- Deep learning (YOLO or similar)
- Visualization
- Modular design
- CLI interface
- Error handling
"""
import cv2
import sys
import numpy as np

class ObjectDetector:
    def __init__(self, model_cfg, model_weights, classes_file):
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
        self.classes = [line.strip() for line in open(classes_file)]
    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416,416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i-1] for i in self.net.getUnconnectedOutLayers()]
        detections = self.net.forward(output_layers)
        boxes, confidences, class_ids = [], [], []
        h, w = frame.shape[:2]
        for output in detections:
            for det in output:
                scores = det[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    box = det[0:4]*np.array([w, h, w, h])
                    center_x, center_y, bw, bh = box.astype('int')
                    x = int(center_x - bw/2)
                    y = int(center_y - bh/2)
                    boxes.append([x, y, int(bw), int(bh)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        return boxes, confidences, class_ids, idxs

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 4:
            print("Usage: python real_time_object_detection_webcam.py <cfg> <weights> <classes>")
            sys.exit(1)
        detector = ObjectDetector(sys.argv[1], sys.argv[2], sys.argv[3])
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            boxes, confidences, class_ids, idxs = detector.detect(frame)
            for i in idxs:
                i = i[0] if isinstance(i, (list, np.ndarray)) else i
                x, y, w, h = boxes[i]
                label = detector.classes[class_ids[i]]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
            show_or_save('Object Detection', frame)
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
