import requests
import json

BASE_URL = "http://localhost:5000"

print("🧪 Testing Backend Connection...")
print("=" * 60)

# Test 1: Check if backend is running
try:
    response = requests.get(f"{BASE_URL}/")
    print("✅ Backend is running!")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")
    print("   Make sure backend is running: python app.py")
    exit(1)

# Test 2: Get attendance data
try:
    response = requests.get(f"{BASE_URL}/api/attendance/today?branch=AIML&section=A")
    data = response.json()
    print("\n✅ Attendance API working!")
    print(f"   Present: {data['data']['present']}")
    print(f"   Total: {data['data']['total']}")
except Exception as e:
    print(f"\n❌ Attendance API failed: {e}")

# Test 3: Test start attendance
try:
    response = requests.post(
        f"{BASE_URL}/api/attendance/start",
        json={"branch": "AIML", "section": "A"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    print(f"\n✅ Start API working!")
    print(f"   Response: {data['message']}")
except Exception as e:
    print(f"\n❌ Start API failed: {e}")

print("=" * 60)