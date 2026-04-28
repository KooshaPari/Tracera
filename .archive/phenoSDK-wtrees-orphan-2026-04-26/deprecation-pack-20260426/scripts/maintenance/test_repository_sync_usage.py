"""
Test synchronous usage of InMemoryRepository (the domain entity repository).

This tests the fix for: "Methods are async but being called synchronously"
The fix makes all Repository methods synchronous so they can be called without await.
"""

from pheno.storage.repository import InMemoryRepository


class Task:
    def __init__(self, id: str, name: str, status: str = "pending"):
        self.id = id
        self.name = name
        self.status = status
        self.version = 1

# Create repository
repo = InMemoryRepository()

# Test 1: Add entities synchronously (no await)
print("Test 1: Adding entities synchronously...")
task1 = Task("task-1", "Implement feature A")
task2 = Task("task-2", "Fix bug B", status="in_progress")

repo.add(task1)
repo.add(task2)
print("✓ Added 2 tasks synchronously")

# Test 2: Get entities synchronously (no await)
print("\nTest 2: Getting entities synchronously...")
retrieved_task = repo.get("task-1")
assert retrieved_task is not None, "Get failed"
assert retrieved_task.name == "Implement feature A", "Wrong task retrieved"
print(f"✓ Retrieved task: {retrieved_task.name}")

# Test 3: List entities with filters synchronously (no await)
print("\nTest 3: Listing entities with filters synchronously...")
in_progress_tasks = repo.list(status="in_progress")
assert len(in_progress_tasks) == 1, "Filtering failed"
assert in_progress_tasks[0].name == "Fix bug B", "Wrong task filtered"
print(f"✓ Found {len(in_progress_tasks)} in-progress task")

# Test 4: Count entities synchronously (no await)
print("\nTest 4: Counting entities synchronously...")
total_count = repo.count()
assert total_count == 2, "Count failed"
print(f"✓ Total tasks: {total_count}")

# Test 5: Update entities synchronously (no await)
print("\nTest 5: Updating entities synchronously...")
task1_updated = Task("task-1", "Implement feature A - UPDATED", status="completed")
task1_updated.version = 2  # Optimistic locking
repo.update(task1_updated)
updated_task = repo.get("task-1")
assert updated_task.status == "completed", "Update failed"
print(f"✓ Updated task status to: {updated_task.status}")

# Test 6: Check existence synchronously (no await)
print("\nTest 6: Checking existence synchronously...")
exists = repo.exists("task-1")
assert exists == True, "Exists check failed"
not_exists = repo.exists("task-999")
assert not_exists == False, "Exists check for non-existent failed"
print("✓ Existence checks work")

# Test 7: Delete entities synchronously (no await)
print("\nTest 7: Deleting entities synchronously...")
repo.delete("task-2")
assert repo.exists("task-2") == False, "Delete failed"
print("✓ Deleted task-2")

print("\n" + "=" * 60)
print("SUCCESS: All repository methods work synchronously!")
print("No async/await required - the fix is working correctly.")
print("=" * 60)
