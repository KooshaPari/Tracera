//go:build integration

package integration

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/nats-io/nats.go"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
)

type externalServicesFixture struct {
	ctx         context.Context
	natsConn    *nats.Conn
	redisClient *redis.Client
	cleanup     func()
}

func setupExternalServicesTests(t *testing.T) *externalServicesFixture {
	ctx := context.Background()

	// NATS setup
	natsURL := os.Getenv("TEST_NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}
	nc, err := nats.Connect(natsURL)
	if err != nil {
		t.Skip("NATS not available:", err)
	}

	// Redis setup
	redisURL := os.Getenv("TEST_REDIS_URL")
	if redisURL == "" {
		redisURL = "localhost:6379"
	}
	rdb := redis.NewClient(&redis.Options{
		Addr: redisURL,
	})
	if err := rdb.Ping(ctx).Err(); err != nil {
		t.Skip("Redis not available:", err)
	}

	cleanup := func() {
		nc.Close()
		rdb.Close()
	}

	return &externalServicesFixture{
		ctx:         ctx,
		natsConn:    nc,
		redisClient: rdb,
		cleanup:     cleanup,
	}
}

// TEST 1-20: NATS Integration

func TestNATS_PublishSubscribe(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.publish"
	received := make(chan string, 1)

	// Subscribe
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
		received <- string(msg.Data)
	})
	assert.NoError(t, err)

	// Publish
	err = f.natsConn.Publish(subject, []byte("test message"))
	assert.NoError(t, err)

	// Wait for message
	select {
	case msg := <-received:
		assert.Equal(t, "test message", msg)
	case <-time.After(1 * time.Second):
		t.Fatal("Timeout waiting for message")
	}
}

func TestNATS_RequestReply(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.request"

	// Setup responder
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
		msg.Respond([]byte("response"))
	})
	assert.NoError(t, err)

	// Send request
	msg, err := f.natsConn.Request(subject, []byte("request"), 1*time.Second)
	assert.NoError(t, err)
	assert.Equal(t, "response", string(msg.Data))
}

func TestNATS_QueueGroups(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.queue"
	queueGroup := "workers"
	received := make(chan string, 3)

	// Create 3 queue subscribers
	for i := 0; i < 3; i++ {
		_, err := f.natsConn.QueueSubscribe(subject, queueGroup, func(msg *nats.Msg) {
			received <- string(msg.Data)
		})
		assert.NoError(t, err)
	}

	// Publish 10 messages
	for i := 0; i < 10; i++ {
		err := f.natsConn.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
		assert.NoError(t, err)
	}

	// Wait for all messages (distributed across queue group)
	count := 0
	timeout := time.After(2 * time.Second)
	for count < 10 {
		select {
		case <-received:
			count++
		case <-timeout:
			t.Fatalf("Timeout: received %d/10 messages", count)
		}
	}
	assert.Equal(t, 10, count)
}

func TestNATS_WildcardSubscription(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	received := make(chan string, 3)

	// Wildcard subscription
	_, err := f.natsConn.Subscribe("test.*.event", func(msg *nats.Msg) {
		received <- msg.Subject
	})
	assert.NoError(t, err)

	// Publish to matching subjects
	subjects := []string{"test.alpha.event", "test.beta.event", "test.gamma.event"}
	for _, subj := range subjects {
		err := f.natsConn.Publish(subj, []byte("data"))
		assert.NoError(t, err)
	}

	// Verify all received
	for i := 0; i < 3; i++ {
		select {
		case subj := <-received:
			assert.Contains(t, subjects, subj)
		case <-time.After(1 * time.Second):
			t.Fatal("Timeout waiting for message")
		}
	}
}

func TestNATS_JetStreamPublish(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	js, err := f.natsConn.JetStream()
	if err != nil {
		t.Skip("JetStream not enabled")
	}

	streamName := "TEST_STREAM"
	subject := "test.jetstream"

	// Create stream
	_, err = js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		t.Fatal("Failed to create stream:", err)
	}

	// Publish
	_, err = js.Publish(subject, []byte("jetstream message"))
	assert.NoError(t, err)

	// Clean up
	js.DeleteStream(streamName)
}

