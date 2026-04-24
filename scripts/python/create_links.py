#!/usr/bin/env python3
"""create_links module."""

from typing import Any

"""Create traceability links between related items to make projects more realistic."""

from pathlib import Path

import yaml


def add_link_to_item(item_path: Any, target_id: Any, link_type: Any) -> bool:
    """Add a link to an item's frontmatter."""
    if not item_path.exists():
        return False

    content = item_path.read_text()

    # Parse frontmatter
    if not content.startswith("---"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    frontmatter_text = parts[1]
    body = parts[2]

    frontmatter = yaml.safe_load(frontmatter_text) or {}

    # Add link if not already present
    links = frontmatter.get("links", [])
    link_exists = any(link.get("target") == target_id and link.get("type") == link_type for link in links)

    if not link_exists:
        links.append({"target": target_id, "type": link_type})
        frontmatter["links"] = links

        # Update frontmatter
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False)
        new_content = f"---\n{new_frontmatter}---{body}"
        item_path.write_text(new_content)
        return True

    return False


def create_demo_project_links() -> None:
    """Create links in DEMO_PROJECT."""
    project_path = Path("./samples/DEMO_PROJECT/.trace")

    # Story -> Endpoint links (implements)
    story_endpoint_pairs = [
        ("STORY-001", "ENDPOINT-004"),  # Login story -> login endpoint
        ("STORY-001", "ENDPOINT-005"),  # Login story -> register endpoint
        ("STORY-009", "ENDPOINT-008"),  # Product search -> GET /api/products
        ("STORY-009", "ENDPOINT-009"),  # Product search -> GET /api/products/:id
        ("STORY-015", "ENDPOINT-010"),  # Add to cart -> POST /api/cart
        ("STORY-016", "ENDPOINT-011"),  # Cart management -> GET /api/cart
        ("STORY-016", "ENDPOINT-012"),  # Cart management -> PUT /api/cart/:itemId
        ("STORY-020", "ENDPOINT-014"),  # Order confirmation -> POST /api/orders
        ("STORY-020", "ENDPOINT-015"),  # Order confirmation -> GET /api/orders/:id
    ]

    for story_id, endpoint_id in story_endpoint_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, endpoint_id, "implemented_by")

    # Story -> Screen links (designs)
    story_screen_pairs = [
        ("STORY-001", "SCREEN-003"),  # Login -> Login Page
        ("STORY-009", "SCREEN-004"),  # Product search -> Product Listing
        ("STORY-009", "SCREEN-005"),  # Product search -> Product Detail
        ("STORY-015", "SCREEN-006"),  # Add to cart -> Shopping Cart
        ("STORY-020", "SCREEN-010"),  # Order confirmation -> Order Confirmation Page
    ]

    for story_id, screen_id in story_screen_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, screen_id, "designs")

    # Story -> Test links (tested_by)
    story_test_pairs = [
        ("STORY-001", "TEST_CASE-004"),  # Login -> Login test
        ("STORY-001", "TEST_CASE-005"),  # Login -> Invalid credentials test
        ("STORY-015", "TEST_CASE-006"),  # Add to cart -> Cart test
        ("STORY-020", "TEST_CASE-008"),  # Checkout -> E2E test
    ]

    for story_id, test_id in story_test_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, test_id, "tested_by")

    # Endpoint -> Table links (uses)
    endpoint_table_pairs = [
        ("ENDPOINT-004", "TABLE-003"),  # Login -> users table
        ("ENDPOINT-008", "TABLE-004"),  # GET products -> products table
        ("ENDPOINT-010", "TABLE-007"),  # POST cart -> cart_items table
        ("ENDPOINT-014", "TABLE-008"),  # POST orders -> orders table
        ("ENDPOINT-014", "TABLE-009"),  # POST orders -> order_items table
    ]

    for endpoint_id, table_id in endpoint_table_pairs:
        endpoint_file = project_path / "endpoints" / f"{endpoint_id}.md"
        if endpoint_file.exists():
            add_link_to_item(endpoint_file, table_id, "uses")


