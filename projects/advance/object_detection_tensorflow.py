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
    cv2.imshow('Object Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Object Detection with TensorFlow")
    parser.add_argument('--image', type=str, help='Path to image file')
    args = parser.parse_args()
    model = load_model()
    detect_objects(model, args.image)

if __name__ == "__main__":
    main()
