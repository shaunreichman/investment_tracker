#!/usr/bin/env python3
"""
Test script to call the fund API endpoint directly and see what data is returned.
This will help us understand why Fund ID 2 is returning Fund ID 3's data.
"""

import requests
import json

def test_fund_api():
    """Test the fund API endpoint directly."""
    
    base_url = "http://localhost:5000"  # Assuming backend runs on port 5000
    
    print("🧪 Testing Fund API Endpoints Directly")
    print("=" * 60)
    
    # Test Fund ID 2
    print("🔍 Testing Fund ID 2:")
    try:
        response = requests.get(f"{base_url}/api/funds/2")
        if response.status_code == 200:
            data = response.json()
            fund = data.get('fund', {})
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🏦 Fund ID: {fund.get('id')}")
            print(f"   📝 Fund Name: {fund.get('name')}")
            print(f"   🏢 Company: {fund.get('investment_company')}")
            print(f"   🔗 Company ID: {fund.get('investment_company_id')}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test Fund ID 3
    print("🔍 Testing Fund ID 3:")
    try:
        response = requests.get(f"{base_url}/api/funds/3")
        if response.status_code == 200:
            data = response.json()
            fund = data.get('fund', {})
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🏦 Fund ID: {fund.get('id')}")
            print(f"   📝 Fund Name: {fund.get('name')}")
            print(f"   🏢 Company: {fund.get('investment_company')}")
            print(f"   🔗 Company ID: {fund.get('investment_company_id')}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print()
    
    # Test Fund ID 1 for comparison
    print("🔍 Testing Fund ID 1:")
    try:
        response = requests.get(f"{base_url}/api/funds/1")
        if response.status_code == 200:
            data = response.json()
            fund = data.get('fund', {})
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🏦 Fund ID: {fund.get('id')}")
            print(f"   📝 Fund Name: {fund.get('name')}")
            print(f"   🏢 Company: {fund.get('investment_company')}")
            print(f"   🔗 Company ID: {fund.get('investment_company_id')}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    test_fund_api()
