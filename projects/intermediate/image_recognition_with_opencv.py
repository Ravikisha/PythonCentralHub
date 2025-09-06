"""
Image Recognition with OpenCV

A Python application that performs basic image recognition using OpenCV.
Features include:
- Loading and displaying an image.
- Detecting objects (e.g., faces) in the image.
"""

import cv2
from tkinter import Tk, Label, Button, filedialog, messagebox


class ImageRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Recognition with OpenCV")

        Label(root, text="Image Recognition App").grid(row=0, column=0, padx=10, pady=10)

        Button(root, text="Load Image", command=self.load_image).grid(row=1, column=0, pady=10)
        Button(root, text="Detect Faces", command=self.detect_faces).grid(row=2, column=0, pady=10)

        self.image_path = None
        self.cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def load_image(self):
        """Load an image file."""
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if self.image_path:
            messagebox.showinfo("Image Loaded", f"Loaded image: {self.image_path}")

    def detect_faces(self):
        """Detect faces in the loaded image."""
        if not self.image_path:
            messagebox.showerror("Error", "Please load an image first.")
            return

        image = cv2.imread(self.image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Detected Faces", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    root = Tk()
    app = ImageRecognitionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
