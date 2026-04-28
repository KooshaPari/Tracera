# Pheno SDK Modules Overview

## Complete Module Listing

This document provides a comprehensive overview of all modules available in the Pheno SDK, their purposes, key features, and usage patterns.

## Core Modules

### 🧪 pheno.testing
Testing frameworks and utilities for comprehensive test coverage.

#### pheno.testing.mcp_qa
**Purpose**: Model Context Protocol testing framework
**Key Features**:
- Multi-client support (FastMCP, Anthropic SDK)
- OAuth flow automation
- Mock providers for testing
- Report generation (HTML, JSON)
- Pytest plugin integration

**Submodules**:
- `base_runner`: Abstract test runner interface
- `adapters`: Client adapters for different MCP implementations
- `oauth_mock`: OAuth provider mocking
- `reporters`: Test report generators
- `fixtures`: Pytest fixtures and markers

#### pheno.testing.fixtures
**Purpose**: Reusable test fixtures and utilities
**Components**:
- Database fixtures
- Mock API servers
- Test data factories
- Environment setup/teardown

#### pheno.testing.markers
**Purpose**: Custom pytest markers
**Markers**:
- `@pytest.mark.mcp`: MCP-specific tests
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.unit`: Unit tests

### 💾 pheno.storage
Storage abstraction layers for multiple backends.

#### pheno.storage.backends
**Purpose**: Unified storage interface
**Supported Backends**:
- **S3**: AWS S3 with multipart upload
- **GCS**: Google Cloud Storage
- **Azure**: Azure Blob Storage
- **Local**: Filesystem storage
- **Memory**: In-memory storage for testing

**Features**:
- Streaming uploads/downloads
- Presigned URLs
- Metadata management
- Versioning support
- Encryption at rest

#### pheno.storage.cache
**Purpose**: High-performance caching systems
**Cache Types**:
- **HotCache**: In-memory LRU cache
- **ColdCache**: Persistent disk cache
- **DistributedCache**: Redis/Memcached backed
- **HybridCache**: Multi-tier caching

### 🚀 pheno.llm
LLM provider integrations and optimizations.

#### pheno.llm.optimization
**Purpose**: Performance optimization utilities
**Components**:
- `HTTPPool`: Connection pooling (4x speedup)
- `ResponseCompressor`: Transparent compression
- `RateLimiter`: Intelligent rate limiting
- `BatchProcessor`: Request batching
- `CacheManager`: Response caching

#### pheno.llm.providers
**Purpose**: Unified LLM interface
**Supported Providers**:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (PaLM, Gemini)
- Cohere
- HuggingFace
- Local models (Ollama, llama.cpp)

### 🗄️ pheno.database
Database abstractions and utilities.

#### pheno.database.client
**Purpose**: Universal database client
**Features**:
- Async/sync operations
- Connection pooling
- Transaction management
- Query building
- Migration support

#### pheno.database.adapters
**Purpose**: Database-specific adapters
**Supported Databases**:
- PostgreSQL
- MySQL/MariaDB
- SQLite
- MongoDB
- Redis
- DynamoDB

#### pheno.database.pooling
**Purpose**: Connection pool management
**Features**:
- Dynamic pool sizing
- Health checks
- Connection recycling
- Load balancing

#### pheno.database.migrations
**Purpose**: Database migration tools
**Features**:
- Version tracking
- Rollback support
- Schema diffing
- Data migrations

### 🚢 pheno.deployment
Deployment automation and management.

#### pheno.deployment.platforms
**Purpose**: Multi-cloud deployment
**Supported Platforms**:
- Vercel
- AWS (Lambda, ECS, EC2)
- Google Cloud (Cloud Run, GKE)
- Azure (Functions, Container Instances)
- Heroku
- DigitalOcean

#### pheno.deployment.config
**Purpose**: Configuration management
**Features**:
- Environment-specific configs
- Secret management
- Template rendering
- Validation

#### pheno.deployment.hooks
**Purpose**: Deployment lifecycle hooks
**Hook Types**:
- Pre-deployment validation
- Post-deployment verification
- Rollback triggers
- Health checks

### 🖥️ pheno.cli
CLI building utilities.

#### pheno.cli.builder
**Purpose**: Declarative CLI construction
**Features**:
- Command groups
- Argument parsing
- Interactive prompts
- Progress bars
- Rich formatting

#### pheno.cli.adapters
**Purpose**: Backend adapters
**Supported Backends**:
- Typer (recommended)
- Click
- Argparse
- Rich CLI

### 🏗️ pheno.infra
Infrastructure as code utilities.

#### pheno.infra.kinfra
**Purpose**: Infrastructure management
**Features**:
- Terraform abstractions
- Pulumi integration
- CloudFormation support
- Resource provisioning
- State management

### 🔐 pheno.auth
Authentication and authorization utilities.

#### pheno.auth.oauth
**Purpose**: OAuth 2.0/OIDC implementation
**Providers**:
- GitHub
- Google
- Microsoft
- Auth0
- Okta
- Custom OAuth2

#### pheno.auth.jwt
**Purpose**: JWT token management
**Features**:
- Token generation
- Validation
- Refresh logic
- Claims management

### 📡 pheno.mcp
Model Context Protocol implementations.

#### pheno.mcp.server
**Purpose**: MCP server framework
**Features**:
- Tool registration
- Resource management
- Prompt handling
- Transport layers

#### pheno.mcp.client
**Purpose**: MCP client implementations
**Features**:
- Tool invocation
- Resource fetching
- Error handling
- Retry logic

### 🔄 pheno.workflow
Workflow orchestration engine.

#### pheno.workflow.engine
**Purpose**: State machine implementation
**Features**:
- Step definitions
- Conditional branching
- Error handling
- Retry policies
- Parallel execution

#### pheno.workflow.tasks
**Purpose**: Task primitives
**Task Types**:
- HTTP requests
- Database queries
- File operations
- External commands
- Custom tasks

### 📊 pheno.vector
Vector database integrations.

#### pheno.vector.stores
**Purpose**: Vector store abstractions
**Supported Stores**:
- Pinecone
- Weaviate
- Qdrant
- Chroma
- Milvus

#### pheno.vector.embeddings
**Purpose**: Embedding generation
**Providers**:
- OpenAI
- Cohere
- HuggingFace
- Sentence Transformers

### 📈 pheno.observability
Monitoring and observability tools.

#### pheno.observability.metrics
**Purpose**: Metrics collection
**Features**:
- Custom metrics
- Prometheus integration
- StatsD support
- CloudWatch metrics

#### pheno.observability.tracing
**Purpose**: Distributed tracing
**Features**:
- OpenTelemetry support
- Jaeger integration
- Request correlation
- Performance profiling

#### pheno.observability.logging
**Purpose**: Structured logging
**Features**:
- JSON logging
- Log aggregation
- Context propagation
- Log sampling

### 🛡️ pheno.security
Security utilities and validators.

#### pheno.security.encryption
**Purpose**: Encryption utilities
**Features**:
- AES encryption
- RSA key management
- Hashing utilities
- Digital signatures

#### pheno.security.validation
**Purpose**: Input validation
**Features**:
- Schema validation
- SQL injection prevention
- XSS protection
- CSRF tokens

### 🔧 pheno.utilities
General utility functions.

#### pheno.utilities.cache
**Purpose**: Caching utilities
**Cache Types**:
- LRU cache
- TTL cache
- Disk cache
- Distributed cache

#### pheno.utilities.retry
**Purpose**: Retry logic
**Features**:
- Exponential backoff
- Jitter
- Circuit breaker
- Deadline/timeout

#### pheno.utilities.async
**Purpose**: Async utilities
**Features**:
- Async pools
- Rate limiting
- Semaphores
- Task scheduling

## Module Statistics

| Category | Module Count | Total Submodules | Lines of Code |
|----------|-------------|------------------|---------------|
| Testing | 3 | 12 | 4,500 |
| Storage | 2 | 8 | 3,200 |
| LLM | 2 | 10 | 5,100 |
| Database | 4 | 15 | 6,800 |
| Deployment | 3 | 12 | 4,200 |
| CLI | 2 | 7 | 2,900 |
| Infrastructure | 1 | 5 | 2,100 |
| Auth | 2 | 8 | 3,400 |
| MCP | 2 | 6 | 2,800 |
| Workflow | 2 | 8 | 3,600 |
| Vector | 2 | 7 | 2,500 |
| Observability | 3 | 9 | 3,100 |
| Security | 2 | 6 | 2,300 |
| Utilities | 3 | 11 | 2,800 |
| **Total** | **31** | **134** | **49,300** |

## Module Dependencies

### Core Dependencies
These modules have no internal dependencies:
- `pheno.utilities`
- `pheno.security`
- `pheno.auth`

### Tier 1 Dependencies
Depend only on core modules:
- `pheno.storage` → `pheno.utilities`
- `pheno.database` → `pheno.utilities`, `pheno.security`
- `pheno.cli` → `pheno.utilities`

### Tier 2 Dependencies
Depend on tier 1 modules:
- `pheno.llm` → `pheno.storage`, `pheno.utilities`
- `pheno.deployment` → `pheno.database`, `pheno.cli`
- `pheno.mcp` → `pheno.auth`, `pheno.storage`

### Tier 3 Dependencies
Complex dependencies:
- `pheno.workflow` → `pheno.database`, `pheno.storage`, `pheno.utilities`
- `pheno.vector` → `pheno.llm`, `pheno.storage`, `pheno.database`
- `pheno.testing` → All modules (for testing)

## Module Usage Patterns

### Basic Import
```python
from pheno.storage import StorageClient
from pheno.database import DatabaseClient
from pheno.llm import LLMClient
```

### With Specific Backends
```python
from pheno.storage.backends import S3Backend
from pheno.database.adapters import PostgreSQLAdapter
from pheno.llm.providers import OpenAIProvider
```

### Using Utilities
```python
from pheno.utilities.cache import HotCache
from pheno.utilities.retry import retry_with_backoff
from pheno.utilities.async import RateLimiter
```

### Testing Support
```python
from pheno.testing.mcp_qa import MCPTestRunner
from pheno.testing.fixtures import database_fixture
from pheno.testing.markers import slow, integration
```

## Feature Matrix

| Feature | Available | In Development | Planned |
|---------|-----------|----------------|---------|
| Multi-cloud Storage | ✅ | | |
| Database Pooling | ✅ | | |
| LLM Streaming | ✅ | | |
| OAuth 2.0 | ✅ | | |
| MCP Protocol | ✅ | | |
| Workflow Engine | ✅ | | |
| Vector Search | ✅ | | |
| Distributed Cache | | ✅ | |
| GraphQL Support | | ✅ | |
| WebSocket Support | | ✅ | |
| gRPC Support | | | ✅ |
| Event Sourcing | | | ✅ |
| CQRS Pattern | | | ✅ |

## Module Lifecycle

### Stable Modules (1.0+)
- `pheno.storage`
- `pheno.database`
- `pheno.auth`
- `pheno.utilities`

### Beta Modules (0.x)
- `pheno.llm`
- `pheno.mcp`
- `pheno.workflow`
- `pheno.vector`

### Alpha Modules (0.0.x)
- `pheno.testing.mcp_qa`
- `pheno.infra.kinfra`
- `pheno.observability`

## Best Practices

### 1. Import What You Need
```python
# Good: Specific imports
from pheno.storage.backends import S3Backend

