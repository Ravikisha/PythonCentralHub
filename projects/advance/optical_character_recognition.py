import cv2
import pytesseract
import numpy as np

class OpticalCharacterRecognition:
    def __init__(self):
        pass

    def recognize_text(self, image):
        text = pytesseract.image_to_string(image)
        print(f"Recognized text: {text}")
        return text

    def demo(self):
        img = np.zeros((100, 300, 3), dtype=np.uint8)
        cv2.putText(img, 'Python OCR', (5, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
        self.recognize_text(img)
        cv2.imshow('OCR Demo', img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Optical Character Recognition Demo")
    ocr = OpticalCharacterRecognition()
    ocr.demo()