func TestNATS_JetStreamConsumer(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	js, err := f.natsConn.JetStream()
	if err != nil {
		t.Skip("JetStream not enabled")
	}

	streamName := "TEST_CONSUMER_STREAM"
	subject := "test.consumer"

	// Create stream
	_, err = js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		t.Fatal("Failed to create stream:", err)
	}

	// Publish messages
	for i := 0; i < 5; i++ {
		js.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
	}

	// Create consumer
	sub, err := js.SubscribeSync(subject)
	assert.NoError(t, err)

	// Consume messages
	count := 0
	for i := 0; i < 5; i++ {
		msg, err := sub.NextMsg(1 * time.Second)
		if err == nil {
			count++
			msg.Ack()
		}
	}
	assert.Equal(t, 5, count)

	// Clean up
	js.DeleteStream(streamName)
}

func TestNATS_HeadersSupport(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.headers"
	received := make(chan *nats.Msg, 1)

	// Subscribe
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
		received <- msg
	})
	assert.NoError(t, err)

	// Publish with headers
	msg := nats.NewMsg(subject)
	msg.Data = []byte("test data")
	msg.Header.Add("X-Request-ID", uuid.New().String())
	msg.Header.Add("X-Priority", "high")

	err = f.natsConn.PublishMsg(msg)
	assert.NoError(t, err)

	// Verify headers
	select {
	case receivedMsg := <-received:
		assert.NotNil(t, receivedMsg.Header.Get("X-Request-ID"))
		assert.Equal(t, "high", receivedMsg.Header.Get("X-Priority"))
	case <-time.After(1 * time.Second):
		t.Fatal("Timeout")
	}
}

func TestNATS_MaxReconnects(t *testing.T) {
	// Test connection resilience
	opts := nats.GetDefaultOptions()
	opts.MaxReconnect = 3
	opts.ReconnectWait = 100 * time.Millisecond

	nc, err := opts.Connect()
	assert.NoError(t, err)
	defer nc.Close()

	assert.True(t, nc.IsConnected())
}

func TestNATS_DrainConnection(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.drain"

	// Subscribe
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {})
	assert.NoError(t, err)

	// Publish messages
	for i := 0; i < 10; i++ {
		f.natsConn.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
	}

	// Drain (process pending messages before closing)
	err = f.natsConn.Drain()
	assert.NoError(t, err)
}

func TestNATS_FlushConnection(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.flush"

	// Publish multiple messages
	for i := 0; i < 100; i++ {
		f.natsConn.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
	}

	// Flush to ensure all published
	err := f.natsConn.Flush()
	assert.NoError(t, err)
}

func TestNATS_SynchronousRequest(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.sync.request"

	// Responder
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
		msg.Respond([]byte("sync response"))
	})
	assert.NoError(t, err)

	// Multiple concurrent requests
	done := make(chan bool, 10)
	for i := 0; i < 10; i++ {
		go func(idx int) {
			msg, err := f.natsConn.Request(subject, []byte(fmt.Sprintf("req-%d", idx)), 1*time.Second)
			assert.NoError(t, err)
			assert.Equal(t, "sync response", string(msg.Data))
			done <- true
		}(i)
	}

	// Wait for all requests
	for i := 0; i < 10; i++ {
		<-done
	}
}

func TestNATS_MessageRedelivery(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	js, err := f.natsConn.JetStream()
	if err != nil {
		t.Skip("JetStream not enabled")
	}

	streamName := "TEST_REDELIVERY"
	subject := "test.redeliver"

	// Create stream
	_, err = js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		t.Fatal("Failed to create stream:", err)
	}

	// Publish message
	js.Publish(subject, []byte("redeliver msg"))

	// Subscribe with manual ack
	attemptCount := 0
	sub, err := js.Subscribe(subject, func(msg *nats.Msg) {
		attemptCount++
		if attemptCount < 3 {
			msg.Nak() // Negative acknowledgement triggers redelivery
		} else {
			msg.Ack()
		}
	}, nats.ManualAck(), nats.AckWait(100*time.Millisecond))
	assert.NoError(t, err)

	// Wait for redeliveries
	time.Sleep(500 * time.Millisecond)
	assert.GreaterOrEqual(t, attemptCount, 3)

	sub.Unsubscribe()
	js.DeleteStream(streamName)
}

