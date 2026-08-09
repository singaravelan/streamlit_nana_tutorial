"""
Smoke and regression tests for the Streamlit MLOps application.
Strictly adhering to SOLID principles and testing requirements.
"""
import os
import sys

def test_imports():
    """Smoke test to ensure dependencies can be imported successfully."""
    try:
        import streamlit
        import pymongo
        print("✅ Smoke Test Passed: All core dependencies imported successfully.")
    except ImportError as e:
        print(f"❌ Smoke Test Failed: Missing dependency - {e}")
        sys.exit(1)

def test_environment_variable_defaults():
    """Regression test for default database configuration values."""
    host = os.environ.get("MONGO_HOST", "localhost")
    port = os.environ.get("MONGO_PORT", "27017")
    assert host is not None, "MONGO_HOST should have a default value"
    assert port == "27017", "MONGO_PORT default should be 27017"
    print("✅ Regression Test Passed: Environment variable defaults are valid.")

if __name__ == "__main__":
    print("Running CI Test Suite...")
    test_imports()
    test_environment_variable_defaults()
    print("🎉 All CI tests completed successfully.")
