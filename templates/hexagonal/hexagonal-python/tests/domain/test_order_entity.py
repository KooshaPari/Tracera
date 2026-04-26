"""Tests for Order entity - Domain layer tests.

Following TDD principles:
- Tests are written BEFORE implementation
- Tests describe desired behavior
- Implementation follows to make tests pass

Domain layer tests have:
- NO external dependencies (database, API, etc.)
- Pure unit tests
- Fast execution
"""

from __future__ import annotations

import pytest
from domain.entities.order import Order, OrderItem, OrderStatus
from domain.value_objects import OrderId, Money
from domain.errors import (
    InvalidStateTransitionError,
    BusinessRuleViolationError,
)


class TestOrderCreation:
    """Tests for Order creation."""

    def test_create_order_with_valid_items(self) -> None:
        """Test creating an order with valid items."""
        # Arrange
        customer_id = "customer-123"
        items = [
            {"product_id": "prod-1", "quantity": 2, "price": Money.amount(10.00)},
            {"product_id": "prod-2", "quantity": 1, "price": Money.amount(25.00)},
        ]

        # Act
        order = Order.create(customer_id=customer_id, items=items)

        # Assert
        assert order.customer_id == customer_id
        assert len(order.items) == 2
        assert order.status == OrderStatus.PENDING
        assert order.total == Money.amount(45.00)

    def test_create_order_with_empty_items_raises_error(self) -> None:
        """Test that creating an order with no items raises an error."""
        with pytest.raises(BusinessRuleViolationError) as exc_info:
            Order.create(customer_id="customer-123", items=[])

        assert "at least one item" in str(exc_info.value)

    def test_create_order_generates_id(self) -> None:
        """Test that creating an order generates a unique ID."""
        order1 = Order.create(customer_id="customer-1", items=[])
        order2 = Order.create(customer_id="customer-2", items=[])

        assert order1.id != order2.id
        assert isinstance(order1.id, OrderId)


class TestOrderStatusTransitions:
    """Tests for Order status transitions."""

    def test_confirm_pending_order(self) -> None:
        """Test confirming a pending order."""
        order = Order.create(customer_id="customer-1", items=[])
        order.confirm()

        assert order.status == OrderStatus.CONFIRMED

    def test_cancel_pending_order(self) -> None:
        """Test cancelling a pending order."""
        order = Order.create(customer_id="customer-1", items=[])
        order.cancel(reason="Customer requested")

        assert order.status == OrderStatus.CANCELLED
        assert order.cancellation_reason == "Customer requested"

    def test_cannot_confirm_cancelled_order(self) -> None:
        """Test that confirming a cancelled order raises an error."""
        order = Order.create(customer_id="customer-1", items=[])
        order.cancel(reason="Customer requested")

        with pytest.raises(InvalidStateTransitionError):
            order.confirm()

    def test_ship_confirmed_order(self) -> None:
        """Test shipping a confirmed order."""
        order = Order.create(customer_id="customer-1", items=[])
        order.confirm()
        order.ship()

        assert order.status == OrderStatus.SHIPPED


class TestOrderValueObjects:
    """Tests for Order value objects."""

    def test_order_total_calculation(self) -> None:
        """Test that order total is calculated correctly."""
        items = [
            {"product_id": "prod-1", "quantity": 3, "price": Money.amount(10.00)},
            {"product_id": "prod-2", "quantity": 2, "price": Money.amount(15.00)},
        ]

        order = Order.create(customer_id="customer-1", items=items)

        # 3 * 10 + 2 * 15 = 30 + 30 = 60
        assert order.total == Money.amount(60.00)

    def test_order_id_equality(self) -> None:
        """Test that OrderId equality works correctly."""
        id1 = OrderId.generate()
        id2 = OrderId.generate()

        assert id1 == id1  # Same instance
        assert id1 != id2  # Different values
