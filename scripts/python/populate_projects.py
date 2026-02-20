#!/usr/bin/env python3
"""Populate incomplete projects with rich, authentic mock data.

Simulates how a real user would create requirements and traceability items.
"""

import subprocess
from pathlib import Path
from typing import Any


def run_cmd(cmd_list: Any, cwd: Any = None) -> None:
    """Run a command and return success status.

    Args:
        cmd_list: List of command arguments (e.g., ['git', 'clone', url])
        cwd: Working directory for the command
    """
    try:
        result = subprocess.run(cmd_list, shell=False, cwd=cwd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def create_item(
    project_path: Any,
    title: Any,
    view: Any,
    item_type: Any,
    description: Any = None,
    status: Any = "todo",
    priority: Any = "medium",
    owner: Any = None,
    parent_id: Any = None,
) -> None:
    """Create an item using rtm CLI."""
    cmd = [
        "rtm",
        "item",
        "create",
        title,
        "--view",
        view,
        "--type",
        item_type,
        "--status",
        status,
        "--priority",
        priority,
    ]
    if description:
        cmd.extend(["--description", description])
    if owner:
        cmd.extend(["--owner", owner])
    if parent_id:
        cmd.extend(["--parent", parent_id])
    cmd.extend(["--project", project_path])

    success, output = run_cmd(cmd, cwd=project_path)
    if success:
        # Extract external_id from output
        for line in output.split("\n"):
            if "Created" in line and "-" in line:
                parts = line.split()
                for part in parts:
                    if "-" in part and part[0].isalpha():
                        return part
    return None


def populate_demo_project() -> None:
    """Populate DEMO_PROJECT with rich e-commerce data."""
    project_path = "./samples/DEMO_PROJECT"

    # Epic 1: User Authentication (already exists, expand it)
    epic1_id = "EPIC-001"

    # Add more stories to Epic 1
    stories = [
        (
            "Password Reset Flow",
            "As a user, I want to reset my password via email so that I can regain access to my account if I forget it.",
            "high",
        ),
        ("Two-Factor Authentication", "As a user, I want to enable 2FA so that my account is more secure.", "medium"),
        (
            "Social Login",
            "As a user, I want to login with Google/GitHub so that I don't need to remember another password.",
            "medium",
        ),
        (
            "Session Management",
            "As a user, I want to see my active sessions and logout from devices so that I can manage my account security.",
            "low",
        ),
    ]

    story_ids = []
    for title, desc, priority in stories:
        story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)
        if story_id:
            story_ids.append(story_id)

    # Epic 2: Product Catalog
    epic2_id = create_item(
        project_path,
        "Product Catalog & Search",
        "FEATURE",
        "epic",
        "Comprehensive product browsing, search, filtering, and discovery experience. Users should be able to find products easily through multiple pathways.",
        "in_progress",
        "high",
    )
    if epic2_id:
        catalog_stories = [
            (
                "Product Search",
                "As a customer, I want to search for products by name, brand, or category so that I can quickly find what I'm looking for.",
                "high",
            ),
            (
                "Advanced Filters",
                "As a customer, I want to filter products by price, rating, brand, and features so that I can narrow down my options.",
                "high",
            ),
            (
                "Product Recommendations",
                "As a customer, I want to see recommended products based on my browsing history so that I can discover new items I might like.",
                "medium",
            ),
            (
                "Product Reviews & Ratings",
                "As a customer, I want to read reviews and see ratings before purchasing so that I can make informed decisions.",
                "high",
            ),
            (
                "Wishlist",
                "As a customer, I want to save products to a wishlist so that I can purchase them later.",
                "medium",
            ),
        ]

        for title, desc, priority in catalog_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)
            if story_id:
                pass

    # Epic 3: Shopping Cart & Checkout
    epic3_id = create_item(
        project_path,
        "Shopping Cart & Checkout",
        "FEATURE",
        "epic",
        "Seamless shopping cart management and secure checkout process. Support multiple payment methods and shipping options.",
        "todo",
        "critical",
    )
    if epic3_id:
        checkout_stories = [
            (
                "Add to Cart",
                "As a customer, I want to add products to my cart so that I can purchase multiple items together.",
                "critical",
            ),
            (
                "Cart Management",
                "As a customer, I want to update quantities, remove items, and see cart total so that I can manage my purchase.",
                "high",
            ),
            (
                "Guest Checkout",
                "As a customer, I want to checkout without creating an account so that I can purchase quickly.",
                "high",
            ),
            (
                "Multiple Payment Methods",
                "As a customer, I want to pay with credit card, PayPal, or Apple Pay so that I can use my preferred payment method.",
                "high",
            ),
            (
                "Shipping Address Management",
                "As a customer, I want to save multiple shipping addresses so that I can ship to different locations.",
                "medium",
            ),
            (
                "Order Confirmation",
                "As a customer, I want to receive order confirmation with tracking number so that I know my order was placed successfully.",
                "critical",
            ),
        ]

        for title, desc, priority in checkout_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic3_id)
            if story_id:
                pass

    # API Endpoints
    api_endpoints = [
        ("POST /api/auth/login", "User login endpoint with email/password validation", "high"),
        ("POST /api/auth/register", "User registration with email verification", "high"),
        ("POST /api/auth/refresh", "Refresh access token using refresh token", "medium"),
        ("GET /api/products", "List products with pagination and filters", "high"),
        ("GET /api/products/:id", "Get product details by ID", "high"),
        ("POST /api/cart", "Add item to shopping cart", "critical"),
        ("GET /api/cart", "Get current user's cart", "high"),
        ("PUT /api/cart/:itemId", "Update cart item quantity", "high"),
        ("DELETE /api/cart/:itemId", "Remove item from cart", "high"),
        ("POST /api/orders", "Create new order from cart", "critical"),
        ("GET /api/orders/:id", "Get order details with tracking", "high"),
    ]

    for title, desc, priority in api_endpoints:
        endpoint_id = create_item(project_path, title, "API", "endpoint", desc, "todo", priority)
        if endpoint_id:
            pass

    # Database Tables
    db_tables = [
        ("users", "User accounts with authentication credentials and profile data", "critical"),
        ("products", "Product catalog with pricing, inventory, and metadata", "critical"),
        ("categories", "Product categories and hierarchical organization", "high"),
        ("cart_items", "Shopping cart items linked to user sessions", "critical"),
        ("orders", "Order records with status and payment information", "critical"),
        ("order_items", "Individual items within an order", "critical"),
        ("reviews", "Product reviews and ratings from customers", "medium"),
        ("wishlists", "User wishlists for saved products", "low"),
    ]

    for title, desc, priority in db_tables:
        table_id = create_item(project_path, title, "DATABASE", "table", desc, "todo", priority)
        if table_id:
            pass

    # Test Cases
    test_cases = [
        ("Login with valid credentials", "Verify successful login returns JWT token", "high"),
        ("Login with invalid credentials", "Verify error message for wrong password", "high"),
        ("Add product to cart", "Verify product appears in cart with correct quantity", "critical"),
        ("Checkout flow", "Verify order creation and payment processing", "critical"),
        ("Product search", "Verify search returns relevant results", "high"),
        ("Filter products", "Verify filters correctly narrow results", "medium"),
    ]

    for title, desc, priority in test_cases:
        test_id = create_item(project_path, title, "TEST", "test_case", desc, "todo", priority)
        if test_id:
            pass

    # Wireframes/Screens
    screens = [
        ("Login Page", "User login form with email/password fields and social login options", "high"),
        ("Product Listing", "Grid view of products with filters and search bar", "high"),
        ("Product Detail", "Product page with images, description, reviews, and add to cart", "high"),
        ("Shopping Cart", "Cart view with items, quantities, and checkout button", "critical"),
        ("Checkout Flow", "Multi-step checkout with shipping and payment forms", "critical"),
        ("Order Confirmation", "Success page with order details and tracking number", "high"),
    ]

    for title, desc, priority in screens:
        screen_id = create_item(project_path, title, "WIREFRAME", "screen", desc, "todo", priority)
        if screen_id:
            pass


