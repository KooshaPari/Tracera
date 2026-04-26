using System;

namespace Hexagon.CS.Domain.Entities;

/// <summary>
/// Base entity with common properties
/// </summary>
public abstract class Entity
{
    public Guid Id { get; protected set; }
    public DateTime CreatedAt { get; protected set; }
    public DateTime? UpdatedAt { get; protected set; }

    protected Entity()
    {
        Id = Guid.NewGuid();
        CreatedAt = DateTime.UtcNow;
    }

    public override bool Equals(object? obj)
    {
        if (obj is not Entity other)
            return false;
        if (ReferenceEquals(this, other))
            return true;
        return Id == other.Id;
    }

    public override int GetHashCode() => Id.GetHashCode();
}

/// <summary>
/// Example domain entity
/// </summary>
public class Order : Entity
{
    public string CustomerId { get; private set; } = string.Empty;
    public OrderStatus Status { get; private set; }
    public decimal TotalAmount { get; private set; }
    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

    private Order() { } // For ORM

    public static Order Create(string customerId)
    {
        return new Order
        {
            CustomerId = customerId,
            Status = OrderStatus.Pending
        };
    }

    public void AddItem(string productId, int quantity, decimal price)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Cannot add items to a non-pending order");

        _items.Add(new OrderItem(productId, quantity, price));
        TotalAmount = _items.Sum(i => i.Subtotal);
    }

    public void Confirm() => Status = OrderStatus.Confirmed;

    public void Cancel() => Status = OrderStatus.Cancelled;
}

public class OrderItem
{
    public Guid Id { get; }
    public string ProductId { get; }
    public int Quantity { get; }
    public decimal Price { get; }
    public decimal Subtotal => Quantity * Price;

    public OrderItem(string productId, int quantity, decimal price)
    {
        Id = Guid.NewGuid();
        ProductId = productId;
        Quantity = quantity;
        Price = price;
    }
}

public enum OrderStatus
{
    Pending,
    Confirmed,
    Cancelled
}
