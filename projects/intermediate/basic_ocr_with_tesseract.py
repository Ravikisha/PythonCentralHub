"""
Basic OCR with Tesseract

A Python application that uses Tesseract OCR to extract text from images. Features include:
- GUI for uploading images
- Displaying extracted text
"""

import pytesseract
from PIL import Image
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, END


class BasicOCR:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic OCR with Tesseract")

        self.label = Label(root, text="Upload an image to extract text:")
        self.label.pack(pady=10)

        self.upload_button = Button(root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=5)

        self.text_area = Text(root, wrap="word", width=60, height=20)
        self.text_area.pack(pady=10)

        self.scrollbar = Scrollbar(root, command=self.text_area.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

    def upload_image(self):
        """Open a file dialog to upload an image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        if file_path:
            self.extract_text(file_path)

    def extract_text(self, file_path):
        """Extract text from the uploaded image using Tesseract OCR."""
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
            self.text_area.delete(1.0, END)
            self.text_area.insert(END, extracted_text)
        except Exception as e:
            self.text_area.delete(1.0, END)
            self.text_area.insert(END, f"Error: {e}")


def main():
    root = Tk()
    app = BasicOCR(root)
    root.mainloop()


if __name__ == "__main__":
    main()
