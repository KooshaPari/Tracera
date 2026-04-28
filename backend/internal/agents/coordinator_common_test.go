//go:build !integration && !e2e

package agents

import (
	"time"
)

const agentHeartbeatDelay = 10 * time.Millisecond
