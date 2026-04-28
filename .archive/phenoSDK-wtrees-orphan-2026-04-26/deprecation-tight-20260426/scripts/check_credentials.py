#!/usr/bin/env python3
"""
Check and display credential status for PhenoSDK.

This script helps verify that credentials are properly configured
and shows where they are being loaded from.
"""

import sys
from pathlib import Path

# Add pheno-sdk to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the simple broker directly to avoid complex broker circular import issues
import importlib.util

spec = importlib.util.spec_from_file_location(
    "credentials",
    Path(__file__).parent.parent / "src" / "pheno" / "credentials.py",
)
credentials = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credentials)

get_credential_broker = credentials.get_credential_broker
auto_detect_cloudflare_credentials = credentials.auto_detect_cloudflare_credentials
check_cloudflare_setup = credentials.check_cloudflare_setup


def main():
    """Check credential status."""
    print("🔍 PhenoSDK Credential Status Check\n")
    print("=" * 60)

    # Initialize broker (triggers auto-migration)
    broker = get_credential_broker()
    print(f"\n📁 Credential Storage: {broker.storage_path}")
    print(f"   Exists: {'✓' if broker.storage_path.exists() else '✗'}")

    # Check for legacy locations
    print("\n🔄 Legacy Credential Locations:")
    for cred_name, paths in broker.LEGACY_LOCATIONS.items():
        for path in paths:
            if path.exists():
                print(f"   ✓ Found: {path}")
                print("     → Will be migrated to global storage")

    # Check Cloudflare credentials
    print("\n☁️  Cloudflare Credentials:")
    cf_creds = auto_detect_cloudflare_credentials()

    for key, value in cf_creds.items():
        if value:
            # Mask the value
            if len(value) > 8:
                masked = value[:4] + "..." + value[-4:]
            else:
                masked = "***"
            print(f"   ✓ {key}: {masked}")
        else:
            print(f"   ✗ {key}: Not found")

    # Overall status
    print("\n" + "=" * 60)
    if check_cloudflare_setup():
        print("✅ All Cloudflare credentials are configured!")
        print("\n🚀 You're ready to use:")
        print("   cd atoms-mcp-prod")
        print("   python atoms_cli.py start")
    else:
        print("⚠️  Some Cloudflare credentials are missing")
        print("\n📝 To set credentials manually:")
        print('   python -c "from pheno.credentials import set_credential;')
        print("              set_credential('CLOUDFLARE_API_TOKEN', 'your-token')\"")
        print("\n   Or place them in ~/.kinfra/cloudflare_token")

    # List all stored credentials
    print("\n📋 All Stored Credentials:")
    all_creds = broker.list_credentials()
    if all_creds:
        for key, masked_value in all_creds.items():
            print(f"   • {key}: {masked_value}")
    else:
        print("   (none)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
