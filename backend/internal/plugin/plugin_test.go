package plugin

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// MockPlugin implements Interface for testing
type MockPlugin struct {
	name    string
	version string
	execFn  func(_ map[string]interface{}) (interface{}, error)
}

func (m *MockPlugin) Name() string {
	return m.name
}

func (m *MockPlugin) Version() string {
	return m.version
}

func (m *MockPlugin) Execute(args map[string]interface{}) (interface{}, error) {
	if m.execFn != nil {
		return m.execFn(args)
	}
	return "mock result", nil
}

// TestNewPluginManager tests plugin manager creation
func TestNewPluginManager(t *testing.T) {
	tests := []struct {
		name      string
		pluginDir string
	}{
		{
			name:      "valid directory path",
			pluginDir: "/tmp/plugins",
		},
		{
			name:      "empty directory path",
			pluginDir: "",
		},
		{
			name:      "relative path",
			pluginDir: "./plugins",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager(tt.pluginDir)

			assert.NotNil(t, pm)
			assert.NotNil(t, pm.plugins)
			assert.Equal(t, tt.pluginDir, pm.pluginDir)
			assert.Empty(t, pm.plugins)
		})
	}
}

// TestPluginManagerLoadPlugin tests loading plugins
func TestPluginManagerLoadPlugin(t *testing.T) {
	tests := []struct {
		name        string
		setupFn     func() string
		pluginName  string
		expectError bool
		errorMsg    string
	}{
		{
			name: "plugin file not found",
			setupFn: func() string {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				return tmpDir
			},
			pluginName:  "nonexistent",
			expectError: true,
			errorMsg:    "plugin not found",
		},
		{
			name: "empty plugin name",
			setupFn: func() string {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				return tmpDir
			},
			pluginName:  "",
			expectError: true,
			errorMsg:    "plugin not found",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pluginDir := tt.setupFn()
			defer func() { require.NoError(t, os.RemoveAll(pluginDir)) }()

			pm := NewManager(pluginDir)
			err := pm.LoadPlugin(tt.pluginName)

			if tt.expectError {
				require.Error(t, err)
				if tt.errorMsg != "" {
					assert.Contains(t, err.Error(), tt.errorMsg)
				}
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// TestPluginManagerLoadAllPlugins tests loading all plugins from directory
func TestPluginManagerLoadAllPlugins(t *testing.T) {
	tests := []struct {
		name        string
		setupFn     func() string
		expectError bool
	}{
		{
			name: "empty directory",
			setupFn: func() string {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				return tmpDir
			},
			expectError: false,
		},
		{
			name: "directory with non-plugin files",
			setupFn: func() string {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				// Create non-.so files
				require.NoError(t, os.WriteFile(filepath.Join(tmpDir, "readme.txt"), []byte("test"), 0o600))
				require.NoError(t, os.WriteFile(filepath.Join(tmpDir, "config.json"), []byte("{}"), 0o600))
				return tmpDir
			},
			expectError: false,
		},
		{
			name: "nonexistent directory",
			setupFn: func() string {
				return "/nonexistent/directory/path"
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pluginDir := tt.setupFn()
			if tt.name != "nonexistent directory" {
				defer func() { require.NoError(t, os.RemoveAll(pluginDir)) }()
			}

			pm := NewManager(pluginDir)
			err := pm.LoadAllPlugins()

			if tt.expectError {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// TestPluginManagerExecutePlugin tests plugin execution
func TestPluginManagerExecutePlugin(t *testing.T) {
	for _, tt := range executePluginCases() {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager("/tmp/plugins")
			tt.setupFn(pm)

			result, err := pm.ExecutePlugin(tt.pluginName, tt.args)

			if tt.expectError {
				require.Error(t, err)
				if tt.errorMsg != "" {
					assert.Contains(t, err.Error(), tt.errorMsg)
				}
				assert.Nil(t, result)
			} else {
				require.NoError(t, err)
				assert.NotNil(t, result)
			}
		})
	}
}

// TestPluginManagerListPlugins tests listing loaded plugins
func TestPluginManagerListPlugins(t *testing.T) {
	tests := []struct {
		name          string
		setupFn       func(*Manager)
		expectedCount int
		expectedNames []string
	}{
		{
			name:          "empty plugin list",
			setupFn:       func(_ *Manager) {},
			expectedCount: 0,
			expectedNames: []string{},
		},
		{
			name: "single plugin",
			setupFn: func(pm *Manager) {
				pm.plugins["plugin1"] = &MockPlugin{name: "plugin1", version: "1.0.0"}
			},
			expectedCount: 1,
			expectedNames: []string{"plugin1"},
		},
		{
			name: "multiple plugins",
			setupFn: func(pm *Manager) {
				pm.plugins["plugin1"] = &MockPlugin{name: "plugin1", version: "1.0.0"}
				pm.plugins["plugin2"] = &MockPlugin{name: "plugin2", version: "2.0.0"}
				pm.plugins["plugin3"] = &MockPlugin{name: "plugin3", version: "1.5.0"}
			},
			expectedCount: 3,
			expectedNames: []string{"plugin1", "plugin2", "plugin3"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager("/tmp/plugins")
			tt.setupFn(pm)

			plugins := pm.ListPlugins()

			assert.Len(t, plugins, tt.expectedCount)
			for _, expectedName := range tt.expectedNames {
				assert.Contains(t, plugins, expectedName)
			}
		})
	}
}

// TestPluginManagerUnloadPlugin tests unloading plugins
func TestPluginManagerUnloadPlugin(t *testing.T) {
	tests := []struct {
		name        string
		setupFn     func(*Manager)
		pluginName  string
		expectError bool
		errorMsg    string
	}{
		{
			name: "unload existing plugin",
			setupFn: func(pm *Manager) {
				pm.plugins["test-plugin"] = &MockPlugin{name: "test-plugin", version: "1.0.0"}
			},
			pluginName:  "test-plugin",
			expectError: false,
		},
		{
			name:        "unload nonexistent plugin",
			setupFn:     func(_ *Manager) {},
			pluginName:  "nonexistent",
			expectError: true,
			errorMsg:    "plugin not found",
		},
		{
			name:        "unload empty plugin name",
			setupFn:     func(_ *Manager) {},
			pluginName:  "",
			expectError: true,
			errorMsg:    "plugin not found",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager("/tmp/plugins")
			tt.setupFn(pm)

			err := pm.UnloadPlugin(tt.pluginName)

			if tt.expectError {
				require.Error(t, err)
				if tt.errorMsg != "" {
					assert.Contains(t, err.Error(), tt.errorMsg)
				}
			} else {
				require.NoError(t, err)
				// Verify plugin was removed
				assert.NotContains(t, pm.plugins, tt.pluginName)
			}
		})
	}
}

// TestPluginManagerBuildPlugin tests building plugins from source
func TestPluginManagerBuildPlugin(t *testing.T) {
	tests := []struct {
		name        string
		setupFn     func() (string, string)
		outputName  string
		expectError bool
	}{
		{
			name: "invalid source path",
			setupFn: func() (string, string) {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				return "/nonexistent/source.go", tmpDir
			},
			outputName:  "test-plugin",
			expectError: true,
		},
		{
			name: "empty output name",
			setupFn: func() (string, string) {
				tmpDir, err := os.MkdirTemp("", "plugin-test-*")
				require.NoError(t, err)
				sourceFile := filepath.Join(tmpDir, "plugin.go")
				require.NoError(t, os.WriteFile(sourceFile, []byte("package main\n"), 0o600))
				return sourceFile, tmpDir
			},
			outputName:  "",
			expectError: false, // Empty name is allowed, creates .so file
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sourcePath, pluginDir := tt.setupFn()
			defer func() { require.NoError(t, os.RemoveAll(pluginDir)) }()

			pm := NewManager(pluginDir)
			err := pm.BuildPlugin(sourcePath, tt.outputName)

			if tt.expectError {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

// TestPluginManagerGetPlugin tests getting plugin by name
func TestPluginManagerGetPlugin(t *testing.T) {
	tests := []struct {
		name        string
		setupFn     func(*Manager)
		pluginName  string
		expectError bool
		errorMsg    string
	}{
		{
			name: "get existing plugin",
			setupFn: func(pm *Manager) {
				pm.plugins["test-plugin"] = &MockPlugin{
					name:    "test-plugin",
					version: "1.0.0",
				}
			},
			pluginName:  "test-plugin",
			expectError: false,
		},
		{
			name:        "get nonexistent plugin",
			setupFn:     func(_ *Manager) {},
			pluginName:  "nonexistent",
			expectError: true,
			errorMsg:    "plugin not found",
		},
		{
			name:        "get with empty name",
			setupFn:     func(_ *Manager) {},
			pluginName:  "",
			expectError: true,
			errorMsg:    "plugin not found",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager("/tmp/plugins")
			tt.setupFn(pm)

			plugin, err := pm.GetPlugin(tt.pluginName)

			if tt.expectError {
				require.Error(t, err)
				assert.Nil(t, plugin)
				if tt.errorMsg != "" {
					assert.Contains(t, err.Error(), tt.errorMsg)
				}
			} else {
				require.NoError(t, err)
				assert.NotNil(t, plugin)
				assert.Equal(t, tt.pluginName, plugin.Name())
			}
		})
	}
}

// TestPluginInterface tests the plugin interface implementation
func TestPluginInterface(t *testing.T) {
	tests := []struct {
		name           string
		plugin         Interface
		expectedName   string
		expectedVer    string
		executeArgs    map[string]interface{}
		expectedResult interface{}
	}{
		{
			name: "basic mock plugin",
			plugin: &MockPlugin{
				name:    "test",
				version: "1.0.0",
			},
			expectedName:   "test",
			expectedVer:    "1.0.0",
			executeArgs:    map[string]interface{}{"input": "data"},
			expectedResult: "mock result",
		},
		{
			name: "plugin with custom execute",
			plugin: &MockPlugin{
				name:    "custom",
				version: "2.0.0",
				execFn: func(args map[string]interface{}) (interface{}, error) {
					return args["value"], nil
				},
			},
			expectedName:   "custom",
			expectedVer:    "2.0.0",
			executeArgs:    map[string]interface{}{"value": 42},
			expectedResult: 42,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.expectedName, tt.plugin.Name())
			assert.Equal(t, tt.expectedVer, tt.plugin.Version())

			result, err := tt.plugin.Execute(tt.executeArgs)
			require.NoError(t, err)
			assert.Equal(t, tt.expectedResult, result)
		})
	}
}

// TestPluginManagerConcurrentOperations tests concurrent plugin operations
func TestPluginManagerConcurrentOperations(t *testing.T) {
	pm := NewManager("/tmp/plugins")

	// Add some plugins
	for i := 0; i < 10; i++ {
		pluginName := "plugin" + string(rune('0'+i))
		pm.plugins[pluginName] = &MockPlugin{
			name:    pluginName,
			version: "1.0.0",
		}
	}

	// Test concurrent ListPlugins calls
	done := make(chan bool, 10)
	for i := 0; i < 10; i++ {
		go func() {
			plugins := pm.ListPlugins()
			assert.Len(t, plugins, 10)
			done <- true
		}()
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}
}

// TestPluginManagerLoadPluginPathConstruction tests path construction
func TestPluginManagerLoadPluginPathConstruction(t *testing.T) {
	tests := []struct {
		name       string
		pluginDir  string
		pluginName string
		expectPath string
	}{
		{
			name:       "simple path",
			pluginDir:  "/plugins",
			pluginName: "test",
			expectPath: "/plugins/test.so",
		},
		{
			name:       "path with trailing slash",
			pluginDir:  "/plugins/",
			pluginName: "test",
			expectPath: "/plugins/test.so",
		},
		{
			name:       "relative path",
			pluginDir:  "./plugins",
			pluginName: "test",
			expectPath: "plugins/test.so", // filepath.Join cleans ./ prefix
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager(tt.pluginDir)
			expectedPath := filepath.Join(pm.pluginDir, tt.pluginName+".so")

			// Verify path construction
			assert.Equal(t, expectedPath, tt.expectPath)
		})
	}
}

// TestPluginManagerMultipleLoadUnload tests loading and unloading multiple plugins
func TestPluginManagerMultipleLoadUnload(t *testing.T) {
	pm := NewManager("/tmp/plugins")

	// Load multiple plugins
	plugins := []string{"plugin1", "plugin2", "plugin3"}
	for _, name := range plugins {
		pm.plugins[name] = &MockPlugin{
			name:    name,
			version: "1.0.0",
		}
	}

	// Verify all loaded
	assert.Len(t, pm.ListPlugins(), 3)

	// Unload one by one
	for _, name := range plugins {
		err := pm.UnloadPlugin(name)
		require.NoError(t, err)
	}

	// Verify all unloaded
	assert.Empty(t, pm.ListPlugins())
}

// TestPluginManagerExecutePluginReturnValues tests different return values from Execute
func TestPluginManagerExecutePluginReturnValues(t *testing.T) {
	for _, tt := range executePluginReturnCases() {
		t.Run(tt.name, func(t *testing.T) {
			pm := NewManager("/tmp/plugins")
			pm.plugins[tt.plugin.name] = tt.plugin

			result, err := pm.ExecutePlugin(tt.plugin.name, tt.args)
			require.NoError(t, err)
			assert.Equal(t, tt.expectedResult, result)
		})
	}
}

type executePluginCase struct {
	name        string
	setupFn     func(*Manager)
	pluginName  string
	args        map[string]interface{}
	expectError bool
	errorMsg    string
}

func executePluginCases() []executePluginCase {
	return []executePluginCase{
		{
			name: "execute existing plugin",
			setupFn: func(pm *Manager) {
				mockPlugin := &MockPlugin{
					name:    "test-plugin",
					version: "1.0.0",
					execFn: func(_ map[string]interface{}) (interface{}, error) {
						return "success", nil
					},
				}
				pm.plugins["test-plugin"] = mockPlugin
			},
			pluginName:  "test-plugin",
			args:        map[string]interface{}{"key": "value"},
			expectError: false,
		},
		{
			name:        "plugin not found",
			setupFn:     func(_ *Manager) {},
			pluginName:  "nonexistent",
			args:        map[string]interface{}{},
			expectError: true,
			errorMsg:    "plugin not found",
		},
		{
			name: "execute with nil args",
			setupFn: func(pm *Manager) {
				mockPlugin := &MockPlugin{
					name:    "test-plugin",
					version: "1.0.0",
				}
				pm.plugins["test-plugin"] = mockPlugin
			},
			pluginName:  "test-plugin",
			args:        nil,
			expectError: false,
		},
		{
			name: "execute with empty args",
			setupFn: func(pm *Manager) {
				mockPlugin := &MockPlugin{
					name:    "test-plugin",
					version: "1.0.0",
				}
				pm.plugins["test-plugin"] = mockPlugin
			},
			pluginName:  "test-plugin",
			args:        map[string]interface{}{},
			expectError: false,
		},
		{
			name:        "empty plugin name",
			setupFn:     func(_ *Manager) {},
			pluginName:  "",
			args:        map[string]interface{}{},
			expectError: true,
			errorMsg:    "plugin not found",
		},
	}
}

type executePluginReturnCase struct {
	name           string
	plugin         *MockPlugin
	args           map[string]interface{}
	expectedResult interface{}
}

func executePluginReturnCases() []executePluginReturnCase {
	return []executePluginReturnCase{
		{
			name: "return string",
			plugin: &MockPlugin{
				name:    "string-plugin",
				version: "1.0.0",
				execFn: func(_ map[string]interface{}) (interface{}, error) {
					return "string result", nil
				},
			},
			args:           map[string]interface{}{},
			expectedResult: "string result",
		},
		{
			name: "return integer",
			plugin: &MockPlugin{
				name:    "int-plugin",
				version: "1.0.0",
				execFn: func(_ map[string]interface{}) (interface{}, error) {
					return 42, nil
				},
			},
			args:           map[string]interface{}{},
			expectedResult: 42,
		},
		{
			name: "return map",
			plugin: &MockPlugin{
				name:    "map-plugin",
				version: "1.0.0",
				execFn: func(_ map[string]interface{}) (interface{}, error) {
					return map[string]interface{}{"key": "value"}, nil
				},
			},
			args:           map[string]interface{}{},
			expectedResult: map[string]interface{}{"key": "value"},
		},
		{
			name: "return nil",
			plugin: &MockPlugin{
				name:    "nil-plugin",
				version: "1.0.0",
				execFn: func(_ map[string]interface{}) (interface{}, error) {
					return nil, nil
				},
			},
			args:           map[string]interface{}{},
			expectedResult: nil,
		},
	}
}

// TestPluginManagerBuildPluginOutputPath tests output path generation for built plugins
func TestPluginManagerBuildPluginOutputPath(t *testing.T) {
	tests := []struct {
		name           string
		pluginDir      string
		outputName     string
		expectedOutput string
	}{
		{
			name:           "simple output path",
			pluginDir:      "/tmp/plugins",
			outputName:     "built-plugin",
			expectedOutput: "/tmp/plugins/built-plugin.so",
		},
		{
			name:           "output with special characters",
			pluginDir:      "/tmp/plugins",
			outputName:     "plugin-v1.0",
			expectedOutput: "/tmp/plugins/plugin-v1.0.so",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			expectedPath := filepath.Join(tt.pluginDir, tt.outputName+".so")
			assert.Equal(t, tt.expectedOutput, expectedPath)
		})
	}
}

// TestPluginManagerEmptyPluginDir tests plugin manager with empty plugin directory
func TestPluginManagerEmptyPluginDir(t *testing.T) {
	pm := NewManager("")

	// Should still work with empty directory
	assert.NotNil(t, pm)
	assert.Empty(t, pm.pluginDir)

	// List should work - may return nil or empty slice
	plugins := pm.ListPlugins()
	assert.Empty(t, plugins)
}

// TestPluginInterfaceNilArgs tests plugin execution with nil arguments
func TestPluginInterfaceNilArgs(t *testing.T) {
	plugin := &MockPlugin{
		name:    "test",
		version: "1.0.0",
		execFn: func(args map[string]interface{}) (interface{}, error) {
			if args == nil {
				return "handled nil", nil
			}
			return "has args", nil
		},
	}

	result, err := plugin.Execute(nil)
	require.NoError(t, err)
	assert.Equal(t, "handled nil", result)
}

// TestPluginManagerGetPluginAfterUnload tests getting plugin after it's unloaded
func TestPluginManagerGetPluginAfterUnload(t *testing.T) {
	pm := NewManager("/tmp/plugins")

	// Load plugin
	pm.plugins["test-plugin"] = &MockPlugin{
		name:    "test-plugin",
		version: "1.0.0",
	}

	// Verify it exists
	plugin, err := pm.GetPlugin("test-plugin")
	require.NoError(t, err)
	assert.NotNil(t, plugin)

	// Unload it
	err = pm.UnloadPlugin("test-plugin")
	require.NoError(t, err)

	// Try to get it again
	plugin, err = pm.GetPlugin("test-plugin")
	require.Error(t, err)
	assert.Nil(t, plugin)
	assert.Contains(t, err.Error(), "plugin not found")
}

// TestPluginManagerListPluginsAfterOperations tests listing after various operations
func TestPluginManagerListPluginsAfterOperations(t *testing.T) {
	pm := NewManager("/tmp/plugins")

	// Initially empty
	assert.Empty(t, pm.ListPlugins())

	// Add plugins
	pm.plugins["plugin1"] = &MockPlugin{name: "plugin1", version: "1.0.0"}
	pm.plugins["plugin2"] = &MockPlugin{name: "plugin2", version: "1.0.0"}
	assert.Len(t, pm.ListPlugins(), 2)

	// Unload one
	require.NoError(t, pm.UnloadPlugin("plugin1"))
	assert.Len(t, pm.ListPlugins(), 1)
	assert.Contains(t, pm.ListPlugins(), "plugin2")
	assert.NotContains(t, pm.ListPlugins(), "plugin1")

	// Add another
	pm.plugins["plugin3"] = &MockPlugin{name: "plugin3", version: "1.0.0"}
	assert.Len(t, pm.ListPlugins(), 2)

	// Unload all
	require.NoError(t, pm.UnloadPlugin("plugin2"))
	require.NoError(t, pm.UnloadPlugin("plugin3"))
	assert.Empty(t, pm.ListPlugins())
}