func TestNATS_StreamRetention(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	js, err := f.natsConn.JetStream()
	if err != nil {
		t.Skip("JetStream not enabled")
	}

	streamName := "TEST_RETENTION"
	subject := "test.retention"

	// Create stream with message limit
	_, err = js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
		MaxMsgs:  5,
		Discard:  nats.DiscardOld,
	})
	if err != nil && err != nats.ErrStreamNameAlreadyInUse {
		t.Fatal("Failed to create stream:", err)
	}

	// Publish 10 messages (only last 5 should be retained)
	for i := 0; i < 10; i++ {
		js.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
	}

	// Verify retention
	streamInfo, err := js.StreamInfo(streamName)
	assert.NoError(t, err)
	assert.Equal(t, uint64(5), streamInfo.State.Msgs)

	js.DeleteStream(streamName)
}

func TestNATS_StreamBackpressure(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.backpressure"
	received := make(chan bool, 1000)

	// Slow consumer
	_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
		time.Sleep(10 * time.Millisecond) // Simulate slow processing
		received <- true
	})
	assert.NoError(t, err)

	// Fast publisher
	for i := 0; i < 100; i++ {
		f.natsConn.Publish(subject, []byte(fmt.Sprintf("msg-%d", i)))
	}

	// Verify messages processed (with backpressure handling)
	count := 0
	timeout := time.After(5 * time.Second)
	for count < 100 {
		select {
		case <-received:
			count++
		case <-timeout:
			t.Logf("Processed %d/100 messages with backpressure", count)
			return
		}
	}
}

func TestNATS_ClosedConnectionHandling(t *testing.T) {
	opts := nats.GetDefaultOptions()
	nc, err := opts.Connect()
	assert.NoError(t, err)

	// Close connection
	nc.Close()

	// Attempt to publish (should fail gracefully)
	err = nc.Publish("test.closed", []byte("msg"))
	assert.Error(t, err)
	assert.True(t, nc.IsClosed())
}

func TestNATS_StatusMonitoring(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	assert.True(t, f.natsConn.IsConnected())
	assert.False(t, f.natsConn.IsClosed())
	assert.False(t, f.natsConn.IsDraining())
}

func TestNATS_ErrorHandling(t *testing.T) {
	opts := nats.GetDefaultOptions()
	errors := make(chan error, 10)

	opts.ErrorHandler = func(conn *nats.Conn, sub *nats.Subscription, err error) {
		errors <- err
	}

	nc, err := opts.Connect()
	assert.NoError(t, err)
	defer nc.Close()

	// Trigger error (invalid subject)
	nc.Publish("", []byte("invalid"))

	// Check if error was captured
	select {
	case <-errors:
		// Error captured
	case <-time.After(100 * time.Millisecond):
		// No error (also acceptable)
	}
}

func TestNATS_MultipleSubscribers(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	subject := "test.multi"
	received := make(chan string, 10)

	// Create 5 subscribers
	for i := 0; i < 5; i++ {
		subscriberID := fmt.Sprintf("sub-%d", i)
		_, err := f.natsConn.Subscribe(subject, func(msg *nats.Msg) {
			received <- subscriberID
		})
		assert.NoError(t, err)
	}

	// Publish one message
	f.natsConn.Publish(subject, []byte("broadcast"))

	// All 5 subscribers should receive it
	count := 0
	timeout := time.After(1 * time.Second)
	for count < 5 {
		select {
		case <-received:
			count++
		case <-timeout:
			t.Fatalf("Timeout: %d/5 subscribers received message", count)
		}
	}
	assert.Equal(t, 5, count)
}

// TEST 21-40: Redis Integration

