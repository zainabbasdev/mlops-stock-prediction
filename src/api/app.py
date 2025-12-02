"""
FastAPI Prediction Service with Prometheus Monitoring
Serves real-time stock volatility predictions
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import Response
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Stock Volatility Prediction API",
    description="Real-time prediction service for stock market volatility",
    version="1.0.0"
)

# Prometheus metrics
prediction_counter = Counter(
    'predictions_total',
    'Total number of predictions made',
    ['model_version', 'status']
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction request latency',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

drift_ratio = Gauge(
    'data_drift_ratio',
    'Ratio of out-of-distribution features'
)

model_score = Gauge(
    'model_prediction_score',
    'Average model prediction score'
)

# Instrument app with Prometheus
Instrumentator().instrument(app).expose(app)


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    close: float = Field(..., description="Current close price")
    open: float = Field(..., description="Current open price")
    high: float = Field(..., description="Current high price")
    low: float = Field(..., description="Current low price")
    volume: int = Field(..., description="Current volume")
    
    # Optional: pre-computed features
    returns: Optional[float] = None
    volatility_5: Optional[float] = None
    rsi: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "close": 150.25,
                "open": 149.80,
                "high": 151.00,
                "low": 149.50,
                "volume": 5000000
            }
        }


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: float = Field(..., description="Predicted volatility")
    timestamp: str = Field(..., description="Prediction timestamp")
    model_version: str = Field(..., description="Model version used")
    confidence_score: Optional[float] = Field(None, description="Prediction confidence")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": 0.0234,
                "timestamp": "2024-12-02T10:30:00",
                "model_version": "v1.0.0",
                "confidence_score": 0.85
            }
        }


class ModelService:
    """Model loading and prediction service"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.model_version = "v1.0.0"
        self.feature_stats = {}  # For drift detection
        
        self.load_model()
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            # Load model
            model_file = os.path.join(self.model_path, "production_model.pkl")
            if not os.path.exists(model_file):
                model_file = os.path.join(self.model_path, "best_model.pkl")
            
            self.model = joblib.load(model_file)
            print(f"✓ Model loaded from: {model_file}")
            
            # Load scaler
            scaler_file = model_file.replace(".pkl", "_scaler.pkl")
            self.scaler = joblib.load(scaler_file)
            print(f"✓ Scaler loaded from: {scaler_file}")
            
            # Load feature columns
            features_file = model_file.replace(".pkl", "_features.json")
            with open(features_file, 'r') as f:
                self.feature_columns = json.load(f)
            print(f"✓ Feature columns loaded: {len(self.feature_columns)} features")
            
            # Load feature statistics for drift detection
            self._initialize_feature_stats()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load model: {e}")
            print(f"ℹ️  Service will start without a model. Train a model first using Airflow.")
            self.model = None
            self.scaler = None
            self.feature_columns = []
    
    def _initialize_feature_stats(self):
        """Initialize feature statistics for drift detection"""
        # In production, load from training data statistics
        # For now, use placeholder values
        self.feature_stats = {
            'mean': {},
            'std': {},
            'min': {},
            'max': {}
        }
    
    def create_features(self, data: Dict) -> pd.DataFrame:
        """
        Create features from input data
        
        Args:
            data: Dictionary with OHLCV data
        
        Returns:
            DataFrame with engineered features
        """
        # Create a simple feature vector
        # In production, this would use the same feature engineering as training
        
        # For demo, create basic features
        features = {}
        
        # Price-based features
        features['close'] = data['close']
        features['returns'] = data.get('returns', 0.0)
        features['volatility_5'] = data.get('volatility_5', 0.0)
        features['rsi'] = data.get('rsi', 50.0)
        
        # Create dummy features for missing ones
        # In production, maintain a sliding window of historical data
        for col in self.feature_columns:
            if col not in features:
                features[col] = 0.0  # Placeholder
        
        # Ensure correct order
        df = pd.DataFrame([features])[self.feature_columns]
        
        return df
    
    def detect_drift(self, features: pd.DataFrame) -> float:
        """
        Detect data drift by checking if features are out of expected range
        
        Args:
            features: Input features
        
        Returns:
            Drift ratio (0-1)
        """
        if not self.feature_stats or not self.feature_stats.get('mean'):
            return 0.0
        
        # Count features outside 3 standard deviations
        out_of_range = 0
        total = len(features.columns)
        
        for col in features.columns:
            if col in self.feature_stats['mean']:
                mean = self.feature_stats['mean'][col]
                std = self.feature_stats['std'][col]
                value = features[col].values[0]
                
                if abs(value - mean) > 3 * std:
                    out_of_range += 1
        
        drift = out_of_range / total if total > 0 else 0.0
        return drift
    
    def predict(self, data: Dict) -> Dict:
        """
        Make a prediction
        
        Args:
            data: Input data dictionary
        
        Returns:
            Prediction result dictionary
        """
        start_time = datetime.now()
        
        try:
            # Create features
            features = self.create_features(data)
            
            # Detect drift
            drift = self.detect_drift(features)
            drift_ratio.set(drift)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            
            # Calculate latency
            latency = (datetime.now() - start_time).total_seconds()
            prediction_latency.observe(latency)
            
            # Update metrics
            prediction_counter.labels(
                model_version=self.model_version,
                status='success'
            ).inc()
            
            model_score.set(float(prediction))
            
            # Calculate confidence (placeholder - in production, use proper methods)
            confidence = max(0.5, 1.0 - drift)
            
            result = {
                'prediction': float(prediction),
                'timestamp': datetime.now().isoformat(),
                'model_version': self.model_version,
                'confidence_score': float(confidence),
                'latency_ms': latency * 1000,
                'drift_detected': drift > 0.1
            }
            
            return result
            
        except Exception as e:
            prediction_counter.labels(
                model_version=self.model_version,
                status='error'
            ).inc()
            raise e


