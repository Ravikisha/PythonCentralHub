"""
Speech Emotion Recognition

This project detects emotions from speech audio using machine learning. It demonstrates feature extraction (MFCC), model training, prediction, and reporting using scikit-learn. Includes CLI for training and prediction.
"""
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import os
import argparse
import joblib

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, duration=3, offset=0.5)
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        return mfccs
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return np.zeros(40)

def load_data(data_folder):
    X, y = [], []
    for file in os.listdir(data_folder):
        if file.endswith('.wav'):
            label = file.split('_')[0]  # e.g., happy_01.wav
            features = extract_features(os.path.join(data_folder, file))
            X.append(features)
            y.append(label)
    return np.array(X), np.array(y)

def train_model(X, y, model_path=None):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(f"Accuracy: {clf.score(X_test, y_test):.2f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    if model_path:
        joblib.dump(clf, model_path)
        print(f"Model saved to {model_path}")
    return clf

def predict_emotion(model, file_path):
    features = extract_features(file_path)
    pred = model.predict([features])[0]
    print(f"Predicted emotion for {file_path}: {pred}")
    return pred

def main():
    parser = argparse.ArgumentParser(description="Speech Emotion Recognition")
    parser.add_argument('--data', type=str, help='Path to audio data folder')
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--model', type=str, default='ser_model.pkl', help='Path to save/load model')
    parser.add_argument('--predict', type=str, help='Path to audio file for prediction')
    args = parser.parse_args()

    if args.train and args.data:
        X, y = load_data(args.data)
        train_model(X, y, args.model)
    elif args.predict:
        if not os.path.exists(args.model):
            print(f"Model file {args.model} not found. Train the model first.")
            return
        model = joblib.load(args.model)
        predict_emotion(model, args.predict)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
