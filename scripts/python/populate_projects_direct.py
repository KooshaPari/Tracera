#!/usr/bin/env python3
"""Populate incomplete projects with rich, authentic mock data.

Creates items directly in .trace/ directories (bypasses database).
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


def create_item_markdown(
    project_path: Any,
    title: Any,
    _view: Any,
    item_type: Any,
    description: Any = None,
    status: Any = "todo",
    priority: Any = "medium",
    owner: Any = None,
    parent_id: Any = None,
    external_id: Any = None,
) -> None:
    """Create item markdown file directly."""
    trace_dir = Path(project_path) / ".trace"
    trace_dir.mkdir(parents=True, exist_ok=True)

    # Load project.yaml to get counters
    project_yaml = trace_dir / "project.yaml"
    if project_yaml.exists():
        with project_yaml.open() as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {"name": Path(project_path).name, "counters": {}, "settings": {}}

    # Generate external_id
    if not external_id:
        counters = config.get("counters", {})
        counter = counters.get(item_type, 0) + 1
        counters[item_type] = counter
        external_id = f"{item_type.upper()}-{counter:03d}"
        config["counters"] = counters

    # Create directory for item type
    type_plural = f"{item_type}s"
    item_dir = trace_dir / type_plural
    item_dir.mkdir(exist_ok=True)

    # Create markdown file
    item_file = item_dir / f"{external_id}.md"

    # Frontmatter
    frontmatter = {
        "created": datetime.now(UTC).isoformat(),
        "external_id": external_id,
        "id": str(uuid.uuid4()),
        "links": [],
        "owner": owner,
        "parent": parent_id,
        "priority": priority,
        "status": status,
        "type": item_type,
        "updated": datetime.now(UTC).isoformat(),
        "version": 1,
    }

    # Add parent link if parent_id provided
    if parent_id:
        frontmatter["links"].append({"target": parent_id, "type": "parent_of"})

    # Write markdown file
    content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

# {title}

## Description

{description or f"{title} - {item_type} item"}

"""

    item_file.write_text(content)

    # Update project.yaml
    with project_yaml.open("w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return external_id


def populate_demo_project() -> None:
    """Populate DEMO_PROJECT with rich e-commerce data."""
    project_path = "./samples/DEMO_PROJECT"

    # Epic 1: User Authentication (already exists)
    epic1_id = "EPIC-001"

    # Add more stories to Epic 1
    stories = [
        (
            "Password Reset Flow",
            "As a user, I want to reset my password via email so that I can regain access to my account if I forget it. The system should send a secure reset link that expires after 1 hour.",
            "high",
        ),
        (
            "Two-Factor Authentication",
            "As a user, I want to enable 2FA using authenticator apps so that my account is more secure. The system should support TOTP codes and backup codes.",
            "medium",
        ),
        (
            "Social Login Integration",
            "As a user, I want to login with Google/GitHub OAuth so that I don't need to remember another password. The system should handle OAuth callbacks and create accounts automatically.",
            "medium",
        ),
        (
            "Session Management Dashboard",
            "As a user, I want to see my active sessions across devices and logout remotely so that I can manage my account security. Show device type, location, and last activity.",
            "low",
        ),
    ]

    for title, desc, priority in stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)

    # Epic 2: Product Catalog
    epic2_id = create_item_markdown(
        project_path,
        "Product Catalog & Search",
        "FEATURE",
        "epic",
        "Comprehensive product browsing, search, filtering, and discovery experience. Users should be able to find products easily through multiple pathways including search, categories, filters, and recommendations.",
        "in_progress",
        "high",
    )

    catalog_stories = [
        (
            "Product Search",
            "As a customer, I want to search for products by name, brand, or category so that I can quickly find what I'm looking for. Search should support autocomplete and typo tolerance.",
            "high",
        ),
        (
            "Advanced Filtering",
            "As a customer, I want to filter products by price range, rating, brand, availability, and features so that I can narrow down my options efficiently.",
            "high",
        ),
        (
            "Product Recommendations",
            "As a customer, I want to see recommended products based on my browsing history and purchase patterns so that I can discover new items I might like.",
            "medium",
        ),
        (
            "Product Reviews & Ratings",
            "As a customer, I want to read detailed reviews and see average ratings before purchasing so that I can make informed decisions. Support photo reviews and verified purchases.",
            "high",
        ),
        (
            "Wishlist Feature",
            "As a customer, I want to save products to a wishlist so that I can purchase them later. Wishlist should support multiple lists and sharing.",
            "medium",
        ),
        (
            "Product Comparison",
            "As a customer, I want to compare multiple products side-by-side so that I can evaluate features and make the best choice.",
            "low",
        ),
    ]

    for title, desc, priority in catalog_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)

    # Epic 3: Shopping Cart & Checkout
    epic3_id = create_item_markdown(
        project_path,
        "Shopping Cart & Checkout",
        "FEATURE",
        "epic",
        "Seamless shopping cart management and secure checkout process. Support multiple payment methods, shipping options, and order tracking. Ensure PCI compliance for payment processing.",
        "todo",
        "critical",
    )

    checkout_stories = [
        (
            "Add to Cart",
            "As a customer, I want to add products to my cart with quantity selection so that I can purchase multiple items together. Show cart count badge and mini-cart preview.",
            "critical",
        ),
        (
            "Cart Management",
            "As a customer, I want to update quantities, remove items, apply promo codes, and see real-time cart total so that I can manage my purchase before checkout.",
            "high",
        ),
        (
            "Guest Checkout",
            "As a customer, I want to checkout without creating an account so that I can purchase quickly. Optionally convert to account after purchase.",
            "high",
        ),
        (
            "Multiple Payment Methods",
            "As a customer, I want to pay with credit card, PayPal, Apple Pay, or Google Pay so that I can use my preferred payment method. Support saved payment methods.",
            "high",
        ),
        (
            "Shipping Address Management",
            "As a customer, I want to save multiple shipping addresses and select default so that I can ship to different locations easily.",
            "medium",
        ),
        (
            "Order Confirmation & Tracking",
            "As a customer, I want to receive order confirmation email with tracking number so that I know my order was placed successfully and can track shipment.",
            "critical",
        ),
        (
            "Order History",
            "As a customer, I want to view my order history with details and reorder functionality so that I can track past purchases and buy again easily.",
            "medium",
        ),
    ]

    for title, desc, priority in checkout_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic3_id)

    # API Endpoints
    api_endpoints = [
        (
            "POST /api/auth/login",
            "User login endpoint with email/password validation. Returns JWT access and refresh tokens. Rate limited to prevent brute force.",
            "high",
        ),
        (
            "POST /api/auth/register",
            "User registration with email verification. Validates email format, password strength, and sends verification email.",
            "high",
        ),
        (
            "POST /api/auth/refresh",
            "Refresh access token using refresh token. Invalidates old refresh token and issues new token pair.",
            "medium",
        ),
        ("POST /api/auth/logout", "Logout endpoint that invalidates refresh token and clears session.", "medium"),
        (
            "GET /api/products",
            "List products with pagination, filters, and sorting. Supports search query parameter and category filtering.",
            "high",
        ),
        (
            "GET /api/products/:id",
            "Get product details by ID including images, variants, inventory status, and related products.",
            "high",
        ),
        (
            "POST /api/cart",
            "Add item to shopping cart. Creates cart if doesn't exist. Validates product availability.",
            "critical",
        ),
        (
            "GET /api/cart",
            "Get current user's cart with all items, quantities, and calculated totals including taxes and shipping.",
            "high",
        ),
        (
            "PUT /api/cart/:itemId",
            "Update cart item quantity. Validates stock availability and removes item if quantity is 0.",
            "high",
        ),
        ("DELETE /api/cart/:itemId", "Remove item from cart. Returns updated cart total.", "high"),
        (
            "POST /api/orders",
            "Create new order from cart. Validates inventory, processes payment, creates order record, and sends confirmation email.",
            "critical",
        ),
        (
            "GET /api/orders/:id",
            "Get order details with tracking information, items, shipping address, and payment status.",
            "high",
        ),
        ("GET /api/orders", "List user's orders with pagination and status filtering.", "medium"),
    ]

    for title, desc, priority in api_endpoints:
        create_item_markdown(project_path, title, "API", "endpoint", desc, "todo", priority)

    # Database Tables
    db_tables = [
        (
            "users",
            "User accounts table with email, password hash, profile fields, and timestamps. Includes email verification status and last login tracking.",
            "critical",
        ),
        (
            "products",
            "Product catalog table with name, description, SKU, price, inventory count, images, and metadata. Supports variants and categories.",
            "critical",
        ),
        (
            "categories",
            "Product categories with hierarchical organization. Supports parent-child relationships and custom ordering.",
            "high",
        ),
        (
            "product_categories",
            "Many-to-many junction table linking products to categories. Allows products in multiple categories.",
            "high",
        ),
        (
            "cart_items",
            "Shopping cart items linked to user sessions. Stores product ID, quantity, and added timestamp. Supports guest carts.",
            "critical",
        ),
        (
            "orders",
            "Order records with customer info, shipping address, payment status, order status, and totals. Includes timestamps for status changes.",
            "critical",
        ),
        (
            "order_items",
            "Individual items within an order. Stores product snapshot (name, price at time of order), quantity, and line total.",
            "critical",
        ),
        (
            "reviews",
            "Product reviews and ratings from customers. Includes rating (1-5), review text, verified purchase flag, and helpful votes.",
            "medium",
        ),
        (
            "wishlists",
            "User wishlists for saved products. Supports multiple wishlists per user with custom names.",
            "low",
        ),
        (
            "payments",
            "Payment transaction records with payment method, amount, status, transaction ID, and timestamps. Links to orders.",
            "high",
        ),
    ]

    for title, desc, priority in db_tables:
        create_item_markdown(project_path, title, "DATABASE", "table", desc, "todo", priority)

    # Test Cases
    test_cases = [
        (
            "Login with valid credentials",
            "Verify successful login returns JWT access and refresh tokens. Token should contain user ID and role.",
            "high",
        ),
        (
            "Login with invalid credentials",
            "Verify error message for wrong password. Should not reveal if email exists. Rate limit after 5 attempts.",
            "high",
        ),
        (
            "Add product to cart",
            "Verify product appears in cart with correct quantity. Cart total should update immediately.",
            "critical",
        ),
        (
            "Update cart item quantity",
            "Verify quantity update reflects in cart total. Should prevent quantity exceeding inventory.",
            "high",
        ),
        (
            "Checkout flow end-to-end",
            "Verify complete checkout: cart validation, payment processing, order creation, inventory deduction, and email confirmation.",
            "critical",
        ),
        (
            "Product search functionality",
            "Verify search returns relevant results with typo tolerance. Results should be ranked by relevance.",
            "high",
        ),
        (
            "Filter products by price",
            "Verify price filter correctly narrows results. Should handle range queries and currency formatting.",
            "medium",
        ),
        (
            "Guest checkout flow",
            "Verify guest can checkout without account. Should prompt for email for order confirmation.",
            "high",
        ),
    ]

    for title, desc, priority in test_cases:
        create_item_markdown(project_path, title, "TEST", "test_case", desc, "todo", priority)

    # Wireframes/Screens
    screens = [
        (
            "Login Page",
            "User login form with email/password fields, 'Remember me' checkbox, social login buttons (Google, GitHub), and 'Forgot password' link. Includes validation errors and loading states.",
            "high",
        ),
        (
            "Product Listing Page",
            "Grid view of products with filters sidebar, search bar, sort dropdown, and pagination. Each product card shows image, name, price, rating, and 'Add to Cart' button.",
            "high",
        ),
        (
            "Product Detail Page",
            "Product page with image gallery, title, price, description, reviews section, quantity selector, and 'Add to Cart' button. Shows related products and recently viewed.",
            "high",
        ),
        (
            "Shopping Cart Page",
            "Cart view with items table (image, name, price, quantity controls, remove), subtotal, shipping calculator, promo code input, and checkout button.",
            "critical",
        ),
        (
            "Checkout Flow - Step 1",
            "Shipping address form with validation. Shows saved addresses and option to add new. Includes shipping method selection.",
            "critical",
        ),
        (
            "Checkout Flow - Step 2",
            "Payment method selection and form. Shows saved payment methods. Includes billing address (same as shipping checkbox).",
            "critical",
        ),
        (
            "Checkout Flow - Step 3",
            "Order review page with items summary, shipping address, payment method, and order total breakdown. Final 'Place Order' button.",
            "critical",
        ),
        (
            "Order Confirmation Page",
            "Success page with order number, estimated delivery date, tracking link, and 'Continue Shopping' button. Shows order summary.",
            "high",
        ),
        (
            "User Dashboard",
            "Dashboard with order history, account settings, wishlist, and saved addresses. Quick access to recent orders and recommendations.",
            "medium",
        ),
    ]

    for title, desc, priority in screens:
        create_item_markdown(project_path, title, "WIREFRAME", "screen", desc, "todo", priority)

    # Tasks for implementation
    tasks = [
        (
            "Setup authentication middleware",
            "Implement JWT validation middleware for protected routes. Handle token refresh and expiration.",
            "high",
            epic1_id,
        ),
        (
            "Implement password hashing",
            "Use bcrypt with salt rounds for secure password storage. Include password strength validation.",
            "critical",
            epic1_id,
        ),
        (
            "Create product search index",
            "Setup Elasticsearch or similar for full-text search. Index product names, descriptions, and tags.",
            "high",
            epic2_id,
        ),
        (
            "Build cart persistence",
            "Implement cart storage in Redis for guest users and database for authenticated users. Sync on login.",
            "high",
            epic3_id,
        ),
        (
            "Integrate payment gateway",
            "Integrate Stripe/PayPal SDK for payment processing. Handle webhooks for payment status updates.",
            "critical",
            epic3_id,
        ),
        (
            "Setup email service",
            "Configure email service (SendGrid/SES) for order confirmations, password resets, and notifications.",
            "medium",
            None,
        ),
    ]

    for title, desc, priority, parent in tasks:
        create_item_markdown(project_path, title, "FEATURE", "task", desc, "todo", priority, None, parent)


