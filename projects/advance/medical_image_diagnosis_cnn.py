"""
Medical Image Diagnosis using CNN

Features:
- Deep learning (CNN) for image classification
- Training, evaluation, prediction
- GUI for image upload and diagnosis
- Modular design
- Error handling
"""
import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import tkinter as tk
from tkinter import filedialog, messagebox

class CNNModel:
    def __init__(self, input_shape=(128,128,3), num_classes=2):
        self.model = models.Sequential([
            layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
            layers.MaxPooling2D(2,2),
            layers.Conv2D(64, (3,3), activation='relu'),
            layers.MaxPooling2D(2,2),
            layers.Conv2D(128, (3,3), activation='relu'),
            layers.MaxPooling2D(2,2),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    def train(self, train_dir, val_dir, epochs=10):
        train_gen = ImageDataGenerator(rescale=1./255)
        val_gen = ImageDataGenerator(rescale=1./255)
        train_data = train_gen.flow_from_directory(train_dir, target_size=(128,128), batch_size=32, class_mode='categorical')
        val_data = val_gen.flow_from_directory(val_dir, target_size=(128,128), batch_size=32, class_mode='categorical')
        self.model.fit(train_data, validation_data=val_data, epochs=epochs)
        self.model.save('medical_cnn_model.h5')

    def predict(self, img_path):
        img = load_img(img_path, target_size=(128,128))
        x = img_to_array(img)/255.0
        x = np.expand_dims(x, axis=0)
        preds = self.model.predict(x)
        return preds

class DiagnosisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Medical Image Diagnosis")
        self.model = CNNModel()
        self.model.model.load_weights('medical_cnn_model.h5')
        self.label = tk.Label(self.root, text="Upload an image for diagnosis")
        self.label.pack()
        self.button = tk.Button(self.root, text="Upload Image", command=self.upload)
        self.button.pack()
        self.result = tk.Label(self.root, text="")
        self.result.pack()

    def upload(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            preds = self.model.predict(file_path)
            diagnosis = np.argmax(preds)
            self.result.config(text=f"Diagnosis: Class {diagnosis}")
            messagebox.showinfo("Result", f"Diagnosis: Class {diagnosis}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        if len(sys.argv) < 4:
            print("Usage: python medical_image_diagnosis_cnn.py train <train_dir> <val_dir>")
            sys.exit(1)
        model = CNNModel()
        model.train(sys.argv[2], sys.argv[3])
    else:
        gui = DiagnosisGUI()
        gui.run()
