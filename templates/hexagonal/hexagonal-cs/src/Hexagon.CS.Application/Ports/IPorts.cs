using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Hexagon.CS.Application.Ports;

/// <summary>
/// Output port - interfaces that the application layer defines
/// </summary>

// Persistence Ports (Driven Adapters)
public interface IOrderRepository
{
    Task<Order> GetByIdAsync(Guid id);
    Task<IEnumerable<Order>> GetAllAsync();
    Task AddAsync(Order order);
    Task UpdateAsync(Order order);
    Task DeleteAsync(Guid id);
}

// Event Bus Port (Driven Adapter)
public interface IEventBus
{
    Task PublishAsync<T>(T domainEvent) where T : class;
}

// Notification Port (Driven Adapter)
public interface INotificationService
{
    Task SendEmailAsync(string to, string subject, string body);
    Task SendSmsAsync(string phoneNumber, string message);
}

// External Service Ports (Driven Adapters)
public interface IPaymentGateway
{
    Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request);
}

public interface IShippingService
{
    Task<ShippingLabel> CreateLabelAsync(ShippingRequest request);
}

// DTOs for external services
public class PaymentRequest
{
    public Guid OrderId { get; set; }
    public decimal Amount { get; set; }
    public string Currency { get; set; } = "USD";
    public PaymentMethod Method { get; set; }
}

public enum PaymentMethod { CreditCard, DebitCard, BankTransfer }

public class PaymentResult
{
    public bool Success { get; set; }
    public string TransactionId { get; set; }
    public string ErrorMessage { get; set; }
}

public class ShippingRequest
{
    public Guid OrderId { get; set; }
    public Address Destination { get; set; }
}

public class ShippingLabel
{
    public string TrackingNumber { get; set; }
    public string Carrier { get; set; }
}