def populate_frontend_project() -> None:
    """Populate frontend project with React/UI components."""
    project_path = "./frontend"

    # Ensure project.yaml exists
    trace_dir = Path(project_path) / ".trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    project_yaml = trace_dir / "project.yaml"
    if not project_yaml.exists():
        config = {
            "name": "Frontend Application",
            "description": "React-based frontend application with modern UI components and design system",
            "version": "1.0.0",
            "counters": {},
            "settings": {"default_priority": "medium", "default_status": "todo"},
        }
        with project_yaml.open("w") as f:
            yaml.dump(config, f, default_flow_style=False)

    # Epic: Component Library
    epic1_id = create_item_markdown(
        project_path,
        "Design System & Component Library",
        "FEATURE",
        "epic",
        "Build a comprehensive design system with reusable React components following design tokens, accessibility standards (WCAG 2.1 AA), and responsive design principles. Components should be documented with Storybook.",
        "in_progress",
        "high",
    )

    component_stories = [
        (
            "Button Component",
            "Create a reusable Button component with variants (primary, secondary, danger, ghost), sizes (sm, md, lg), loading states, and icon support. Should be fully accessible with keyboard navigation.",
            "high",
        ),
        (
            "Form Input Components",
            "Create Input, Textarea, Select, Checkbox, and Radio components with validation states (error, success), helper text, labels, and required indicators. Support controlled and uncontrolled modes.",
            "high",
        ),
        (
            "Modal/Dialog Component",
            "Create accessible modal component with focus trap, backdrop, close on ESC, and ARIA attributes. Support different sizes and custom content.",
            "medium",
        ),
        (
            "Data Table Component",
            "Create table component with sorting, filtering, pagination, row selection, and responsive design. Support custom cell renderers and column configuration.",
            "high",
        ),
        (
            "Toast Notification System",
            "Create toast notification component for success/error/info messages. Support auto-dismiss, manual dismiss, and stacking multiple toasts.",
            "medium",
        ),
        (
            "Loading States",
            "Create Skeleton loaders and Spinner components for async operations. Support different sizes and overlay modes.",
            "medium",
        ),
        (
            "Navigation Components",
            "Create Sidebar, Navbar, Breadcrumb, and Tab components with active states and keyboard navigation.",
            "medium",
        ),
        (
            "Card Component",
            "Create flexible Card component with header, body, footer, and image support. Used for product cards, dashboards, and content containers.",
            "high",
        ),
    ]

    for title, desc, priority in component_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)

    # Epic: Authentication UI
    epic2_id = create_item_markdown(
        project_path,
        "Authentication UI",
        "FEATURE",
        "epic",
        "Complete authentication user interface with login, registration, password reset flows. Includes form validation, error handling, loading states, and integration with auth API.",
        "todo",
        "high",
    )

    auth_stories = [
        (
            "Login Page",
            "Build login page with email/password form, validation, error handling, 'Remember me' checkbox, and social login buttons. Include loading states and success redirect.",
            "high",
        ),
        (
            "Registration Page",
            "Build registration form with email, password (with strength indicator), confirm password, terms acceptance checkbox, and email verification notice.",
            "high",
        ),
        (
            "Password Reset Flow",
            "Build password reset request page and confirmation page with token validation. Include success messages and error handling.",
            "medium",
        ),
        (
            "Protected Route Wrapper",
            "Create HOC/component to protect routes requiring authentication. Redirect to login with return URL. Show loading state during auth check.",
            "high",
        ),
        (
            "Auth Context Provider",
            "Create React Context for authentication state management. Provide user data, login/logout functions, and loading states to entire app.",
            "high",
        ),
    ]

    for title, desc, priority in auth_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)

    # Epic: Product Catalog UI
    epic3_id = create_item_markdown(
        project_path,
        "Product Catalog UI",
        "FEATURE",
        "epic",
        "Product browsing, search, and filtering interface. Includes product listing, detail pages, search functionality, and filter sidebar.",
        "todo",
        "high",
    )

    catalog_stories = [
        (
            "Product Grid View",
            "Build responsive product grid with lazy loading, infinite scroll, and skeleton loaders. Each card shows image, name, price, rating, and quick actions.",
            "high",
        ),
        (
            "Product Detail Page",
            "Build product detail page with image gallery, variant selection, quantity picker, add to cart button, reviews section, and related products.",
            "high",
        ),
        (
            "Search Interface",
            "Build search bar with autocomplete, recent searches, and search results page with filters and sorting options.",
            "high",
        ),
        (
            "Filter Sidebar",
            "Build collapsible filter sidebar with price range slider, category tree, brand checkboxes, and rating filters. Show active filter count.",
            "medium",
        ),
    ]

    for title, desc, priority in catalog_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic3_id)

    # Code Components (React)
    react_components = [
        (
            "Button.tsx",
            "Reusable button component with TypeScript types, variants, sizes, and loading states. Exports ButtonProps interface.",
            "high",
        ),
        (
            "Input.tsx",
            "Form input component with validation states, error messages, and label support. Supports controlled/uncontrolled modes.",
            "high",
        ),
        (
            "Modal.tsx",
            "Accessible modal dialog component with focus trap, backdrop, and portal rendering. Uses Radix UI primitives.",
            "medium",
        ),
        (
            "DataTable.tsx",
            "Data table component with sorting, filtering, pagination, and row selection. Generic type support for any data structure.",
            "high",
        ),
        (
            "Toast.tsx",
            "Toast notification component with auto-dismiss, manual dismiss, and stacking. Uses React Context for global state.",
            "medium",
        ),
        (
            "useAuth.ts",
            "Custom React hook for authentication state. Returns user, loading, login, logout functions. Handles token refresh automatically.",
            "high",
        ),
        (
            "useApi.ts",
            "Custom hook for API calls with error handling, loading states, and retry logic. Supports GET, POST, PUT, DELETE methods.",
            "high",
        ),
        (
            "AuthProvider.tsx",
            "Context provider for authentication. Manages user state, tokens, and provides auth methods to children. Handles token refresh.",
            "high",
        ),
        (
            "ProductCard.tsx",
            "Product card component for grid view. Shows image, name, price, rating, and add to cart button. Handles image loading and errors.",
            "high",
        ),
        (
            "CartDrawer.tsx",
            "Slide-out cart drawer component. Shows cart items, quantities, totals, and checkout button. Updates in real-time.",
            "high",
        ),
    ]

    for title, desc, priority in react_components:
        create_item_markdown(project_path, title, "CODE", "file", desc, "todo", priority)

    # Wireframes
    wireframes = [
        (
            "Dashboard Layout",
            "Main application layout with sidebar navigation, header with user menu, and content area. Responsive with mobile hamburger menu.",
            "high",
        ),
        (
            "Product Grid View",
            "Responsive grid layout for product cards. Adapts from 4 columns (desktop) to 2 columns (tablet) to 1 column (mobile).",
            "high",
        ),
        (
            "User Profile Page",
            "Profile page with editable form fields, avatar upload, password change section, and account settings. Tabbed interface.",
            "medium",
        ),
        (
            "Settings Page",
            "Settings page with tabbed navigation (Account, Notifications, Privacy, Billing). Each tab has relevant form fields.",
            "low",
        ),
        (
            "Checkout Flow Wireframes",
            "Multi-step checkout flow wireframes: Cart Review → Shipping → Payment → Confirmation. Show progress indicator.",
            "critical",
        ),
    ]

    for title, desc, priority in wireframes:
        create_item_markdown(project_path, title, "WIREFRAME", "screen", desc, "todo", priority)


