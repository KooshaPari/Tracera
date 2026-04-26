// Package cli provides shared CLI utilities for Phenotype services.
package cli

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

// RootCommandConfig holds configuration for creating a root cobra command.
type RootCommandConfig struct {
	// Name is the name of the CLI tool.
	Name string

	// Short is a short description of the tool.
	Short string

	// Long is a long description of the tool.
	Long string

	// Version is the semantic version of the tool.
	Version string

	// Examples are usage examples for the tool.
	Examples string
}

// CreateRootCommand creates a new root cobra command with standard scaffolding.
// It includes built-in flags for verbose logging and version information.
//
// Parameters:
//   - config: The root command configuration
//   - runFunc: The function to execute when the root command is run
//
// Returns:
//   - *cobra.Command: A new root cobra command
func CreateRootCommand(config RootCommandConfig, runFunc func(cmd *cobra.Command, args []string) error) *cobra.Command {
	// Create the root command
	rootCmd := &cobra.Command{
		Use:     config.Name,
		Short:   config.Short,
		Long:    config.Long,
		Version: config.Version,
		Examples: config.Examples,
		RunE:    runFunc,
		CompletionOptions: cobra.CompletionOptions{
			DisableDefaultCmd: false,
		},
	}

	// Add verbose flag
	rootCmd.PersistentFlags().BoolP("verbose", "v", false, "Enable verbose logging")

	return rootCmd
}

// AddCommand adds a subcommand to the root command.
//
// Parameters:
//   - rootCmd: The root command to add the subcommand to
//   - subCmd: The subcommand to add
func AddCommand(rootCmd *cobra.Command, subCmd *cobra.Command) {
	rootCmd.AddCommand(subCmd)
}

// CreateCommand creates a new cobra command with standard scaffolding.
//
// Parameters:
//   - use: The command name
//   - short: Short description
//   - long: Long description
//   - examples: Usage examples
//   - runFunc: The function to execute when the command is run
//
// Returns:
//   - *cobra.Command: A new cobra command
func CreateCommand(use string, short string, long string, examples string, runFunc func(cmd *cobra.Command, args []string) error) *cobra.Command {
	return &cobra.Command{
		Use:      use,
		Short:    short,
		Long:     long,
		Examples: examples,
		RunE:     runFunc,
	}
}

// ExecuteCommand executes a cobra command and handles errors.
// This is a convenience function for executing the root command.
//
// Parameters:
//   - rootCmd: The root command to execute
//
// Returns:
//   - int: The exit code (0 for success, non-zero for error)
func ExecuteCommand(rootCmd *cobra.Command) int {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		return 1
	}
	return 0
}

// VersionFlagValue is a custom flag value type for handling version display.
// It implements the pflag.Value interface.
type VersionFlagValue struct {
	version string
	called  bool
}

// String returns the string representation of the version.
func (v *VersionFlagValue) String() string {
	return v.version
}

// Set handles the flag being set.
func (v *VersionFlagValue) Set(val string) error {
	v.called = true
	v.version = val
	return nil
}

// Type returns the type name of the flag.
func (v *VersionFlagValue) Type() string {
	return "version"
}

// IsCalled returns true if the version flag was set.
func (v *VersionFlagValue) IsCalled() bool {
	return v.called
}

// CommandBuilder provides a fluent interface for building cobra commands.
type CommandBuilder struct {
	cmd *cobra.Command
}

// NewCommandBuilder creates a new CommandBuilder.
//
// Parameters:
//   - use: The command name
//
// Returns:
//   - *CommandBuilder: A new CommandBuilder instance
func NewCommandBuilder(use string) *CommandBuilder {
	return &CommandBuilder{
		cmd: &cobra.Command{
			Use: use,
		},
	}
}

// Short sets the short description of the command.
func (cb *CommandBuilder) Short(short string) *CommandBuilder {
	cb.cmd.Short = short
	return cb
}

// Long sets the long description of the command.
func (cb *CommandBuilder) Long(long string) *CommandBuilder {
	cb.cmd.Long = long
	return cb
}

// Examples sets the usage examples of the command.
func (cb *CommandBuilder) Examples(examples string) *CommandBuilder {
	cb.cmd.Examples = examples
	return cb
}

// RunE sets the RunE function of the command.
func (cb *CommandBuilder) RunE(runFunc func(cmd *cobra.Command, args []string) error) *CommandBuilder {
	cb.cmd.RunE = runFunc
	return cb
}

// Run sets the Run function of the command.
func (cb *CommandBuilder) Run(runFunc func(cmd *cobra.Command, args []string)) *CommandBuilder {
	cb.cmd.Run = runFunc
	return cb
}

// StringFlag adds a string flag to the command.
func (cb *CommandBuilder) StringFlag(name string, shorthand string, defaultValue string, usage string) *CommandBuilder {
	cb.cmd.Flags().StringP(name, shorthand, defaultValue, usage)
	return cb
}

// BoolFlag adds a boolean flag to the command.
func (cb *CommandBuilder) BoolFlag(name string, shorthand string, defaultValue bool, usage string) *CommandBuilder {
	cb.cmd.Flags().BoolP(name, shorthand, defaultValue, usage)
	return cb
}

// IntFlag adds an integer flag to the command.
func (cb *CommandBuilder) IntFlag(name string, shorthand string, defaultValue int, usage string) *CommandBuilder {
	cb.cmd.Flags().IntP(name, shorthand, defaultValue, usage)
	return cb
}

// AddSubcommand adds a subcommand to the command.
func (cb *CommandBuilder) AddSubcommand(subCmd *cobra.Command) *CommandBuilder {
	cb.cmd.AddCommand(subCmd)
	return cb
}

// Build returns the constructed cobra command.
func (cb *CommandBuilder) Build() *cobra.Command {
	return cb.cmd
}

// StandardErrorHandler provides standard error handling for commands.
// It logs the error and returns an appropriate exit code.
//
// Parameters:
//   - rootCmd: The root command
//   - err: The error that occurred
//
// Returns:
//   - int: The exit code
func StandardErrorHandler(rootCmd *cobra.Command, err error) int {
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		return 1
	}
	return 0
}
