# Basic Usage Tutorial

This tutorial will guide you through the basic usage of the Pheno SDK.

## Prerequisites

- Python 3.8 or higher
- Basic knowledge of Python
- Pheno SDK installed

## Installation

```bash
pip install pheno-sdk
```

## Getting Started

### 1. Import the SDK

```python
from pheno import PhenoSDK
```

### 2. Initialize the SDK

```python
# Basic initialization
sdk = PhenoSDK()

# With configuration
sdk = PhenoSDK(config={
    'debug': True,
    'log_level': 'INFO'
})
```

### 3. Process Data

```python
# Process simple data
data = "Hello, World!"
result = sdk.process_data(data)
print(result)

# Process complex data
complex_data = {
    'text': 'Hello, World!',
    'metadata': {'source': 'tutorial'}
}
result = sdk.process_data(complex_data)
print(result)
```

### 4. Get Analytics

```python
# Get basic analytics
analytics = sdk.get_analytics()
print(f"Processed items: {analytics['processed_count']}")
print(f"Success rate: {analytics['success_rate']}%")
```

## Next Steps

- [Advanced Features Tutorial](advanced-features.md)
- [Integration Examples](integration.md)
- [API Reference](../api/)

---

*This tutorial is automatically generated.*
