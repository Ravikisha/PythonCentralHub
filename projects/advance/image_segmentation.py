"""
Image Segmentation

A full image segmentation pipeline using OpenCV and scikit-image. Includes image loading, segmentation (thresholding, k-means), visualization, and CLI for batch processing.
"""
import cv2
import numpy as np
import argparse
from skimage import filters
from sklearn.cluster import KMeans
import os

def threshold_segmentation(image_path):
    img = cv2.imread(image_path, 0)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return None
    thresh_val = filters.threshold_otsu(img)
    binary = img > thresh_val
    show_or_save('Threshold Segmentation', binary.astype(np.uint8)*255)
    wait_or_skip(0)
    cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None
    return binary

def kmeans_segmentation(image_path, k=2):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return None
    Z = img.reshape((-1,3))
    Z = np.float32(Z)
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(Z)
    centers = np.uint8(kmeans.cluster_centers_)
    segmented = centers[labels].reshape(img.shape)
    show_or_save('K-means Segmentation', segmented)
    wait_or_skip(0)
    cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None
    return segmented

def sample_image():
    """Write a small scene with known regions, so there is something to segment.

    Requiring --image means the project cannot be run without finding a
    picture first. Generating one keeps the demo self-contained, and a scene
    with known regions is more useful for judging a segmentation than an
    arbitrary photograph.
    """
    import tempfile
    from pathlib import Path

    import numpy as np
    from PIL import Image

    size = 240
    grid_y, grid_x = np.mgrid[0:size, 0:size] / size
    scene = np.where(grid_y > 0.55, 60, 190).astype("uint8")
    disc = np.hypot(grid_x - 0.35, grid_y - 0.35) < 0.18
    scene[disc] = 125
    rng = np.random.default_rng(0)
    scene = np.clip(scene + rng.normal(0, 6, scene.shape), 0, 255)

    path = Path(tempfile.mkdtemp(prefix="segmentation-demo-")) / "scene.png"
    Image.fromarray(scene.astype("uint8")).save(path)
    print(f"no --image given, so a test scene was written to {path}")
    print("it has three regions: a bright sky, a dark ground and a mid disc\n")
    return str(path)


def main():
    parser = argparse.ArgumentParser(description="Image Segmentation")
    parser.add_argument('--image', type=str, default=None,
                        help='Path to image file (a demo scene is generated '
                             'when this is omitted)')
    parser.add_argument('--mode', type=str, choices=['threshold', 'kmeans'],
                        default='kmeans', help='Segmentation mode')
    parser.add_argument('--k', type=int, default=2, help='Number of clusters for k-means')
    args = parser.parse_args()
    if args.image is None:
        args.image = sample_image()
    if args.mode == 'threshold':
        threshold_segmentation(args.image)
    elif args.mode == 'kmeans':
        kmeans_segmentation(args.image, args.k)

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