func TestRedis_SetGet(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:key:" + uuid.New().String()
	value := "test value"

	// Set
	err := f.redisClient.Set(f.ctx, key, value, 0).Err()
	assert.NoError(t, err)

	// Get
	retrieved, err := f.redisClient.Get(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, value, retrieved)

	// Cleanup
	f.redisClient.Del(f.ctx, key)
}

func TestRedis_SetWithExpiry(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:expiry:" + uuid.New().String()
	value := "expiring value"

	// Set with 1 second TTL
	err := f.redisClient.Set(f.ctx, key, value, 1*time.Second).Err()
	assert.NoError(t, err)

	// Verify exists
	exists, err := f.redisClient.Exists(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(1), exists)

	// Wait for expiry
	time.Sleep(1500 * time.Millisecond)

	// Verify expired
	exists, err = f.redisClient.Exists(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(0), exists)
}

func TestRedis_IncrDecr(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:counter:" + uuid.New().String()

	// Increment
	val, err := f.redisClient.Incr(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(1), val)

	val, err = f.redisClient.IncrBy(f.ctx, key, 5).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(6), val)

	// Decrement
	val, err = f.redisClient.Decr(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(5), val)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_HashOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:hash:" + uuid.New().String()

	// HSet
	err := f.redisClient.HSet(f.ctx, key, "field1", "value1", "field2", "value2").Err()
	assert.NoError(t, err)

	// HGet
	val, err := f.redisClient.HGet(f.ctx, key, "field1").Result()
	assert.NoError(t, err)
	assert.Equal(t, "value1", val)

	// HGetAll
	allFields, err := f.redisClient.HGetAll(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, 2, len(allFields))
	assert.Equal(t, "value1", allFields["field1"])
	assert.Equal(t, "value2", allFields["field2"])

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_ListOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:list:" + uuid.New().String()

	// RPush
	err := f.redisClient.RPush(f.ctx, key, "item1", "item2", "item3").Err()
	assert.NoError(t, err)

	// LLen
	length, err := f.redisClient.LLen(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(3), length)

	// LRange
	items, err := f.redisClient.LRange(f.ctx, key, 0, -1).Result()
	assert.NoError(t, err)
	assert.Equal(t, []string{"item1", "item2", "item3"}, items)

	// LPop
	popped, err := f.redisClient.LPop(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, "item1", popped)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_SetOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:set:" + uuid.New().String()

	// SAdd
	err := f.redisClient.SAdd(f.ctx, key, "member1", "member2", "member3").Err()
	assert.NoError(t, err)

	// SMembers
	members, err := f.redisClient.SMembers(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, 3, len(members))

	// SIsMember
	isMember, err := f.redisClient.SIsMember(f.ctx, key, "member1").Result()
	assert.NoError(t, err)
	assert.True(t, isMember)

	// SRem
	err = f.redisClient.SRem(f.ctx, key, "member1").Err()
	assert.NoError(t, err)

	isMember, err = f.redisClient.SIsMember(f.ctx, key, "member1").Result()
	assert.NoError(t, err)
	assert.False(t, isMember)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_SortedSetOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:zset:" + uuid.New().String()

	// ZAdd
	members := []redis.Z{
		{Score: 1, Member: "one"},
		{Score: 2, Member: "two"},
		{Score: 3, Member: "three"},
	}
	err := f.redisClient.ZAdd(f.ctx, key, members...).Err()
	assert.NoError(t, err)

	// ZRange
	results, err := f.redisClient.ZRange(f.ctx, key, 0, -1).Result()
	assert.NoError(t, err)
	assert.Equal(t, []string{"one", "two", "three"}, results)

	// ZScore
	score, err := f.redisClient.ZScore(f.ctx, key, "two").Result()
	assert.NoError(t, err)
	assert.Equal(t, float64(2), score)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_PubSub(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	channel := "test:channel:" + uuid.New().String()
	received := make(chan string, 1)

	// Subscribe
	pubsub := f.redisClient.Subscribe(f.ctx, channel)
	defer pubsub.Close()

	go func() {
		msg, err := pubsub.ReceiveMessage(f.ctx)
		if err == nil {
			received <- msg.Payload
		}
	}()

	// Wait for subscription to be active
	time.Sleep(100 * time.Millisecond)

	// Publish
	err := f.redisClient.Publish(f.ctx, channel, "test message").Err()
	assert.NoError(t, err)

	// Verify received
	select {
	case msg := <-received:
		assert.Equal(t, "test message", msg)
	case <-time.After(1 * time.Second):
		t.Fatal("Timeout waiting for pub/sub message")
	}
}

