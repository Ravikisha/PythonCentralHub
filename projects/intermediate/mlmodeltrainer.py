import pandas as pd
import numpy as np
import sqlite3
import pickle
import json
import os
import warnings
from datetime import datetime, timedelta
import logging
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

# Machine Learning Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score, confusion_matrix,
    classification_report, roc_curve, precision_recall_curve
)

# Models
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier, MLPRegressor
from xgboost import XGBClassifier, XGBRegressor

# Flask for web interface
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import zipfile
import io

warnings.filterwarnings('ignore')

class MLDatabase:
    def __init__(self, db_path="ml_trainer.db"):
        """Initialize the ML trainer database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables for ML experiments."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Datasets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                rows INTEGER,
                columns INTEGER,
                target_column TEXT,
                problem_type TEXT CHECK(problem_type IN ('classification', 'regression')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dataset_id INTEGER NOT NULL,
                algorithm TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                hyperparameters TEXT,
                training_time REAL,
                model_path TEXT,
                status TEXT CHECK(status IN ('training', 'completed', 'failed')) DEFAULT 'training',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets (id)
            )
        ''')
        
        # Model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT CHECK(metric_type IN ('train', 'test', 'cv')) DEFAULT 'test',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # Experiments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                dataset_id INTEGER NOT NULL,
                target_column TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                test_size REAL DEFAULT 0.2,
                random_state INTEGER DEFAULT 42,
                cv_folds INTEGER DEFAULT 5,
                status TEXT CHECK(status IN ('created', 'running', 'completed', 'failed')) DEFAULT 'created',
                best_model_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets (id),
                FOREIGN KEY (best_model_id) REFERENCES models (id)
            )
        ''')
        
        # Feature importance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_importance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                feature_name TEXT NOT NULL,
                importance_score REAL NOT NULL,
                rank_position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # Hyperparameter tuning results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hyperparameter_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                algorithm TEXT NOT NULL,
                parameters TEXT NOT NULL,
                cv_score REAL NOT NULL,
                std_score REAL,
                rank_position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments (id)
            )
        ''')
        
        conn.commit()
        conn.close()

class DataProcessor:
    def __init__(self):
        """Initialize data processor."""
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        self.label_encoders = {}
    
    def load_dataset(self, file_path):
        """Load dataset from various file formats."""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return df
        except Exception as e:
            logging.error(f"Error loading dataset: {e}")
            return None
    
    def analyze_dataset(self, df):
        """Analyze dataset and provide insights."""
        analysis = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'sample_data': df.head().to_dict('records')
        }
        
        # Basic statistics for numeric columns
        if analysis['numeric_columns']:
            analysis['numeric_stats'] = df[analysis['numeric_columns']].describe().to_dict()
        
        # Unique values for categorical columns
        categorical_info = {}
        for col in analysis['categorical_columns']:
            unique_count = df[col].nunique()
            categorical_info[col] = {
                'unique_count': unique_count,
                'unique_values': df[col].unique().tolist()[:10] if unique_count <= 10 else df[col].unique().tolist()[:10]
            }
        analysis['categorical_info'] = categorical_info
        
        return analysis
    
    def preprocess_data(self, df, target_column, problem_type, preprocessing_options=None):
        """Preprocess data for machine learning."""
        if preprocessing_options is None:
            preprocessing_options = {
                'handle_missing': 'drop',
                'scaling': 'standard',
                'encode_categorical': True,
                'feature_selection': None
            }
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Handle missing values
        if preprocessing_options['handle_missing'] == 'drop':
            # Drop rows with missing values
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
        elif preprocessing_options['handle_missing'] == 'fill_mean':
            # Fill numeric columns with mean
            for col in X.select_dtypes(include=[np.number]).columns:
                X[col].fillna(X[col].mean(), inplace=True)
            # Fill categorical columns with mode
            for col in X.select_dtypes(include=['object']).columns:
                X[col].fillna(X[col].mode()[0] if not X[col].mode().empty else 'Unknown', inplace=True)
        
        # Encode categorical variables
        if preprocessing_options['encode_categorical']:
            categorical_columns = X.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    X[col] = self.label_encoders[col].fit_transform(X[col].astype(str))
                else:
                    X[col] = self.label_encoders[col].transform(X[col].astype(str))
        
        # Encode target for classification
        if problem_type == 'classification' and y.dtype == 'object':
            if 'target' not in self.label_encoders:
                self.label_encoders['target'] = LabelEncoder()
                y = self.label_encoders['target'].fit_transform(y)
            else:
                y = self.label_encoders['target'].transform(y)
        
        # Feature scaling
        if preprocessing_options['scaling'] and preprocessing_options['scaling'] != 'none':
            scaler = self.scalers[preprocessing_options['scaling']]
            X = pd.DataFrame(
                scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        
        # Feature selection
        if preprocessing_options['feature_selection']:
            if preprocessing_options['feature_selection']['method'] == 'k_best':
                k = preprocessing_options['feature_selection']['k']
                if problem_type == 'classification':
                    selector = SelectKBest(f_classif, k=k)
                else:
                    selector = SelectKBest(f_regression, k=k)
                X = pd.DataFrame(
                    selector.fit_transform(X, y),
                    columns=X.columns[selector.get_support()],
                    index=X.index
                )
        
        return X, y

class ModelTrainer:
    def __init__(self):
        """Initialize model trainer with available algorithms."""
        self.classification_models = {
            'random_forest': RandomForestClassifier(random_state=42),
            'logistic_regression': LogisticRegression(random_state=42),
            'svc': SVC(random_state=42),
            'decision_tree': DecisionTreeClassifier(random_state=42),
            'knn': KNeighborsClassifier(),
            'naive_bayes': GaussianNB(),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'mlp': MLPClassifier(random_state=42),
            'xgboost': XGBClassifier(random_state=42, eval_metric='logloss')
        }
        
        self.regression_models = {
            'random_forest': RandomForestRegressor(random_state=42),
            'linear_regression': LinearRegression(),
            'ridge': Ridge(random_state=42),
            'lasso': Lasso(random_state=42),
            'elastic_net': ElasticNet(random_state=42),
            'svr': SVR(),
            'decision_tree': DecisionTreeRegressor(random_state=42),
            'knn': KNeighborsRegressor(),
            'gradient_boosting': GradientBoostingRegressor(random_state=42),
            'mlp': MLPRegressor(random_state=42),
            'xgboost': XGBRegressor(random_state=42)
        }
        
        self.hyperparameter_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 10, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'logistic_regression': {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            },
            'svc': {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
                'kernel': ['rbf', 'linear', 'poly']
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            }
        }
    
    def train_model(self, X_train, X_test, y_train, y_test, algorithm, problem_type, hyperparameters=None):
        """Train a single model with given parameters."""
        try:
            # Get the model
            if problem_type == 'classification':
                model = self.classification_models[algorithm]
            else:
                model = self.regression_models[algorithm]
            
            # Set hyperparameters if provided
            if hyperparameters:
                model.set_params(**hyperparameters)
            
            # Train the model
            start_time = datetime.now()
            model.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                y_train, y_test, y_train_pred, y_test_pred, problem_type, model, X_test
            )
            
            # Get feature importance if available
            feature_importance = None
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                feature_importance = np.abs(model.coef_).flatten()
            
            return {
                'model': model,
                'metrics': metrics,
                'training_time': training_time,
                'feature_importance': feature_importance,
                'predictions': {
                    'train': y_train_pred,
                    'test': y_test_pred
                }
            }
            
        except Exception as e:
            logging.error(f"Error training {algorithm}: {e}")
            return None
    
    def _calculate_metrics(self, y_train, y_test, y_train_pred, y_test_pred, problem_type, model, X_test):
        """Calculate performance metrics based on problem type."""
        metrics = {}
        
        if problem_type == 'classification':
            # Training metrics
            metrics['train_accuracy'] = accuracy_score(y_train, y_train_pred)
            metrics['train_precision'] = precision_score(y_train, y_train_pred, average='weighted', zero_division=0)
            metrics['train_recall'] = recall_score(y_train, y_train_pred, average='weighted', zero_division=0)
            metrics['train_f1'] = f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
            
            # Test metrics
            metrics['test_accuracy'] = accuracy_score(y_test, y_test_pred)
            metrics['test_precision'] = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
            metrics['test_recall'] = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
            metrics['test_f1'] = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
            
            # ROC AUC for binary classification
            if len(np.unique(y_test)) == 2:
                try:
                    if hasattr(model, 'predict_proba'):
                        y_test_proba = model.predict_proba(X_test)[:, 1]
                        metrics['test_roc_auc'] = roc_auc_score(y_test, y_test_proba)
                    elif hasattr(model, 'decision_function'):
                        y_test_scores = model.decision_function(X_test)
                        metrics['test_roc_auc'] = roc_auc_score(y_test, y_test_scores)
                except:
                    metrics['test_roc_auc'] = None
        
        else:  # regression
            # Training metrics
            metrics['train_mse'] = mean_squared_error(y_train, y_train_pred)
            metrics['train_rmse'] = np.sqrt(metrics['train_mse'])
            metrics['train_mae'] = mean_absolute_error(y_train, y_train_pred)
            metrics['train_r2'] = r2_score(y_train, y_train_pred)
            
            # Test metrics
            metrics['test_mse'] = mean_squared_error(y_test, y_test_pred)
            metrics['test_rmse'] = np.sqrt(metrics['test_mse'])
            metrics['test_mae'] = mean_absolute_error(y_test, y_test_pred)
            metrics['test_r2'] = r2_score(y_test, y_test_pred)
        
        return metrics
    
    def hyperparameter_tuning(self, X_train, y_train, algorithm, problem_type, cv_folds=5, search_type='grid'):
        """Perform hyperparameter tuning."""
        try:
            # Get model and parameter grid
            if problem_type == 'classification':
                model = self.classification_models[algorithm]
            else:
                model = self.regression_models[algorithm]
            
            param_grid = self.hyperparameter_grids.get(algorithm, {})
            
            if not param_grid:
                return None
            
            # Choose search strategy
            if search_type == 'grid':
                search = GridSearchCV(
                    model, param_grid, cv=cv_folds, 
                    scoring='accuracy' if problem_type == 'classification' else 'r2',
                    n_jobs=-1
                )
            else:  # random search
                search = RandomizedSearchCV(
                    model, param_grid, cv=cv_folds,
                    scoring='accuracy' if problem_type == 'classification' else 'r2',
                    n_iter=20, n_jobs=-1, random_state=42
                )
            
            # Perform search
            search.fit(X_train, y_train)
            
            # Extract results
            results = []
            for i, (params, score, std) in enumerate(zip(
                search.cv_results_['params'],
                search.cv_results_['mean_test_score'],
                search.cv_results_['std_test_score']
            )):
                results.append({
                    'parameters': params,
                    'cv_score': score,
                    'std_score': std,
                    'rank': search.cv_results_['rank_test_score'][i]
                })
            
            return {
                'best_params': search.best_params_,
                'best_score': search.best_score_,
                'all_results': results
            }
            
        except Exception as e:
            logging.error(f"Error in hyperparameter tuning for {algorithm}: {e}")
            return None
    
    def compare_models(self, X_train, X_test, y_train, y_test, problem_type, algorithms=None):
        """Compare multiple algorithms."""
        if algorithms is None:
            if problem_type == 'classification':
                algorithms = list(self.classification_models.keys())
            else:
                algorithms = list(self.regression_models.keys())
        
        results = {}
        
        for algorithm in algorithms:
            print(f"Training {algorithm}...")
            result = self.train_model(X_train, X_test, y_train, y_test, algorithm, problem_type)
            if result:
                results[algorithm] = result
        
        return results

class MLExperimentManager:
    def __init__(self):
        """Initialize ML experiment manager."""
        self.db = MLDatabase()
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.models_dir = Path("trained_models")
        self.models_dir.mkdir(exist_ok=True)
    
    def create_experiment(self, name, description, dataset_path, target_column, problem_type, test_size=0.2):
        """Create a new ML experiment."""
        # Load and analyze dataset
        df = self.data_processor.load_dataset(dataset_path)
        if df is None:
            return None
        
        analysis = self.data_processor.analyze_dataset(df)
        
        # Save dataset to database
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO datasets (name, description, file_path, rows, columns, target_column, problem_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            Path(dataset_path).stem, f"Dataset for {name}", dataset_path,
            analysis['shape'][0], analysis['shape'][1], target_column, problem_type
        ))
        
        dataset_id = cursor.lastrowid
        
        # Create experiment
        cursor.execute('''
            INSERT INTO experiments (name, description, dataset_id, target_column, problem_type, test_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, dataset_id, target_column, problem_type, test_size))
        
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'experiment_id': experiment_id,
            'dataset_id': dataset_id,
            'dataset_analysis': analysis
        }
    
    def run_experiment(self, experiment_id, algorithms=None, hyperparameter_tuning=False):
        """Run ML experiment with multiple algorithms."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get experiment details
        cursor.execute('''
            SELECT e.*, d.file_path FROM experiments e
            JOIN datasets d ON e.dataset_id = d.id
            WHERE e.id = ?
        ''', (experiment_id,))
        
        exp_data = cursor.fetchone()
        if not exp_data:
            return None
        
        # Update experiment status
        cursor.execute('UPDATE experiments SET status = "running" WHERE id = ?', (experiment_id,))
        conn.commit()
        
        try:
            # Load and preprocess data
            df = self.data_processor.load_dataset(exp_data[7])  # file_path
            X, y = self.data_processor.preprocess_data(df, exp_data[4], exp_data[5])  # target_column, problem_type
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=exp_data[6], random_state=exp_data[8]  # test_size, random_state
            )
            
            # Compare models
            if algorithms is None:
                algorithms = ['random_forest', 'logistic_regression', 'gradient_boosting'] if exp_data[5] == 'classification' else ['random_forest', 'linear_regression', 'gradient_boosting']
            
            results = self.model_trainer.compare_models(X_train, X_test, y_train, y_test, exp_data[5], algorithms)
            
            best_score = -np.inf
            best_model_id = None
            
            # Save results
            for algorithm, result in results.items():
                if result is None:
                    continue
                
                # Save model
                model_path = self.models_dir / f"experiment_{experiment_id}_{algorithm}.pkl"
                joblib.dump(result['model'], model_path)
                
                # Save model record
                cursor.execute('''
                    INSERT INTO models (name, dataset_id, algorithm, problem_type, training_time, model_path, status)
                    VALUES (?, ?, ?, ?, ?, ?, "completed")
                ''', (
                    f"{exp_data[1]}_{algorithm}", exp_data[2], algorithm, exp_data[5], 
                    result['training_time'], str(model_path)
                ))
                
                model_id = cursor.lastrowid
                
                # Save metrics
                for metric_name, metric_value in result['metrics'].items():
                    if metric_value is not None:
                        metric_type = 'train' if 'train' in metric_name else 'test'
                        cursor.execute('''
                            INSERT INTO model_metrics (model_id, metric_name, metric_value, metric_type)
                            VALUES (?, ?, ?, ?)
                        ''', (model_id, metric_name, metric_value, metric_type))
                
                # Save feature importance
                if result['feature_importance'] is not None:
                    feature_names = X.columns if hasattr(X, 'columns') else [f'feature_{i}' for i in range(len(result['feature_importance']))]
                    for i, (feature, importance) in enumerate(zip(feature_names, result['feature_importance'])):
                        cursor.execute('''
                            INSERT INTO feature_importance (model_id, feature_name, importance_score, rank_position)
                            VALUES (?, ?, ?, ?)
                        ''', (model_id, feature, importance, i + 1))
                
                # Track best model
                primary_metric = 'test_accuracy' if exp_data[5] == 'classification' else 'test_r2'
                if primary_metric in result['metrics'] and result['metrics'][primary_metric] > best_score:
                    best_score = result['metrics'][primary_metric]
                    best_model_id = model_id
                
                # Hyperparameter tuning if requested
                if hyperparameter_tuning:
                    tuning_result = self.model_trainer.hyperparameter_tuning(
                        X_train, y_train, algorithm, exp_data[5]
                    )
                    
                    if tuning_result:
                        for result_data in tuning_result['all_results']:
                            cursor.execute('''
                                INSERT INTO hyperparameter_results 
                                (experiment_id, algorithm, parameters, cv_score, std_score, rank_position)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                experiment_id, algorithm, json.dumps(result_data['parameters']),
                                result_data['cv_score'], result_data['std_score'], result_data['rank']
                            ))
            
            # Update experiment with best model
            cursor.execute('''
                UPDATE experiments 
                SET status = "completed", best_model_id = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (best_model_id, experiment_id))
            
            conn.commit()
            return results
            
        except Exception as e:
            logging.error(f"Error running experiment: {e}")
            cursor.execute('UPDATE experiments SET status = "failed" WHERE id = ?', (experiment_id,))
            conn.commit()
            return None
        finally:
            conn.close()

