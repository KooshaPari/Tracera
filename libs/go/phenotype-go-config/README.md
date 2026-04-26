# phenotype-go-config

Shared configuration utilities for Phenotype services using Viper.

## Features

- **YAML Configuration**: Load configuration from YAML files
- **Environment Variables**: Automatic environment variable binding
- **Type-Safe Getters**: Methods for string, int, bool, and map values
- **Default Values**: Built-in defaults for common settings
- **Template Generation**: Bootstrap configuration files

## Installation

```bash
go get github.com/KooshaPari/phenotype-go-config
```

## Quick Start

```go
import "github.com/KooshaPari/phenotype-go-config"

// Create loader
loader := config.NewConfigLoader("./config.yaml")

// Load configuration
if err := loader.Load(); err != nil {
    log.Fatal(err)
}

// Get values
serverPort := loader.GetInt("server.port")
logLevel := loader.GetString("log.level")

// Unmarshal to struct
var appConfig struct {
    Server struct {
        Host string
        Port int
    }
}
loader.Unmarshal(&appConfig)
```

## License

MIT
