"""
Basic Photo Editor

A photo editing application with the following features:
- Open and save images
- Apply filters (grayscale, sepia, etc.)
- Resize and crop images
- Adjust brightness and contrast
- Rotate and flip images
"""

from tkinter import Tk, Label, Button, filedialog, Canvas, PhotoImage, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageOps


class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor")

        self.image = None
        self.photo = None

        self.canvas = Canvas(self.root, width=800, height=600, bg="gray")
        self.canvas.pack()

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Button(self.root, text="Open Image", command=self.open_image).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Save Image", command=self.save_image).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Grayscale", command=self.apply_grayscale).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Sepia", command=self.apply_sepia).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Resize", command=self.resize_image).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Crop", command=self.crop_image).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Brightness", command=self.adjust_brightness).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Contrast", command=self.adjust_contrast).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Rotate", command=self.rotate_image).pack(side="left", padx=10, pady=10)
        Button(self.root, text="Flip", command=self.flip_image).pack(side="left", padx=10, pady=10)

    def open_image(self):
        """Open an image file."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
        if not file_path:
            return

        self.image = Image.open(file_path)
        self.display_image()

    def save_image(self):
        """Save the current image to a file."""
        if self.image is None:
            messagebox.showerror("Error", "No image to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if not file_path:
            return

        self.image.save(file_path)
        messagebox.showinfo("Success", "Image saved successfully.")

    def display_image(self):
        """Display the current image on the canvas."""
        if self.image is None:
            return

        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(400, 300, image=self.photo, anchor="center")

    def apply_grayscale(self):
        """Apply a grayscale filter to the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        self.image = ImageOps.grayscale(self.image)
        self.display_image()

    def apply_sepia(self):
        """Apply a sepia filter to the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        sepia_image = ImageOps.colorize(ImageOps.grayscale(self.image), "#704214", "#C0A080")
        self.image = sepia_image
        self.display_image()

    def resize_image(self):
        """Resize the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        width = simpledialog.askinteger("Resize", "Enter new width:")
        height = simpledialog.askinteger("Resize", "Enter new height:")
        if not width or not height:
            return

        self.image = self.image.resize((width, height))
        self.display_image()

    def crop_image(self):
        """Crop the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        left = simpledialog.askinteger("Crop", "Enter left coordinate:")
        top = simpledialog.askinteger("Crop", "Enter top coordinate:")
        right = simpledialog.askinteger("Crop", "Enter right coordinate:")
        bottom = simpledialog.askinteger("Crop", "Enter bottom coordinate:")
        if not left or not top or not right or not bottom:
            return

        self.image = self.image.crop((left, top, right, bottom))
        self.display_image()

    def adjust_brightness(self):
        """Adjust the brightness of the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        factor = simpledialog.askfloat("Brightness", "Enter brightness factor (e.g., 1.0 for no change):")
        if not factor:
            return

        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(factor)
        self.display_image()

    def adjust_contrast(self):
        """Adjust the contrast of the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        factor = simpledialog.askfloat("Contrast", "Enter contrast factor (e.g., 1.0 for no change):")
        if not factor:
            return

        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(factor)
        self.display_image()

    def rotate_image(self):
        """Rotate the image."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        angle = simpledialog.askinteger("Rotate", "Enter rotation angle (in degrees):")
        if not angle:
            return

        self.image = self.image.rotate(angle)
        self.display_image()

    def flip_image(self):
        """Flip the image horizontally or vertically."""
        if self.image is None:
            messagebox.showerror("Error", "No image loaded.")
            return

        direction = messagebox.askquestion("Flip", "Flip horizontally? (No for vertical)")
        if direction == "yes":
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
        self.display_image()


def main():
    root = Tk()
    app = PhotoEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
