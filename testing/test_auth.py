# test_auth.py - Test authentication setup
import requests

BASE_URL = "http://localhost:8000"


def test_endpoints():
    """Test various endpoints to check authentication."""
    print("🔍 Testing API Authentication Setup")
    print("=" * 50)

    endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/docs", "API Documentation"),
        ("/api/projects/", "Projects API")
    ]

    for endpoint, name in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"\n{name} ({endpoint}):")
        print(f"  Status: {response.status_code}")

        if response.status_code == 401:
            print("  ❌ Authentication required")
            print("  Fix: Update app/dependencies.py to allow development access")
        elif response.status_code == 200:
            print("  ✓ Accessible")
        else:
            print(f"  ⚠️ Unexpected status: {response.text[:100]}")

    # Check environment
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"\nEnvironment: {data.get('environment', 'unknown')}")
        if data.get('environment') != 'development':
            print("⚠️  Not in development mode. Set ENV=development in .env file")


if __name__ == "__main__":
    test_endpoints()