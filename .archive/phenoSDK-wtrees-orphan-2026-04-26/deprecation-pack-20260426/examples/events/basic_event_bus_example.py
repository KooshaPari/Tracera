"""Basic Event Bus Example.

Demonstrates pheno.events usage for in-memory event handling.
"""

import asyncio

from pheno.events import Event, SimpleEventBus


async def main():
    # Create event bus
    bus = SimpleEventBus()

    # Subscribe to events
    @bus.subscribe("user.created")
    async def handle_user_created(event: Event):
        print(f"✅ User created: {event.data}")

    @bus.subscribe("user.updated")
    async def handle_user_updated(event: Event):
        print(f"✅ User updated: {event.data}")

    @bus.subscribe("user.*")  # Wildcard subscription
    async def handle_all_user_events(event: Event):
        print(f"📢 User event: {event.type}")

    # Publish events
    print("Publishing events...\n")

    await bus.publish(Event(type="user.created", data={"id": 123, "name": "Alice"}))

    await bus.publish(Event(type="user.updated", data={"id": 123, "name": "Alice Smith"}))

    await bus.publish(Event(type="user.deleted", data={"id": 123}))

    print("\n✅ All events published and handled")


if __name__ == "__main__":
    asyncio.run(main())