def populate_backend_project() -> None:
    """Populate backend project with API and service data."""
    project_path = "./backend"

    # Ensure project.yaml exists
    trace_dir = Path(project_path) / ".trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    project_yaml = trace_dir / "project.yaml"
    if not project_yaml.exists():
        config = {
            "name": "Backend API",
            "description": "RESTful API backend with authentication, business logic, and data persistence",
            "version": "1.0.0",
            "counters": {},
            "settings": {"default_priority": "medium", "default_status": "todo"},
        }
        with project_yaml.open("w") as f:
            yaml.dump(config, f, default_flow_style=False)

    # Epic: Authentication Service
    epic1_id = create_item_markdown(
        project_path,
        "Authentication & Authorization Service",
        "FEATURE",
        "epic",
        "Complete authentication system with JWT tokens, password hashing, role-based access control, and session management. Includes refresh token rotation and password reset flows.",
        "in_progress",
        "critical",
    )

    auth_stories = [
        (
            "JWT Token Generation",
            "Implement JWT token generation with access tokens (15min expiry) and refresh tokens (7 day expiry). Include user ID, email, and roles in claims.",
            "critical",
        ),
        (
            "Password Hashing",
            "Implement secure password hashing with bcrypt (12 rounds) and salt. Include password strength validation and history checking.",
            "critical",
        ),
        (
            "Role-Based Access Control",
            "Implement RBAC middleware for route protection. Support role hierarchies and permission checking. Cache permissions for performance.",
            "high",
        ),
        (
            "Session Management",
            "Implement session tracking in database with device info, IP address, and last activity. Support session revocation and listing active sessions.",
            "medium",
        ),
        (
            "OAuth Integration",
            "Integrate OAuth providers (Google, GitHub) for social login. Handle OAuth callbacks, user creation, and account linking.",
            "medium",
        ),
        (
            "Password Reset Flow",
            "Implement secure password reset with time-limited tokens sent via email. Invalidate token after use and on password change.",
            "high",
        ),
    ]

    for title, desc, priority in auth_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic1_id)

    # Epic: Product Service
    epic2_id = create_item_markdown(
        project_path,
        "Product Management Service",
        "FEATURE",
        "epic",
        "Service for managing product catalog, inventory, pricing, and search functionality. Includes CRUD operations, bulk operations, and search indexing.",
        "todo",
        "high",
    )

    product_stories = [
        (
            "Product CRUD Operations",
            "Implement create, read, update, delete operations for products with validation, image upload, and variant management. Support soft delete.",
            "high",
        ),
        (
            "Product Search",
            "Implement full-text search with filters (price, category, rating), pagination, and sorting. Use Elasticsearch or PostgreSQL full-text search.",
            "high",
        ),
        (
            "Inventory Management",
            "Track product inventory levels, handle stock updates, low stock alerts, and prevent overselling. Support multiple warehouses.",
            "high",
        ),
        (
            "Price Management",
            "Support multiple pricing tiers (regular, sale, member), discount codes, and bulk pricing updates. Track price history.",
            "medium",
        ),
        (
            "Product Recommendations",
            "Implement recommendation engine based on user behavior, purchase history, and collaborative filtering. Cache recommendations.",
            "low",
        ),
        (
            "Bulk Product Import",
            "Support CSV/JSON bulk import of products with validation and error reporting. Handle large files with streaming.",
            "medium",
        ),
    ]

    for title, desc, priority in product_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic2_id)

    # Epic: Order Processing Service
    epic3_id = create_item_markdown(
        project_path,
        "Order Processing Service",
        "FEATURE",
        "epic",
        "Complete order processing system including cart management, checkout, payment processing, inventory deduction, and order fulfillment.",
        "todo",
        "critical",
    )

    order_stories = [
        (
            "Cart Management",
            "Implement shopping cart service with add/update/remove operations. Support guest carts (Redis) and user carts (database). Sync on login.",
            "high",
        ),
        (
            "Checkout Process",
            "Implement checkout flow: validate cart, calculate totals (including taxes and shipping), process payment, create order, and send confirmation.",
            "critical",
        ),
        (
            "Payment Integration",
            "Integrate payment gateway (Stripe/PayPal) for processing payments. Handle webhooks for payment status updates and refunds.",
            "critical",
        ),
        (
            "Order Fulfillment",
            "Manage order status workflow: pending → paid → processing → shipped → delivered. Update inventory and send status emails.",
            "high",
        ),
        (
            "Order Tracking",
            "Integrate with shipping carriers (UPS, FedEx) for tracking numbers and delivery updates. Webhook handling for status changes.",
            "medium",
        ),
    ]

    for title, desc, priority in order_stories:
        create_item_markdown(project_path, title, "FEATURE", "story", desc, "todo", priority, None, epic3_id)

    # API Endpoints
    api_endpoints = [
        (
            "POST /api/v1/auth/login",
            "Authenticate user with email/password. Returns JWT access and refresh tokens. Rate limited (5 attempts per 15min).",
            "critical",
        ),
        (
            "POST /api/v1/auth/register",
            "Register new user account. Validates email format, password strength. Sends verification email.",
            "critical",
        ),
        (
            "POST /api/v1/auth/refresh",
            "Refresh access token using refresh token. Implements refresh token rotation for security.",
            "high",
        ),
        (
            "POST /api/v1/auth/logout",
            "Logout endpoint that invalidates refresh token and clears session. Returns success confirmation.",
            "medium",
        ),
        (
            "GET /api/v1/products",
            "List products with pagination (limit, offset), filters (category, price range, rating), sorting, and search query.",
            "high",
        ),
        (
            "GET /api/v1/products/:id",
            "Get product details by ID including images, variants, inventory status, related products, and reviews summary.",
            "high",
        ),
        (
            "POST /api/v1/products",
            "Create new product (admin only). Validates required fields, handles image uploads, creates variants.",
            "high",
        ),
        (
            "PUT /api/v1/products/:id",
            "Update product (admin only). Supports partial updates, image management, and variant updates.",
            "high",
        ),
        (
            "DELETE /api/v1/products/:id",
            "Soft delete product (admin only). Marks as deleted but preserves data for order history.",
            "medium",
        ),
        (
            "GET /api/v1/cart",
            "Get user's shopping cart with all items, quantities, prices, and calculated totals (subtotal, tax, shipping, total).",
            "high",
        ),
        (
            "POST /api/v1/cart/items",
            "Add item to cart. Validates product availability, creates cart if needed, updates totals.",
            "critical",
        ),
        (
            "PUT /api/v1/cart/items/:id",
            "Update cart item quantity. Validates stock availability, removes if quantity is 0, recalculates totals.",
            "high",
        ),
        (
            "DELETE /api/v1/cart/items/:id",
            "Remove item from cart. Returns updated cart with recalculated totals.",
            "high",
        ),
        (
            "POST /api/v1/orders",
            "Create order from cart. Validates inventory, processes payment, creates order record, deducts inventory, sends email.",
            "critical",
        ),
        (
            "GET /api/v1/orders/:id",
            "Get order details with items, shipping address, payment status, tracking info, and status history.",
            "high",
        ),
        (
            "GET /api/v1/orders",
            "List user's orders with pagination and status filtering. Returns order summaries with key details.",
            "medium",
        ),
    ]

    for title, desc, priority in api_endpoints:
        create_item_markdown(project_path, title, "API", "endpoint", desc, "todo", priority)

    # Database Tables
    db_tables = [
        (
            "users",
            "User accounts table with email (unique), password hash, first_name, last_name, email_verified, created_at, updated_at, last_login_at. Indexed on email.",
            "critical",
        ),
        (
            "roles",
            "Role definitions table with name (admin, customer, vendor), description, and permissions JSON. Supports role hierarchies.",
            "high",
        ),
        (
            "user_roles",
            "Many-to-many junction table linking users to roles. Includes assigned_at timestamp and assigned_by user ID.",
            "high",
        ),
        (
            "products",
            "Product catalog table with name, description, SKU (unique), price, compare_at_price, inventory_count, status, images JSON, metadata JSON, created_at, updated_at.",
            "critical",
        ),
        (
            "categories",
            "Product categories with name, slug, description, parent_id (for hierarchy), image_url, sort_order. Supports nested categories.",
            "high",
        ),
        (
            "product_categories",
            "Many-to-many junction table linking products to categories. Allows products in multiple categories with is_primary flag.",
            "high",
        ),
        (
            "cart_items",
            "Shopping cart items with user_id (nullable for guests), product_id, quantity, price_at_added, created_at. Indexed on user_id.",
            "critical",
        ),
        (
            "orders",
            "Order records with user_id, order_number (unique), status, subtotal, tax_amount, shipping_amount, total, shipping_address JSON, billing_address JSON, payment_status, created_at, updated_at.",
            "critical",
        ),
        (
            "order_items",
            "Items within orders with order_id, product_id, product_name (snapshot), product_sku, quantity, unit_price, line_total. Preserves product info at time of order.",
            "critical",
        ),
        (
            "payments",
            "Payment transaction records with order_id, payment_method, amount, currency, status, transaction_id, gateway_response JSON, processed_at, created_at.",
            "high",
        ),
        (
            "sessions",
            "User session tracking with user_id, token_hash, device_info JSON, ip_address, last_activity_at, expires_at, revoked_at. Indexed on user_id and token_hash.",
            "medium",
        ),
        (
            "product_reviews",
            "Product reviews with user_id, product_id, rating (1-5), review_text, verified_purchase boolean, helpful_count, created_at, updated_at.",
            "medium",
        ),
    ]

    for title, desc, priority in db_tables:
        create_item_markdown(project_path, title, "DATABASE", "table", desc, "todo", priority)

    # Code Files (Services)
    service_files = [
        (
            "auth_service.py",
            "Authentication service with JWT generation/validation, password hashing, and session management. Handles login, registration, token refresh.",
            "critical",
        ),
        (
            "product_service.py",
            "Product business logic and CRUD operations. Handles product creation, updates, search, and inventory management. Includes caching.",
            "high",
        ),
        (
            "cart_service.py",
            "Shopping cart management service. Handles add/update/remove operations, total calculations, and cart persistence (Redis + DB).",
            "high",
        ),
        (
            "order_service.py",
            "Order processing service. Handles order creation, payment processing, inventory deduction, and status updates. Integrates with payment gateway.",
            "critical",
        ),
        (
            "email_service.py",
            "Email sending service for order confirmations, password resets, and notifications. Uses SendGrid/SES with templates and retry logic.",
            "medium",
        ),
        (
            "search_service.py",
            "Full-text search implementation using Elasticsearch or PostgreSQL. Handles indexing, query parsing, filtering, and result ranking.",
            "high",
        ),
        (
            "payment_service.py",
            "Payment processing service. Integrates with Stripe/PayPal, handles webhooks, processes refunds, and manages payment status.",
            "critical",
        ),
        (
            "inventory_service.py",
            "Inventory management service. Tracks stock levels, handles reservations, prevents overselling, and sends low stock alerts.",
            "high",
        ),
    ]

    for title, desc, priority in service_files:
        create_item_markdown(project_path, title, "CODE", "file", desc, "todo", priority)

    # Test Suites
    test_suites = [
        (
            "Authentication Tests",
            "Test suite for login, registration, token refresh, password reset, and session management. Includes edge cases and security tests.",
            "high",
        ),
        (
            "Product API Tests",
            "Test suite for product CRUD, search, filtering, and pagination endpoints. Tests validation, error handling, and performance.",
            "high",
        ),
        (
            "Cart API Tests",
            "Test suite for cart management endpoints. Tests add/update/remove operations, total calculations, and guest/user cart sync.",
            "high",
        ),
        (
            "Order API Tests",
            "Test suite for order creation, payment processing, inventory deduction, and status updates. Includes integration tests with payment gateway mocks.",
            "critical",
        ),
        (
            "Database Tests",
            "Test suite for database operations including migrations, constraints, indexes, and data integrity. Tests foreign key relationships.",
            "medium",
        ),
    ]

    for title, desc, priority in test_suites:
        create_item_markdown(project_path, title, "TEST", "test_suite", desc, "todo", priority)


def main() -> None:
    """Main function to populate all projects."""
    # Populate each project
    populate_demo_project()
    populate_frontend_project()
    populate_backend_project()


if __name__ == "__main__":
    main()
