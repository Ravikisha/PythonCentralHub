"""
Deep Learning Image Classifier

Features:
- Image classification using deep learning
- Training and prediction modules
- Modular design
- CLI interface
- Error handling
"""
import sys
import os
import numpy as np
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
except ImportError:
    tf = None
    layers = None
    models = None

class ImageClassifier:
    def __init__(self, input_shape=(64,64,3), num_classes=2):
        self.model = models.Sequential([
            layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
            layers.MaxPooling2D(2,2),
            layers.Conv2D(64, (3,3), activation='relu'),
            layers.MaxPooling2D(2,2),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ]) if models else None
        if self.model:
            self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    def train(self, train_dir, epochs=5):
        if self.model:
            datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
            train_data = datagen.flow_from_directory(train_dir, target_size=(64,64), batch_size=32, class_mode='categorical')
            self.model.fit(train_data, epochs=epochs)
            self.model.save('image_classifier.h5')
    def predict(self, img_path):
        if self.model:
            img = tf.keras.preprocessing.image.load_img(img_path, target_size=(64,64))
            x = tf.keras.preprocessing.image.img_to_array(img)/255.0
            x = np.expand_dims(x, axis=0)
            preds = self.model.predict(x)
            return np.argmax(preds)
        return None

class CLI:
    @staticmethod
    def run():
        print("Deep Learning Image Classifier")
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: train <train_dir>")
                    continue
                clf = ImageClassifier()
                clf.train(parts[1])
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <img_path>")
                    continue
                clf = ImageClassifier()
                clf.model.load_weights('image_classifier.h5')
                label = clf.predict(parts[1])
                print(f"Predicted class: {label}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