class MLWebInterface:
    def __init__(self):
        """Initialize Flask web interface for ML trainer."""
        self.app = Flask(__name__)
        self.app.secret_key = 'ml_trainer_secret_2024'
        self.app.config['UPLOAD_FOLDER'] = 'datasets'
        self.app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
        
        # Create directories
        Path(self.app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
        
        self.experiment_manager = MLExperimentManager()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            return render_template('ml_dashboard.html')
        
        @self.app.route('/experiments')
        def experiments():
            conn = sqlite3.connect(self.experiment_manager.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.*, d.name as dataset_name, 
                       (SELECT COUNT(*) FROM models WHERE dataset_id = e.dataset_id) as model_count
                FROM experiments e
                JOIN datasets d ON e.dataset_id = d.id
                ORDER BY e.created_at DESC
            ''')
            
            experiments = cursor.fetchall()
            conn.close()
            
            return render_template('experiments.html', experiments=experiments)
        
        @self.app.route('/experiment/<int:experiment_id>')
        def experiment_detail(experiment_id):
            conn = sqlite3.connect(self.experiment_manager.db.db_path)
            cursor = conn.cursor()
            
            # Get experiment details
            cursor.execute('''
                SELECT e.*, d.name as dataset_name FROM experiments e
                JOIN datasets d ON e.dataset_id = d.id
                WHERE e.id = ?
            ''', (experiment_id,))
            
            experiment = cursor.fetchone()
            
            # Get models for this experiment
            cursor.execute('''
                SELECT m.*, 
                       MAX(CASE WHEN mm.metric_name LIKE '%accuracy%' OR mm.metric_name LIKE '%r2%' THEN mm.metric_value END) as score
                FROM models m
                LEFT JOIN model_metrics mm ON m.id = mm.model_id
                WHERE m.dataset_id = (SELECT dataset_id FROM experiments WHERE id = ?)
                GROUP BY m.id
                ORDER BY score DESC
            ''', (experiment_id,))
            
            models = cursor.fetchall()
            conn.close()
            
            return render_template('experiment_detail.html', experiment=experiment, models=models)
        
        @self.app.route('/upload', methods=['GET', 'POST'])
        def upload_dataset():
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file selected')
                    return redirect(request.url)
                
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected')
                    return redirect(request.url)
                
                if file:
                    filename = file.filename
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Analyze dataset
                    df = self.experiment_manager.data_processor.load_dataset(filepath)
                    if df is not None:
                        analysis = self.experiment_manager.data_processor.analyze_dataset(df)
                        return render_template('create_experiment.html', 
                                             dataset_path=filepath, 
                                             analysis=analysis)
                    else:
                        flash('Error loading dataset')
                        return redirect(request.url)
            
            return render_template('upload.html')
        
        @self.app.route('/create_experiment', methods=['POST'])
        def create_experiment():
            data = request.form
            
            result = self.experiment_manager.create_experiment(
                name=data['name'],
                description=data['description'],
                dataset_path=data['dataset_path'],
                target_column=data['target_column'],
                problem_type=data['problem_type'],
                test_size=float(data.get('test_size', 0.2))
            )
            
            if result:
                flash('Experiment created successfully!')
                return redirect(url_for('experiment_detail', experiment_id=result['experiment_id']))
            else:
                flash('Error creating experiment')
                return redirect(url_for('upload_dataset'))
        
        @self.app.route('/run_experiment/<int:experiment_id>', methods=['POST'])
        def run_experiment(experiment_id):
            algorithms = request.form.getlist('algorithms')
            hyperparameter_tuning = 'hyperparameter_tuning' in request.form
            
            # Run experiment in background (simplified for demo)
            results = self.experiment_manager.run_experiment(
                experiment_id, algorithms, hyperparameter_tuning
            )
            
            if results:
                flash('Experiment completed successfully!')
            else:
                flash('Error running experiment')
            
            return redirect(url_for('experiment_detail', experiment_id=experiment_id))
        
        @self.app.route('/api/model_metrics/<int:model_id>')
        def get_model_metrics(model_id):
            conn = sqlite3.connect(self.experiment_manager.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_name, metric_value, metric_type FROM model_metrics
                WHERE model_id = ?
            ''', (model_id,))
            
            metrics = cursor.fetchall()
            conn.close()
            
            return jsonify([{
                'name': metric[0],
                'value': metric[1],
                'type': metric[2]
            } for metric in metrics])
        
        @self.app.route('/api/feature_importance/<int:model_id>')
        def get_feature_importance(model_id):
            conn = sqlite3.connect(self.experiment_manager.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT feature_name, importance_score FROM feature_importance
                WHERE model_id = ? ORDER BY importance_score DESC LIMIT 10
            ''', (model_id,))
            
            features = cursor.fetchall()
            conn.close()
            
            return jsonify([{
                'feature': feature[0],
                'importance': feature[1]
            } for feature in features])
        
        @self.app.route('/download_model/<int:model_id>')
        def download_model(model_id):
            conn = sqlite3.connect(self.experiment_manager.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT model_path, name FROM models WHERE id = ?', (model_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and os.path.exists(result[0]):
                return send_file(result[0], as_attachment=True, download_name=f"{result[1]}.pkl")
            else:
                flash('Model file not found')
                return redirect(url_for('dashboard'))
    
    def create_templates(self):
        """Create HTML templates."""
        template_dir = 'templates'
        os.makedirs(template_dir, exist_ok=True)
        
        # Dashboard template
        dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Model Trainer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; }
        .feature-card { height: 100%; transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain"></i> ML Trainer</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/experiments">Experiments</a>
                <a class="nav-link" href="/upload">Upload Dataset</a>
            </div>
        </div>
    </nav>

    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 mb-4">Machine Learning Model Trainer</h1>
            <p class="lead mb-4">Automated ML model training, evaluation, and comparison platform</p>
            <a href="/upload" class="btn btn-light btn-lg">
                <i class="fas fa-upload"></i> Start New Experiment
            </a>
        </div>
    </section>

    <div class="container py-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                        <h5>Automated Training</h5>
                        <p>Train multiple ML algorithms automatically with hyperparameter tuning</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-bar fa-3x text-success mb-3"></i>
                        <h5>Model Comparison</h5>
                        <p>Compare model performance with comprehensive metrics and visualizations</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-download fa-3x text-info mb-3"></i>
                        <h5>Model Export</h5>
                        <p>Download trained models for deployment in production environments</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-12">
                <h3 class="text-center mb-4">Supported Algorithms</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-sitemap"></i> Classification</h5>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success"></i> Random Forest</li>
                            <li><i class="fas fa-check text-success"></i> Logistic Regression</li>
                            <li><i class="fas fa-check text-success"></i> Support Vector Machine</li>
                            <li><i class="fas fa-check text-success"></i> Gradient Boosting</li>
                            <li><i class="fas fa-check text-success"></i> XGBoost</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-chart-line"></i> Regression</h5>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success"></i> Random Forest</li>
                            <li><i class="fas fa-check text-success"></i> Linear Regression</li>
                            <li><i class="fas fa-check text-success"></i> Ridge & Lasso</li>
                            <li><i class="fas fa-check text-success"></i> Support Vector Regression</li>
                            <li><i class="fas fa-check text-success"></i> XGBoost</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        # Upload template
        upload_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Dataset - ML Trainer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain"></i> ML Trainer</a>
        </div>
    </nav>

    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-upload"></i> Upload Dataset</h4>
                    </div>
                    <div class="card-body">
                        <form method="POST" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="file" class="form-label">Select Dataset File</label>
                                <input type="file" class="form-control" id="file" name="file" 
                                       accept=".csv,.xlsx,.xls,.json" required>
                                <div class="form-text">Supported formats: CSV, Excel, JSON</div>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-upload"></i> Upload and Analyze
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        # Create experiment template
        create_experiment_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Experiment - ML Trainer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain"></i> ML Trainer</a>
        </div>
    </nav>

    <div class="container py-5">
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-flask"></i> Create ML Experiment</h4>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="/create_experiment">
                            <input type="hidden" name="dataset_path" value="{{ dataset_path }}">
                            
                            <div class="mb-3">
                                <label for="name" class="form-label">Experiment Name</label>
                                <input type="text" class="form-control" id="name" name="name" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="description" class="form-label">Description</label>
                                <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label for="target_column" class="form-label">Target Column</label>
                                <select class="form-select" id="target_column" name="target_column" required>
                                    {% for column in analysis.columns %}
                                    <option value="{{ column }}">{{ column }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="problem_type" class="form-label">Problem Type</label>
                                <select class="form-select" id="problem_type" name="problem_type" required>
                                    <option value="classification">Classification</option>
                                    <option value="regression">Regression</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="test_size" class="form-label">Test Size</label>
                                <input type="number" class="form-control" id="test_size" name="test_size" 
                                       value="0.2" min="0.1" max="0.5" step="0.1">
                            </div>
                            
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-play"></i> Create Experiment
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-bar"></i> Dataset Summary</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Shape:</strong> {{ analysis.shape[0] }} rows × {{ analysis.shape[1] }} columns</p>
                        <p><strong>Numeric Columns:</strong> {{ analysis.numeric_columns|length }}</p>
                        <p><strong>Categorical Columns:</strong> {{ analysis.categorical_columns|length }}</p>
                        <p><strong>Missing Values:</strong> {{ analysis.missing_values.values()|sum }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        # Save templates
        with open(os.path.join(template_dir, 'ml_dashboard.html'), 'w') as f:
            f.write(dashboard_html)
        
        with open(os.path.join(template_dir, 'upload.html'), 'w') as f:
            f.write(upload_html)
        
        with open(os.path.join(template_dir, 'create_experiment.html'), 'w') as f:
            f.write(create_experiment_html)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the ML trainer web interface."""
        self.create_templates()
        
        print("🤖 Machine Learning Model Trainer")
        print("=" * 50)
        print(f"🚀 Starting ML training platform...")
        print(f"🌐 Access the dashboard at: http://{host}:{port}")
        print("\n🔥 ML Features:")
        print("   - Automated model training and comparison")
        print("   - Hyperparameter tuning with Grid/Random Search")
        print("   - Multiple algorithms for classification/regression")
        print("   - Model performance evaluation and metrics")
        print("   - Feature importance analysis")
        print("   - Model export and deployment")
        print("   - Experiment tracking and management")
        print("   - Web-based interface for easy use")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function to run the ML trainer."""
    print("🤖 Machine Learning Model Trainer")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Web Interface\n2. CLI Demo\nEnter choice (1-2): ")
    
    if choice == '2':
        # CLI demo
        print("\n🤖 ML Trainer - CLI Demo")
        print("Creating sample experiment...")
        
        # Create sample data
        from sklearn.datasets import make_classification, make_regression
        
        # Classification dataset
        X_class, y_class = make_classification(n_samples=1000, n_features=20, n_informative=10, 
                                             n_redundant=10, n_classes=2, random_state=42)
        df_class = pd.DataFrame(X_class, columns=[f'feature_{i}' for i in range(20)])
        df_class['target'] = y_class
        df_class.to_csv('sample_classification.csv', index=False)
        
        # Initialize experiment manager
        manager = MLExperimentManager()
        
        # Create experiment
        exp_result = manager.create_experiment(
            name="Sample Classification",
            description="Demo classification experiment",
            dataset_path="sample_classification.csv",
            target_column="target",
            problem_type="classification"
        )
        
        if exp_result:
            print(f"✅ Experiment created with ID: {exp_result['experiment_id']}")
            
            # Run experiment
            print("🏃 Running experiment with multiple algorithms...")
            results = manager.run_experiment(
                exp_result['experiment_id'],
                algorithms=['random_forest', 'logistic_regression', 'gradient_boosting'],
                hyperparameter_tuning=False
            )
            
            if results:
                print("\n📊 Results Summary:")
                for algorithm, result in results.items():
                    if result:
                        acc = result['metrics'].get('test_accuracy', 0)
                        print(f"  {algorithm}: {acc:.3f} accuracy")
                
                print("\n✅ Experiment completed successfully!")
            else:
                print("❌ Experiment failed")
        else:
            print("❌ Failed to create experiment")
    
    else:
        # Run web interface
        app = MLWebInterface()
        app.run()

if __name__ == "__main__":
    main()
