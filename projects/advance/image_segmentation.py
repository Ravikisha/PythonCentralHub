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
    cv2.imshow('Threshold Segmentation', binary.astype(np.uint8)*255)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
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
    cv2.imshow('K-means Segmentation', segmented)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return segmented

def main():
    parser = argparse.ArgumentParser(description="Image Segmentation")
    parser.add_argument('--image', type=str, required=True, help='Path to image file')
    parser.add_argument('--mode', type=str, choices=['threshold', 'kmeans'], required=True, help='Segmentation mode')
    parser.add_argument('--k', type=int, default=2, help='Number of clusters for k-means')
    args = parser.parse_args()
    if args.mode == 'threshold':
        threshold_segmentation(args.image)
    elif args.mode == 'kmeans':
        kmeans_segmentation(args.image, args.k)

if __name__ == "__main__":
    main()
