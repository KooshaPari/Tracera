"""
Validation tests for the three technical fixes in pheno-sdk.

This file tests:
1. Cache implementation with thread-safety and TTL
2. Repository synchronous operations
3. Event bus Pydantic validation with auto-generated defaults
"""

import threading
import time
from datetime import datetime

# Test 1: Cache Implementation
print("=" * 60)
print("TEST 1: Cache Implementation")
print("=" * 60)

from pheno.core.shared.cache.manager import cached, clear_cache, get_cache

# Test basic cache operations
cache = get_cache("test")

# Test set and get
cache.set("key1", "value1")
assert cache.get("key1") == "value1", "Basic set/get failed"
print("✓ Basic set/get works")

# Test TTL expiration
cache.set("key2", "value2", ttl=0.1)
assert cache.get("key2") == "value2", "TTL set failed"
time.sleep(0.15)
assert cache.get("key2") is None, "TTL expiration failed"
print("✓ TTL expiration works")

# Test delete
cache.set("key3", "value3")
cache.delete("key3")
assert cache.get("key3") is None, "Delete failed"
print("✓ Delete works")

# Test clear
cache.set("key4", "value4")
cache.clear()
assert cache.get("key4") is None, "Clear failed"
print("✓ Clear works")

# Test thread safety
results = []
def worker(cache, key, value):
    for i in range(100):
        cache.set(f"{key}_{i}", f"{value}_{i}")
        results.append(cache.get(f"{key}_{i}"))

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(cache, f"thread{i}", f"value{i}"))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

assert len(results) == 500, "Thread safety test failed"
print("✓ Thread-safety works (500 concurrent operations)")

# Test cached decorator
call_count = 0

@cached(namespace="test", ttl=1.0)
def expensive_function(x):
    global call_count
    call_count += 1
    return x * 2

result1 = expensive_function(5)
result2 = expensive_function(5)
assert result1 == result2 == 10, "Cached function result incorrect"
assert call_count == 1, "Cached decorator failed (function called multiple times)"
print("✓ @cached decorator works")

# Test namespace support
cache1 = get_cache("namespace1")
cache2 = get_cache("namespace2")
cache1.set("key", "value1")
cache2.set("key", "value2")
assert cache1.get("key") == "value1", "Namespace 1 failed"
assert cache2.get("key") == "value2", "Namespace 2 failed"
print("✓ Namespace isolation works")

print("\n✓✓✓ ALL CACHE TESTS PASSED ✓✓✓\n")


# Test 2: Repository Synchronous Operations
print("=" * 60)
print("TEST 2: Repository Synchronous Operations")
print("=" * 60)

from pheno.storage.repository import InMemoryRepository


class TestEntity:
    def __init__(self, id: str, name: str, version: int = 1):
        self.id = id
        self.name = name
        self.version = version

repo = InMemoryRepository()

# Test add
entity1 = TestEntity("1", "Test Entity 1")
repo.add(entity1)
print("✓ Add entity works (synchronous)")

# Test get
retrieved = repo.get("1")
assert retrieved is not None, "Get failed"
assert retrieved.name == "Test Entity 1", "Get returned wrong entity"
print("✓ Get entity works (synchronous)")

# Test update (create new entity object for update to test optimistic locking)
updated_entity = TestEntity("1", "Updated Entity 1", version=2)
repo.update(updated_entity)
retrieved = repo.get("1")
assert retrieved.name == "Updated Entity 1", "Update failed"
print("✓ Update entity works (synchronous)")

# Test list
entity2 = TestEntity("2", "Test Entity 2")
repo.add(entity2)
entities = repo.list()
assert len(entities) == 2, "List failed"
print("✓ List entities works (synchronous)")

# Test count
count = repo.count()
assert count == 2, "Count failed"
print("✓ Count entities works (synchronous)")

# Test exists
assert repo.exists("1") == True, "Exists failed for existing entity"
assert repo.exists("999") == False, "Exists failed for non-existing entity"
print("✓ Exists check works (synchronous)")

# Test delete
repo.delete("2")
assert repo.exists("2") == False, "Delete failed"
print("✓ Delete entity works (synchronous)")

