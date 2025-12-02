"""
Airflow DAG for Stock Volatility Prediction Pipeline
Orchestrates ETL and Model Training
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, '/opt/airflow/src')

from data.extract import DataExtractor
from data.quality_check import DataQualityChecker
from data.transform import StockDataTransformer
from models.train import VolatilityPredictor

from dotenv import load_dotenv
import pandas as pd
from ydata_profiling import ProfileReport

load_dotenv('/opt/airflow/.env')

# Default arguments
default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'stock_volatility_pipeline',
    default_args=default_args,
    description='End-to-end pipeline for stock volatility prediction',
    schedule_interval='@daily',  # Run daily
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'stock', 'volatility', 'prediction'],
)


def extract_data(**context):
    """Task 1: Extract data from Alpha Vantage API"""
    symbol = os.getenv("STOCK_SYMBOL", "AAPL")
    
    print(f"Extracting data for {symbol}...")
    extractor = DataExtractor(symbol=symbol)
    
    # Fetch daily data (uses fewer API calls than intraday)
    # Note: Free tier only supports "compact" (100 days)
    df = extractor.fetch_daily_data(outputsize="compact")
    
    # Save raw data
    output_path = "/opt/airflow/data/raw"
    filepath = extractor.save_raw_data(df, output_path)
    
    # Push filepath to XCom for next tasks
    context['ti'].xcom_push(key='raw_data_path', value=filepath)
    
    print(f"✓ Data extraction complete: {len(df)} rows")
    return filepath


def quality_check(**context):
    """Task 2: Perform data quality checks"""
    # Get raw data path from XCom
    ti = context['ti']
    raw_data_path = ti.xcom_pull(key='raw_data_path', task_ids='extract_data')
    
    print(f"Loading data from: {raw_data_path}")
    df = pd.read_csv(raw_data_path, index_col=0, parse_dates=True)
    
    # Run quality checks
    checker = DataQualityChecker(null_threshold=0.01)
    all_passed, checks, issues = checker.run_all_checks(df, min_rows=100)
    
    # Generate and save report
    report = checker.generate_report(df)
    print(report)
    
    report_path = raw_data_path.replace('.csv', '_quality_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Fail task if quality checks don't pass
    if not all_passed:
        raise ValueError(f"Data quality checks failed! Issues: {issues}")
    
    print("✓ All quality checks passed")
    ti.xcom_push(key='quality_passed', value=True)
    
    return report_path


def transform_data(**context):
    """Task 3: Transform data and engineer features"""
    ti = context['ti']
    raw_data_path = ti.xcom_pull(key='raw_data_path', task_ids='extract_data')
    
    print(f"Loading data from: {raw_data_path}")
    df = pd.read_csv(raw_data_path, index_col=0, parse_dates=True)
    
    # Transform data
    transformer = StockDataTransformer(target_column='close')
    df_transformed = transformer.transform(df, horizon=1)
    
    # Save processed data
    symbol = os.getenv("STOCK_SYMBOL", "AAPL")
    output_path = "/opt/airflow/data/processed"
    processed_path = transformer.save_processed_data(df_transformed, output_path, symbol)
    
    # Push processed data path to XCom
    ti.xcom_push(key='processed_data_path', value=processed_path)
    
    print(f"✓ Data transformation complete: {df_transformed.shape}")
    return processed_path


def generate_data_profile(**context):
    """Task 4: Generate data profiling report"""
    ti = context['ti']
    processed_data_path = ti.xcom_pull(key='processed_data_path', task_ids='transform_data')
    
    print(f"Generating data profile from: {processed_data_path}")
    df = pd.read_csv(processed_data_path, index_col=0, parse_dates=True)
    
    # Generate profile
    profile = ProfileReport(
        df,
        title="Stock Data Profiling Report",
        explorative=True,
        minimal=False
    )
    
    # Save report
    report_path = processed_data_path.replace('.csv', '_profile.html')
    profile.to_file(report_path)
    
    # Also save to reports directory
    reports_dir = "/opt/airflow/reports"
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_copy = os.path.join(reports_dir, f"data_profile_{timestamp}.html")
    profile.to_file(report_copy)
    
    ti.xcom_push(key='profile_report_path', value=report_path)
    
    print(f"✓ Data profile generated: {report_path}")
    return report_path


def train_model(**context):
    """Task 5: Train the prediction model"""
    ti = context['ti']
    processed_data_path = ti.xcom_pull(key='processed_data_path', task_ids='transform_data')
    
    print(f"Loading processed data from: {processed_data_path}")
    df = pd.read_csv(processed_data_path, index_col=0, parse_dates=True)
    
    # Train model
    predictor = VolatilityPredictor(experiment_name="stock_volatility_prediction")
    
    result = predictor.train_and_log(
        df,
        model_type="random_forest",
        hyperparameters={"n_estimators": 100, "max_depth": 10, "random_state": 42},
        run_name=f"airflow_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    # Save model locally
    predictor.save_model_locally("/opt/airflow/models", "production_model")
    
    # Push results to XCom
    ti.xcom_push(key='model_run_id', value=result['run_id'])
    ti.xcom_push(key='model_metrics', value=result['metrics'])
    
    print(f"✓ Model training complete")
    print(f"  Run ID: {result['run_id']}")
    print(f"  RMSE: {result['metrics']['rmse']:.6f}")
    print(f"  R²: {result['metrics']['r2']:.4f}")
    
    return result['run_id']


def version_data_with_dvc(**context):
    """Task 6: Version processed data with DVC"""
    ti = context['ti']
    processed_data_path = ti.xcom_pull(key='processed_data_path', task_ids='transform_data')
    
    print(f"Versioning data with DVC: {processed_data_path}")
    
    # Note: This assumes DVC is initialized
    # In production, you would run: dvc add {processed_data_path} && dvc push
    
    print("✓ Data versioned with DVC (placeholder)")
    return True


# Define tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

task_quality = PythonOperator(
    task_id='quality_check',
    python_callable=quality_check,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

task_profile = PythonOperator(
    task_id='generate_data_profile',
    python_callable=generate_data_profile,
    dag=dag,
)

task_train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

task_version = PythonOperator(
    task_id='version_data_dvc',
    python_callable=version_data_with_dvc,
    dag=dag,
)

# Define task dependencies
task_extract >> task_quality >> task_transform >> [task_profile, task_version] >> task_train
