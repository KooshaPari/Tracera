// Package main runs a NGS NATS connectivity test.
package main

import (
	"log"
	"time"

	nats "github.com/nats-io/nats.go"
	"github.com/nats-io/nkeys"
)

func main() {
	const (
		connectionHoldDuration = 2 * time.Second
		defaultNATSURL         = "tls://connect.ngs.global:4222"
	)

	log.Println("========== TESTING NGS NATS CONNECTION ==========")

	// New NGS credentials
	url := defaultNATSURL
	userJWT := "eyJ0eXAiOiJKV1QiLCJhbGciOiJlZDI1NTE5LW5rZXkifQ." +
		"eyJqdGkiOiJIRFRES0JLN0FETEIyQ1FFUlk2Qk1ZT0RVSU0yMlRPWlYyNEtEQUlaS000UlRYS1FXQTVRIiwi" +
		"aWF0IjoxNzY2NTc1NzE4LCJpc3MiOiJBQVNUWEhLU1c0N0k0M08yVVNTSldURU9CUEpDVkszNENHSkFaVDZJ" +
		"T0pUVVBXV1pZVEFRSkZNMyIsIm5hbWUiOiJBcHAgVXNlciIsInN1YiI6IlVEM0hEQTVaVTVPNVpOTUhGNkxO" +
		"NUY2R05PRkpOVzVNSVBWN1dISUFUQ1lER042SFZTWFg2T0wyIiwibmF0cyI6eyJwdWIiOnt9LCJzdWIiOnt9" +
		"LCJzdWJzIjotMSwiZGF0YSI6LTEsInBheWxvYWQiOi0xLCJpc3N1ZXJfYWNjb3VudCI6IkFCNkJTNFpES0pD" +
		"UUs0S0JUQVRLN1hMR0VJM1RaU0dXVzdET0pWTVhCRFpPSUZCTlZNT1hMNE5KIiwidHlwZSI6InVzZXIiLCJ2" +
		"ZXJzaW9uIjoyfX0." +
		"iEUKMsTIwLD9HBFGQLtPygzqJk-WVyDfQcZ1dKm5zpSxfcFap11v0THVwocySMucF-aPdQzyselLxOy1YWVXAQ"
	nkeySeed := "SUAHT6FMKRMOCTT4U7OY636264HH3WKRVLEQ475CQSEVWO4ZBEN2EA7DUM"

	log.Printf("Testing connection to: %s\n", url)

	// Parse nkey
	kp, err := nkeys.FromSeed([]byte(nkeySeed))
	if err != nil {
		log.Fatalf("Failed to parse nkey: %v\n", err)
	}

	// Create options
	opts := []nats.Option{
		nats.Name("test-client-ngs"),
		nats.UserJWT(
			func() (string, error) {
				return userJWT, nil
			},
			func(nonce []byte) ([]byte, error) {
				return kp.Sign(nonce)
			},
		),
		nats.ConnectHandler(func(conn *nats.Conn) {
			log.Printf("✅ Connected to %s\n", conn.ConnectedUrl())
		}),
		nats.DisconnectErrHandler(func(_ *nats.Conn, err error) {
			log.Printf("❌ Disconnected: %v\n", err)
		}),
		nats.ClosedHandler(func(_ *nats.Conn) {
			log.Printf("❌ Connection closed\n")
		}),
	}

	// Try to connect with timeout
	log.Println("Attempting connection...")
	nc, err := nats.Connect(url, opts...)
	if err != nil {
		log.Printf("❌ Failed to connect: %v\n", err)
		return
	}
	defer func() {
		nc.Close()
	}()

	log.Printf("✅ Successfully connected!\n")
	log.Printf("Connected URL: %s\n", nc.ConnectedUrl())
	log.Printf("Connected servers: %v\n", nc.Servers())

	time.Sleep(connectionHoldDuration)
}
