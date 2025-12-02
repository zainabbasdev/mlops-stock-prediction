# Instructions for Team Members

## 📦 Package Distribution

Two zip files have been created in `team_packages/` directory:
- `member2_data_ml_pipeline.zip` - For Member 2
- `member3_api_monitoring.zip` - For Member 3

---

## 👤 SibghatUllah - Data Pipeline & ML Training

### Your Package Contents:
- `src/data/` - Data extraction, quality checks, transformation
- `src/models/` - Model training with MLflow
- `tests/` - Unit tests for data pipeline
- `requirements.txt` - Dependencies

### Setup Instructions:

1. **Extract your files:**
   ```bash
   unzip member2_data_ml_pipeline.zip -d member2_workspace
   cd member2_workspace
   ```

2. **Clone the main repository:**
   ```bash
   git clone <repo-url-from-member1>
   cd mlops-project
   ```

3. **Create your feature branch:**
   ```bash
   git checkout -b feature/data-pipeline
   ```

4. **Copy your files to the repository:**
   ```bash
   cp -r ../member2_workspace/src ./
   cp -r ../member2_workspace/tests ./
   ```

5. **Setup Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Test your code locally:**
   ```bash
   # Test data extraction
   export ALPHA_VANTAGE_API_KEY=your_key
   python src/data/extract.py
   
   # Test transformation
   python src/data/transform.py
   
   # Test model training
   python src/models/train.py
   
   # Run unit tests
   pytest tests/ -v
   ```

7. **Commit your work:**
   ```bash
   git add src/data/ src/models/ tests/
   git commit -m "feat: implement data pipeline and ML training
   
   - Add data extraction from Alpha Vantage API
   - Implement quality validation checks
   - Add feature engineering with 50+ features
   - Implement model training with MLflow
   - Add comprehensive unit tests"
   
   git push origin feature/data-pipeline
   ```

8. **Create Pull Request:**
   - Go to GitHub repository
   - Create PR from `feature/data-pipeline` to `dev`
   - Add description of your changes
   - Request review from team

### Your Responsibilities:
- ✅ Data extraction from API
- ✅ Data quality validation
- ✅ Feature engineering (50+ features)
- ✅ Model training with MLflow
- ✅ Unit tests for all components
- ✅ Documentation in code

### Key Files You Own:
- `src/data/extract.py` - API data fetching
- `src/data/quality_check.py` - Quality validation
- `src/data/transform.py` - Feature engineering
- `src/models/train.py` - Model training
- `tests/test_*.py` - Unit tests

---

## Ali Hamza - API Service & Monitoring

### Your Package Contents:
- `src/api/` - FastAPI prediction service
- `monitoring/` - Prometheus & Grafana configs
- `scripts/test_api.py` - API testing script
- `requirements.txt` - Dependencies

### Setup Instructions:

1. **Extract your files:**
   ```bash
   unzip member3_api_monitoring.zip -d member3_workspace
   cd member3_workspace
   ```

2. **Clone the main repository:**
   ```bash
   git clone <repo-url-from-member1>
   cd mlops-project
   ```

3. **Create your feature branch:**
   ```bash
   git checkout -b feature/api-monitoring
   ```

4. **Copy your files to the repository:**
   ```bash
   cp -r ../member3_workspace/src/api ./src/
   cp -r ../member3_workspace/monitoring ./
   cp ../member3_workspace/scripts/test_api.py ./scripts/
   ```

5. **Setup Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Test your code locally:**
   ```bash
   # Start API service
   cd src/api
   uvicorn app:app --reload
   
   # In another terminal, test the API
   python scripts/test_api.py
   
   # Test endpoints manually
   curl http://localhost:8000/health
   curl http://localhost:8000/metrics
   ```

7. **Commit your work:**
   ```bash
   git add src/api/ monitoring/ scripts/test_api.py
   git commit -m "feat: implement API service and monitoring
   
   - Add FastAPI prediction service with 6 endpoints
   - Implement Prometheus metrics collection
   - Create Grafana dashboards for monitoring
   - Add data drift detection
   - Implement automated alerting
   - Add comprehensive API testing"
   
   git push origin feature/api-monitoring
   ```

8. **Create Pull Request:**
   - Go to GitHub repository
   - Create PR from `feature/api-monitoring` to `dev`
   - Add description of your changes
   - Request review from team

### Your Responsibilities:
- ✅ FastAPI prediction service
- ✅ Prometheus metrics integration
- ✅ Grafana dashboard creation
- ✅ Data drift detection
- ✅ API endpoint testing
- ✅ Documentation in code

