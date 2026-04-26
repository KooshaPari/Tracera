using Hexagon.CS.Domain.Entities;
using Hexagon.CS.Domain.ValueObjects;
using Hexagon.CS.Domain.Services;
using Xunit;

namespace Hexagon.CS.Tests.Unit;

public class OrderTests
{
    [Fact]
    public void Create_WithValidData_ReturnsOrderWithPendingStatus()
    {
        // Arrange
        var customerId = Guid.NewGuid();
        var items = new List<OrderItem>
        {
            OrderItem.Create(Guid.NewGuid(), 2, 100.00m)
        };

        // Act
        var order = Order.Create(customerId, items);

        // Assert
        Assert.NotNull(order);
        Assert.Equal(OrderStatus.Pending, order.Status);
        Assert.Single(order.Items);
        Assert.Equal(200.00m, order.TotalAmount);
    }

    [Fact]
    public void AddItem_WithValidItem_IncreasesItemCount()
    {
        // Arrange
        var order = Order.Create(Guid.NewGuid(), new List<OrderItem>());
        var newItem = OrderItem.Create(Guid.NewGuid(), 1, 50.00m);

        // Act
        order.AddItem(newItem);

        // Assert
        Assert.Single(order.Items);
    }

    [Fact]
    public void Confirm_WithPendingOrder_ChangesStatusToConfirmed()
    {
        // Arrange
        var order = Order.Create(
            Guid.NewGuid(),
            new List<OrderItem> { OrderItem.Create(Guid.NewGuid(), 1, 100.00m) }
        );

        // Act
        order.Confirm();

        // Assert
        Assert.Equal(OrderStatus.Confirmed, order.Status);
    }

    [Fact]
    public void Confirm_WithAlreadyConfirmedOrder_ThrowsException()
    {
        // Arrange
        var order = Order.Create(
            Guid.NewGuid(),
            new List<OrderItem> { OrderItem.Create(Guid.NewGuid(), 1, 100.00m) }
        );
        order.Confirm();

        // Act & Assert
        Assert.Throws<InvalidOperationException>(() => order.Confirm());
    }
}

public class EmailTests
{
    [Fact]
    public void Create_WithValidEmail_ReturnsEmailObject()
    {
        // Arrange
        var emailAddress = "user@example.com";

        // Act
        var email = Email.Create(emailAddress);

        // Assert
        Assert.NotNull(email);
        Assert.Equal("user@example.com", email.Value);
    }

    [Fact]
    public void Create_WithInvalidEmail_ThrowsException()
    {
        // Arrange
        var invalidEmail = "invalid-email";

        // Act & Assert
        Assert.Throws<ArgumentException>(() => Email.Create(invalidEmail));
    }
}

public class OrderCalculationServiceTests
{
    [Fact]
    public void CalculateTotal_WithMultipleItems_ReturnsCorrectSum()
    {
        // Arrange
        var items = new List<OrderItem>
        {
            OrderItem.Create(Guid.NewGuid(), 2, 100.00m),
            OrderItem.Create(Guid.NewGuid(), 3, 50.00m)
        };

        var service = new OrderCalculationService();

        // Act
        var total = service.CalculateTotal(items);

        // Assert
        Assert.Equal(350.00m, total);
    }
}
