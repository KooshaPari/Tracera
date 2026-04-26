namespace HexagonalCSharp.Domain.Ports.Inbound;

/// <summary>
/// Port for creating orders.
/// </summary>
public interface ICreateOrderUseCase
{
    Task<OrderResult> ExecuteAsync(CreateOrderCommand command, CancellationToken cancellationToken = default);
}

/// <summary>
/// Command for creating an order.
/// </summary>
public record CreateOrderCommand(
    string CustomerId,
    IReadOnlyList<OrderItemCommand> Items,
    AddressCommand ShippingAddress
);

/// <summary>
/// Order item in command form.
/// </summary>
public record OrderItemCommand(string ProductId, int Quantity, decimal Price);

/// <summary>
/// Address in command form.
/// </summary>
public record AddressCommand(string Street, string City, string State, string ZipCode, string Country);

/// <summary>
/// Result of order creation.
/// </summary>
public record OrderResult(string OrderId, string Status, decimal Total);

/// <summary>
/// Port for retrieving orders.
/// </summary>
public interface IGetOrderUseCase
{
    Task<Order?> ExecuteAsync(string orderId, CancellationToken cancellationToken = default);
}

/// <summary>
/// Order representation.
/// </summary>
public record Order(
    string Id,
    string CustomerId,
    IReadOnlyList<OrderItem> Items,
    string Status,
    decimal Total,
    DateTime CreatedAt,
    DateTime UpdatedAt,
    string? CancellationReason = null
);

/// <summary>
/// Order item representation.
/// </summary>
public record OrderItem(string ProductId, int Quantity, decimal Price);

/// <summary>
/// Port for cancelling orders.
/// </summary>
public interface ICancelOrderUseCase
{
    Task ExecuteAsync(string orderId, string reason, CancellationToken cancellationToken = default);
}
