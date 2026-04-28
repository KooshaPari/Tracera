"""
Integration test template for {module_name}.
"""

import pytest
from {module_path} import {class_name}


@pytest.mark.integration
class Test{class_name}Integration:
    """Integration tests for {class_name}."""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self):
        """Set up integration test environment."""
        # Set up test database, external services, etc.
        pass
    
    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # Test the entire flow from start to finish
        pass
    
    def test_external_service_integration(self):
        """Test integration with external services."""
        # Test actual external service calls
        pass