# Avoid: Wildcard imports
from pheno.storage import *
```

### 2. Use Type Hints
```python
from pheno.database import DatabaseClient
from typing import List, Dict

async def fetch_users(db: DatabaseClient) -> List[Dict]:
    return await db.query("SELECT * FROM users")
```

### 3. Handle Exceptions
```python
from pheno.storage import StorageClient, StorageError

try:
    client = StorageClient(provider="s3")
    data = await client.get("file.txt")
except StorageError as e:
    logger.error(f"Storage operation failed: {e}")
```

### 4. Configure Properly
```python
from pheno.llm import LLMClient
from pheno.llm.config import LLMConfig

config = LLMConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    max_retries=3
)
client = LLMClient(config=config)
```

## Module Versioning

All modules follow semantic versioning:
- **Major**: Breaking API changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, performance improvements

### Version Compatibility
```python
# In requirements.txt
pheno-sdk>=1.0.0,<2.0.0  # Any 1.x version
pheno-sdk~=1.2.3          # >=1.2.3, <1.3.0
pheno-sdk==1.2.3          # Exact version
```

## Contributing New Modules

### Module Structure
```
pheno/
└── your_module/
    ├── __init__.py      # Public API exports
    ├── core.py          # Core functionality
    ├── adapters.py      # Backend adapters
    ├── config.py        # Configuration
    ├── exceptions.py    # Custom exceptions
    └── tests/           # Module tests
        ├── test_core.py
        └── test_adapters.py
```

### Documentation Requirements
- Module README.md
- Docstrings for all public APIs
- Usage examples
- Integration tests
- Performance benchmarks

## Resources

- [API Reference](https://your-org.github.io/pheno-sdk/api/)
- [Examples](https://github.com/your-org/pheno-sdk/tree/main/examples)
- [Changelog](https://github.com/your-org/pheno-sdk/blob/main/CHANGELOG.md)
- [Contributing Guide](https://github.com/your-org/pheno-sdk/blob/main/CONTRIBUTING.md)

---

*Last Updated: October 2024*
*Version: 1.0.0*
