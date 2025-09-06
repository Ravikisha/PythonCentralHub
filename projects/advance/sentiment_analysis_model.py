"""
Sentiment Analysis Model

A full sentiment analysis pipeline using scikit-learn and NLTK. Includes data loading, preprocessing, model training, prediction, and CLI for batch analysis.
"""
import pandas as pd
import numpy as np
import argparse
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import joblib
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = [w for w in text.lower().split() if w.isalpha() and w not in stop_words]
    return ' '.join(tokens)

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df['text'] = df['text'].apply(preprocess)
    return df

def train_model(df, model_path=None):
    X = df['text']
    y = df['label']
    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)
    clf = MultinomialNB()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    if model_path:
        joblib.dump((clf, vectorizer), model_path)
        print(f"Model saved to {model_path}")
    return clf, vectorizer

def predict(model, vectorizer, texts):
    texts = [preprocess(t) for t in texts]
    X_vec = vectorizer.transform(texts)
    preds = model.predict(X_vec)
    return preds

def main():
    parser = argparse.ArgumentParser(description="Sentiment Analysis Model")
    parser.add_argument('--data', type=str, help='Path to CSV data file')
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--model', type=str, default='sentiment_model.pkl', help='Path to save/load model')
    parser.add_argument('--predict', type=str, help='Text to predict sentiment')
    args = parser.parse_args()

    if args.train and args.data:
        df = load_data(args.data)
        train_model(df, args.model)
    elif args.predict:
        if not os.path.exists(args.model):
            print(f"Model file {args.model} not found. Train the model first.")
            return
        clf, vectorizer = joblib.load(args.model)
        result = predict(clf, vectorizer, [args.predict])
        print(f"Sentiment: {result[0]}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
