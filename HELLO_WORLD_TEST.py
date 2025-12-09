"""
HELLO_WORLD_TEST.py - Day 1 Starter Test

This is a 10-line starter test template. Run this immediately on Day 1.
Tests real database (not mocked). Can be run and modified as your first test.

Instructions:
1. Copy this file: cp HELLO_WORLD_TEST.py tests/test_hello_world.py
2. Run it: pytest tests/test_hello_world.py -v
3. Expected: TEST PASSED ✅
4. Modify it: Change test_example to test something real

Setup: Fresh SQLite database for each test (auto cleanup)
Teardown: Database automatically closed after test completes
"""

import pytest


class TestHelloWorldDatabase:
    """
    Minimal test suite - proves the environment works.

    This test class demonstrates:
    - Using a real database
    - Executing a database operation
    - Asserting the result
    - Automatic cleanup
    """

    def test_database_exists_and_works(self):
        """
        Verify: Database connection works (3 assertions)
        This test proves your environment is ready.
        """
        # Setup: Create in-memory database
        import sqlite3
        db = sqlite3.connect(":memory:")
        cursor = db.cursor()

        # Action: Create a table and insert data
        cursor.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO items (name) VALUES ('Hello World')")
        db.commit()

        # Verify: Data was inserted
        cursor.execute("SELECT name FROM items WHERE id = 1")
        result = cursor.fetchone()

        # Assertions
        assert result is not None, "Row should exist"
        assert result[0] == "Hello World", "Name should match"
        assert db is not None, "Database should exist"

        # Cleanup
        db.close()
