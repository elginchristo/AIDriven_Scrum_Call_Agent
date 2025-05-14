# verify_setup.py - Verify database and API setup
import requests
import pymongo
from datetime import datetime


def check_mongodb():
    """Check MongoDB connection and data."""
    print("🔍 Checking MongoDB...")
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client.scrum_agent

        collections = db.list_collection_names()
        print(f"✓ Connected to MongoDB")
        print(f"  Collections: {collections}")

        # Check data counts
        counts = {
            "projects": db.projects.count_documents({}),
            "sprints": db.sprint_progress.count_documents({}),
            "stories": db.user_stories.count_documents({}),
            "team_members": db.contact_details.count_documents({}),
            "blockers": db.blockers.count_documents({}),
            "scheduled_calls": db.scheduled_calls.count_documents({})
        }

        print("\n📊 Data counts:")
        for collection, count in counts.items():
            print(f"  {collection}: {count}")

        return True
    except Exception as e:
        print(f"✗ MongoDB error: {e}")
        return False


def check_api():
    """Check API endpoints."""
    print("\n🔍 Checking API...")
    try:
        # Check health
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ API is running")
            health_data = response.json()
            print(f"  Status: {health_data['status']}")
            print(f"  Database: {health_data['database']}")
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False

        # Check projects endpoint
        response = requests.get("http://localhost:8000/api/projects/")
        if response.status_code == 200:
            projects = response.json()
            print(f"✓ Projects endpoint working - {len(projects)} projects found")
        else:
            print(f"✗ Projects endpoint failed: {response.status_code}")

        return True
    except Exception as e:
        print(f"✗ API error: {e}")
        print("  Make sure the API is running: uvicorn app.main:app --reload")
        return False


def show_sample_data():
    """Show sample data from the database."""
    print("\n📋 Sample Data:")
    try:
        # Show a project
        response = requests.get("http://localhost:8000/api/projects/")
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project = projects[0]
                print(f"\nProject: {project['project_name']}")
                print(f"  ID: {project['project_id']}")
                print(f"  Lead: {project['project_lead']}")

                # Show stories for this project
                response = requests.get(f"http://localhost:8000/api/stories/?project_id={project['project_id']}")
                if response.status_code == 200:
                    stories = response.json()
                    print(f"\n  User Stories ({len(stories)} total):")
                    for story in stories[:3]:
                        print(f"    - {story['story_title']} ({story['status']})")
    except Exception as e:
        print(f"Error showing sample data: {e}")


if __name__ == "__main__":
    print("🚀 Verifying Scrum Agent Setup")
    print("=" * 40)

    # Check MongoDB
    mongodb_ok = check_mongodb()

    # Check API
    api_ok = check_api()

    # Show sample data if everything is working
    if mongodb_ok and api_ok:
        show_sample_data()
        print("\n✅ Setup verified successfully!")
        print("\nNext steps:")
        print("1. Access API docs: http://localhost:8000/docs")
        print("2. Run comprehensive tests: python test_with_mock_data.py")
        print("3. View dashboard: python view_dashboard.py")
    else:
        print("\n❌ Setup verification failed. Please fix the issues above.")