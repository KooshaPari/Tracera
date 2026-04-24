// Package main runs Synadia API connectivity tests.
package main

import (
	"context"
	"flag"
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	pat := flag.String("token", "", "Synadia PAT token")
	flag.Parse()

	if *pat == "" {
		*pat = os.Getenv("SYNADIA_PAT")
	}

	if *pat == "" {
		log.Fatal("PAT token required (set SYNADIA_PAT env var or use -token flag)")
	}

	log.Println("========== SYNADIA API DIAGNOSTICS ==========")

	// Try multiple Synadia API endpoints
	endpoints := []string{
		"https://api.synadia.com/api/v1/account",
		"https://api.nats.cloud/api/v1/account",
		"https://cloud.nats.io/api/v1/account",
	}

	for _, endpoint := range endpoints {
		log.Printf("Trying endpoint: %s\n", endpoint)
		checkSyndiaAPI(endpoint, *pat)
		log.Println()
	}

	// Also try to get account info
	log.Println("\nTrying account endpoints:")
	accountEndpoints := []string{
		"https://api.synadia.com/api/v1/account/info",
		"https://api.nats.cloud/api/v1/account/info",
		"https://cloud.nats.io/api/v1/accounts",
	}

	for _, endpoint := range accountEndpoints {
		log.Printf("Trying: %s\n", endpoint)
		checkSyndiaAPI(endpoint, *pat)
		log.Println()
	}
}

func checkSyndiaAPI(endpoint string, pat string) {
	client := &http.Client{}
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, endpoint, nil)
	if err != nil {
		log.Printf("  ❌ Failed to create request: %v\n", err)
		return
	}

	req.Header.Set("Authorization", "Bearer "+pat)
	req.Header.Set("User-Agent", "NATS-Diagnostic/1.0")

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("  ❌ Request failed: %v\n", err)
		return
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			log.Printf("error closing response body: %v", err)
		}
	}()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("  ❌ Failed to read response body: %v\n", err)
		return
	}

	switch resp.StatusCode {
	case http.StatusOK:
		log.Printf("  ✅ Status: %d\n", resp.StatusCode)
		log.Printf("  Response: %s\n", string(body))
	case http.StatusUnauthorized:
		log.Printf("  ❌ Status: %d (Unauthorized - check PAT token)\n", resp.StatusCode)
	case http.StatusNotFound:
		log.Printf("  ❌ Status: %d (Not Found - endpoint doesn't exist)\n", resp.StatusCode)
	default:
		log.Printf("  ⚠️  Status: %d\n", resp.StatusCode)
		log.Printf("  Response: %s\n", string(body))
	}
}
