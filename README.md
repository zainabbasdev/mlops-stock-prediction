# MLOps Real-Time Predictive System
## Stock Volatility Prediction with Complete MLOps Pipeline

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready MLOps pipeline for predicting stock market volatility using real-time data from Alpha Vantage API.

---

## 🎯 Overview

This project implements a comprehensive MLOps pipeline demonstrating:
- **Automated ETL Pipeline** with Apache Airflow
- **Data Quality Validation** with mandatory quality gates
- **Feature Engineering** with 50+ technical indicators
- **Model Training & Tracking** with MLflow
- **Real-time Predictions** via FastAPI
- **Continuous Monitoring** with Prometheus & Grafana
- **CI/CD Pipeline** with GitHub Actions

### Problem Statement
Predict short-term stock volatility (1-hour ahead) using historical OHLCV data and technical indicators.

---

## 🏗️ Architecture

```
Alpha Vantage API → Airflow DAG → [Extract → Validate → Transform → Train]
                                          ↓
                                    MLflow + DVC
                                          ↓
                                    FastAPI Service
                                          ↓
                              Prometheus + Grafana
```

---

## 🛠️ Tech Stack

- **Orchestration**: Apache Airflow
- **ML Framework**: Scikit-learn, MLflow
- **API**: FastAPI
- **Monitoring**: Prometheus, Grafana
- **Data Versioning**: DVC, MinIO
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions, CML

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Alpha Vantage API Key ([Get free key](https://www.alphavantage.co/support/#api-key))

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/your-username/mlops-stock-prediction.git
   cd mlops-stock-prediction
   ```

2. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ALPHA_VANTAGE_API_KEY
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access services**
   - Airflow UI: http://localhost:8080 (admin/admin)
   - Prediction API: http://localhost:8000/docs
   - Grafana: http://localhost:3000 (admin/admin)
   - MinIO: http://localhost:9001 (minioadmin/minioadmin)

5. **Trigger pipeline**
   - Open Airflow UI
   - Enable `stock_volatility_pipeline` DAG
   - Trigger manually or wait for scheduled run

---

## 📊 Features

### Data Pipeline
- ✅ Live API integration with Alpha Vantage
- ✅ Automated quality validation (fails on issues >1%)
- ✅ 50+ engineered features (RSI, MACD, Bollinger Bands)
- ✅ Data versioning with DVC + MinIO

### ML Pipeline
- ✅ Multiple algorithms (Random Forest, Gradient Boosting)
- ✅ MLflow experiment tracking
- ✅ Automated model selection
- ✅ Feature importance analysis

### Deployment
- ✅ REST API for predictions
- ✅ Batch prediction support
- ✅ Docker containerization
- ✅ Health monitoring endpoints

### Monitoring
- ✅ Real-time metrics (latency, throughput)
- ✅ Data drift detection
- ✅ Grafana dashboards
- ✅ Automated alerting

### CI/CD
- ✅ Automated testing (pytest, linting)
- ✅ Model performance comparison (CML)
- ✅ Continuous deployment
- ✅ Docker registry integration

---

## 📖 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Make Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "close": 150.25,
    "open": 149.80,
    "high": 151.00,
    "low": 149.50,
    "volume": 5000000
  }'
```

### Batch Predictions
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {"close": 150.25, "open": 149.80, "high": 151.00, "low": 149.50, "volume": 5000000},
    {"close": 151.30, "open": 150.90, "high": 152.00, "low": 150.50, "volume": 5200000}
  ]'
```

---

## 🔄 CI/CD Pipeline

### Branch Strategy
- `dev` → Development and integration
- `test` → Staging with model validation
- `main` → Production deployment

### Automated Workflows
1. **Dev Branch**: Code quality checks, linting, unit tests
2. **Test Branch**: Full model retraining, CML comparison
3. **Main Branch**: Docker build, registry push, deployment

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v --cov=src

# Test API
python scripts/test_api.py

# Lint code
flake8 src/ --max-line-length=100
```

---

## 📈 Monitoring

Access Grafana at http://localhost:3000 to view:
- Prediction request rates
- API latency (p95, p99)
- Data drift metrics
- Model performance
- System health

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Project Structure

```
├── airflow/              # Airflow DAGs and configuration
├── src/
│   ├── data/            # Data pipeline (extraction, validation, transformation)
│   ├── models/          # Model training and evaluation
│   └── api/             # FastAPI prediction service
├── monitoring/          # Prometheus & Grafana configurations
├── tests/               # Unit tests
├── scripts/             # Utility scripts
├── .github/workflows/   # CI/CD pipelines
└── docker-compose.yml   # Service orchestration
```

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ End-to-end MLOps pipeline
- ✅ Production ML system design
- ✅ Automated data validation
- ✅ Model monitoring & drift detection
- ✅ CI/CD for ML systems
- ✅ Infrastructure as Code
- ✅ Microservices architecture

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by the MLOps Team

---

## 🙏 Acknowledgments

- [Alpha Vantage](https://www.alphavantage.co/) for stock market data API
- [MLflow](https://mlflow.org/) for experiment tracking
- [Apache Airflow](https://airflow.apache.org/) for orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for API framework

---

## 📞 Support

For questions or issues, please [open an issue](https://github.com/your-username/mlops-stock-prediction/issues).

---

**⭐ If you find this project useful, please give it a star!**
