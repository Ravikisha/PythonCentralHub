"""
Advanced OCR with Tesseract

This project demonstrates advanced Optical Character Recognition (OCR) using Tesseract and Python. It supports multi-language recognition, image preprocessing, batch processing, and saving results to text files. Includes CLI for batch and single image OCR.

Requirements:
pip install pytesseract pillow
Make sure Tesseract is installed and in your PATH

Example usage:
python advanced_ocr_with_tesseract.py --image sample.png --lang eng --out result.txt
python advanced_ocr_with_tesseract.py --folder images/ --lang eng --out results/
"""
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import os
import argparse

def preprocess_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('L')
        img = img.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)
        return img
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def ocr_image(image_path, lang='eng', out_path=None):
    img = preprocess_image(image_path)
    if img is None:
        return ""
    text = pytesseract.image_to_string(img, lang=lang)
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
    return text

def batch_ocr(folder, lang='eng', out_folder=None):
    results = {}
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            path = os.path.join(folder, filename)
            out_path = None
            if out_folder:
                os.makedirs(out_folder, exist_ok=True)
                out_path = os.path.join(out_folder, filename + '.txt')
            results[filename] = ocr_image(path, lang, out_path)
    return results

def main():
    parser = argparse.ArgumentParser(description="Advanced OCR with Tesseract")
    parser.add_argument('--image', type=str, help='Path to image file for OCR')
    parser.add_argument('--folder', type=str, help='Path to folder for batch OCR')
    parser.add_argument('--lang', type=str, default='eng', help='Language for OCR')
    parser.add_argument('--out', type=str, help='Output file or folder')
    args = parser.parse_args()

    if args.image:
        text = ocr_image(args.image, args.lang, args.out)
        print(text)
    elif args.folder:
        batch_ocr(args.folder, args.lang, args.out)
        print(f"Batch OCR completed. Results saved to {args.out}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
