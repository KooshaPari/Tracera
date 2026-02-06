// Package main runs a basic NATS connectivity test.
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
		defaultNATSURL         = "tls://connect.nats.us:4222"
	)

	url := defaultNATSURL
	userJWT := "eyJ0eXAiOiJKV1QiLCJhbGciOiJlZDI1NTE5LW5rZXkifQ.eyJqdGkiOiJNNkJZU1FTSUFC" +
		"QlY2N0lBRTZRNEJDRERCQVBNRE1MVDdMSkg0QzIzVlVWNU4zUTczUUhRIiwiaWF0IjoxNzY0" +
		"Mzg0MjMwLCJpc3MiOiJBQjRBQUxYTkY2VlZHRDJVVk1GRzNDU0lQUktWNUNUN043NUI0WVpS" +
		"Vk1PWktTRVFGNFdXU1QzRiIsIm5hbWUiOiJDTEkiLCJzdWIiOiJVREVISE5ZVlNMNUNJU1lM" +
		"UVVJWE1ZUlhPQU5WUDJJMjYzWVcySk1LQ1RFQVFXM0JBV1JHWU8zTCIsIm5hdHMiOnsicHVi" +
		"Ijp7fSwic3ViIjp7fSwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMSwiaXNzdWVy" +
		"X2FjY291bnQiOiJBRDc1NlZKWDRQSzVZNlZYUUdXM0hUVlVMWE81VjZBVzNXNllCQU1WNEtU" +
		"TDJZNURXNU5WWE1NWiIsInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Mn19.OJMi3_CYXpNK" +
		"sg9xZeo3Xn-wIkR60gwvD7eO05muespTJtyhtqy2k6A1iF64PsrXI3hMh-Bg3Trs9X47R2sMBg"
	nkeySeed := "SUAJFTH46RAIJDZKJSSY64OEKV26YKPVQ4TGDNFMI7WVDOTVBV4ZVRC64Q"

	log.Printf("Testing NATS connection to: %s\n", url)

	// Parse nkey
	keyPair, err := nkeys.FromSeed([]byte(nkeySeed))
	if err != nil {
		log.Fatalf("Failed to parse nkey: %v\n", err)
	}

	// Create options
	opts := []nats.Option{
		nats.Name("test-client"),
		nats.UserJWT(
			func() (string, error) {
				return userJWT, nil
			},
			func(nonce []byte) ([]byte, error) {
				return keyPair.Sign(nonce)
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
	connection, err := nats.Connect(url, opts...)
	if err != nil {
		log.Printf("❌ Failed to connect: %v\n", err)
		return
	}
	defer func() {
		connection.Close()
	}()

	log.Printf("✅ Successfully connected!\n")
	log.Printf("Connected URL: %s\n", connection.ConnectedUrl())

	time.Sleep(connectionHoldDuration)
}
