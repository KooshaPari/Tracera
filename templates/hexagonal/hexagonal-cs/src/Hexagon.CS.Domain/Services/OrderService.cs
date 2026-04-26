using System;
using Hexagon.CS.Domain.ValueObjects;

namespace Hexagon.CS.Domain.Entities;

/// <summary>
/// Domain service for order operations
/// </summary>
public class OrderService
{
    public void Place(Order order)
    {
        if (order is null)
            throw new ArgumentNullException(nameof(order));

        order.Status = OrderStatus.Placed;
        order.PlacedAt = DateTime.UtcNow;
    }

    public void Cancel(Order order, string reason)
    {
        if (order is null)
            throw new ArgumentNullException(nameof(order));
        if (string.IsNullOrWhiteSpace(reason))
            throw new ArgumentException("Cancellation reason required", nameof(reason));

        order.Status = OrderStatus.Cancelled;
        order.CancelledAt = DateTime.UtcNow;
        order.AddDomainEvent(new OrderCancelledEvent(order.Id, reason));
    }

    public void Complete(Order order)
    {
        if (order is null)
            throw new ArgumentNullException(nameof(order));

        order.Status = OrderStatus.Completed;
        order.CompletedAt = DateTime.UtcNow;
        order.AddDomainEvent(new OrderCompletedEvent(order.Id));
    }
}