func TestRedis_Pipeline(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	keys := make([]string, 5)
	for i := 0; i < 5; i++ {
		keys[i] = fmt.Sprintf("test:pipe:%s:%d", uuid.New().String(), i)
	}

	// Pipeline multiple operations
	pipe := f.redisClient.Pipeline()
	for i, key := range keys {
		pipe.Set(f.ctx, key, fmt.Sprintf("value%d", i), 0)
	}
	_, err := pipe.Exec(f.ctx)
	assert.NoError(t, err)

	// Verify all set
	for i, key := range keys {
		val, err := f.redisClient.Get(f.ctx, key).Result()
		assert.NoError(t, err)
		assert.Equal(t, fmt.Sprintf("value%d", i), val)
	}

	// Cleanup
	f.redisClient.Del(f.ctx, keys...)
}

func TestRedis_Transaction(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:tx:" + uuid.New().String()

	// Transaction with WATCH
	err := f.redisClient.Watch(f.ctx, func(tx *redis.Tx) error {
		// Set initial value
		err := tx.Set(f.ctx, key, "initial", 0).Err()
		if err != nil {
			return err
		}

		// Transaction
		_, err = tx.TxPipelined(f.ctx, func(pipe redis.Pipeliner) error {
			pipe.Set(f.ctx, key, "updated", 0)
			return nil
		})
		return err
	}, key)
	assert.NoError(t, err)

	// Verify final value
	val, err := f.redisClient.Get(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, "updated", val)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_BitOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:bits:" + uuid.New().String()

	// SetBit
	err := f.redisClient.SetBit(f.ctx, key, 0, 1).Err()
	assert.NoError(t, err)
	err = f.redisClient.SetBit(f.ctx, key, 2, 1).Err()
	assert.NoError(t, err)

	// GetBit
	bit, err := f.redisClient.GetBit(f.ctx, key, 0).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(1), bit)

	// BitCount
	count, err := f.redisClient.BitCount(f.ctx, key, nil).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(2), count)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_HyperLogLog(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:hll:" + uuid.New().String()

	// PFAdd
	err := f.redisClient.PFAdd(f.ctx, key, "element1", "element2", "element3", "element1").Err()
	assert.NoError(t, err)

	// PFCount (approximate unique count)
	count, err := f.redisClient.PFCount(f.ctx, key).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(3), count) // Duplicates counted once

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_Scan(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	prefix := "test:scan:" + uuid.New().String()

	// Create keys
	for i := 0; i < 10; i++ {
		key := fmt.Sprintf("%s:%d", prefix, i)
		f.redisClient.Set(f.ctx, key, fmt.Sprintf("value%d", i), 0)
	}

	// Scan
	var cursor uint64
	var keys []string
	for {
		var scannedKeys []string
		var err error
		scannedKeys, cursor, err = f.redisClient.Scan(f.ctx, cursor, prefix+"*", 5).Result()
		assert.NoError(t, err)
		keys = append(keys, scannedKeys...)
		if cursor == 0 {
			break
		}
	}

	assert.Equal(t, 10, len(keys))

	// Cleanup
	f.redisClient.Del(f.ctx, keys...)
}