### Key Files You Own:
- `src/api/app.py` - FastAPI service
- `src/api/Dockerfile` - API container
- `monitoring/prometheus/prometheus.yml` - Metrics config
- `monitoring/grafana/dashboards/` - Dashboards
- `scripts/test_api.py` - API tests

---

## 🔄 Integration Workflow

### For Both Members 2 & 3:

1. **Stay Updated:**
   ```bash
   git fetch origin
   git rebase origin/dev
   ```

2. **Before Creating PR:**
   - Run your tests: `pytest tests/` or `python scripts/test_api.py`
   - Check code quality: `flake8 src/`
   - Format code: `black src/`

3. **PR Description Template:**
   ```markdown
   ## Changes
   - List your main changes
   
   ## Testing
   - Describe how you tested
   
   ## Screenshots (if applicable)
   - Add screenshots of dashboards, API responses, etc.
   
   ## Checklist
   - [ ] Code tested locally
   - [ ] Unit tests pass
   - [ ] Code formatted with black
   - [ ] No linting errors
   - [ ] Documentation updated
   ```

4. **After PR Review:**
   - Address review comments
   - Update code as needed
   - Request re-review

5. **After Merge:**
   - Delete your feature branch
   - Pull latest dev: `git checkout dev && git pull`

---

## 📋 Dependencies Between Components

**Member 2 → Member 3**: 
- API (Member 3) needs models trained by Member 2
- API loads model files from `models/` directory
- API uses same feature engineering logic

**Member 1 → Members 2 & 3**:
- Both need docker-compose from Member 1
- Both need .env.example for configuration
- Both need airflow DAG structure

---

## 🧪 Testing Guidelines

### Member 2 Testing:
```bash
# Test data extraction
export ALPHA_VANTAGE_API_KEY=demo  # Use demo key for testing
python src/data/extract.py

# Test quality checks
pytest tests/test_quality_check.py -v

# Test transformation
pytest tests/test_transform.py -v

# Test model training (with dummy data)
pytest tests/ --cov=src/data --cov=src/models
```

### Member 3 Testing:
```bash
# Start API locally
cd src/api
uvicorn app:app --reload --port 8000

# Run test script
python scripts/test_api.py

# Manual tests
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"close":150,"open":149,"high":151,"low":149,"volume":5000000}'
```

---

## 📞 Communication

### Daily Updates:
- Share progress in team chat
- Report any blockers
- Ask questions early

### Code Reviews:
- Review each other's PRs
- Provide constructive feedback
- Test the changes locally

### Integration Meeting:
- Schedule after both members complete their parts
- Test integration together
- Fix any integration issues

---

## ⚠️ Common Issues & Solutions

### Issue: Import errors
**Solution**: Make sure `__init__.py` files are present in all directories

### Issue: API can't find model
**Solution**: Ensure Member 2 has trained and saved models first

### Issue: Tests fail
**Solution**: Check if you have all required dependencies installed

### Issue: Git conflicts
**Solution**: Communicate before working on shared files

---

## 🎯 Definition of Done

### For Member 2:
- [ ] All data pipeline code committed
- [ ] Unit tests pass (>80% coverage)
- [ ] Code formatted and linted
- [ ] Can extract data from API
- [ ] Can train model successfully
- [ ] Models saved to `models/` directory
- [ ] PR created and reviewed

### For Member 3:
- [ ] API service code committed
- [ ] Monitoring configurations committed
- [ ] API responds to all endpoints
- [ ] Metrics exposed correctly
- [ ] Grafana dashboard loads
- [ ] API tests pass
- [ ] PR created and reviewed

---

## 📚 Resources

### For Member 2:
- Alpha Vantage API: https://www.alphavantage.co/documentation/
- MLflow Docs: https://mlflow.org/docs/latest/
- Pandas: https://pandas.pydata.org/docs/
- Scikit-learn: https://scikit-learn.org/

### For Member 3:
- FastAPI: https://fastapi.tiangolo.com/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- Pydantic: https://docs.pydantic.dev/

---

## 🚀 Timeline

**Week 1**: Individual development and testing
**Week 2**: Create PRs and code review
**Week 3**: Integration and testing
**Week 4**: Final deployment

---

## ✉️ Contact

If you have questions:
1. Check this documentation first
2. Check TEAM_DISTRIBUTION.md
3. Ask in team chat
4. Schedule a call with team

---

**Good luck! Let's build something amazing together! 🎉**