def populate_frontend_project() -> None:
    """Populate frontend project with React/UI components."""
    project_path = "./frontend"

    # Initialize if needed
    if not (Path(project_path) / ".trace" / "project.yaml").exists():
        run_cmd([
            "rtm",
            "init",
            "--name",
            "Frontend Application",
            "--description",
            "React-based frontend application with modern UI components",
            "--path",
            project_path,
        ])

    # Epic: Component Library
    epic1_id = create_item(
        project_path,
        "Design System & Component Library",
        "FEATURE",
        "epic",
        "Build a comprehensive design system with reusable React components following design tokens and accessibility standards.",
        "in_progress",
        "high",
    )
    if epic1_id:
        component_stories = [
            (
                "Button Component",
                "Create a reusable Button component with variants (primary, secondary, danger) and sizes (sm, md, lg)",
                "high",
            ),
            (
                "Form Input Components",
                "Create Input, Textarea, Select, and Checkbox components with validation states",
                "high",
            ),
            ("Modal/Dialog Component", "Create accessible modal component with focus trap and backdrop", "medium"),
            ("Data Table Component", "Create table component with sorting, filtering, and pagination", "high"),
            ("Toast Notification System", "Create toast notification component for success/error messages", "medium"),
            ("Loading States", "Create Skeleton loaders and Spinner components for async operations", "medium"),
        ]

        for title, desc, priority in component_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)
            if story_id:
                pass

    # Epic: Authentication UI
    epic2_id = create_item(
        project_path,
        "Authentication UI",
        "FEATURE",
        "epic",
        "Complete authentication user interface with login, registration, password reset flows.",
        "todo",
        "high",
    )
    if epic2_id:
        auth_stories = [
            ("Login Page", "Build login page with email/password form, validation, and error handling", "high"),
            (
                "Registration Page",
                "Build registration form with password strength indicator and terms acceptance",
                "high",
            ),
            ("Password Reset Flow", "Build password reset request and confirmation pages", "medium"),
            ("Protected Route Wrapper", "Create HOC/component to protect routes requiring authentication", "high"),
        ]

        for title, desc, priority in auth_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)
            if story_id:
                pass

    # Code Components (React)
    react_components = [
        ("Button.tsx", "Reusable button component with TypeScript", "high"),
        ("Input.tsx", "Form input component with validation", "high"),
        ("Modal.tsx", "Accessible modal dialog component", "medium"),
        ("DataTable.tsx", "Data table with sorting and pagination", "high"),
        ("Toast.tsx", "Toast notification component", "medium"),
        ("useAuth.ts", "Custom hook for authentication state", "high"),
        ("useApi.ts", "Custom hook for API calls with error handling", "high"),
        ("AuthProvider.tsx", "Context provider for authentication", "high"),
    ]

    for title, desc, priority in react_components:
        comp_id = create_item(project_path, title, "CODE", "file", desc, "todo", priority)
        if comp_id:
            pass

    # Wireframes
    wireframes = [
        ("Dashboard Layout", "Main application layout with sidebar navigation and header", "high"),
        ("Product Grid View", "Responsive grid layout for product cards", "high"),
        ("User Profile Page", "Profile page with editable form fields", "medium"),
        ("Settings Page", "Settings page with tabbed navigation", "low"),
    ]

    for title, desc, priority in wireframes:
        wireframe_id = create_item(project_path, title, "WIREFRAME", "screen", desc, "todo", priority)
        if wireframe_id:
            pass


