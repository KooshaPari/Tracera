"""
Unit test template for {module_name}.
"""

import pytest
from unittest.mock import Mock, patch
from {module_path} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {class_name}()
    
    def test_initialization(self):
        """Test object initialization."""
        assert self.instance is not None
    
    def test_method_example(self):
        """Test example method."""
        # Arrange
        input_value = "test"
        
        # Act
        result = self.instance.example_method(input_value)
        
        # Assert
        assert result is not None
    
    @pytest.mark.parametrize("input_val,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_parametrized(self, input_val, expected):
        """Test with multiple parameters."""
        result = self.instance.example_method(input_val)
        assert result == expected
    
    @patch('{module_path}.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies."""
        mock_dependency.return_value = "mocked"
        result = self.instance.method_with_dependency()
        assert result == "mocked"
        mock_dependency.assert_called_once()
