#!/bin/bash

# Quick Start Script for MLOps Project
# This script helps you get started quickly

set -e

echo "======================================"
echo "MLOps Project - Quick Start"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker found${NC}"

command -v docker-compose >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker Compose found${NC}"

command -v python3 >/dev/null 2>&1 || {
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Python 3 found${NC}"

echo ""

# Setup environment
echo "Setting up environment..."

if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys!${NC}"
    echo -e "${YELLOW}  - ALPHA_VANTAGE_API_KEY${NC}"
    echo -e "${YELLOW}  - MLFLOW credentials (optional)${NC}"
    echo ""
    read -p "Press Enter after you've updated .env..."
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/raw data/processed data/cache models reports logs
touch data/raw/.gitkeep data/processed/.gitkeep models/.gitkeep reports/.gitkeep
echo -e "${GREEN}✓ Directories created${NC}"

# Initialize DVC
echo "Initializing DVC..."
if [ ! -d ".dvc" ]; then
    dvc init > /dev/null 2>&1
    echo -e "${GREEN}✓ DVC initialized${NC}"
else
    echo -e "${GREEN}✓ DVC already initialized${NC}"
fi

# Generate Fernet key for Airflow
if ! grep -q "AIRFLOW__CORE__FERNET_KEY=.*[a-zA-Z0-9]" .env; then
    echo "Generating Fernet key for Airflow..."
    FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY" >> .env
    echo -e "${GREEN}✓ Fernet key generated${NC}"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Start services: docker-compose up -d"
echo "2. Wait for services to start (2-3 minutes)"
echo "3. Access services:"
echo "   - Airflow: http://localhost:8080 (admin/admin)"
echo "   - MinIO: http://localhost:9001 (minioadmin/minioadmin)"
echo "   - API: http://localhost:8000/docs"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "4. Create MinIO bucket 'mlops-data'"
echo "5. Trigger Airflow DAG: stock_volatility_pipeline"
echo ""
echo -e "${GREEN}Happy MLOps! 🚀${NC}"
