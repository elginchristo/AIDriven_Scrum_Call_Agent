# test_projects_minimal.py - Minimal test for projects endpoint
import requests
import json


def test_projects_api():
    """Test projects API with minimal complexity."""
    base_url = "http://localhost:8000"

    print("🔍 Testing Projects API")
    print("=" * 40)

    # 1. Test GET projects (should work without auth in dev mode)
    print("\n1. GET /api/projects/")
    try:
        response = requests.get(f"{base_url}/api/projects/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 401:
            print("\n❌ Authentication is required!")
            print("Fix: Update app/dependencies.py or set ENV=development")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test POST project with minimal data
    print("\n2. POST /api/projects/")
    minimal_project = {
        "project_id": "MIN-001",
        "project_key": "MIN",
        "project_name": "Minimal Test",
        "project_type": "Software",
        "project_lead": "Test User"
    }

    try:
        response = requests.post(
            f"{base_url}/api/projects/",
            json=minimal_project
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 422:
            print("\n⚠️ Validation error - check required fields")
        elif response.status_code == 401:
            print("\n❌ Authentication required!")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test with all required fields
    print("\n3. POST /api/projects/ (all fields)")
    full_project = {
        "project_id": "FULL-001",
        "project_key": "FULL",
        "project_name": "Full Test Project",
        "project_type": "Software",
        "project_lead": "Test User",
        "project_description": "Test description",
        "project_url": "https://test.com",
        "project_category": "Test"
    }

    try:
        response = requests.post(
            f"{base_url}/api/projects/",
            json=full_project,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_projects_api()