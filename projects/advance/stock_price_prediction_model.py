"""
Stock Price Prediction Model

This project builds a stock price prediction model using historical data and machine learning (scikit-learn). It demonstrates data loading, feature engineering, model training, prediction, and visualization. Includes CLI for training and prediction.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import argparse
import joblib
import os

def load_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return None
    df = pd.read_csv(csv_path)
    return df

def train_model(df, model_path=None):
    X = df[['Open', 'High', 'Low', 'Volume']]
    y = df['Close']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    if model_path:
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}")
    return model, X_test, y_test

def plot_predictions(model, X_test, y_test):
    predictions = model.predict(X_test)
    plt.figure(figsize=(10,5))
    plt.plot(y_test.values, label='Actual')
    plt.plot(predictions, label='Predicted')
    plt.xlabel('Sample')
    plt.ylabel('Stock Price')
    plt.title('Stock Price Prediction')
    plt.legend()
    plt.show()

def predict(model, X):
    return model.predict(X)

def main():
    parser = argparse.ArgumentParser(description="Stock Price Prediction Model")
    parser.add_argument('--data', type=str, help='Path to CSV data file')
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--model', type=str, default='stock_model.pkl', help='Path to save/load model')
    parser.add_argument('--predict', type=str, help='Path to CSV file for prediction')
    args = parser.parse_args()

    if args.train and args.data:
        df = load_data(args.data)
        if df is not None:
            model, X_test, y_test = train_model(df, args.model)
            plot_predictions(model, X_test, y_test)
    elif args.predict:
        if not os.path.exists(args.model):
            print(f"Model file {args.model} not found. Train the model first.")
            return
        model = joblib.load(args.model)
        df = load_data(args.predict)
        if df is not None:
            X = df[['Open', 'High', 'Low', 'Volume']]
            preds = predict(model, X)
            print("Predictions:", preds)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
