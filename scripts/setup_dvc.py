"""
DVC Configuration Script
Initialize DVC and configure remote storage
"""

import subprocess
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Run shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Output: {result.stdout}")
    return result


def initialize_dvc():
    """Initialize DVC in the project"""
    print("\n=== Initializing DVC ===")
    
    # Initialize DVC
    run_command("dvc init", check=False)
    
    # Configure DVC remote (MinIO/S3)
    print("\n=== Configuring DVC Remote ===")
    
    # Add remote storage
    run_command(
        "dvc remote add -d minio s3://mlops-data",
        check=False
    )
    
    # Configure endpoint for MinIO
    run_command(
        "dvc remote modify minio endpointurl http://localhost:9000",
        check=False
    )
    
    # Set credentials
    run_command(
        "dvc remote modify minio access_key_id minioadmin",
        check=False
    )
    
    run_command(
        "dvc remote modify minio secret_access_key minioadmin",
        check=False
    )
    
    print("\n✓ DVC initialized successfully")
    print("Remote storage: MinIO (S3-compatible) at http://localhost:9000")


def add_data_to_dvc():
    """Add data files to DVC tracking"""
    print("\n=== Adding data to DVC ===")
    
    # Track processed data
    data_paths = [
        "data/processed",
        "data/raw"
    ]
    
    for path in data_paths:
        if os.path.exists(path):
            run_command(f"dvc add {path}", check=False)
            print(f"✓ Added {path} to DVC tracking")
    
    print("\n✓ Data files added to DVC")
    print("Remember to commit .dvc files to git:")
    print("  git add data/*.dvc .dvcignore")
    print("  git commit -m 'Add data tracking with DVC'")


def push_data_to_remote():
    """Push data to remote storage"""
    print("\n=== Pushing data to remote ===")
    
    result = run_command("dvc push", check=False)
    
    if result.returncode == 0:
        print("✓ Data pushed to remote storage")
    else:
        print("⚠ Could not push data. Ensure MinIO is running and accessible.")


if __name__ == "__main__":
    print("=" * 60)
    print("DVC Setup for MLOps Project")
    print("=" * 60)
    
    initialize_dvc()
    
    print("\n" + "=" * 60)
    print("DVC setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start MinIO: docker-compose up -d minio")
    print("2. Create bucket 'mlops-data' in MinIO console (http://localhost:9001)")
    print("3. Run this script again to add and push data")
    print("4. Use 'dvc add <file>' to track new data files")
    print("5. Use 'dvc push' to sync data to remote storage")
