using System;
using Hexagon.CS.Domain.Entities;
using Hexagon.CS.Domain.ValueObjects;

namespace Hexagon.CS.Domain.Events;

/// <summary>
/// Base class for domain events
/// </summary>
public abstract class DomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

public class OrderPlacedEvent : DomainEvent
{
    public Guid OrderId { get; }
    public Email CustomerEmail { get; }

    public OrderPlacedEvent(Guid orderId, Email customerEmail)
    {
        OrderId = orderId;
        CustomerEmail = customerEmail;
    }
}

public class OrderCancelledEvent : DomainEvent
{
    public Guid OrderId { get; }
    public string Reason { get; }

    public OrderCancelledEvent(Guid orderId, string reason)
    {
        OrderId = orderId;
        Reason = reason;
    }
}

public class OrderCompletedEvent : DomainEvent
{
    public Guid OrderId { get; }

    public OrderCompletedEvent(Guid orderId)
    {
        OrderId = orderId;
    }
}
