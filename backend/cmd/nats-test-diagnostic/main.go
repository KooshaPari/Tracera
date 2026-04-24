// Package main provides diagnostic tooling for NATS connectivity.
package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"log"
	"net"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	nats "github.com/nats-io/nats.go"
	"github.com/nats-io/nkeys"
)

// JWTClaims represents the JWT claims structure for NATS
type JWTClaims struct {
	JTI           string `json:"jti"`
	Iat           int64  `json:"iat"`
	Exp           int64  `json:"exp"`
	Iss           string `json:"iss"`
	Name          string `json:"name"`
	Sub           string `json:"sub"`
	IssuerAccount string `json:"issuer_account"`
	Type          string `json:"type"`
	Version       int    `json:"version"`
}

const (
	defaultNATSHost       = "connect.nats.us"
	defaultNATSPort       = 4222
	defaultNATSURL        = "tls://connect.nats.us:4222"
	altNATS443Endpoint    = "connect.nats.us:443"
	altNATSUS4222Endpoint = "connect.nats.us:4222"
	altNATSIO4222Endpoint = "connect.nats.io:4222"
	defaultUserJWT        = "eyJ0eXAiOiJKV1QiLCJhbGciOiJlZDI1NTE5LW5rZXkifQ.eyJqdGkiOiJNNkJZU1FTSUFC" +
		"QlY2N0lBRTZRNEJDRERCQVBNRE1MVDdMSkg0QzIzVlVWNU4zUTczUUhRIiwiaWF0IjoxNzY0" +
		"Mzg0MjMwLCJpc3MiOiJBQjRBQUxYTkY2VlZHRDJVVk1GRzNDU0lQUktWNUNUN043NUI0WVpS" +
		"Vk1PWktTRVFGNFdXU1QzRiIsIm5hbWUiOiJDTEkiLCJzdWIiOiJVREVISE5ZVlNMNUNJU1lM" +
		"UVVJWE1ZUlhPQU5WUDJJMjYzWVcySk1LQ1RFQVFXM0JBV1JHWU8zTCIsIm5hdHMiOnsicHVi" +
		"Ijp7fSwic3ViIjp7fSwic3VicyI6LTEsImRhdGEiOi0xLCJwYXlsb2FkIjotMSwiaXNzdWVy" +
		"X2FjY291bnQiOiJBRDc1NlZKWDRQSzVZNlZYUUdXM0hUVlVMWE81VjZBVzNXNllCQU1WNEtU" +
		"TDJZNURXNU5WWE01NWiIsInR5cGUiOiJ1c2VyIiwidmVyc2lvbiI6Mn19.OJMi3_CYXpNK" +
		"sg9xZeo3Xn-wIkR60gwvD7eO05muespTJtyhtqy2k6A1iF64PsrXI3hMh-Bg3Trs9X47R2sMBg"
	jwtPartsCount           = 3
	jwtPaddingBase          = 4
	secondsPerDay           = 86400
	dnsLookupTimeout        = 5 * time.Second
	tcpConnectivityTimeout  = 5 * time.Second
	altEndpointTimeout      = 2 * time.Second
	connectionTimeoutShort  = 5 * time.Second
	connectionTimeoutMedium = 10 * time.Second
	connectionTimeoutLong   = 30 * time.Second
)

func main() {
	url := defaultNATSURL
	userJWT := os.Getenv("NATS_USER_JWT")
	if userJWT == "" {
		userJWT = defaultUserJWT
	}
	nkeySeed := os.Getenv("NATS_USER_NKEY_SEED")
	if nkeySeed == "" {
		nkeySeed = "SUAJFTH46RAIJDZKJSSY64OEKV26YKPVQ4TGDNFMI7WVDOTVBV4ZVRC64Q"
	}

	log.Println("========== NATS DIAGNOSTIC REPORT ==========")

	// 1. Decode and check JWT
	log.Println("1️⃣  JWT Validation:")
	checkJWT(userJWT)

	// 2. Check nkey seed
	log.Println("\n2️⃣  NKey Seed Validation:")
	checkNkeySeed(nkeySeed)

	// 3. DNS resolution
	log.Println("\n3️⃣  DNS Resolution:")
	checkDNS(url)

	// 4. TCP connectivity tests
	log.Println("\n4️⃣  TCP Connectivity Tests:")
	testTCPConnectivity(defaultNATSHost, defaultNATSPort)

	// 5. Try connection with different timeouts
	log.Println("\n5️⃣  NATS Connection Attempts (with timeouts):")
	testConnectionWithTimeouts(url, userJWT, nkeySeed)

	// 6. Check for alternative endpoints
	log.Println("\n6️⃣  Synadia Alternative Endpoints:")
	checkAlternativeEndpoints()
}

