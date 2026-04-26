package nats

import (
	"context"
	"fmt"
	"github.com/nats-io/nats.go"
)

// NatsAdapter wraps NATS client (Wrap-Over pattern)
type NatsAdapter struct {
	nc *nats.Conn
}

// Compile-time interface check
var _ EventPublisher = (*NatsAdapter)(nil)

type EventPublisher interface {
	Publish(ctx context.Context, subject string, data []byte) error
	Subscribe(subject string, handler nats.MsgHandler) error
}

func NewNatsAdapter(url string) (*NatsAdapter, error) {
	nc, err := nats.Connect(url)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}
	return &NatsAdapter{nc: nc}, nil
}

func (a *NatsAdapter) Close() {
	a.nc.Close()
}

func (a *NatsAdapter) Publish(ctx context.Context, subject string, data []byte) error {
	return a.nc.Publish(subject, data)
}

func (a *NatsAdapter) Subscribe(subject string, handler nats.MsgHandler) error {
	_, err := a.nc.Subscribe(subject, handler)
	return err
}
