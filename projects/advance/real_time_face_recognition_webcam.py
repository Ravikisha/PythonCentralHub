"""
Real-time Face Recognition (Webcam)

Features:
- Real-time face recognition from webcam
- Deep learning (face_recognition)
- Visualization
- Modular design
- CLI interface
- Error handling
"""
import cv2
import face_recognition
import sys
import os

class FaceRecognizer:
    def __init__(self, known_dir):
        self.known_encodings = []
        self.known_names = []
        for name in os.listdir(known_dir):
            img_path = os.path.join(known_dir, name)
            img = face_recognition.load_image_file(img_path)
            enc = face_recognition.face_encodings(img)
            if enc:
                self.known_encodings.append(enc[0])
                self.known_names.append(name)
    def recognize(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        for enc in encodings:
            matches = face_recognition.compare_faces(self.known_encodings, enc)
            name = "Unknown"
            if True in matches:
                first_match = matches.index(True)
                name = self.known_names[first_match]
            names.append(name)
        return boxes, names

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python real_time_face_recognition_webcam.py <known_dir>")
            sys.exit(1)
        recognizer = FaceRecognizer(sys.argv[1])
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            boxes, names = recognizer.recognize(frame)
            for (top, right, bottom, left), name in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
                cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
            cv2.imshow('Face Recognition', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