func checkJWT(jwtToken string) {
	parts := strings.Split(jwtToken, ".")
	if len(parts) != jwtPartsCount {
		log.Println("❌ Invalid JWT format (not 3 parts)")
		return
	}

	// Decode payload
	payload := parts[1]
	// Add padding if needed
	padding := jwtPaddingBase - (len(payload) % jwtPaddingBase)
	if padding != jwtPaddingBase {
		payload += strings.Repeat("=", padding)
	}

	decoded, err := base64.StdEncoding.DecodeString(payload)
	if err != nil {
		log.Printf("❌ Failed to decode JWT payload: %v\n", err)
		return
	}

	var claims JWTClaims
	err = json.Unmarshal(decoded, &claims)
	if err != nil {
		log.Printf("❌ Failed to parse JWT claims: %v\n", err)
		return
	}

	log.Printf("✅ JWT is valid")
	log.Printf("   - Issued at: %s (timestamp: %d)\n", time.Unix(claims.Iat, 0), claims.Iat)
	if claims.Exp > 0 {
		log.Printf("   - Expires at: %s (timestamp: %d)\n", time.Unix(claims.Exp, 0), claims.Exp)
		if time.Now().Unix() > claims.Exp {
			log.Printf("   ⚠️  JWT HAS EXPIRED!\n")
		} else {
			secondsUntilExpiry := claims.Exp - time.Now().Unix()
			daysUntilExpiry := float64(secondsUntilExpiry) / secondsPerDay
			log.Printf("   - Expires in: %d seconds (%.1f days)\n", secondsUntilExpiry, daysUntilExpiry)
		}
	} else {
		log.Printf("   - No expiration set\n")
	}
	log.Printf("   - User: %s\n", claims.Name)
	log.Printf("   - Sub (User ID): %s\n", claims.Sub)
	log.Printf("   - Issuer Account: %s\n", claims.IssuerAccount)
}

func checkNkeySeed(seed string) {
	kp, err := nkeys.FromSeed([]byte(seed))
	if err != nil {
		log.Printf("❌ Failed to parse nkey seed: %v\n", err)
		return
	}

	pubKey, err := kp.PublicKey()
	if err != nil {
		log.Printf("❌ Failed to get public key: %v\n", err)
		return
	}

	log.Printf("✅ NKey seed is valid")
	log.Printf("   - Public Key: %s\n", pubKey)
	log.Printf("   - Type: %s\n", string(seed[0]))
}

func checkDNS(natsURL string) {
	// Parse URL to get hostname
	parsedURL, err := url.Parse(natsURL)
	if err != nil {
		log.Printf("❌ Failed to parse URL: %v\n", err)
		return
	}

	host := strings.Split(parsedURL.Host, ":")[0]
	log.Printf("Resolving hostname: %s\n", host)

	// Try multiple DNS lookups
	ctx, cancel := context.WithTimeout(context.Background(), dnsLookupTimeout)
	defer cancel()

	resolver := net.Resolver{}
	ips, err := resolver.LookupIPAddr(ctx, host)
	if err != nil {
		log.Printf("❌ DNS lookup failed: %v\n", err)
		return
	}

	log.Printf("✅ DNS resolved successfully")
	for _, ip := range ips {
		log.Printf("   - %s\n", ip.IP.String())
	}
}

func testTCPConnectivity(host string, port int) {
	address := net.JoinHostPort(host, strconv.Itoa(port))

	// Test with short timeout
	log.Printf("Testing TCP connection to %s (5 second timeout)...\n", address)
	ctx, cancel := context.WithTimeout(context.Background(), tcpConnectivityTimeout)
	defer cancel()

	dialer := net.Dialer{Timeout: tcpConnectivityTimeout}
	conn, err := dialer.DialContext(ctx, "tcp", address)
	if err != nil {
		log.Printf("❌ TCP connection failed: %v\n", err)
		log.Printf("   This suggests the port is either:\n")
		log.Printf("   - Blocked by a firewall\n")
		log.Printf("   - Not listening on the server\n")
		log.Printf("   - Server is unreachable\n")
		return
	}
	defer func() {
		if err := conn.Close(); err != nil {
			log.Printf("❌ Failed to close connection: %v\n", err)
		}
	}()

	log.Printf("✅ TCP connection successful\n")
	log.Printf("   Connected to: %s\n", conn.RemoteAddr().String())
}

func testConnectionWithTimeouts(natsURL string, userJWT, nkeySeed string) {
	timeouts := []time.Duration{
		connectionTimeoutShort,
		connectionTimeoutMedium,
		connectionTimeoutLong,
	}

	for _, timeout := range timeouts {
		log.Printf("\nAttempting NATS connection (timeout: %v)...\n", timeout)

		keyPair, err := nkeys.FromSeed([]byte(nkeySeed))
		if err != nil {
			log.Printf("❌ Failed to parse nkey seed: %v\n", err)
			continue
		}

		opts := []nats.Option{
			nats.Name("test-client-diagnostic"),
			nats.Timeout(timeout),
			nats.ConnectHandler(func(conn *nats.Conn) {
				log.Printf("✅ Connected to %s\n", conn.ConnectedUrl())
			}),
			nats.DisconnectErrHandler(func(_ *nats.Conn, err error) {
				log.Printf("❌ Disconnected: %v\n", err)
			}),
			nats.UserJWT(
				func() (string, error) {
					return userJWT, nil
				},
				func(nonce []byte) ([]byte, error) {
					return keyPair.Sign(nonce)
				},
			),
		}

		nc, err := nats.Connect(natsURL, opts...)

		if err != nil {
			log.Printf("❌ Connection failed: %v\n", err)
		} else {
			log.Printf("✅ Connection succeeded!\n")
			nc.Close()
			return
		}
	}
}

func checkAlternativeEndpoints() {
	endpoints := []string{
		altNATSUS4222Endpoint,
		altNATS443Endpoint,
		altNATSIO4222Endpoint,
	}

	for _, ep := range endpoints {
		log.Printf("Checking %s...\n", ep)
		ctx, cancel := context.WithTimeout(context.Background(), altEndpointTimeout)
		dialer := net.Dialer{Timeout: altEndpointTimeout}
		conn, err := dialer.DialContext(ctx, "tcp", ep)
		cancel()
		if err != nil {
			log.Printf("  ❌ Failed: %v\n", err)
		} else {
			log.Printf("  ✅ Reachable\n")
			if err := conn.Close(); err != nil {
				log.Printf("  ❌ Failed to close connection: %v\n", err)
			}
		}
	}
}
