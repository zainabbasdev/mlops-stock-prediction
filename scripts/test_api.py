"""
Utility script to test the prediction API
"""

import requests
import json
import time
from datetime import datetime


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_prediction():
    """Test prediction endpoint"""
    print("\n=== Testing Prediction Endpoint ===")
    
    data = {
        "close": 150.25,
        "open": 149.80,
        "high": 151.00,
        "low": 149.50,
        "volume": 5000000
    }
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:8000/predict", json=data)
        latency = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Latency: {latency*1000:.2f} ms")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("\n=== Testing Batch Prediction Endpoint ===")
    
    data = [
        {
            "close": 150.25,
            "open": 149.80,
            "high": 151.00,
            "low": 149.50,
            "volume": 5000000
        },
        {
            "close": 151.30,
            "open": 150.90,
            "high": 152.00,
            "low": 150.50,
            "volume": 5200000
        },
        {
            "close": 149.80,
            "open": 150.20,
            "high": 151.50,
            "low": 149.00,
            "volume": 4800000
        }
    ]
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:8000/predict/batch", json=data)
        latency = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Latency: {latency*1000:.2f} ms")
        print(f"Predictions: {response.json()['count']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_model_info():
    """Test model info endpoint"""
    print("\n=== Testing Model Info Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/model/info")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_metrics():
    """Test Prometheus metrics endpoint"""
    print("\n=== Testing Metrics Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/metrics")
        print(f"Status: {response.status_code}")
        print("Sample metrics:")
        lines = response.text.split('\n')[:20]
        for line in lines:
            if line and not line.startswith('#'):
                print(f"  {line}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_load_test(num_requests=100):
    """Run a simple load test"""
    print(f"\n=== Running Load Test ({num_requests} requests) ===")
    
    data = {
        "close": 150.25,
        "open": 149.80,
        "high": 151.00,
        "low": 149.50,
        "volume": 5000000
    }
    
    latencies = []
    successes = 0
    failures = 0
    
    start_time = time.time()
    
    for i in range(num_requests):
        try:
            req_start = time.time()
            response = requests.post("http://localhost:8000/predict", json=data)
            req_latency = time.time() - req_start
            
            if response.status_code == 200:
                successes += 1
                latencies.append(req_latency)
            else:
                failures += 1
                
        except Exception as e:
            failures += 1
    
    total_time = time.time() - start_time
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print(f"\nResults:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successes}")
        print(f"  Failed: {failures}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Requests/sec: {num_requests/total_time:.2f}")
        print(f"  Avg latency: {avg_latency*1000:.2f} ms")
        print(f"  P95 latency: {p95_latency*1000:.2f} ms")
    else:
        print("No successful requests!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Single Prediction", test_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("Model Info", test_model_info),
        ("Metrics", test_metrics)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
        time.sleep(0.5)
    
    # Run load test
    run_load_test(num_requests=50)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
