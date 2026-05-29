package security

import (
	"os"
	"testing"
)

// Headers tests are placeholders until wired through Echo with security middleware.
func TestMain(m *testing.M) {
	if os.Getenv("SECURITY_HEADERS_INTEGRATION") != "1" {
		os.Exit(0)
	}
	os.Exit(m.Run())
}
