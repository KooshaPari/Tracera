using System;
using System.Threading.Tasks;
using Hexagon.CS.Domain.Entities;
using Hexagon.CS.Domain.ValueObjects;
using Hexagon.CS.Domain.Services;
using Hexagon.CS.Domain.Events;
using Hexagon.CS.Application.Ports;

namespace Hexagon.CS.Application.UseCases;

/// <summary>
/// Application service - orchestrates use cases
/// Coordinates ports (interfaces) and domain services
/// </summary>

public class CreateOrderUseCase
{
    private readonly IOrderRepository _orderRepository;
    private readonly IEventBus _eventBus;
    private readonly IDomainEventDispatcher _eventDispatcher;

    public CreateOrderUseCase(
        IOrderRepository orderRepository,
        IEventBus eventBus,
        IDomainEventDispatcher eventDispatcher)
    {
        _orderRepository = orderRepository;
        _eventBus = eventBus;
        _eventDispatcher = eventDispatcher;
    }

    public async Task<OrderDto> ExecuteAsync(CreateOrderInput input)
    {
        // 1. Create domain entity (pure domain logic)
        var order = Order.Create(
            customerId: input.CustomerId,
            email: Email.Create(input.CustomerEmail),
            shippingAddress: new Address(
                input.Street,
                input.City,
                input.State,
                input.ZipCode,
                input.Country
            )
        );

        // 2. Add order items
        foreach (var item in input.Items)
        {
            order.AddItem(
                productId: item.ProductId,
                productName: item.ProductName,
                quantity: item.Quantity,
                unitPrice: item.UnitPrice
            );
        }

        // 3. Validate domain rules
        order.Validate();

        // 4. Persist (through port - infrastructure adapter)
        await _orderRepository.AddAsync(order);

        // 5. Dispatch domain events
        var events = order.GetDomainEvents();
        foreach (var evt in events)
        {
            await _eventDispatcher.DispatchAsync(evt);
        }

        return new OrderDto
        {
            Id = order.Id,
            CustomerId = order.CustomerId,
            Status = order.Status.ToString(),
            TotalAmount = order.TotalAmount,
            CreatedAt = order.CreatedAt
        };
    }
}

public class CreateOrderInput
{
    public Guid CustomerId { get; set; }
    public string CustomerEmail { get; set; }
    public string Street { get; set; }
    public string City { get; set; }
    public string State { get; set; }
    public string ZipCode { get; set; }
    public string Country { get; set; }
    public List<OrderItemInput> Items { get; set; } = new();
}

public class OrderItemInput
{
    public Guid ProductId { get; set; }
    public string ProductName { get; set; }
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
}

public class OrderDto
{
    public Guid Id { get; set; }
    public Guid CustomerId { get; set; }
    public string Status { get; set; }
    public decimal TotalAmount { get; set; }
    public DateTime CreatedAt { get; set; }
}
