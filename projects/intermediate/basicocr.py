#!/usr/bin/env python3
"""
Basic OCR (Optical Character Recognition)
A comprehensive OCR application using Tesseract and OpenCV for text extraction.

Features:
- Text extraction from images
- Image preprocessing for better OCR accuracy
- Support for multiple image formats
- Batch processing capabilities
- Text output in various formats
- Confidence scores and bounding boxes

Requirements:
- opencv-python
- pytesseract
- Pillow (PIL)
- numpy
- tesseract-ocr (system dependency)

Author: Python Central Hub
Date: 2025-09-05
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import json
import argparse
from datetime import datetime
import re


class OCRProcessor:
    """Advanced OCR processor with image preprocessing capabilities."""
    
    def __init__(self, tesseract_path=None):
        """Initialize OCR processor with optional Tesseract path."""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
        self.preprocessing_methods = {
            'grayscale': self.convert_to_grayscale,
            'threshold': self.apply_threshold,
            'denoise': self.denoise_image,
            'deskew': self.deskew_image,
            'enhance': self.enhance_image
        }
    
    def check_tesseract_installation(self):
        """Check if Tesseract is properly installed."""
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            print("Please install Tesseract OCR:")
            print("Ubuntu/Debian: sudo apt install tesseract-ocr")
            print("macOS: brew install tesseract")
            print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    
    def load_image(self, image_path):
        """Load image from file path."""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            return image
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def convert_to_grayscale(self, image):
        """Convert image to grayscale."""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def apply_threshold(self, image, threshold_type='adaptive'):
        """Apply thresholding to image."""
        gray = self.convert_to_grayscale(image)
        
        if threshold_type == 'adaptive':
            return cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        elif threshold_type == 'otsu':
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
        else:  # Simple threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            return thresh
    
    def denoise_image(self, image):
        """Remove noise from image."""
        return cv2.medianBlur(image, 5)
    
    def deskew_image(self, image):
        """Deskew image by detecting and correcting rotation."""
        gray = self.convert_to_grayscale(image)
        
        # Apply threshold
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Find contours and get the largest one
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get minimum area rectangle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Correct angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotate image
        if abs(angle) > 0.5:  # Only rotate if angle is significant
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                   flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
    
    def enhance_image(self, image):
        """Enhance image contrast and sharpness."""
        # Convert to PIL for enhancement
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.2)
        
        # Convert back to OpenCV format
        if len(image.shape) == 3:
            return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
        else:
            return np.array(enhanced)
    
    def preprocess_image(self, image, methods=['grayscale', 'denoise', 'threshold']):
        """Apply multiple preprocessing methods to image."""
        processed = image.copy()
        
        for method in methods:
            if method in self.preprocessing_methods:
                processed = self.preprocessing_methods[method](processed)
        
        return processed
    
    def extract_text(self, image, config='--psm 6'):
        """Extract text from image using Tesseract."""
        try:
            # Ensure image is in correct format
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(image)
            
            # Extract text
            text = pytesseract.image_to_string(pil_image, config=config)
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def get_text_with_confidence(self, image, config='--psm 6'):
        """Get text with confidence scores."""
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            pil_image = Image.fromarray(image)
            
            # Get detailed data
            data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
            
            # Extract text with confidence
            results = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Filter out low confidence
                    results.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': (data['left'][i], data['top'][i], 
                                data['width'][i], data['height'][i])
                    })
            
            return results
        
        except Exception as e:
            print(f"Error getting text with confidence: {e}")
            return []
    
    def draw_bounding_boxes(self, image, text_data):
        """Draw bounding boxes around detected text."""
        output_image = image.copy()
        
        for item in text_data:
            if item['confidence'] > 30:  # Only draw boxes for confident detections
                x, y, w, h = item['bbox']
                cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add confidence score
                cv2.putText(output_image, f"{item['confidence']}%", 
                           (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        return output_image
    
    def process_single_image(self, image_path, output_dir=None, preprocessing=True):
        """Process a single image and extract text."""
        print(f"📷 Processing: {os.path.basename(image_path)}")
        
        # Load image
        image = self.load_image(image_path)
        if image is None:
            return None
        
        results = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'preprocessing_applied': preprocessing
        }
        
        # Original text extraction
        original_text = self.extract_text(image)
        results['original_text'] = original_text
        
        if preprocessing:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text from processed image
            processed_text = self.extract_text(processed_image)
            results['processed_text'] = processed_text
            
            # Get text with confidence scores
            confidence_data = self.get_text_with_confidence(processed_image)
            results['confidence_data'] = confidence_data
            
            # Save processed image if output directory specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                processed_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
                cv2.imwrite(processed_path, processed_image)
                
                # Save image with bounding boxes
                bbox_image = self.draw_bounding_boxes(image, confidence_data)
                bbox_path = os.path.join(output_dir, f"bbox_{os.path.basename(image_path)}")
                cv2.imwrite(bbox_path, bbox_image)
                
                results['processed_image_path'] = processed_path
                results['bbox_image_path'] = bbox_path
        
        return results
    
    def batch_process(self, input_dir, output_dir=None):
        """Process multiple images in a directory."""
        if not os.path.exists(input_dir):
            print(f"❌ Input directory not found: {input_dir}")
            return []
        
        # Find all image files
        image_files = []
        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in self.supported_formats):
                image_files.append(os.path.join(input_dir, file))
        
        if not image_files:
            print(f"❌ No supported image files found in {input_dir}")
            return []
        
        print(f"📁 Found {len(image_files)} images to process")
        
        # Process each image
        results = []
        for image_path in image_files:
            result = self.process_single_image(image_path, output_dir)
            if result:
                results.append(result)
        
        # Save batch results
        if output_dir and results:
            results_path = os.path.join(output_dir, 'ocr_results.json')
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"💾 Results saved to: {results_path}")
        
        return results


class OCRApplication:
    """Interactive OCR application with GUI-like interface."""
    
    def __init__(self):
        self.processor = OCRProcessor()
        
    def run_interactive_mode(self):
        """Run interactive OCR application."""
        if not self.processor.check_tesseract_installation():
            return
        
        print("🔍 OCR Text Extraction Tool")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Process single image")
            print("2. Batch process directory")
            print("3. Compare preprocessing methods")
            print("4. Extract text with confidence scores")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self.process_single_image()
            elif choice == '2':
                self.batch_process_directory()
            elif choice == '3':
                self.compare_preprocessing()
            elif choice == '4':
                self.extract_with_confidence()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please select 1-5.")
    
    def process_single_image(self):
        """Interactive single image processing."""
        image_path = input("Enter image path: ").strip()
        if not os.path.exists(image_path):
            print("❌ Image file not found!")
            return
        
        use_preprocessing = input("Apply preprocessing? (y/n): ").lower().startswith('y')
        output_dir = input("Output directory (optional): ").strip() or None
        
        result = self.processor.process_single_image(image_path, output_dir, use_preprocessing)
        
        if result:
            print("\n📄 Extracted Text:")
            print("-" * 30)
            if use_preprocessing and result.get('processed_text'):
                print(result['processed_text'])
            else:
                print(result.get('original_text', 'No text found'))
            print("-" * 30)
        else:
            print("❌ Failed to process image!")
    
    def batch_process_directory(self):
        """Interactive batch processing."""
        input_dir = input("Enter input directory path: ").strip()
        output_dir = input("Enter output directory path: ").strip()
        
        results = self.processor.batch_process(input_dir, output_dir)
        
        if results:
            print(f"\n✅ Successfully processed {len(results)} images")
            total_chars = sum(len(r.get('processed_text', '')) for r in results)
            print(f"📊 Total characters extracted: {total_chars}")
        else:
            print("❌ No images processed!")
    
    def compare_preprocessing(self):
        """Compare different preprocessing methods."""
        image_path = input("Enter image path: ").strip()
        if not os.path.exists(image_path):
            print("❌ Image file not found!")
            return
        
        image = self.processor.load_image(image_path)
        if image is None:
            return
        
        methods = [
            ['grayscale'],
            ['grayscale', 'threshold'],
            ['grayscale', 'denoise', 'threshold'],
            ['grayscale', 'denoise', 'threshold', 'enhance'],
            ['grayscale', 'deskew', 'denoise', 'threshold']
        ]
        
        print("\n🔬 Comparing Preprocessing Methods:")
        print("=" * 50)
        
        for i, method_list in enumerate(methods, 1):
            processed = self.processor.preprocess_image(image, method_list)
            text = self.processor.extract_text(processed)
            
            print(f"\nMethod {i}: {' + '.join(method_list)}")
            print(f"Characters extracted: {len(text)}")
            if text:
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"Preview: {repr(preview)}")
    
    def extract_with_confidence(self):
        """Extract text with confidence scores."""
        image_path = input("Enter image path: ").strip()
        if not os.path.exists(image_path):
            print("❌ Image file not found!")
            return
        
        image = self.processor.load_image(image_path)
        if image is None:
            return
        
        # Preprocess image
        processed = self.processor.preprocess_image(image)
        
        # Get confidence data
        confidence_data = self.processor.get_text_with_confidence(processed)
        
        if confidence_data:
            print("\n📊 Text with Confidence Scores:")
            print("=" * 50)
            
            for item in confidence_data:
                if item['text'].strip() and item['confidence'] > 30:
                    print(f"Text: '{item['text']}' | Confidence: {item['confidence']}%")
            
            # Statistics
            confidences = [item['confidence'] for item in confidence_data if item['text'].strip()]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"\n📈 Average confidence: {avg_confidence:.1f}%")
                print(f"📈 Highest confidence: {max(confidences)}%")
                print(f"📈 Lowest confidence: {min(confidences)}%")
        else:
            print("❌ No text detected with sufficient confidence!")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='OCR Text Extraction Tool')
    parser.add_argument('--image', help='Path to single image file')
    parser.add_argument('--directory', help='Path to directory with images')
    parser.add_argument('--output', help='Output directory for results')
    parser.add_argument('--no-preprocessing', action='store_true', help='Skip image preprocessing')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    processor = OCRProcessor()
    
    if not processor.check_tesseract_installation():
        return
    
    if args.interactive or (not args.image and not args.directory):
        app = OCRApplication()
        app.run_interactive_mode()
    elif args.image:
        result = processor.process_single_image(
            args.image, 
            args.output, 
            not args.no_preprocessing
        )
        if result:
            print("Extracted Text:")
            print("-" * 30)
            text = result.get('processed_text') or result.get('original_text', '')
            print(text)
            print("-" * 30)
    elif args.directory:
        results = processor.batch_process(args.directory, args.output)
        print(f"Processed {len(results)} images")


if __name__ == "__main__":
    main()
