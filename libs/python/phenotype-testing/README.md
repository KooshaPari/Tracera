# phenotype-testing

Shared pytest fixtures and testing utilities for Phenotype services.

## Features

- **tmp_dir Fixture**: Temporary directory for test files
- **mock_config Fixture**: BaseConfig instance with test defaults
- **mock_request_context Fixture**: Mock request context data
- **AsyncTestHelper**: Utilities for async test operations

## Installation

```bash
pip install phenotype-testing
```

## Quick Start

```python
import pytest

def test_something(tmp_dir, mock_config, async_helper):
    # tmp_dir is a temporary Path
    # mock_config is BaseConfig with environment="test"
    # async_helper provides wait_for_condition()
    pass

# In conftest.py, make fixtures available
import pytest
from phenotype_testing import tmp_dir, mock_config, async_helper
```

## License

MIT
