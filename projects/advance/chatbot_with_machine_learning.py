"""
Chatbot with Machine Learning

A full chatbot implementation using scikit-learn and NLTK. Includes intent classification, response generation, training, and CLI for chat interaction.
"""
import pandas as pd
import numpy as np
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import nltk
nltk.download('punkt')

# Example intents dataset
intents = [
    {'intent': 'greeting', 'patterns': ['hello', 'hi', 'hey'], 'responses': ['Hello!', 'Hi there!', 'Hey!']},
    {'intent': 'goodbye', 'patterns': ['bye', 'goodbye', 'see you'], 'responses': ['Goodbye!', 'See you later!', 'Bye!']},
    {'intent': 'thanks', 'patterns': ['thanks', 'thank you'], 'responses': ['You are welcome!', 'No problem!']},
]

def build_dataset(intents):
    X, y = [], []
    for intent in intents:
        for pattern in intent['patterns']:
            X.append(pattern)
            y.append(intent['intent'])
    return X, y

def train_model(X, y, model_path=None):
    vectorizer = TfidfVectorizer()
    X_vec = vectorizer.fit_transform(X)
    clf = LogisticRegression()
    clf.fit(X_vec, y)
    if model_path:
        joblib.dump((clf, vectorizer), model_path)
        print(f"Model saved to {model_path}")
    return clf, vectorizer

def get_response(intent):
    for item in intents:
        if item['intent'] == intent:
            return np.random.choice(item['responses'])
    return "I don't understand."

def chat(model, vectorizer):
    print("Chatbot is ready! Type 'quit' to exit.")
    while True:
        user_input = input('You: ')
        if user_input.lower() == 'quit':
            break
        X_vec = vectorizer.transform([user_input])
        intent = model.predict(X_vec)[0]
        print('Bot:', get_response(intent))

def main():
    parser = argparse.ArgumentParser(description="Chatbot with Machine Learning")
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--model', type=str, default='chatbot_model.pkl', help='Path to save/load model')
    parser.add_argument('--chat', action='store_true', help='Start chat')
    args = parser.parse_args()

    if args.train:
        X, y = build_dataset(intents)
        train_model(X, y, args.model)
    elif args.chat:
        if not os.path.exists(args.model):
            print(f"Model file {args.model} not found. Train the model first.")
            return
        clf, vectorizer = joblib.load(args.model)
        chat(clf, vectorizer)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
