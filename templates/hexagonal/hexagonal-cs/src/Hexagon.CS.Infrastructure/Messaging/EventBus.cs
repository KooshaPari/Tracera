using System;
using System.Threading.Tasks;
using Hexagon.CS.Domain.Events;
using Hexagon.CS.Application.Ports;

namespace Hexagon.CS.Infrastructure.Messaging;

/// <summary>
/// Messaging adapter - handles async event-driven communication
/// Implements IEventPublisher to publish domain events to message broker
/// </summary>
public class EventBus : IEventPublisher
{
    public Task PublishAsync<T>(T @event) where T : IDomainEvent
    {
        // In production: publish to RabbitMQ, Kafka, Azure Service Bus, etc.
        Console.WriteLine($"[EventBus] Publishing event: {@event.GetType().Name}");
        Console.WriteLine($"  AggregateId: {@event.AggregateId}");
        Console.WriteLine($"  Timestamp: {@event.OccurredAt}");

        return Task.CompletedTask;
    }

    public Task PublishAsync<T>(params T[] events) where T : IDomainEvent
    {
        foreach (var @event in events)
        {
            PublishAsync(@event).Wait();
        }
        return Task.CompletedTask;
    }
}
