"""
Simple test to verify testing infrastructure.
"""


import pytest


def test_basic_functionality():
    """Test basic functionality."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    text = "Hello, World!"
    assert len(text) == 13
    assert text.upper() == "HELLO, WORLD!"


def test_list_operations():
    """Test list operations."""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15
    assert max(numbers) == 5
    assert min(numbers) == 1


@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_doubling(input_val, expected):
    """Test parametrized doubling function."""
    assert input_val * 2 == expected


class TestMathOperations:
    """Test class for math operations."""

    def test_addition(self):
        """Test addition."""
        assert 2 + 3 == 5

    def test_subtraction(self):
        """Test subtraction."""
        assert 5 - 3 == 2

    def test_multiplication(self):
        """Test multiplication."""
        assert 3 * 4 == 12

    def test_division(self):
        """Test division."""
        assert 12 / 3 == 4


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
