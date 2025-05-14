# test_redis.py - Test Redis connection and basic operations
import redis
import json
import asyncio
from datetime import datetime


def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("Testing Redis connection...")

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    try:
        # Test connection
        if r.ping():
            print("✓ Redis connection successful!")
        else:
            print("✗ Redis connection failed!")
            return False
    except Exception as e:
        print(f"✗ Redis connection error: {e}")
        return False

    # Test basic operations
    print("\nTesting basic Redis operations...")

    # SET operation
    test_key = "test:scrum:agent"
    test_value = {"message": "Hello from Scrum Agent!", "timestamp": datetime.utcnow().isoformat()}

    try:
        r.set(test_key, json.dumps(test_value))
        print(f"✓ SET operation successful - Key: {test_key}")
    except Exception as e:
        print(f"✗ SET operation failed: {e}")
        return False

    # GET operation
    try:
        retrieved = r.get(test_key)
        if retrieved:
            data = json.loads(retrieved)
            print(f"✓ GET operation successful - Value: {data}")
        else:
            print("✗ GET operation failed - No value found")
            return False
    except Exception as e:
        print(f"✗ GET operation failed: {e}")
        return False

    # Expiry test
    try:
        r.expire(test_key, 60)  # Expire in 60 seconds
        ttl = r.ttl(test_key)
        print(f"✓ EXPIRE operation successful - TTL: {ttl} seconds")
    except Exception as e:
        print(f"✗ EXPIRE operation failed: {e}")
        return False

    # List operations
    list_key = "test:scrum:list"
    try:
        r.lpush(list_key, "Agent1", "Agent2", "Agent3")
        list_length = r.llen(list_key)
        print(f"✓ LPUSH operation successful - List length: {list_length}")

        items = r.lrange(list_key, 0, -1)
        print(f"✓ LRANGE operation successful - Items: {items}")
    except Exception as e:
        print(f"✗ List operations failed: {e}")
        return False

    # Hash operations
    hash_key = "test:scrum:call:123"
    try:
        r.hset(hash_key, mapping={
            "status": "in_progress",
            "participants": json.dumps(["John", "Jane", "Bob"]),
            "start_time": datetime.utcnow().isoformat()
        })
        print(f"✓ HSET operation successful")

        call_status = r.hget(hash_key, "status")
        print(f"✓ HGET operation successful - Status: {call_status}")

        all_fields = r.hgetall(hash_key)
        print(f"✓ HGETALL operation successful - Fields: {all_fields}")
    except Exception as e:
        print(f"✗ Hash operations failed: {e}")
        return False

    # Pub/Sub test
    print("\nTesting Pub/Sub functionality...")
    channel = "scrum:notifications"

    try:
        # Publish a message
        r.publish(channel, json.dumps({"event": "test", "data": "Hello Agents!"}))
        print(f"✓ PUBLISH operation successful - Channel: {channel}")
    except Exception as e:
        print(f"✗ PUBLISH operation failed: {e}")
        return False

    # Clean up
    try:
        r.delete(test_key, list_key, hash_key)
        print("\n✓ Cleanup successful")
    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")

    print("\nAll Redis tests completed successfully!")
    return True


def test_redis_for_agents():
    """Test Redis operations specific to agent communication."""
    print("\nTesting Redis for agent communication...")

    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Simulate agent communication
    call_id = "test_call_001"

    # DrivingCall Agent stores questions
    questions_key = f"call:{call_id}:questions"
    questions = [
        {"team_member": "John", "question": "What did you complete yesterday?"},
        {"team_member": "John", "question": "What are you working on today?"},
        {"team_member": "John", "question": "Any blockers?"}
    ]

    try:
        r.set(questions_key, json.dumps(questions), ex=3600)
        print(f"✓ DrivingCall Agent stored questions")
    except Exception as e:
        print(f"✗ Failed to store questions: {e}")
        return False

    # UserValidation Agent retrieves and processes
    try:
        retrieved_questions = json.loads(r.get(questions_key))
        print(f"✓ UserValidation Agent retrieved {len(retrieved_questions)} questions")
    except Exception as e:
        print(f"✗ Failed to retrieve questions: {e}")
        return False

    # Store response
    response_key = f"call:{call_id}:response:john"
    response = {
        "team_member": "John",
        "response": "Completed login module. Working on authentication. No blockers.",
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        r.set(response_key, json.dumps(response), ex=3600)
        print(f"✓ Response stored for John")
    except Exception as e:
        print(f"✗ Failed to store response: {e}")
        return False

    # Overall Agent aggregates data
    status_key = f"call:{call_id}:status"
    try:
        r.hset(status_key, mapping={
            "total_participants": "4",
            "responses_received": "1",
            "blockers_identified": "0",
            "status": "in_progress"
        })

        status = r.hgetall(status_key)
        print(f"✓ Overall Agent updated status: {status}")
    except Exception as e:
        print(f"✗ Failed to update status: {e}")
        return False

    print("\nAgent communication tests completed successfully!")
    return True


if __name__ == "__main__":
    print("=== Redis Testing Suite for Scrum Agent ===\n")

    # Test basic Redis functionality
    if test_redis_connection():
        # Test agent-specific operations
        test_redis_for_agents()
    else:
        print("\nRedis connection failed. Please ensure Redis is running:")
        print("brew services start redis")