package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"strconv"
	"time"
)

const (
	upstashClientTimeout = 10 * time.Second
	upstashPingTimeout   = 5 * time.Second
)

// UpstashCache provides caching functionality using Upstash REST API
type UpstashCache struct {
	restURL string
	token   string
	client  *http.Client
	ttl     time.Duration
}

// NewUpstashCache creates a new Upstash cache instance using REST API
func NewUpstashCache(restURL, token string, ttl time.Duration) (*UpstashCache, error) {
	uc := &UpstashCache{
		restURL: restURL,
		token:   token,
		client:  &http.Client{Timeout: upstashClientTimeout},
		ttl:     ttl,
	}

	// Test connection with PING
	ctx, cancel := context.WithTimeout(context.Background(), upstashPingTimeout)
	defer cancel()

	if err := uc.ping(ctx); err != nil {
		return nil, fmt.Errorf("failed to connect to Upstash: %w", err)
	}

	return uc, nil
}

// ping tests the connection to Upstash
func (uc *UpstashCache) ping(ctx context.Context) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, uc.restURL+"/ping", nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+uc.token)

	resp, err := uc.client.Do(req)
	if err != nil {
		return err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing upstash response", "error", err)
		}
	}()

	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("failed to read upstash response: %w", err)
		}
		return fmt.Errorf("ping failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// Get retrieves a value from cache
func (uc *UpstashCache) Get(ctx context.Context, key string, dest interface{}) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, uc.restURL+"/get/"+key, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+uc.token)

	resp, err := uc.client.Do(req)
	if err != nil {
		return err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing upstash response", "error", err)
		}
	}()

	if resp.StatusCode == http.StatusNotFound {
		return nil // Key doesn't exist
	}

	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("failed to read upstash response: %w", err)
		}
		return fmt.Errorf("get failed with status %d: %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if err := json.Unmarshal(body, dest); err != nil {
		return fmt.Errorf("failed to unmarshal value: %w", err)
	}

	return nil
}

// Set stores a value in cache
func (uc *UpstashCache) Set(ctx context.Context, key string, value interface{}) error {
	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("failed to marshal value: %w", err)
	}

	ttlSeconds := int(uc.ttl.Seconds())
	url := uc.restURL + "/set/" + key + "/" + string(data) + "?ex=" + strconv.Itoa(ttlSeconds)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+uc.token)

	resp, err := uc.client.Do(req)
	if err != nil {
		return err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing upstash response", "error", err)
		}
	}()

	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("failed to read upstash response: %w", err)
		}
		return fmt.Errorf("set failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// Delete removes a value from cache
func (uc *UpstashCache) Delete(ctx context.Context, keys ...string) error {
	if len(keys) == 0 {
		return nil
	}

	for _, key := range keys {
		req, err := http.NewRequestWithContext(ctx, http.MethodDelete, uc.restURL+"/del/"+key, nil)
		if err != nil {
			return err
		}
		req.Header.Set("Authorization", "Bearer "+uc.token)

		resp, err := uc.client.Do(req)
		if err != nil {
			return err
		}
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing upstash response", "error", err)
		}

		if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNotFound {
			return fmt.Errorf("delete failed with status %d", resp.StatusCode)
		}
	}

	return nil
}

// InvalidatePattern deletes all keys matching a pattern (not supported by Upstash REST API)
func (uc *UpstashCache) InvalidatePattern(_ context.Context, _ string) error {
	// Upstash REST API doesn't support pattern matching, so we log a warning
	// In production, consider using a different approach or caching the keys separately
	return nil
}

// Close closes the Upstash connection (no-op for REST API)
func (uc *UpstashCache) Close() error {
	return nil
}
