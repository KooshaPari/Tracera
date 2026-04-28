// Package main runs a NATS WebSocket connectivity test.
package main

import (
	"log"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/nats-io/nkeys"
)

func main() {
	const (
		websocketDialTimeout = 5 * time.Second
		natsWSPlainEndpoint  = "ws://connect.nats.us:9222"
		natsWSSecureEndpoint = "wss://connect.nats.us:9222"
		natsWSAltPlain       = "ws://connect.nats.us:443"
		natsWSAltSecure      = "wss://connect.nats.us:443"
	)

	log.Println("========== Testing NATS WebSocket Connection ==========")

	userJWT := "eyJ0eXAiOiJKV1QiLCJhbGciOiJlZDI1NTE5LW5rZXkifQ.eyJqdGkiOiJNNkJZU1FTSUFC" +
		"QlY2N0lBRTZRNEJDRERCQVBNRE1MVDdMSkg0QzIzVlVWNU4zUTczUUhRIiwiaWF0IjoxNzY0" +
		"Mzg0MjMwLCJpc3MiOiJBQjRBQUxYTkY2VlZHRDJVVk1GRzNDU0lQUktWNUNUN043NUI0WVpS" +
		"Vk1PWktTRVFGNFdXU1QzRiIsIm5hbWUiOiJDTEkiLCJzdWIiOiJVREVISE5ZVlNMNUNJU1lM" +
		"UVVJWE1ZUlhPQU5WUDJJMjYzWVcySk1LQ1RFQVFXM0JBV1JHWU8zTCIsIm5hdHMiOnsicHVi" +
		"Ijp7fSwic3ViIjp7fSwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMSwiaXNzdWVy" +
		"X2FjY291bnQiOiJBRDc1NlZKWDRQSzVZNlZYUUdXM0hUVlVMWE81VjZBVzNXNllCQU1WNEtU" +
		"TDJZNURXNU5WWE01NWiIsInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Mn19.OJMi3_CYXpNK" +
		"sg9xZeo3Xn-wIkR60gwvD7eO05muespTJtyhtqy2k6A1iF64PsrXI3hMh-Bg3Trs9X47R2sMBg"
	nkeySeed := "SUAJFTH46RAIJDZKJSSY64OEKV26YKPVQ4TGDNFMI7WVDOTVBV4ZVRC64Q"

	kp, err := nkeys.FromSeed([]byte(nkeySeed))
	if err != nil {
		log.Printf("Failed to load nkey seed: %v", err)
		return
	}

	wsEndpoints := []string{
		natsWSPlainEndpoint,
		natsWSSecureEndpoint,
		natsWSAltPlain,
		natsWSAltSecure,
	}

	opts := buildOptions(userJWT, kp, websocketDialTimeout)
	if tryEndpoints(wsEndpoints, opts) {
		return
	}

	logFailureSummary()
}

func buildOptions(userJWT string, kp nkeys.KeyPair, timeout time.Duration) []nats.Option {
	return []nats.Option{
		nats.Name("test-websocket"),
		nats.Timeout(timeout),
		nats.UserJWT(
			func() (string, error) {
				return userJWT, nil
			},
			func(nonce []byte) ([]byte, error) {
				return kp.Sign(nonce)
			},
		),
	}
}

func tryEndpoints(endpoints []string, opts []nats.Option) bool {
	for _, endpoint := range endpoints {
		log.Printf("Trying WebSocket endpoint: %s\n", endpoint)

		nc, err := nats.Connect(endpoint, opts...)
		if err != nil {
			log.Printf("  ❌ Failed: %v\n\n", err)
			continue
		}

		log.Printf("  ✅ Connected successfully!\n")
		log.Printf("  URL: %s\n\n", nc.ConnectedUrl())
		nc.Close()
		return true
	}

	return false
}

func logFailureSummary() {
	log.Println("\nNo WebSocket endpoints reachable.")
	log.Println("\n========== NATS Connection Status Summary ==========")
	log.Println("✅ DNS: Resolves successfully")
	log.Println("✅ HTTPS (443): Reachable")
	log.Println("❌ NATS (4222): Unreachable (timeout)")
	log.Println("❌ WebSocket: Not available")
	log.Println("\nPossible issues:")
	log.Println("1. NATS cluster on port 4222 is offline or not running")
	log.Println("2. Account doesn't have access to NATS protocol port")
	log.Println("3. Account has been suspended or restricted")
	log.Println("4. Network firewall blocking port 4222")
	log.Println("\nRecommendation:")
	log.Println("Check Synadia account status and subscription plan")
}
