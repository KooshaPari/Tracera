# phenotype-go-kit

**DEPRECATED**: This monolithic kit has been split into standalone packages. Please use the individual packages instead:

- [phenotype-go-auth](../phenotype-go-auth) - Authentication and token management
- [phenotype-go-middleware](../phenotype-go-middleware) - HTTP middleware utilities
- [phenotype-go-config](../phenotype-go-config) - Configuration loading
- [phenotype-go-cli](../phenotype-go-cli) - CLI command utilities
- [phenotype-id](../phenotype-id) - ID/UUID generation (cross-language)

This module is maintained for backward compatibility only. New projects should use the standalone packages above.

---

A shared Go module for common functionality across Phenotype services, including authentication, middleware, configuration, and CLI scaffolding.

## Features

### Authentication (`pkg/auth/`)
- **TokenStorage Interface**: Generic token storage interface for OAuth2 tokens
- **BaseTokenStorage**: Base implementation with common fields (access token, refresh token, ID token, email, etc.)
- **OAuth Support**:
  - PKCE code generation for secure OAuth flows
  - OAuthServer for handling local OAuth callbacks
  - Standard OAuth result handling

### Middleware (`pkg/middleware/`)
- **DefaultMiddlewareStack**: Pre-configured chi router middleware including:
  - Panic recovery
  - Request logging
  - CORS support
  - Request ID tracking
- **Health check handlers** for liveness and readiness probes

### Configuration (`pkg/config/`)
- **ConfigLoader**: Viper-based YAML configuration loading with:
  - Support for both file and directory paths
  - Environment variable binding
  - Type-safe getter methods
  - Default configuration values

### CLI (`pkg/cli/`)
- **Root Command Scaffolding**: Create cobra root commands with built-in flags
- **CommandBuilder**: Fluent interface for building cobra commands
- **Standard error handling** for CLI applications

## Installation

```bash
go get github.com/KooshaPari/phenotype-go-kit
```

## Usage Examples

### Authentication

```go
import "github.com/KooshaPari/phenotype-go-kit/pkg/auth"

// Create a token storage
storage := auth.NewBaseTokenStorage("/path/to/token.json")

// Load token from file
if err := storage.Load(); err != nil {
    log.Fatal(err)
}

// Use token data
email := storage.GetEmail()
accessToken := storage.GetAccessToken()

// Save token
if err := storage.Save(); err != nil {
    log.Fatal(err)
}

// Generate PKCE codes for OAuth
codes, err := auth.GeneratePKCECodes()
if err != nil {
    log.Fatal(err)
}

// Start OAuth callback server
oauthServer := auth.NewOAuthServer(8080)
if err := oauthServer.Start(); err != nil {
    log.Fatal(err)
}

// Wait for callback
result, err := oauthServer.WaitForCallback(5 * time.Minute)
if err != nil {
    log.Fatal(err)
}
```

### Middleware

```go
import (
    "github.com/go-chi/chi/v5"
    "github.com/KooshaPari/phenotype-go-kit/pkg/middleware"
)

router := chi.NewRouter()

// Apply default middleware stack
if err := middleware.DefaultMiddlewareStack(router); err != nil {
    log.Fatal(err)
}

// Add routes
router.Get("/health", middleware.HealthCheckHandler)
router.Get("/ready", middleware.ReadinessCheckHandler)
```

### Configuration

```go
import "github.com/KooshaPari/phenotype-go-kit/pkg/config"

// Load configuration
loader := config.NewConfigLoader("./config.yaml")
if err := loader.Load(); err != nil {
    log.Fatal(err)
}

// Get configuration values
serverPort := loader.GetInt("server.port")
logLevel := loader.GetString("log.level")

// Unmarshal to struct
var appConfig struct {
    Server struct {
        Host string
        Port int
    }
    Log struct {
        Level string
    }
}
if err := loader.Unmarshal(&appConfig); err != nil {
    log.Fatal(err)
}
```

### CLI

```go
import "github.com/KooshaPari/phenotype-go-kit/pkg/cli"

func main() {
    rootCmd := cli.CreateRootCommand(
        cli.RootCommandConfig{
            Name:    "myapp",
            Short:   "My application",
            Long:    "A longer description of my application",
            Version: "1.0.0",
        },
        func(cmd *cobra.Command, args []string) error {
            fmt.Println("Hello from myapp!")
            return nil
        },
    )

    os.Exit(cli.ExecuteCommand(rootCmd))
}
```

## BaseTokenStorage Fields

The `BaseTokenStorage` struct includes the following fields:

- `IDToken` (string): JWT ID token with user claims
- `AccessToken` (string): OAuth2 access token for API requests
- `RefreshToken` (string): Token for obtaining new access tokens
- `LastRefresh` (string): Timestamp of last token refresh
- `Email` (string): Email associated with the token
- `Type` (string): Provider type (e.g., "claude", "github-copilot")
- `Expire` (string): Expiration timestamp of the access token
- `Metadata` (map[string]any): Arbitrary provider-specific data

## License

MIT
