# phenotype-id

Cross-language UUID generation utilities for Phenotype services.

## Overview

This package provides consistent ID generation across Go, Python, and TypeScript implementations.

## Features

- **UUID Generation**: Standard UUID v4 generation
- **Prefixed IDs**: Request, trace, and correlation ID generation with prefixes
- **UUID Validation**: Validate UUID strings
- **Cross-Language**: Identical APIs across Go, Python, and TypeScript

## Installation

### Go

```bash
go get github.com/KooshaPari/phenotype-id
```

### Python

```bash
pip install phenotype-id
```

### TypeScript

```bash
npm install @phenotype/id
```

## Quick Start

### Go

```go
import "github.com/KooshaPari/phenotype-id"

gen := id.NewGenerator()
requestID := gen.GenerateRequestID()  // "req-<uuid>"
traceID := gen.GenerateTraceID()      // "trace-<uuid>"
```

### Python

```python
from phenotype_id import Generator

gen = Generator()
request_id = gen.generate_request_id()  # "req-<uuid>"
trace_id = gen.generate_trace_id()      # "trace-<uuid>"
```

### TypeScript

```typescript
import Generator from "@phenotype/id";

const requestID = Generator.generateRequestID();  // "req-<uuid>"
const traceID = Generator.generateTraceID();      // "trace-<uuid>"
```

## License

MIT
