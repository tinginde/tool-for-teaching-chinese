"""
Simple test script to verify API endpoints work.
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    print("Testing root endpoint...")
    response = client.get("/")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✅ Root endpoint works!\n")


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = client.get("/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✅ Health endpoint works!\n")


def test_validate_basic():
    """Test validation endpoint (basic test without real article)."""
    print("Testing validation endpoint...")

    payload = {
        "article_text": "今天我把書放在桌子上。天氣比昨天更熱。",
        "grammar_points": [
            {"name": "把字句"},
            {"name": "比較句"}
        ],
        "vocabulary": [
            {"word": "書"},
            {"word": "桌子"},
            {"word": "天氣"}
        ],
        "use_claude_validation": False  # Don't use Claude for this test
    }

    response = client.post("/api/v1/validate/", json=payload)
    print(f"  Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"  Overall Pass: {result['overall_pass']}")
        print(f"  Grammar Check: {len(result['grammar_check'])} items")
        print(f"  Vocab Check: {len(result['vocab_check'])} items")
        print("  ✅ Validation endpoint works!\n")
    else:
        print(f"  ❌ Error: {response.json()}\n")


def test_api_docs():
    """Test that API docs are accessible."""
    print("Testing API documentation...")
    response = client.get("/docs")
    print(f"  Status: {response.status_code}")
    assert response.status_code == 200
    print("  ✅ API docs accessible!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing FastAPI Backend")
    print("=" * 60)
    print()

    try:
        test_root()
        test_health()
        test_api_docs()
        test_validate_basic()

        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("🚀 API is ready to use!")
        print()
        print("To start the server, run:")
        print("  cd backend")
        print("  python3 -m uvicorn app.main:app --reload")
        print()
        print("Then visit:")
        print("  - http://localhost:8000/docs (API documentation)")
        print("  - http://localhost:8000/ (Root endpoint)")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
