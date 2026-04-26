# phenotype-logging

Structured logging utilities for Phenotype services using structlog.

## Features

- **JSON Logging**: Machine-readable JSON output
- **Structured Logging**: Context-aware logging with structlog
- **Service Identification**: Optional service name in all logs
- **Level Control**: DEBUG, INFO, WARNING, ERROR, CRITICAL levels

## Installation

```bash
pip install phenotype-logging
```

## Quick Start

```python
from phenotype_logging import configure_logging, get_logger

# Configure logging
configure_logging(level="DEBUG", service_name="my-service")

# Get logger
logger = get_logger(__name__)

# Log structured data
logger.info("service started", version="1.0.0", environment="production")
logger.error("request failed", request_id="123", status_code=500)
```

## License

MIT
