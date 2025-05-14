# verify_api.py - Quick API verification
import requests
import json
from datetime import datetime


def verify_api():
    """Verify the API is running correctly."""
    base_url = "http://localhost:8000"

    print("🔍 Verifying API endpoints...\n")

    # 1. Check root endpoint
    print("1. Checking root endpoint...")
    response = requests.get(f"{base_url}/")
    if response.status_code == 200:
        print(f"✓ Root endpoint: {response.json()['message']}")
    else:
        print(f"✗ Root endpoint failed: {response.status_code}")

    # 2. Check health endpoint
    print("\n2. Checking health endpoint...")
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"✓ Health check: {health_data['status']}")
        print(f"  Environment: {health_data['environment']}")
        print(f"  Database: {health_data['database']}")
    else:
        print(f"✗ Health check failed: {response.status_code}")

    # 3. Check API documentation
    print("\n3. Checking API documentation...")
    response = requests.get(f"{base_url}/docs")
    if response.status_code == 200:
        print("✓ API documentation is accessible")
        print(f"  Access it at: {base_url}/docs")
    else:
        print(f"✗ API documentation failed: {response.status_code}")

    # 4. Try to create a test project
    print("\n4. Testing project creation...")
    project_data = {
        "project_id": f"TEST-{int(datetime.now().timestamp())}",
        "project_key": "TEST",
        "project_name": "API Test Project",
        "project_type": "Software",
        "project_lead": "Test User",
        "project_description": "Created by API verification script"
    }

    response = requests.post(f"{base_url}/api/projects/", json=project_data)
    if response.status_code == 201:
        project = response.json()
        print(f"✓ Project created: {project['project_id']}")
    else:
        print(f"✗ Project creation failed: {response.status_code}")
        print(f"  Response: {response.text}")

    print("\n✅ API verification complete!")
    print(f"\nYou can now:")
    print(f"- Access the API at: {base_url}")
    print(f"- View the documentation at: {base_url}/docs")
    print(f"- Run full tests with: python test_run.py")


if __name__ == "__main__":
    verify_api()