def create_frontend_links() -> None:
    """Create links in frontend project."""
    project_path = Path("./frontend/.trace")

    # Story -> Component links (implemented_by)
    story_component_pairs = [
        ("STORY-001", "FILE-001"),  # Button Component -> Button.tsx
        ("STORY-002", "FILE-002"),  # Form Input -> Input.tsx
        ("STORY-003", "FILE-003"),  # Modal -> Modal.tsx
        ("STORY-004", "FILE-004"),  # Data Table -> DataTable.tsx
        ("STORY-005", "FILE-005"),  # Toast -> Toast.tsx
        ("STORY-009", "FILE-008"),  # Login Page -> AuthProvider.tsx
        ("STORY-012", "FILE-006"),  # Protected Route -> useAuth.ts
        ("STORY-014", "FILE-009"),  # Product Grid -> ProductCard.tsx
        ("STORY-015", "FILE-010"),  # Product Detail -> CartDrawer.tsx
    ]

    for story_id, file_id in story_component_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, file_id, "implemented_by")

    # Story -> Screen links
    story_screen_pairs = [
        ("STORY-009", "SCREEN-001"),  # Login Page -> Dashboard Layout
        ("STORY-014", "SCREEN-002"),  # Product Grid -> Product Grid View wireframe
        ("STORY-010", "SCREEN-003"),  # Registration -> User Profile Page
    ]

    for story_id, screen_id in story_screen_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, screen_id, "designs")


def create_backend_links() -> None:
    """Create links in backend project."""
    project_path = Path("./backend/.trace")

    # Story -> Service links (implemented_by)
    story_service_pairs = [
        ("STORY-001", "FILE-001"),  # JWT Generation -> auth_service.py
        ("STORY-002", "FILE-001"),  # Password Hashing -> auth_service.py
        ("STORY-007", "FILE-002"),  # Product CRUD -> product_service.py
        ("STORY-008", "FILE-006"),  # Product Search -> search_service.py
        ("STORY-013", "FILE-003"),  # Cart Management -> cart_service.py
        ("STORY-014", "FILE-004"),  # Checkout -> order_service.py
        ("STORY-015", "FILE-007"),  # Payment Integration -> payment_service.py
    ]

    for story_id, file_id in story_service_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, file_id, "implemented_by")

    # Story -> Endpoint links
    story_endpoint_pairs = [
        ("STORY-001", "ENDPOINT-001"),  # JWT -> POST /api/v1/auth/login
        ("STORY-002", "ENDPOINT-002"),  # Password -> POST /api/v1/auth/register
        ("STORY-007", "ENDPOINT-005"),  # Product CRUD -> GET /api/v1/products
        ("STORY-007", "ENDPOINT-006"),  # Product CRUD -> GET /api/v1/products/:id
        ("STORY-013", "ENDPOINT-010"),  # Cart -> GET /api/v1/cart
        ("STORY-013", "ENDPOINT-011"),  # Cart -> POST /api/v1/cart/items
        ("STORY-014", "ENDPOINT-014"),  # Checkout -> POST /api/v1/orders
    ]

    for story_id, endpoint_id in story_endpoint_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, endpoint_id, "implemented_by")

    # Endpoint -> Table links
    endpoint_table_pairs = [
        ("ENDPOINT-001", "TABLE-001"),  # Login -> users
        ("ENDPOINT-005", "TABLE-004"),  # GET products -> products
        ("ENDPOINT-010", "TABLE-007"),  # GET cart -> cart_items
        ("ENDPOINT-014", "TABLE-008"),  # POST orders -> orders
        ("ENDPOINT-014", "TABLE-009"),  # POST orders -> order_items
    ]

    for endpoint_id, table_id in endpoint_table_pairs:
        endpoint_file = project_path / "endpoints" / f"{endpoint_id}.md"
        if endpoint_file.exists():
            add_link_to_item(endpoint_file, table_id, "uses")

    # Story -> Test Suite links
    story_test_pairs = [
        ("STORY-001", "TEST_SUITE-001"),  # Auth stories -> Authentication Tests
        ("STORY-007", "TEST_SUITE-002"),  # Product stories -> Product API Tests
        ("STORY-013", "TEST_SUITE-003"),  # Cart stories -> Cart API Tests
        ("STORY-014", "TEST_SUITE-004"),  # Order stories -> Order API Tests
    ]

    for story_id, test_id in story_test_pairs:
        story_file = project_path / "stories" / f"{story_id}.md"
        if story_file.exists():
            add_link_to_item(story_file, test_id, "tested_by")


def main() -> None:
    """Create links between items."""
    create_demo_project_links()
    create_frontend_links()
    create_backend_links()


if __name__ == "__main__":
    main()
