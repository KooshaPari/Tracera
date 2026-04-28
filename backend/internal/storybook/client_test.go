package storybook

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

const storybookClientTimeout = 5 * time.Second

func TestNewClient(t *testing.T) {
	tests := []struct {
		name    string
		config  *Config
		wantErr bool
		errMsg  string
	}{
		{
			name: "valid config",
			config: &Config{
				BaseURL:        "http://localhost:6006",
				TimeoutSeconds: 30,
				MaxRetries:     3,
			},
			wantErr: false,
		},
		{
			name:    "missing base URL",
			config:  &Config{},
			wantErr: true,
			errMsg:  "storybook base URL is required",
		},
		{
			name: "default timeout",
			config: &Config{
				BaseURL: "http://localhost:6006",
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client, err := NewClient(tt.config)
			if (err != nil) != tt.wantErr {
				t.Fatalf("NewClient() error = %v, wantErr %v", err, tt.wantErr)
			}
			if tt.wantErr && err.Error() != tt.errMsg {
				t.Fatalf("NewClient() error = %v, want %v", err.Error(), tt.errMsg)
			}
			if !tt.wantErr && client == nil {
				t.Fatal("NewClient() returned nil client")
			}
		})
	}
}

func TestFetchStoriesJSON(t *testing.T) {
	// Create a mock Storybook server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/stories.json" {
			w.Header().Set("Content-Type", "application/json")
			response := StoriesResponse{
				V: 5,
				Stories: map[string]StoryEntry{
					"components-button--primary": {
						ID:    "components-button--primary",
						Title: "Components/Button/Primary",
						Name:  "Primary",
					},
				},
				Metadata: Metadata{
					Version: "7.0.0",
				},
			}
			if err := json.NewEncoder(w).Encode(response); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
		} else {
			http.Error(w, "Not found", http.StatusNotFound)
		}
	}))
	defer server.Close()

	config := &Config{
		BaseURL: server.URL,
	}

	client, err := NewClient(config)
	if err != nil {
		t.Fatalf("NewClient() failed: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), storybookClientTimeout)
	defer cancel()

	stories, err := client.FetchStoriesJSON(ctx)
	if err != nil {
		t.Fatalf("FetchStoriesJSON() failed: %v", err)
	}

	if stories == nil {
		t.Fatal("FetchStoriesJSON() returned nil")
	}

	if stories.V != 5 {
		t.Errorf("Expected version 5, got %d", stories.V)
	}

	if len(stories.Stories) != 1 {
		t.Errorf("Expected 1 story, got %d", len(stories.Stories))
	}

	if stories.Metadata.Version != "7.0.0" {
		t.Errorf("Expected version 7.0.0, got %s", stories.Metadata.Version)
	}
}

func TestExtractComponentName(t *testing.T) {
	client, err := NewClient(&Config{BaseURL: "http://localhost:6006"})
	require.NoError(t, err)

	tests := []struct {
		title    string
		expected string
	}{
		{"Components/Button", "Button"},
		{"Components/Button/Default", "Default"},
		{"Button", "Button"},
		{"", ""},
		{"Components/Form/Input/Text", "Text"},
	}

	for _, tt := range tests {
		t.Run(tt.title, func(t *testing.T) {
			result := client.ExtractComponentName(tt.title)
			if result != tt.expected {
				t.Errorf("ExtractComponentName(%s) = %s, want %s", tt.title, result, tt.expected)
			}
		})
	}
}

func TestExtractCategory(t *testing.T) {
	client, err := NewClient(&Config{BaseURL: "http://localhost:6006"})
	require.NoError(t, err)

	tests := []struct {
		title    string
		expected string
	}{
		{"Components/Button", "Components"},
		{"Components/Button/Default", "Components/Button"},
		{"Button", "Button"},
		{"", ""},
		{"Components/Form/Input/Text", "Components/Form/Input"},
	}

	for _, tt := range tests {
		t.Run(tt.title, func(t *testing.T) {
			result := client.ExtractCategory(tt.title)
			if result != tt.expected {
				t.Errorf("ExtractCategory(%s) = %s, want %s", tt.title, result, tt.expected)
			}
		})
	}
}

func TestExtractPropsFromArgTypes(t *testing.T) {
	client, err := NewClient(&Config{BaseURL: "http://localhost:6006"})
	require.NoError(t, err)

	argTypes := map[string]ArgType{
		"label": {
			Name:        "label",
			Description: "Button label",
			Required:    true,
			Type: &TypeInfo{
				Name: "string",
			},
		},
		"variant": {
			Name:        "variant",
			Description: "Button variant",
			Required:    false,
			Type: &TypeInfo{
				Name: "string",
			},
			Options: []string{"primary", "secondary"},
		},
	}

	props := client.ExtractPropsFromArgTypes(argTypes)

	if len(props) != 2 {
		t.Errorf("Expected 2 props, got %d", len(props))
	}

	// Check label prop
	found := false
	for _, prop := range props {
		if prop.Name == "label" {
			found = true
			if prop.Type != "string" {
				t.Errorf("Expected label type 'string', got %s", prop.Type)
			}
			if !prop.Required {
				t.Error("Expected label to be required")
			}
		}
	}
	if !found {
		t.Error("Label prop not found")
	}
}

func TestHealthCheck(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/stories.json" {
			w.Header().Set("Content-Type", "application/json")
			response := StoriesResponse{
				V:       5,
				Stories: map[string]StoryEntry{},
			}
			if err := json.NewEncoder(w).Encode(response); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
		}
	}))
	defer server.Close()

	config := &Config{
		BaseURL: server.URL,
	}

	client, err := NewClient(config)
	require.NoError(t, err)

	ctx, cancel := context.WithTimeout(context.Background(), storybookClientTimeout)
	defer cancel()

	err = client.HealthCheck(ctx)
	if err != nil {
		t.Fatalf("HealthCheck() failed: %v", err)
	}
}

func TestHealthCheckFailure(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		http.Error(w, "Unavailable", http.StatusServiceUnavailable)
	}))
	defer server.Close()

	config := &Config{
		BaseURL: server.URL,
	}

	client, err := NewClient(config)
	require.NoError(t, err)

	ctx, cancel := context.WithTimeout(context.Background(), storybookClientTimeout)
	defer cancel()

	err = client.HealthCheck(ctx)
	if err == nil {
		t.Fatal("HealthCheck() should have failed")
	}
}
