namespace HexagonalCSharp.Domain.Ports.Outbound;

/// <summary>
/// Port for order persistence operations.
/// </summary>
public interface IOrderRepository
{
    Task SaveAsync(Order order, CancellationToken cancellationToken = default);
    Task<Order?> FindByIdAsync(string orderId, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<Order>> FindByCustomerAsync(string customerId, int limit = 100, int offset = 0, CancellationToken cancellationToken = default);
    Task DeleteAsync(string orderId, CancellationToken cancellationToken = default);
}

/// <summary>
/// Order entity for persistence (separate from domain entity for clean separation).
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
/// Order item for persistence.
/// </summary>
public record OrderItem(string ProductId, int Quantity, decimal Price);
