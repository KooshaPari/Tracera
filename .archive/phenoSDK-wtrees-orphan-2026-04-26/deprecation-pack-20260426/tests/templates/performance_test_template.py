"""
Performance test template for {module_name}.
"""

import pytest
import time
from {module_path} import {class_name}


@pytest.mark.performance
class Test{class_name}Performance:
    """Performance tests for {class_name}."""
    
    def test_execution_time(self):
        """Test method execution time."""
        instance = {class_name}()
        
        start_time = time.time()
        result = instance.example_method("test")
        execution_time = time.time() - start_time
        
        assert execution_time < 1.0  # Should complete within 1 second
        assert result is not None
    
    @pytest.mark.benchmark
    def test_benchmark_performance(self, benchmark):
        """Benchmark performance of critical methods."""
        instance = {class_name}()
        result = benchmark(instance.example_method, "test")
        assert result is not None
