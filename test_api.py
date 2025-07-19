#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:5001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health check: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test portfolio summary
    try:
        response = requests.get(f"{base_url}/api/dashboard/portfolio-summary")
        print(f"Portfolio summary: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Total funds: {data.get('total_funds')}")
            print(f"Total equity: {data.get('total_equity_balance')}")
    except Exception as e:
        print(f"Portfolio summary failed: {e}")
    
    # Test funds endpoint
    try:
        response = requests.get(f"{base_url}/api/dashboard/funds")
        print(f"Funds endpoint: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Number of funds: {len(data.get('funds', []))}")
    except Exception as e:
        print(f"Funds endpoint failed: {e}")

if __name__ == "__main__":
    test_api() 