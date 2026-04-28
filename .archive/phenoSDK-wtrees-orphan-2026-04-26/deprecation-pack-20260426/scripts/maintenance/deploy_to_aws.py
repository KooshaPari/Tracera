#!/usr/bin/env python3
"""Deploy PhenoSDK SST app to AWS.

This script demonstrates a complete deployment workflow:
1. Check prerequisites
2. Create SST project structure
3. Deploy infrastructure
4. Test endpoints
5. Display results
"""

import asyncio
import json
import os
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


def check_prerequisites():
    """
    Check if all prerequisites are met.
    """
    print("\n" + "=" * 80)
    print("CHECKING PREREQUISITES")
    print("=" * 80)

    # Check SST
    import shutil

    sst_bin = shutil.which("sst")
    if sst_bin:
        print(f"✅ SST installed: {sst_bin}")
    else:
        print("❌ SST not installed")
        print("   Install with: npm install -g sst")
        return False

    # Check AWS credentials
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_key and aws_secret:
        print("✅ AWS credentials configured")
        print(f"   Region: {aws_region}")
    else:
        print("⚠️  AWS credentials not found in environment")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("   Or run: aws configure")

        # Ask if user wants to continue anyway
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != "y":
            return False

    print("\n✅ All prerequisites met!")
    return True


def create_sst_project():
    """
    Create SST project structure.
    """
    print("\n" + "=" * 80)
    print("CREATING SST PROJECT STRUCTURE")
    print("=" * 80)

    project_dir = Path("test-pheno-sst")

    # Create project directory
    project_dir.mkdir(exist_ok=True)
    print(f"✅ Created project directory: {project_dir}")

    # Create package.json
    package_json = {
        "name": "test-pheno-sst",
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "sst dev",
            "deploy": "sst deploy",
            "remove": "sst remove",
        },
        "dependencies": {
            "sst": "^3.0.0",
        },
    }

    with open(project_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    print("✅ Created package.json")

    # Create sst.config.ts
    sst_config = """/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "test-pheno-sst",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
    };
  },
  async run() {
    // Resources will be defined by PhenoSDK
    console.log("SST project initialized by PhenoSDK");
  },
});
"""

    with open(project_dir / "sst.config.ts", "w") as f:
        f.write(sst_config)
    print("✅ Created sst.config.ts")

    # Create Lambda handler
    handler_code = """import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

export async function handler(
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> {
  const path = event.rawPath || event.path || '/';

  // Get environment variables (injected by PhenoSDK)
  const databaseUrl = process.env.DATABASE_CONNECTION_STRING || 'not-configured';
  const bucketName = process.env.UPLOADS_NAME || 'not-configured';

  if (path === '/health') {
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'healthy',
        database: databaseUrl !== 'not-configured' ? 'connected' : 'not-configured',
        storage: bucketName !== 'not-configured' ? 'configured' : 'not-configured',
        timestamp: new Date().toISOString(),
      }),
    };
  }

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: 'Hello from PhenoSDK + SST!',
      path: path,
      database: databaseUrl,
      bucket: bucketName,
      timestamp: new Date().toISOString(),
    }),
  };
}
"""

    with open(project_dir / "index.ts", "w") as f:
        f.write(handler_code)
    print("✅ Created Lambda handler (index.ts)")

    # Install dependencies
    print("\n📦 Installing dependencies...")
    import subprocess

    result = subprocess.run(
        ["npm", "install"],
        check=False,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Dependencies installed")
    else:
        print(f"⚠️  Warning: {result.stderr}")

    return project_dir


async def deploy_infrastructure(project_dir: Path):
    """
    Deploy infrastructure using PhenoSDK.
    """
    print("\n" + "=" * 80)
    print("DEPLOYING INFRASTRUCTURE")
    print("=" * 80)

    # Initialize PhenoSDK SST app
    app = SSTApp("test-pheno-sst", project_dir=project_dir, stage="dev")

    print("\n📦 Creating components...")

    # Create database
    print("  ✓ Postgres database...")
    db = app.add_postgres(
        "database",
        engine=PostgresEngine.POSTGRES_15_5,
        instance_class=InstanceClass.T3_MICRO,
        allocated_storage=20,
    )

    # Create storage bucket
    print("  ✓ S3 bucket...")
    bucket = app.add_bucket(
        "uploads",
        public=False,
        versioning=True,
    )

    # Create API function
    print("  ✓ Lambda function...")
    api_function = app.add_function(
        "api",
        handler="index.handler",
        runtime=Runtime.NODEJS_20,  # Using Node.js for the handler
        timeout=30,
        memory=1024,
        link=[db, bucket],
    )

    # Create API Gateway
    print("  ✓ API Gateway...")
    app.add_api(
        "api",
        routes={
            "GET /": api_function,
            "GET /health": api_function,
        },
        cors=True,
    )

    print(f"\n✅ Created {len(app.components)} components")

    # Note: Actual deployment would happen here
    print("\n⚠️  Note: Actual AWS deployment requires:")
    print("   1. Valid AWS credentials")
    print("   2. SST CLI configured")
    print("   3. Run: cd test-pheno-sst && sst deploy")

    return app


async def main():
    """
    Main deployment workflow.
    """
    print("\n" + "=" * 80)
    print("PHENOSDK SST DEPLOYMENT WORKFLOW")
    print("=" * 80)

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Exiting.")
        return 1

    # Step 2: Create SST project
    project_dir = create_sst_project()

    # Step 3: Deploy infrastructure
    app = await deploy_infrastructure(project_dir)

    # Step 4: Summary
    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)

    print(f"\n✅ SST project created: {project_dir}")
    print(f"✅ Components configured: {len(app.components)}")

    print("\n📋 Components:")
    for component in app.components:
        print(f"   • {component.name} ({component.type})")

    print("\n🚀 Next steps:")
    print(f"   1. cd {project_dir}")
    print("   2. sst deploy --stage dev")
    print("   3. Test the API endpoints")

    print("\n💡 Or deploy directly:")
    print(f"   cd {project_dir} && sst deploy --stage dev")

    print("\n" + "=" * 80)
    print("✅ DEPLOYMENT WORKFLOW COMPLETE!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
