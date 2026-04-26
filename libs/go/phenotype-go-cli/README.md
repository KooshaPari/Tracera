# phenotype-go-cli

Shared CLI utilities for Phenotype services using Cobra.

## Features

- **Root Command Scaffolding**: Create cobra root commands with standard flags
- **CommandBuilder**: Fluent interface for building commands
- **Error Handling**: Standard error handling and exit codes
- **Version Support**: Built-in version flag handling

## Installation

```bash
go get github.com/KooshaPari/phenotype-go-cli
```

## Quick Start

```go
import (
    "github.com/KooshaPari/phenotype-go-cli"
    "github.com/spf13/cobra"
)

func main() {
    rootCmd := cli.CreateRootCommand(
        cli.RootCommandConfig{
            Name:    "myapp",
            Short:   "My application",
            Long:    "A longer description",
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

## License

MIT