def populate_backend_project() -> None:
    """Populate backend project with API and service data."""
    project_path = "./backend"

    # Initialize if needed
    if not (Path(project_path) / ".trace" / "project.yaml").exists():
        run_cmd([
            "rtm",
            "init",
            "--name",
            "Backend API",
            "--description",
            "RESTful API backend with authentication, business logic, and data persistence",
            "--path",
            project_path,
        ])

    # Epic: Authentication Service
    epic1_id = create_item(
        project_path,
        "Authentication & Authorization Service",
        "FEATURE",
        "epic",
        "Complete authentication system with JWT tokens, password hashing, role-based access control, and session management.",
        "in_progress",
        "critical",
    )
    if epic1_id:
        auth_stories = [
            ("JWT Token Generation", "Implement JWT token generation with access and refresh tokens", "critical"),
            ("Password Hashing", "Implement secure password hashing with bcrypt and salt", "critical"),
            ("Role-Based Access Control", "Implement RBAC middleware for route protection", "high"),
            ("Session Management", "Implement session tracking and revocation", "medium"),
            ("OAuth Integration", "Integrate OAuth providers (Google, GitHub) for social login", "medium"),
        ]

        for title, desc, priority in auth_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)
            if story_id:
                pass

    # Epic: Product Service
    epic2_id = create_item(
        project_path,
        "Product Management Service",
        "FEATURE",
        "epic",
        "Service for managing product catalog, inventory, pricing, and search functionality.",
        "todo",
        "high",
    )
    if epic2_id:
        product_stories = [
            ("Product CRUD Operations", "Implement create, read, update, delete operations for products", "high"),
            ("Product Search", "Implement full-text search with filters and pagination", "high"),
            ("Inventory Management", "Track product inventory levels and handle stock updates", "high"),
            ("Price Management", "Support multiple pricing tiers and discount codes", "medium"),
            ("Product Recommendations", "Implement recommendation engine based on user behavior", "low"),
        ]

        for title, desc, priority in product_stories:
            story_id = create_item(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)
            if story_id:
                pass

    # API Endpoints
    api_endpoints = [
        ("POST /api/v1/auth/login", "Authenticate user and return JWT tokens", "critical"),
        ("POST /api/v1/auth/register", "Register new user account", "critical"),
        ("POST /api/v1/auth/refresh", "Refresh access token", "high"),
        ("GET /api/v1/products", "List products with pagination", "high"),
        ("GET /api/v1/products/:id", "Get product by ID", "high"),
        ("POST /api/v1/products", "Create new product (admin)", "high"),
        ("PUT /api/v1/products/:id", "Update product (admin)", "high"),
        ("DELETE /api/v1/products/:id", "Delete product (admin)", "medium"),
        ("GET /api/v1/cart", "Get user's shopping cart", "high"),
        ("POST /api/v1/cart/items", "Add item to cart", "critical"),
        ("PUT /api/v1/cart/items/:id", "Update cart item quantity", "high"),
        ("DELETE /api/v1/cart/items/:id", "Remove item from cart", "high"),
        ("POST /api/v1/orders", "Create order from cart", "critical"),
        ("GET /api/v1/orders/:id", "Get order details", "high"),
    ]

    for title, desc, priority in api_endpoints:
        endpoint_id = create_item(project_path, title, "API", "endpoint", desc, "todo", priority)
        if endpoint_id:
            pass

    # Database Tables
    db_tables = [
        ("users", "User accounts table with email, password hash, and profile fields", "critical"),
        ("roles", "Role definitions for RBAC", "high"),
        ("user_roles", "Many-to-many relationship between users and roles", "high"),
        ("products", "Product catalog table", "critical"),
        ("categories", "Product categories with hierarchy", "high"),
        ("product_categories", "Many-to-many product-category relationship", "high"),
        ("cart_items", "Shopping cart items", "critical"),
        ("orders", "Order records", "critical"),
        ("order_items", "Items within orders", "critical"),
        ("payments", "Payment transaction records", "high"),
        ("sessions", "User session tracking", "medium"),
    ]

    for title, desc, priority in db_tables:
        table_id = create_item(project_path, title, "DATABASE", "table", desc, "todo", priority)
        if table_id:
            pass

    # Code Files (Services)
    service_files = [
        ("auth_service.py", "Authentication service with JWT and password hashing", "critical"),
        ("product_service.py", "Product business logic and CRUD operations", "high"),
        ("cart_service.py", "Shopping cart management service", "high"),
        ("order_service.py", "Order processing and payment integration", "critical"),
        ("email_service.py", "Email sending service for notifications", "medium"),
        ("search_service.py", "Full-text search implementation", "high"),
    ]

    for title, desc, priority in service_files:
        file_id = create_item(project_path, title, "CODE", "file", desc, "todo", priority)
        if file_id:
            pass

    # Test Suites
    test_suites = [
        ("Authentication Tests", "Test suite for login, registration, and token validation", "high"),
        ("Product API Tests", "Test suite for product CRUD and search endpoints", "high"),
        ("Cart API Tests", "Test suite for cart management endpoints", "high"),
        ("Order API Tests", "Test suite for order creation and processing", "critical"),
    ]

    for title, desc, priority in test_suites:
        suite_id = create_item(project_path, title, "TEST", "test_suite", desc, "todo", priority)
        if suite_id:
            pass


def main() -> None:
    """Main function to populate all projects."""
    # Populate each project
    populate_demo_project()
    populate_frontend_project()
    populate_backend_project()


if __name__ == "__main__":
    main()