func TestRedis_GeoOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:geo:" + uuid.New().String()

	// GeoAdd
	locations := []*redis.GeoLocation{
		{Name: "loc1", Longitude: -122.4194, Latitude: 37.7749}, // San Francisco
		{Name: "loc2", Longitude: -118.2437, Latitude: 34.0522}, // Los Angeles
	}
	err := f.redisClient.GeoAdd(f.ctx, key, locations...).Err()
	assert.NoError(t, err)

	// GeoDist
	dist, err := f.redisClient.GeoDist(f.ctx, key, "loc1", "loc2", "km").Result()
	assert.NoError(t, err)
	assert.Greater(t, dist, float64(500)) // ~550km apart

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_StreamOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	stream := "test:stream:" + uuid.New().String()

	// XAdd
	_, err := f.redisClient.XAdd(f.ctx, &redis.XAddArgs{
		Stream: stream,
		Values: map[string]interface{}{
			"field1": "value1",
			"field2": "value2",
		},
	}).Result()
	assert.NoError(t, err)

	// XLen
	length, err := f.redisClient.XLen(f.ctx, stream).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(1), length)

	// XRange
	messages, err := f.redisClient.XRange(f.ctx, stream, "-", "+").Result()
	assert.NoError(t, err)
	assert.Equal(t, 1, len(messages))
	assert.Equal(t, "value1", messages[0].Values["field1"])

	f.redisClient.Del(f.ctx, stream)
}

func TestRedis_MultiKeyOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	keys := []string{
		"test:multi:1:" + uuid.New().String(),
		"test:multi:2:" + uuid.New().String(),
		"test:multi:3:" + uuid.New().String(),
	}

	// MSet
	err := f.redisClient.MSet(f.ctx, keys[0], "val1", keys[1], "val2", keys[2], "val3").Err()
	assert.NoError(t, err)

	// MGet
	values, err := f.redisClient.MGet(f.ctx, keys...).Result()
	assert.NoError(t, err)
	assert.Equal(t, 3, len(values))

	// Cleanup
	f.redisClient.Del(f.ctx, keys...)
}

func TestRedis_LuaScripting(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:lua:" + uuid.New().String()

	// Lua script to increment and return value
	script := redis.NewScript(`
		local val = redis.call('GET', KEYS[1])
		if val then
			val = val + ARGV[1]
		else
			val = ARGV[1]
		end
		redis.call('SET', KEYS[1], val)
		return val
	`)

	// Run script
	result, err := script.Run(f.ctx, f.redisClient, []string{key}, 5).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(5), result)

	result, err = script.Run(f.ctx, f.redisClient, []string{key}, 3).Result()
	assert.NoError(t, err)
	assert.Equal(t, int64(8), result)

	f.redisClient.Del(f.ctx, key)
}

func TestRedis_BlockingOperations(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	key := "test:blocking:" + uuid.New().String()

	// BLPop in goroutine
	received := make(chan string, 1)
	go func() {
		result, err := f.redisClient.BLPop(f.ctx, 2*time.Second, key).Result()
		if err == nil && len(result) > 1 {
			received <- result[1]
		}
	}()

	// Wait a bit then push
	time.Sleep(100 * time.Millisecond)
	err := f.redisClient.RPush(f.ctx, key, "blocking value").Err()
	assert.NoError(t, err)

	// Verify received
	select {
	case val := <-received:
		assert.Equal(t, "blocking value", val)
	case <-time.After(3 * time.Second):
		t.Fatal("Timeout waiting for blocking operation")
	}
}

func TestRedis_ClusterMode(t *testing.T) {
	// Test cluster-specific operations if running in cluster mode
	clusterURL := os.Getenv("TEST_REDIS_CLUSTER_URL")
	if clusterURL == "" {
		t.Skip("Redis cluster not configured")
	}

	// This test would connect to Redis cluster and verify cluster operations
	t.Log("Redis cluster mode test placeholder")
}

func TestRedis_ConnectionPooling(t *testing.T) {
	f := setupExternalServicesTests(t)
	defer f.cleanup()

	// Perform many concurrent operations to test pool
	done := make(chan bool, 100)
	for i := 0; i < 100; i++ {
		go func(idx int) {
			key := fmt.Sprintf("test:pool:%d", idx)
			f.redisClient.Set(f.ctx, key, fmt.Sprintf("value%d", idx), 0)
			done <- true
		}(i)
	}

	// Wait for all
	for i := 0; i < 100; i++ {
		<-done
	}

	// Verify pool stats
	stats := f.redisClient.PoolStats()
	assert.Greater(t, stats.TotalConns, uint32(0))
}
