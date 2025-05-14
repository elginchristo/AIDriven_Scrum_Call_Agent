# verify_system.py - System verification script
import subprocess
import requests
import psutil
import sys


def check_service_running(service_name):
    """Check if a service is running."""
    for proc in psutil.process_iter(['pid', 'name']):
        if service_name.lower() in proc.info['name'].lower():
            return True
    return False


def check_port_open(port):
    """Check if a port is open."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0


def verify_system():
    """Verify the entire system is running correctly."""
    print("🔍 Verifying Scrum Agent System...\n")

    all_good = True

    # Check MongoDB
    print("1. Checking MongoDB...")
    if check_service_running('mongod'):
        print("   ✓ MongoDB is running")
        if check_port_open(27017):
            print("   ✓ MongoDB port 27017 is open")
        else:
            print("   ✗ MongoDB port 27017 is not accessible")
            all_good = False
    else:
        print("   ✗ MongoDB is not running")
        print("   Run: brew services start mongodb-community")
        all_good = False

    # Check Redis
    print("\n2. Checking Redis...")
    if check_service_running('redis'):
        print("   ✓ Redis is running")
        if check_port_open(6379):
            print("   ✓ Redis port 6379 is open")
        else:
            print("   ✗ Redis port 6379 is not accessible")
            all_good = False
    else:
        print("   ✗ Redis is not running")
        print("   Run: brew services start redis")
        all_good = False

    # Check FastAPI
    print("\n3. Checking FastAPI...")
    if check_port_open(8000):
        print("   ✓ FastAPI port 8000 is open")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("   ✓ FastAPI is responding")
            else:
                print("   ✗ FastAPI health check failed")
                all_good = False
        except:
            print("   ✗ FastAPI is not responding")
            all_good = False
    else:
        print("   ✗ FastAPI is not running")
        print("   Run: uvicorn app.main:app --reload")
        all_good = False

    # Check Python version
    print("\n4. Checking Python version...")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 10:
        print(f"   ✓ Python {python_version.major}.{python_version.minor} is installed")
    else:
        print(f"   ✗ Python 3.10+ required, found {python_version.major}.{python_version.minor}")
        all_good = False

    # Summary
    print("\n" + "=" * 40)
    if all_good:
        print("✅ All systems are running correctly!")
        print("\nYou can now:")
        print("1. Access the API at: http://localhost:8000")
        print("2. View API docs at: http://localhost:8000/docs")
        print("3. Run tests with: python test_run.py")
    else:
        print("❌ Some systems are not running correctly.")
        print("Please fix the issues above before proceeding.")

    return all_good


if __name__ == "__main__":
    verify_system()