"""Inbound ports (Primary/Driving ports).

These ports define the interface that drives the application.
They represent use cases from the perspective of the outside world.

Following Hexagonal Architecture:
- Inbound ports are the "primary" or "driving" ports
- They define what the application can do (use cases)
- Implementation is in the application layer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities import Order
    from domain.value_objects import OrderId


class CreateOrderUseCase(ABC):
    """Port for creating orders.

    This port defines the interface for the create order use case.
    Implementation details are in the application layer.
    """

    @abstractmethod
    async def execute(
        self,
        customer_id: str,
        items: list[dict],
        shipping_address: dict,
    ) -> OrderId:
        """Execute the create order use case.

        Args:
            customer_id: The customer's identifier
            items: List of order items with product_id and quantity
            shipping_address: Shipping address details

        Returns:
            The created order's identifier

        Raises:
            DomainError: If business rules are violated
        """
        ...


class GetOrderUseCase(ABC):
    """Port for retrieving orders."""

    @abstractmethod
    async def execute(self, order_id: OrderId) -> Order:
        """Execute the get order use case.

        Args:
            order_id: The order identifier

        Returns:
            The requested order

        Raises:
            EntityNotFoundError: If order doesn't exist
        """
        ...


class CancelOrderUseCase(ABC):
    """Port for canceling orders."""

    @abstractmethod
    async def execute(self, order_id: OrderId, reason: str) -> None:
        """Execute the cancel order use case.

        Args:
            order_id: The order identifier
            reason: Cancellation reason

        Raises:
            EntityNotFoundError: If order doesn't exist
            InvalidStateTransitionError: If order cannot be cancelled
        """
        ...


__all__ = [
    "CreateOrderUseCase",
    "GetOrderUseCase",
    "CancelOrderUseCase",
]
