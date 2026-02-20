// Package plugin provides plugin interfaces and management.
package plugin

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"path/filepath"
	"plugin"
)

// Interface defines the interface all plugins must implement
type Interface interface {
	Name() string
	Version() string
	Execute(args map[string]interface{}) (interface{}, error)
}

// Manager manages plugin loading and execution
type Manager struct {
	plugins   map[string]Interface
	pluginDir string
}

// NewManager creates a new plugin manager.
func NewManager(pluginDir string) *Manager {
	return &Manager{
		plugins:   make(map[string]Interface),
		pluginDir: pluginDir,
	}
}

// LoadPlugin loads a plugin from a .so file
func (pm *Manager) LoadPlugin(name string) error {
	pluginPath := filepath.Join(pm.pluginDir, name+".so")

	// Check if plugin file exists
	if _, err := os.Stat(pluginPath); err != nil {
		return fmt.Errorf("plugin not found: %s", pluginPath)
	}

	// Load the plugin
	p, err := plugin.Open(pluginPath)
	if err != nil {
		return fmt.Errorf("failed to load plugin: %w", err)
	}

	// Look for the New function
	newFunc, err := p.Lookup("New")
	if err != nil {
		return fmt.Errorf("plugin missing New function: %w", err)
	}

	// Call the New function to get the plugin instance
	pluginInstance, ok := newFunc.(func() Interface)
	if !ok {
		return errors.New("invalid plugin interface")
	}

	instance := pluginInstance()
	pm.plugins[instance.Name()] = instance
	slog.Info("Loaded plugin (v )", "name", instance.Name(), "detail", instance.Version())

	return nil
}

// LoadAllPlugins loads all plugins from the plugin directory
func (pm *Manager) LoadAllPlugins() error {
	entries, err := os.ReadDir(pm.pluginDir)
	if err != nil {
		return fmt.Errorf("failed to read plugin directory: %w", err)
	}

	for _, entry := range entries {
		if !entry.IsDir() && filepath.Ext(entry.Name()) == ".so" {
			name := entry.Name()[:len(entry.Name())-3] // Remove .so extension
			if err := pm.LoadPlugin(name); err != nil {
				slog.Error("Warning: failed to load plugin", "error", name, "error", err)
			}
		}
	}

	return nil
}

// ExecutePlugin executes a plugin with the given arguments
func (pm *Manager) ExecutePlugin(name string, args map[string]interface{}) (interface{}, error) {
	p, ok := pm.plugins[name]
	if !ok {
		return nil, fmt.Errorf("plugin not found: %s", name)
	}

	return p.Execute(args)
}

// ListPlugins returns a list of loaded plugins
func (pm *Manager) ListPlugins() []string {
	names := make([]string, 0, len(pm.plugins))
	for name := range pm.plugins {
		names = append(names, name)
	}
	return names
}

// UnloadPlugin unloads a plugin
func (pm *Manager) UnloadPlugin(name string) error {
	if _, ok := pm.plugins[name]; !ok {
		return fmt.Errorf("plugin not found: %s", name)
	}

	delete(pm.plugins, name)
	slog.Info("Unloaded plugin", "name", name)
	return nil
}

// BuildPlugin builds a plugin from source
func (pm *Manager) BuildPlugin(sourcePath string, outputName string) error {
	outputPath := filepath.Join(pm.pluginDir, outputName+".so")
	cmd := exec.CommandContext( //nolint:gosec // G204: paths are controlled by plugin manager, not arbitrary user input
		context.Background(), "go", "build", "-buildmode=plugin", "-o", outputPath, sourcePath,
	)
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to build plugin: %w", err)
	}

	slog.Info("Built plugin", "name", outputName)
	return nil
}

// GetPlugin returns a plugin by name
func (pm *Manager) GetPlugin(name string) (Interface, error) {
	p, ok := pm.plugins[name]
	if !ok {
		return nil, fmt.Errorf("plugin not found: %s", name)
	}
	return p, nil
}
