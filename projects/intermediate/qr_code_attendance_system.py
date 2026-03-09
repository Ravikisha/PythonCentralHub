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

            cv2.imshow("QR Code Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


def main():
    root = Tk()
    app = QRCodeAttendanceSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
