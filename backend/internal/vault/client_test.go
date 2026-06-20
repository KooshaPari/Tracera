//go:build !integration

package vault

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGetStringField(t *testing.T) {
	tests := []struct {
		name  string
		data  map[string]interface{}
		field string
		want  string
	}{
		{
			name:  "existing string field",
			data:  map[string]interface{}{"host": "localhost", "port": "5432"},
			field: "host",
			want:  "localhost",
		},
		{
			name:  "missing field",
			data:  map[string]interface{}{"host": "localhost"},
			field: "port",
			want:  "",
		},
		{
			name:  "non-string field",
			data:  map[string]interface{}{"port": 5432},
			field: "port",
			want:  "",
		},
		{
			name:  "empty data",
			data:  map[string]interface{}{},
			field: "anything",
			want:  "",
		},
		{
			name:  "nil value",
			data:  map[string]interface{}{"key": nil},
			field: "key",
			want:  "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := getStringField(tt.data, tt.field)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDatabaseCredentials_Struct(t *testing.T) {
	creds := DatabaseCredentials{
		URL:      "postgres://localhost:5432/db",
		Host:     "localhost",
		Port:     "5432",
		User:     "admin",
		Password: "secret",
		Name:     "tracertm",
	}

	assert.Equal(t, "localhost", creds.Host)
	assert.Equal(t, "5432", creds.Port)
	assert.Equal(t, "admin", creds.User)
	assert.Equal(t, "secret", creds.Password)
	assert.Equal(t, "tracertm", creds.Name)
}

func TestNeo4jCredentials_Struct(t *testing.T) {
	creds := Neo4jCredentials{
		URI:      "bolt://localhost:7687",
		User:     "neo4j",
		Password: "password",
		Auth:     "basic",
	}

	assert.Equal(t, "bolt://localhost:7687", creds.URI)
	assert.Equal(t, "neo4j", creds.User)
}

func TestS3Credentials_Struct(t *testing.T) {
	creds := S3Credentials{
		Endpoint:        "http://localhost:9000",
		AccessKeyID:     "minio",
		SecretAccessKey: "minio123",
		Bucket:          "tracertm",
		Region:          "us-east-1",
	}

	assert.Equal(t, "http://localhost:9000", creds.Endpoint)
	assert.Equal(t, "tracertm", creds.Bucket)
}

func TestWorkOSCredentials_Struct(t *testing.T) {
	creds := WorkOSCredentials{
		APIKey:      "sk_test_xxx",
		ClientID:    "client_xxx",
		RedirectURI: "http://localhost:3000/callback",
	}

	assert.Equal(t, "sk_test_xxx", creds.APIKey)
	assert.Equal(t, "client_xxx", creds.ClientID)
	assert.Equal(t, "http://localhost:3000/callback", creds.RedirectURI)
}

func TestWorkOSCredentials_Empty(t *testing.T) {
	creds := WorkOSCredentials{}
	assert.Empty(t, creds.APIKey)
	assert.Empty(t, creds.ClientID)
	assert.Empty(t, creds.RedirectURI)
}

func TestNewClient_MissingToken(t *testing.T) {
	// Ensure VAULT_TOKEN is not set
	t.Setenv("VAULT_TOKEN", "")
	t.Setenv("VAULT_ADDR", "http://127.0.0.1:8200")

	client, err := NewClient()
	require.Error(t, err)
	assert.Nil(t, client)
	assert.Contains(t, err.Error(), "VAULT_TOKEN")
}

func TestNewClient_WithToken(t *testing.T) {
	t.Setenv("VAULT_TOKEN", "test-token")
	t.Setenv("VAULT_ADDR", "http://127.0.0.1:8200")

	client, err := NewClient()
	require.NoError(t, err)
	assert.NotNil(t, client)
	assert.Equal(t, "secret/data/tracertm", client.prefix)
}

func TestNewClient_DefaultAddr(t *testing.T) {
	t.Setenv("VAULT_TOKEN", "test-token")
	t.Setenv("VAULT_ADDR", "")

	client, err := NewClient()
	require.NoError(t, err)
	assert.NotNil(t, client)
}
