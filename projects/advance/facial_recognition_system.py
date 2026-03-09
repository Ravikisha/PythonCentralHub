"""
Facial Recognition System

This project implements a facial recognition system using OpenCV and face_recognition library. It supports face detection, encoding, registration, and real-time recognition from webcam. Includes CLI for registering new faces and running recognition.
"""
import cv2
import face_recognition
import os
import argparse
import pickle

def load_known_faces(db_path):
    """Load known faces and their encodings from the database."""
    if os.path.exists(db_path):
        with open(db_path, 'rb') as f:
            data = pickle.load(f)
        return data['encodings'], data['names']
    return [], []

def save_known_faces(encodings, names, db_path):
    """Save known faces and their encodings to the database."""
    with open(db_path, 'wb') as f:
        pickle.dump({'encodings': encodings, 'names': names}, f)

def register_face(image_path, name, db_path):
    """Register a new face by adding its encoding to the database."""
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    if encodings:
        known_encodings, known_names = load_known_faces(db_path)
        known_encodings.append(encodings[0])
        known_names.append(name)
        save_known_faces(known_encodings, known_names, db_path)
        print(f"Registered face for {name}")
    else:
        print("No face found in image.")

def recognize_faces(db_path):
    """Run real-time face recognition on webcam feed."""
    known_encodings, known_names = load_known_faces(db_path)
    video = cv2.VideoCapture(0)
    print("Press 'q' to quit.")
    while True:
        ret, frame = video.read()
        rgb = frame[:, :, ::-1]
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)
        for (top, right, bottom, left), encoding in zip(faces, encodings):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                name = known_names[matches.index(True)]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
        cv2.imshow('Facial Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Facial Recognition System")
    parser.add_argument('--register', nargs=2, metavar=('IMAGE', 'NAME'), help='Register a new face')
    parser.add_argument('--db', type=str, default='faces.db', help='Path to face database')
    parser.add_argument('--recognize', action='store_true', help='Run real-time recognition')
    args = parser.parse_args()

    if args.register:
        image_path, name = args.register
        register_face(image_path, name, args.db)
    elif args.recognize:
        recognize_faces(args.db)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
