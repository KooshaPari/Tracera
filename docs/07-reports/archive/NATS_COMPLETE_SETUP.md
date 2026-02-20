# NATS Complete Setup Guide

## Local Development (Docker)

```bash
# Start NATS with persistence
docker run -d \
  --name nats \
  -p 4222:4222 \
  -p 8222:8222 \
  -v nats_data:/data \
  nats:latest \
  -js -sd /data

# Test connection
nats-cli server info
```

## Production Setup (Synadia Cloud)

### 1. Create Synadia Account
- Go to https://app.synadia.com
- Sign up with GitHub/Google
- Create new NATS account

### 2. Get Connection String
```
Connection String: nats://user:password@host:port
```

### 3. Environment Variable
```bash
export NATS_URL="nats://user:password@host:port"
```

## Go Integration

### 1. Install Package
```bash
go get github.com/nats-io/nats.go
```

### 2. Create NATS Publisher

```go
// backend/internal/nats/publisher.go
package nats

import (
    "encoding/json"
    "github.com/nats-io/nats.go"
)

type EventPublisher struct {
    conn *nats.Conn
}

func NewEventPublisher(url string) (*EventPublisher, error) {
    conn, err := nats.Connect(url)
    if err != nil {
        return nil, err
    }
    return &EventPublisher{conn: conn}, nil
}

func (p *EventPublisher) PublishItemEvent(event interface{}) error {
    data, _ := json.Marshal(event)
    return p.conn.Publish("items.events", data)
}

func (p *EventPublisher) PublishLinkEvent(event interface{}) error {
    data, _ := json.Marshal(event)
    return p.conn.Publish("links.events", data)
}

func (p *EventPublisher) PublishAgentEvent(event interface{}) error {
    data, _ := json.Marshal(event)
    return p.conn.Publish("agents.events", data)
}

func (p *EventPublisher) Close() {
    p.conn.Close()
}
```

### 3. Create NATS Subscriber

```go
// backend/internal/nats/subscriber.go
package nats

import (
    "encoding/json"
    "github.com/nats-io/nats.go"
)

type EventSubscriber struct {
    conn *nats.Conn
}

func NewEventSubscriber(url string) (*EventSubscriber, error) {
    conn, err := nats.Connect(url)
    if err != nil {
        return nil, err
    }
    return &EventSubscriber{conn: conn}, nil
}

func (s *EventSubscriber) SubscribeToItems(handler func(interface{}) error) error {
    _, err := s.conn.Subscribe("items.events", func(msg *nats.Msg) {
        var event interface{}
        json.Unmarshal(msg.Data, &event)
        handler(event)
    })
    return err
}

func (s *EventSubscriber) Close() {
    s.conn.Close()
}
```

### 4. Initialize in main.go

```go
// backend/main.go
publisher, err := nats.NewEventPublisher(os.Getenv("NATS_URL"))
if err != nil {
    log.Fatal("Failed to connect to NATS:", err)
}
defer publisher.Close()

subscriber, err := nats.NewEventSubscriber(os.Getenv("NATS_URL"))
if err != nil {
    log.Fatal("Failed to connect to NATS:", err)
}
defer subscriber.Close()
```

## Usage Patterns

### Publish Events
```go
func (h *ItemHandler) CreateItem(c echo.Context) error {
    item, err := h.db.CreateItem(c.Request().Context(), req)
    if err != nil {
        return err
    }
    
    // Publish event
    h.publisher.PublishItemEvent(map[string]interface{}{
        "type": "item.created",
        "id":   item.ID,
        "data": item,
    })
    
    return c.JSON(201, item)
}
```

### Subscribe to Events
```go
func (s *Service) StartEventListener() {
    s.subscriber.SubscribeToItems(func(event interface{}) error {
        // Handle event
        log.Printf("Received event: %v", event)
        return nil
    })
}
```

## Subject Hierarchy

```
items.events          → All item events
items.events.created  → Item created
items.events.updated  → Item updated
items.events.deleted  → Item deleted

links.events          → All link events
links.events.created  → Link created

agents.events         → All agent events
agents.events.created → Agent created
```

## Monitoring

### NATS CLI
```bash
# Server info
nats-cli server info

# List subjects
nats-cli pub --list

# Monitor messages
nats-cli sub ">"

# Check JetStream status
nats-cli stream list
```

### Synadia Dashboard
- Message throughput
- Connected clients
- Subject distribution
- Error rates

## Performance Tuning

### Connection Pooling
```go
opts := []nats.Option{
    nats.MaxReconnects(-1),
    nats.ReconnectWait(2 * time.Second),
}
conn, _ := nats.Connect(url, opts...)
```

### Async Publishing
```go
// Async publish (fire and forget)
conn.PublishAsync("subject", data)
```

## Troubleshooting

### Connection Issues
```bash
# Test connection
nats-cli server info

# Check network
telnet host port
```

### Message Issues
```bash
# Monitor all messages
nats-cli sub ">"

# Check subject stats
nats-cli stream info
```

## Cost

- **Local**: Free (Docker)
- **Synadia Free Tier**:
  - 1 million messages/month
  - 5GB storage
  - Perfect for development
- **Synadia Pro**: $0.10/million messages

## Next Steps

1. Set up local NATS with Docker
2. Create EventPublisher struct in Go
3. Create EventSubscriber struct in Go
4. Integrate with handlers
5. Test pub/sub pattern
6. Deploy to Synadia for production

