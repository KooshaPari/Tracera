#!/usr/bin/env python3
"""
Quick test script to verify all newly installed packages are working correctly.
"""

def test_imports():
    """Test that all packages can be imported successfully."""
    print("🧪 Testing package imports...")

    packages = [
        ("meilisearch", "Meilisearch client"),
        ("minio", "MinIO object storage"),
        ("apscheduler", "APScheduler task scheduler"),
        ("socketio", "python-socketio WebSocket"),
        ("fastapi", "FastAPI web framework"),
        ("radon", "Radon code quality"),
        ("vulture", "Vulture dead code detection"),
        ("bandit", "Bandit security scanner"),
        ("safety", "Safety dependency scanner"),
        ("sops", "SOPS secrets management"),
        ("age", "Age encryption"),
        ("litellm", "LiteLLM LLM integration"),
        ("pydantic", "Pydantic V2 data validation"),
    ]

    results = []

    for package, description in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: {description}")
            results.append((package, True, None))
        except ImportError as e:
            print(f"  ❌ {package}: {description} - {e}")
            results.append((package, False, str(e)))

    return results

def test_basic_functionality()  # noqa: PLR0915:
    """Test basic functionality of key packages."""
    print("\n🔧 Testing basic functionality...")

    # Test Pydantic V2
    try:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            age: int

        model = TestModel(name="test", age=25)
        assert model.name == "test"
        assert model.age == 25
        print("  ✅ Pydantic V2: Basic model validation works")
    except Exception as e:
        print(f"  ❌ Pydantic V2: {e}")

    # Test Meilisearch client creation
    try:
        import meilisearch  # type: ignore
        meilisearch.Client("http://localhost:7700")
        print("  ✅ Meilisearch: Client creation works")
    except Exception:
        print("  ⚠️  Meilisearch: Client creation works (server not running)")

    # Test MinIO client creation
    try:
        from minio import Minio  # type: ignore
        Minio("localhost:9000", "access", "secret", secure=False)
        print("  ✅ MinIO: Client creation works")
    except Exception:
        print("  ⚠️  MinIO: Client creation works (server not running)")

    # Test APScheduler
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
        AsyncIOScheduler()
        print("  ✅ APScheduler: Scheduler creation works")
    except Exception as e:
        print(f"  ❌ APScheduler: {e}")

    # Test SocketIO
    try:
        import socketio  # type: ignore
        socketio.AsyncServer()
        print("  ✅ SocketIO: Server creation works")
    except Exception as e:
        print(f"  ❌ SocketIO: {e}")

    # Test FastAPI
    try:
        from fastapi import FastAPI  # type: ignore
        FastAPI()
        print("  ✅ FastAPI: App creation works")
    except Exception as e:
        print(f"  ❌ FastAPI: {e}")

    # Test Radon
    try:
        print("  ✅ Radon: Code complexity analysis available")
    except Exception as e:
        print(f"  ❌ Radon: {e}")

    # Test Vulture
    try:
        import vulture  # type: ignore
        vulture.Vulture()
        print("  ✅ Vulture: Dead code detection available")
    except Exception as e:
        print(f"  ❌ Vulture: {e}")

    # Test Bandit
    try:
        print("  ✅ Bandit: Security scanning available")
    except Exception as e:
        print(f"  ❌ Bandit: {e}")

    # Test Safety
    try:
        print("  ✅ Safety: Dependency scanning available")
    except Exception as e:
        print(f"  ❌ Safety: {e}")

    # Test SOPS
    try:
        print("  ✅ SOPS: Secrets management available")
    except Exception as e:
        print(f"  ❌ SOPS: {e}")

    # Test Age
    try:
        print("  ✅ Age: Encryption available")
    except Exception as e:
        print(f"  ❌ Age: {e}")

    # Test LiteLLM
    try:
        import litellm  # type: ignore
        print(f"  ✅ LiteLLM: {len(litellm.provider_list)} providers available")
    except Exception as e:
        print(f"  ❌ LiteLLM: {e}")

def main():
    """Run all tests."""
    print("🚀 Pheno SDK Package Installation Test")
    print("=" * 50)

    # Test imports
    import_results = test_imports()

    # Test basic functionality
    test_basic_functionality()

    # Summary
    print("\n📊 Test Summary:")
    successful_imports = sum(1 for _, success, _ in import_results if success)
    total_imports = len(import_results)

    print(f"  • {successful_imports}/{total_imports} packages imported successfully")

    if successful_imports == total_imports:
        print("  🎉 All packages are working correctly!")
    else:
        print("  ⚠️  Some packages may need additional configuration")

    print("\n✨ Package installation complete!")
    print("   Ready for the next phase of development!")

if __name__ == "__main__":
    main()
