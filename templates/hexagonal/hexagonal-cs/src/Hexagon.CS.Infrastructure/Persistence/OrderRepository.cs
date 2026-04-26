using System;
using System.Threading.Tasks;
using Hexagon.CS.Domain.Entities;
using Hexagon.CS.Domain.ValueObjects;
using Hexagon.CS.Application.Ports;

namespace Hexagon.CS.Infrastructure.Persistence;

/// <summary>
/// Persistence adapter - implements IOrderRepository
/// Uses Entity Framework Core
/// </summary>

public class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _context;

    public OrderRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task AddAsync(Order order)
    {
        var entity = new OrderEntity
        {
            Id = order.Id,
            CustomerId = order.CustomerId,
            CustomerEmail = order.Email.Value,
            Status = order.Status.ToString(),
            TotalAmount = order.TotalAmount,
            Street = order.ShippingAddress.Street,
            City = order.ShippingAddress.City,
            State = order.ShippingAddress.State,
            ZipCode = order.ShippingAddress.ZipCode,
            Country = order.ShippingAddress.Country,
            CreatedAt = order.CreatedAt
        };

        _context.Orders.Add(entity);
        await _context.SaveChangesAsync();
    }

    public async Task<Order> GetByIdAsync(Guid id)
    {
        var entity = await _context.Orders.FindAsync(id);
        if (entity == null) return null;

        return OrderReconstitute.FromPersistence(entity);
    }
}

// Entity Framework DbContext
public class AppDbContext : Microsoft.EntityFrameworkCore.DbContext
{
    public Microsoft.EntityFrameworkCore.DbSet<OrderEntity> Orders { get; set; }
}

// EF Core entity (infrastructure detail)
public class OrderEntity
{
    public Guid Id { get; set; }
    public Guid CustomerId { get; set; }
    public string CustomerEmail { get; set; }
    public string Status { get; set; }
    public decimal TotalAmount { get; set; }
    public string Street { get; set; }
    public string City { get; set; }
    public string State { get; set; }
    public string ZipCode { get; set; }
    public string Country { get; set; }
    public DateTime CreatedAt { get; set; }
}
