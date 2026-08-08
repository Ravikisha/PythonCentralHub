"""
QR Code Attendance System

A Python application that generates QR codes for users and scans them to mark attendance. Features include:
- Generating QR codes for user identification.
- Scanning QR codes to mark attendance.
"""

import qrcode
import cv2
from tkinter import Tk, Label, Entry, Button, messagebox
from datetime import datetime


class QRCodeAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Attendance System")

        Label(root, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=10)
        self.user_id_entry = Entry(root, width=30)
        self.user_id_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(root, text="Generate QR Code", command=self.generate_qr_code).grid(row=1, column=0, columnspan=2, pady=10)
        Button(root, text="Scan QR Code", command=self.scan_qr_code).grid(row=2, column=0, columnspan=2, pady=10)

    def generate_qr_code(self):
        """Generate a QR code for the entered user ID."""
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please enter a User ID.")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(user_id)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img_path = f"{user_id}_qr.png"
        img.save(img_path)

        messagebox.showinfo("Success", f"QR Code generated and saved as {img_path}.")

    def scan_qr_code(self):
        """Scan a QR code to mark attendance."""
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                messagebox.showinfo("Attendance Marked", f"User ID: {data}\nTime: {timestamp}")
                break

            show_or_save("QR Code Scanner", frame)
            if wait_or_skip(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows() if "--show" in __import__("sys").argv else None


def main():
    root = Tk()
    app = QRCodeAttendanceSystem(root)
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
