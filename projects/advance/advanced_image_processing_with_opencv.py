"""
Advanced Image Processing with OpenCV

This project demonstrates advanced image processing techniques using OpenCV, including edge detection, filtering, morphological operations, color transformations, and saving processed images. Includes CLI for selecting processing type.
"""
import cv2
import numpy as np
import argparse
import os

def test_pattern(size=320):
    """A synthetic image with the features each mode is meant to show.

    Hard edges for Canny, a smooth gradient for the blur, isolated specks for
    the morphological close, and saturated colour for the HSV conversion. A
    photograph would work too; this one is here so the file runs with no
    arguments and no downloaded asset.
    """
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:, :, 0] = np.linspace(0, 255, size, dtype=np.uint8)      # gradient
    cv2.rectangle(img, (40, 40), (150, 150), (0, 220, 255), -1)   # hard edges
    cv2.circle(img, (230, 230), 55, (255, 60, 60), -1)
    cv2.line(img, (0, size - 1), (size - 1, 0), (255, 255, 255), 2)
    rng = np.random.default_rng(20260809)                          # specks
    for y, x in rng.integers(0, size, (120, 2)):
        img[y, x] = (255, 255, 255)
    return img


def process_image(image_path, mode, out_path=None):
    if image_path:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return
        print(f"loaded {image_path}: {img.shape[1]}x{img.shape[0]}")
    else:
        img = test_pattern()
        print(f"no --image given, using a generated "
              f"{img.shape[1]}x{img.shape[0]} test pattern")
    if mode == 'gray':
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif mode == 'edges':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.Canny(gray, 100, 200)
    elif mode == 'blur':
        result = cv2.GaussianBlur(img, (5,5), 0)
    elif mode == 'morph':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
    elif mode == 'hsv':
        result = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    else:
        print(f"Unknown mode: {mode}")
        return
    print(f"mode {mode}: output is {result.shape} "
      f"{'grayscale' if result.ndim == 2 else 'colour'}, "
      f"range {result.min()} to {result.max()}")
    show_or_save(f'{mode.capitalize()} Image', result)
    wait_or_skip(0)
    cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None
    if out_path:
        if len(result.shape) == 2:
            cv2.imwrite(out_path, result)
        else:
            cv2.imwrite(out_path, cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        print(f"Saved processed image to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Advanced Image Processing with OpenCV")
    parser.add_argument('--image', type=str, help='Path to image file; a generated test pattern is used when omitted')
    parser.add_argument('--mode', type=str, choices=['gray', 'edges', 'blur', 'morph', 'hsv'], default='edges', help='Processing mode')
    parser.add_argument('--out', type=str, help='Output file path')
    args = parser.parse_args()
    process_image(args.image, args.mode, args.out)

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
