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

        show_or_save("Detected Faces", image)
        wait_or_skip(0)
        cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None


def main():
    root = Tk()
    app = ImageRecognitionApp(root)
    root.mainloop()


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