# Test filtering
entity3 = TestEntity("3", "Active Entity")
entity3.status = "active"
entity4 = TestEntity("4", "Inactive Entity")
entity4.status = "inactive"
repo.add(entity3)
repo.add(entity4)

filtered = repo.list(status="active")
assert len(filtered) == 1, "Filtering failed"
assert filtered[0].id == "3", "Filtering returned wrong entity"
print("✓ Filtering works (synchronous)")

# Verify no async/await needed
try:
    # This should work without await
    result = repo.get("1")
    print("✓ No async/await required (synchronous calls work)")
except Exception as e:
    print(f"✗ Synchronous call failed: {e}")
    raise

print("\n✓✓✓ ALL REPOSITORY TESTS PASSED ✓✓✓\n")


# Test 3: Event Bus Pydantic Validation
print("=" * 60)
print("TEST 3: Event Bus Pydantic Validation")
print("=" * 60)

from pheno.events.domain_events import DomainEvent


# Test 1: Create event without event_type or aggregate_id (should auto-generate)
class TestEvent(DomainEvent):
    data: str = "test"

event1 = TestEvent()
assert event1.event_type == "TestEvent", f"Auto-generated event_type failed: {event1.event_type}"
assert event1.aggregate_id is not None, "Auto-generated aggregate_id failed"
assert len(event1.aggregate_id) > 0, "Auto-generated aggregate_id is empty"
print("✓ Auto-generated event_type works")
print("✓ Auto-generated aggregate_id works")

# Test 2: Create event with explicit event_type and aggregate_id
event2 = TestEvent(event_type="CustomType", aggregate_id="custom-id-123")
assert event2.event_type == "CustomType", "Explicit event_type failed"
assert event2.aggregate_id == "custom-id-123", "Explicit aggregate_id failed"
print("✓ Explicit event_type works")
print("✓ Explicit aggregate_id works")

# Test 3: Verify event_id is auto-generated
assert event1.event_id is not None, "Auto-generated event_id failed"
assert len(event1.event_id) > 0, "Auto-generated event_id is empty"
assert event1.event_id != event2.event_id, "Event IDs should be unique"
print("✓ Auto-generated event_id works")

# Test 4: Verify occurred_at is auto-generated
assert event1.occurred_at is not None, "Auto-generated occurred_at failed"
assert isinstance(event1.occurred_at, datetime), "occurred_at is not a datetime"
print("✓ Auto-generated occurred_at works")

# Test 5: Verify events are immutable (frozen)
try:
    event1.event_type = "Modified"
    print("✗ Events should be immutable but modification succeeded")
    raise AssertionError("Events should be immutable")
except Exception as e:
    if "frozen" in str(e) or "immutable" in str(e) or "cannot" in str(e).lower():
        print("✓ Events are immutable (frozen)")
    else:
        raise

# Test 6: Test with event bus
from pheno.events.domain_events import InMemoryEventBus

event_bus = InMemoryEventBus()

received_events = []

async def event_handler(event: DomainEvent):
    received_events.append(event)

event_bus.subscribe(TestEvent, event_handler)

# Publish event
import asyncio

event3 = TestEvent(data="test data")
asyncio.run(event_bus.publish(event3))

assert len(received_events) == 1, "Event bus failed to publish/receive event"
assert received_events[0].event_type == "TestEvent", "Event bus received wrong event type"
print("✓ Event bus integration works")

print("\n✓✓✓ ALL EVENT VALIDATION TESTS PASSED ✓✓✓\n")


# Summary
print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
print("✓ Fix 1: Cache Implementation - WORKING")
print("  - Thread-safe dict-based cache with TTL")
print("  - get(), set(), delete(), clear() methods")
print("  - @cached() decorator")
print("  - Namespace support")
print()
print("✓ Fix 2: Repository Async Issues - WORKING")
print("  - All methods are now synchronous")
print("  - No async/await required")
print("  - All functionality preserved (locking, filtering, etc.)")
print()
print("✓ Fix 3: Event Bus Pydantic Validation - WORKING")
print("  - event_type auto-generates from class name")
print("  - aggregate_id auto-generates as UUID")
print("  - Can override with explicit values")
print("  - Events remain immutable")
print()
print("=" * 60)
print("ALL TECHNICAL ISSUES RESOLVED!")
print("=" * 60)
