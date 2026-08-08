"""
Object Detection with TensorFlow

A full object detection pipeline using TensorFlow and pre-trained models. Includes image loading, detection, visualization, and CLI for batch processing.
"""
import tensorflow as tf
import numpy as np
import cv2
import argparse
import os

# Load pre-trained model (SSD MobileNet)
def load_model():
    model = tf.saved_model.load('ssd_mobilenet_v2_fpnlite_320x320/saved_model')
    return model

def detect_objects(model, image_path):
    img = cv2.imread(image_path)
    input_tensor = tf.convert_to_tensor(img)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = model(input_tensor)
    boxes = detections['detection_boxes'][0].numpy()
    scores = detections['detection_scores'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(np.int32)
    h, w, _ = img.shape
    for i in range(len(scores)):
        if scores[i] > 0.5:
            box = boxes[i]
            y1, x1, y2, x2 = box
            cv2.rectangle(img, (int(x1*w), int(y1*h)), (int(x2*w), int(y2*h)), (0,255,0), 2)
            cv2.putText(img, str(classes[i]), (int(x1*w), int(y1*h)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
    show_or_save('Object Detection', img)
    wait_or_skip(0)
    cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None

def main():
    parser = argparse.ArgumentParser(description="Object Detection with TensorFlow")
    parser.add_argument('--image', type=str, help='Path to image file')
    args = parser.parse_args()
    model = load_model()
    detect_objects(model, args.image)

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
    main()
