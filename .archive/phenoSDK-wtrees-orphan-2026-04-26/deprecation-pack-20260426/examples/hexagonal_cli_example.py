#!/usr/bin/env python3
"""Example demonstrating the hexagonal architecture CLI adapter.

This example shows how to use the CLI adapter with dependency injection to manage users,
deployments, services, and configurations.
"""

import asyncio

from pheno.adapters.cli.commands import (
    ConfigurationCommands,
    DeploymentCommands,
    ServiceCommands,
    UserCommands,
)
from pheno.adapters.container_config import configure_in_memory_container


async def main():
    """
    Run CLI adapter examples.
    """
    print("=" * 60)
    print("Hexagonal Architecture CLI Adapter Example")
    print("=" * 60)
    print()

    # Configure container with in-memory implementations
    container = configure_in_memory_container()

    # Resolve command handlers
    user_commands = container.resolve(UserCommands)
    deployment_commands = container.resolve(DeploymentCommands)
    service_commands = container.resolve(ServiceCommands)
    config_commands = container.resolve(ConfigurationCommands)

    # ========== User Management Examples ==========
    print("\n" + "=" * 60)
    print("USER MANAGEMENT")
    print("=" * 60)

    # Create users
    print("\n1. Creating users...")
    await user_commands.create("alice@example.com", "Alice Smith")
    await user_commands.create("bob@example.com", "Bob Johnson")
    await user_commands.create("charlie@example.com", "Charlie Brown")

    # List users
    print("\n2. Listing all users...")
    await user_commands.list()

    # Get specific user (you'll need to get the ID from the list above)
    # await user_commands.get("user-id-here")

    # ========== Deployment Management Examples ==========
    print("\n" + "=" * 60)
    print("DEPLOYMENT MANAGEMENT")
    print("=" * 60)

    # Create deployments
    print("\n1. Creating deployments...")
    await deployment_commands.create("production", "blue_green")
    await deployment_commands.create("staging", "rolling")
    await deployment_commands.create("development", "recreate")

    # List deployments
    print("\n2. Listing all deployments...")
    await deployment_commands.list()

    # Get deployment statistics
    print("\n3. Getting deployment statistics...")
    await deployment_commands.statistics()
    await deployment_commands.statistics("production")

    # ========== Service Management Examples ==========
    print("\n" + "=" * 60)
    print("SERVICE MANAGEMENT")
    print("=" * 60)

    # Create services
    print("\n1. Creating services...")
    await service_commands.create("api-server", 8000, "http")
    await service_commands.create("grpc-server", 50051, "grpc")
    await service_commands.create("websocket-server", 8080, "http")

    # List services
    print("\n2. Listing all services...")
    await service_commands.list()

    # Get service health
    print("\n3. Getting service health status...")
    await service_commands.health()

    # ========== Configuration Management Examples ==========
    print("\n" + "=" * 60)
    print("CONFIGURATION MANAGEMENT")
    print("=" * 60)

    # Create configurations
    print("\n1. Creating configurations...")
    await config_commands.create("app.name", "Pheno SDK", "Application name")
    await config_commands.create("app.version", "2.0.0", "Application version")
    await config_commands.create("app.debug", False, "Debug mode enabled")
    await config_commands.create("database.host", "localhost", "Database host")
    await config_commands.create("database.port", 5432, "Database port")

    # List configurations
    print("\n2. Listing all configurations...")
    await config_commands.list()

    # Get specific configuration
    print("\n3. Getting specific configuration...")
    await config_commands.get("app.name")

    # Update configuration
    print("\n4. Updating configuration...")
    await config_commands.update("app.version", value="2.1.0")
    await config_commands.get("app.version")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