# Initialize model service
model_service = ModelService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Stock Volatility Prediction API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_service.model is not None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make a volatility prediction
    
    Args:
        request: Prediction request with stock data
    
    Returns:
        Prediction response
    """
    try:
        # Convert request to dict
        data = request.dict()
        
        # Make prediction
        result = model_service.predict(data)
        
        return PredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    """
    Make batch predictions
    
    Args:
        requests: List of prediction requests
    
    Returns:
        List of predictions
    """
    try:
        results = []
        for req in requests:
            data = req.dict()
            result = model_service.predict(data)
            results.append(result)
        
        return {"predictions": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/model/info")
async def model_info():
    """Get model information"""
    return {
        "model_version": model_service.model_version,
        "model_type": type(model_service.model).__name__,
        "feature_count": len(model_service.feature_columns),
        "features": model_service.feature_columns[:10]  # First 10 features
    }


@app.post("/alerts")
async def receive_alert(request: Request):
    """
    Webhook endpoint to receive Grafana alerts
    Logs alerts to file for monitoring
    """
    try:
        alert_data = await request.json()
        
        # Log alert to file
        log_dir = "/app/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "grafana_alerts.log")
        
        timestamp = datetime.now().isoformat()
        log_entry = f"\n{'='*80}\n"
        log_entry += f"[{timestamp}] GRAFANA ALERT RECEIVED\n"
        log_entry += f"{'-'*80}\n"
        log_entry += json.dumps(alert_data, indent=2)
        log_entry += f"\n{'='*80}\n"
        
        with open(log_file, "a") as f:
            f.write(log_entry)
        
        print(f"⚠️  Alert received and logged to {log_file}")
        
        return {
            "status": "received",
            "timestamp": timestamp,
            "message": "Alert logged successfully"
        }
        
    except Exception as e:
        print(f"Error processing alert: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
