"""
Model Training Module with MLflow Integration
Train models to predict stock volatility
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
from datetime import datetime
import joblib
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv
import json

load_dotenv()


class VolatilityPredictor:
    """Train and evaluate volatility prediction models"""
    
    def __init__(self, experiment_name: str = "stock_volatility_prediction"):
        """
        Initialize the predictor
        
        Args:
            experiment_name: Name for MLflow experiment
        """
        self.experiment_name = experiment_name
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = None
        
        # Setup MLflow
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Configure MLflow tracking"""
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set experiment
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                mlflow.create_experiment(self.experiment_name)
        except Exception as e:
            print(f"Warning: Could not set MLflow experiment: {e}")
        
        mlflow.set_experiment(self.experiment_name)
        print(f"MLflow tracking URI: {tracking_uri}")
        print(f"Experiment: {self.experiment_name}")
    
    def prepare_features(self, df: pd.DataFrame, target_col: str = 'target_volatility') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target
        
        Args:
            df: Processed dataframe
            target_col: Name of target column
        
        Returns:
            Tuple of (features, target)
        """
        # Exclude non-feature columns
        exclude_cols = [
            target_col, 'target_realized_vol', 'future_returns',
            'symbol', 'fetch_timestamp', 'open', 'high', 'low', 'close', 'volume'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y = df[target_col]
        
        self.feature_columns = feature_cols
        
        print(f"Features prepared: {len(feature_cols)} features")
        print(f"Target: {target_col}")
        print(f"Samples: {len(X)}")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Tuple:
        """
        Split data into train and test sets (time-aware)
        
        Args:
            X: Features
            y: Target
            test_size: Proportion of data for testing
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Use time-based split (last 20% for testing)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]
        
        print(f"Train set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict] = None
    ) -> object:
        """
        Train a model
        
        Args:
            X_train: Training features
            y_train: Training target
            model_type: Type of model to train
            hyperparameters: Model hyperparameters
        
        Returns:
            Trained model
        """
        # Default hyperparameters
        default_params = {
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "random_state": 42
            },
            "gradient_boosting": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 5,
                "random_state": 42
            },
            "ridge": {
                "alpha": 1.0,
                "random_state": 42
            },
            "lasso": {
                "alpha": 0.1,
                "random_state": 42
            }
        }
        
        params = hyperparameters or default_params.get(model_type, {})
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Initialize model
        if model_type == "random_forest":
            self.model = RandomForestRegressor(**params)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(**params)
        elif model_type == "ridge":
            self.model = Ridge(**params)
        elif model_type == "lasso":
            self.model = Lasso(**params)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        print(f"Training {model_type} model...")
        self.model.fit(X_train_scaled, y_train)
        print("✓ Model training complete")
        
        return self.model
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test target
        
        Returns:
            Dictionary of metrics
        """
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "mae": mean_absolute_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
            "mape": np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        }
        
        print(f"\nModel Evaluation:")
        print(f"  RMSE: {metrics['rmse']:.6f}")
        print(f"  MAE: {metrics['mae']:.6f}")
        print(f"  R²: {metrics['r2']:.4f}")
        print(f"  MAPE: {metrics['mape']:.2f}%")
        
        return metrics
    
    def train_and_log(
        self,
        df: pd.DataFrame,
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict] = None,
        run_name: Optional[str] = None
    ) -> Dict:
        """
        Complete training pipeline with MLflow logging
        
        Args:
            df: Processed dataframe
            model_type: Type of model to train
            hyperparameters: Model hyperparameters
            run_name: Name for MLflow run
        
        Returns:
            Dictionary with metrics and model info
        """
        with mlflow.start_run(run_name=run_name):
            # Prepare data
            X, y = self.prepare_features(df)
            X_train, X_test, y_train, y_test = self.split_data(X, y)
            
            # Log dataset info
            mlflow.log_param("dataset_size", len(df))
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            mlflow.log_param("n_features", len(self.feature_columns))
            
            # Log model type and hyperparameters
            mlflow.log_param("model_type", model_type)
            if hyperparameters:
                for key, value in hyperparameters.items():
                    mlflow.log_param(f"param_{key}", value)
            
            # Train model
            self.train_model(X_train, y_train, model_type, hyperparameters)
            
            # Evaluate model
            metrics = self.evaluate_model(X_test, y_test)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log feature importances for tree-based models
            if hasattr(self.model, 'feature_importances_'):
                feature_importance = pd.DataFrame({
                    'feature': self.feature_columns,
                    'importance': self.model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                # Save and log feature importance
                importance_path = "feature_importance.csv"
                feature_importance.to_csv(importance_path, index=False)
                mlflow.log_artifact(importance_path)
                os.remove(importance_path)
                
                print(f"\nTop 10 Important Features:")
                print(feature_importance.head(10))
            
            # Log model
            mlflow.sklearn.log_model(
                self.model,
                "model",
                registered_model_name=os.getenv("MODEL_NAME", "stock_volatility_predictor")
            )
            
            # Log scaler
            scaler_path = "scaler.pkl"
            joblib.dump(self.scaler, scaler_path)
            mlflow.log_artifact(scaler_path)
            os.remove(scaler_path)
            
            # Log feature columns
            with open("feature_columns.json", "w") as f:
                json.dump(self.feature_columns, f)
            mlflow.log_artifact("feature_columns.json")
            os.remove("feature_columns.json")
            
            run_id = mlflow.active_run().info.run_id
            print(f"\n✓ MLflow run completed: {run_id}")
            
            return {
                "run_id": run_id,
                "metrics": metrics,
                "model_type": model_type
            }
    
    def save_model_locally(self, output_path: str, model_name: str):
        """Save model and scaler locally"""
        os.makedirs(output_path, exist_ok=True)
        
        # Save model
        model_path = os.path.join(output_path, f"{model_name}.pkl")
        joblib.dump(self.model, model_path)
        
        # Save scaler
        scaler_path = os.path.join(output_path, f"{model_name}_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        # Save feature columns
        features_path = os.path.join(output_path, f"{model_name}_features.json")
        with open(features_path, "w") as f:
            json.dump(self.feature_columns, f)
        
        print(f"Model saved to: {model_path}")


def main():
    """Main training function"""
    # Load processed data
    data_path = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
    
    # Find most recent processed file
    files = [f for f in os.listdir(data_path) if f.startswith("processed_") and f.endswith(".csv")]
    if not files:
        print("No processed data found!")
        return
    
    latest_file = sorted(files)[-1]
    filepath = os.path.join(data_path, latest_file)
    
    print(f"Loading data from: {filepath}")
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    # Train model
    predictor = VolatilityPredictor()
    
    # Train multiple models for comparison
    models = [
        ("random_forest", {"n_estimators": 100, "max_depth": 10}),
        ("gradient_boosting", {"n_estimators": 100, "learning_rate": 0.1}),
        ("ridge", {"alpha": 1.0})
    ]
    
    results = []
    for model_type, params in models:
        print(f"\n{'='*60}")
        print(f"Training {model_type.upper()} model")
        print(f"{'='*60}")
        
        result = predictor.train_and_log(
            df,
            model_type=model_type,
            hyperparameters=params,
            run_name=f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        results.append(result)
        
        # Save best model locally
        if model_type == "random_forest":
            predictor.save_model_locally("./models", "best_model")
    
    print(f"\n{'='*60}")
    print("TRAINING SUMMARY")
    print(f"{'='*60}")
    for i, (model_type, _) in enumerate(models):
        print(f"\n{model_type.upper()}:")
        print(f"  Run ID: {results[i]['run_id']}")
        print(f"  RMSE: {results[i]['metrics']['rmse']:.6f}")
        print(f"  R²: {results[i]['metrics']['r2']:.4f}")


if __name__ == "__main__":
    main()
