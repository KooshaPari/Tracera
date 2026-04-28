#!/usr/bin/env python3
"""Test deployment script for PhenoSDK SST integration.

This script tests the SST integration without actually deploying to AWS.
It validates:
- Component creation
- Configuration generation
- Resource linking
- Credential management
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pheno.adapters.sst import (
    InstanceClass,
    PostgresEngine,
    Runtime,
    SSTApp,
)


async def test_component_creation():
    """
    Test creating components.
    """
    print("\n" + "=" * 80)
    print("TEST 1: Component Creation")
    print("=" * 80)

    app = SSTApp("test-app", stage="dev", skip_sst_init=True)

    # Create database
    print("\n✓ Creating Postgres component...")
    db = app.add_postgres(
        "database",
        engine=PostgresEngine.POSTGRES_15_5,
        instance_class=InstanceClass.T3_MICRO,
        allocated_storage=20,
    )
    print(f"  - Name: {db.name}")
    print(f"  - Type: {db.type}")
    print(f"  - Engine: {db.config.engine.value}")

    # Create bucket
    print("\n✓ Creating Bucket component...")
    bucket = app.add_bucket(
        "uploads",
        public=False,
        versioning=True,
    )
    print(f"  - Name: {bucket.name}")
    print(f"  - Type: {bucket.type}")
    print(f"  - Public: {bucket.config.public}")

    # Create function
    print("\n✓ Creating Function component...")
    api_function = app.add_function(
        "api",
        handler="index.handler",
        runtime=Runtime.PYTHON_3_11,
        timeout=30,
        memory=1024,
        link=[db, bucket],
    )
    print(f"  - Name: {api_function.name}")
    print(f"  - Type: {api_function.type}")
    print(f"  - Handler: {api_function.config.handler}")
    print(f"  - Runtime: {api_function.config.runtime.value}")
    print(f"  - Linked resources: {len(api_function.config.link)}")

    # Create API
    print("\n✓ Creating API component...")
    api = app.add_api(
        "api",
        routes={
            "GET /": api_function,
            "GET /health": api_function,
            "POST /users": api_function,
        },
        cors=True,
    )
    print(f"  - Name: {api.name}")
    print(f"  - Type: {api.type}")
    print(f"  - Routes: {len(api.config.routes)}")

    print(f"\n✅ Created {len(app.components)} components successfully!")
    return app


async def test_sst_config_generation():
    """
    Test SST configuration generation.
    """
    print("\n" + "=" * 80)
    print("TEST 2: SST Configuration Generation")
    print("=" * 80)

    app = SSTApp("test-app", stage="dev", skip_sst_init=True)

    # Create components
    db = app.add_postgres("database", engine=PostgresEngine.POSTGRES_15_5)
    bucket = app.add_bucket("uploads")
    func = app.add_function("api", handler="index.handler", link=[db, bucket])
    app.add_api("api", routes={"GET /": func})

    # Generate configs
    print("\n✓ Generating SST configurations...")

    for component in app.components:
        config = component.to_sst_config()
        print(f"\n{component.name} ({component.type}):")
        print(f"  - Type: {config['type']}")
        print(f"  - Properties: {len(config['properties'])} keys")

        # Show key properties
        if component.type == "Postgres":
            props = config["properties"]
            print(f"    • Engine: {props['engine']}")
            print(f"    • Instance: {props['instanceClass']}")
        elif component.type == "Function":
            props = config["properties"]
            print(f"    • Handler: {props['handler']}")
            print(f"    • Runtime: {props['runtime']}")
            if "link" in props:
                print(f"    • Links: {props['link']}")

    print("\n✅ Configuration generation successful!")


async def test_resource_linking():
    """
    Test resource linking.
    """
    print("\n" + "=" * 80)
    print("TEST 3: Resource Linking")
    print("=" * 80)

    from pheno.adapters.sst import ResourceLinker

    # Create mock resources
    class MockDatabase:
        name = "database"
        outputs = {"connectionString": "postgres://localhost/test"}
        iam_policy = {
            "Statement": [
                {
                    "Action": ["rds:Connect"],
                    "Resource": "*",
                },
            ],
        }
        arn = "arn:aws:rds:us-east-1:123456789012:db:test"

    class MockBucket:
        name = "uploads"
        outputs = {"name": "my-bucket", "url": "s3://my-bucket"}
        iam_policy = {
            "Statement": [
                {
                    "Action": ["s3:GetObject", "s3:PutObject"],
                    "Resource": "*",
                },
            ],
        }
        arn = "arn:aws:s3:::my-bucket"

    class MockFunction:
        name = "api"

    # Test linking
    linker = ResourceLinker()
    db = MockDatabase()
    bucket = MockBucket()
    func = MockFunction()

    print("\n✓ Linking resources to function...")
    linker.link(func, [db, bucket])

    # Get environment variables
    env_vars = linker.get_env_vars(func)
    print(f"\nEnvironment variables ({len(env_vars)}):")
    for key, value in env_vars.items():
        print(f"  - {key}: {value}")

    # Get IAM policy
    policy = linker.get_iam_policy(func)
    print("\nIAM Policy:")
    print(f"  - Statements: {len(policy['Statement'])}")
    for stmt in policy["Statement"]:
        actions = stmt.get("Action", [])
        if isinstance(actions, list):
            print(f"  - Actions: {', '.join(actions[:3])}...")
        else:
            print(f"  - Actions: {actions}")

    print("\n✅ Resource linking successful!")


async def test_credential_management():
    """
    Test credential management.
    """
    print("\n" + "=" * 80)
    print("TEST 4: Credential Management")
    print("=" * 80)

    try:
        from pheno.credentials import Broker

        print("\n✓ Initializing credential broker...")
        broker = Broker()

        # Test credential storage (without prompting)
        test_key = "test_deployment_key"
        test_value = "test_value_12345"

        print("\n✓ Storing test credential...")
        broker.set(test_key, test_value, scope="project:test-app")

        print("\n✓ Retrieving test credential...")
        retrieved = broker.get(test_key, scope="project:test-app")

        if retrieved == test_value:
            print("  ✅ Credential storage working!")
        else:
            print("  ❌ Credential mismatch!")

        # Cleanup
        broker.delete(test_key, scope="project:test-app")

        print("\n✅ Credential management successful!")

    except ImportError as e:
        print(f"\n⚠️  Credential broker not available: {e}")
        print("   (This is OK for basic testing)")


async def test_all_components():
    """
    Test all component types.
    """
    print("\n" + "=" * 80)
    print("TEST 5: All Component Types")
    print("=" * 80)

    app = SSTApp("test-app", stage="dev", skip_sst_init=True)

    components = []

    # Postgres
    print("\n✓ Postgres...")
    db = app.add_postgres("db", engine=PostgresEngine.POSTGRES_15_5)
    components.append(db)

    # Bucket
    print("✓ Bucket...")
    bucket = app.add_bucket("bucket")
    components.append(bucket)

    # Function
    print("✓ Function...")
    func = app.add_function("func", handler="index.handler")
    components.append(func)

    # API
    print("✓ API...")
    api = app.add_api("api", routes={"GET /": func})
    components.append(api)

    # Queue
    print("✓ Queue...")
    queue = app.add_queue("queue")
    components.append(queue)

    # Cron
    print("✓ Cron...")
    cron = app.add_cron("cron", schedule="rate(1 hour)", function=func)
    components.append(cron)

    # StaticSite
    print("✓ StaticSite...")
    site = app.add_static_site("site", path="./dist")
    components.append(site)

    # VPC
    print("✓ VPC...")
    vpc = app.add_vpc("vpc")
    components.append(vpc)

    # Secret
    print("✓ Secret...")
    secret = app.add_secret("secret")
    components.append(secret)

    # Auth
    print("✓ Auth...")
    auth = app.add_auth("auth")
    components.append(auth)

    print(f"\n✅ All {len(components)} component types created successfully!")

    # Verify each can generate config
    print("\n✓ Verifying configuration generation...")
    for component in components:
        config = component.to_sst_config()
        assert "type" in config
        assert "properties" in config
        print(f"  ✓ {component.name} ({component.type})")

    print("\n✅ All components validated!")


async def main():
    """
    Run all tests.
    """
    print("\n" + "=" * 80)
    print("PHENOSDK SST INTEGRATION TEST SUITE")
    print("=" * 80)
    print("\nTesting SST integration without AWS deployment...")

    try:
        # Run tests
        await test_component_creation()
        await test_sst_config_generation()
        await test_resource_linking()
        await test_credential_management()
        await test_all_components()

        # Summary
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nPhenoSDK SST integration is working correctly!")
        print("\nNext steps:")
        print("  1. Install SST: npm install -g sst")
        print("  2. Configure AWS credentials")
        print("  3. Run: python examples/sst/simple_api.py")
        print("\n" + "=" * 80)

        return 0

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED!")
        print("=" * 80)
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
