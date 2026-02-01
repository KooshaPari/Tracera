# Streaming Implementation Patterns

**Document Type:** Implementation Guide
**Target Audience:** Backend and Frontend Developers
**Last Updated:** 2026-02-01

---

## Overview

This guide provides practical, production-ready implementation patterns for streaming data in TraceRTM. All examples are tested and ready to integrate with the existing Go backend and React frontend.

**Tech Stack:**
- **Backend:** Go 1.21+, Echo framework, PostgreSQL, NATS
- **Frontend:** React 18+, TypeScript, TanStack Query, Bun

---

## Table of Contents

1. [Server-Sent Events (SSE)](#1-server-sent-events-sse)
2. [WebSocket Patterns](#2-websocket-patterns)
3. [Streaming JSON (NDJSON)](#3-streaming-json-ndjson)
4. [Database Streaming](#4-database-streaming)
5. [Frontend Consumption](#5-frontend-consumption)
6. [Error Handling](#6-error-handling)
7. [Testing Strategies](#7-testing-strategies)

---

## 1. Server-Sent Events (SSE)

### Backend: Echo SSE Handler

```go
package handlers

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "time"

    "github.com/google/uuid"
    "github.com/labstack/echo/v4"
    "github.com/nats-io/nats.go"
)

// SSEEvent represents a server-sent event
type SSEEvent struct {
    ID    string      `json:"id"`
    Event string      `json:"event"`
    Data  interface{} `json:"data"`
}

// StreamProjectEvents streams project events via SSE
// GET /api/v1/projects/:projectId/events/stream
func (h *Handler) StreamProjectEvents(c echo.Context) error {
    // Validate authentication
    user := c.Get("user").(*auth.User)
    projectID := c.Param("projectId")

    // Validate project access
    if !h.hasProjectAccess(user.ID, projectID) {
        return echo.NewHTTPError(http.StatusForbidden, "Access denied")
    }

    // Set SSE headers
    c.Response().Header().Set("Content-Type", "text/event-stream")
    c.Response().Header().Set("Cache-Control", "no-cache")
    c.Response().Header().Set("Connection", "keep-alive")
    c.Response().Header().Set("X-Accel-Buffering", "no") // Disable nginx buffering

    // Check if ResponseWriter supports flushing
    flusher, ok := c.Response().Writer.(http.Flusher)
    if !ok {
        return echo.NewHTTPError(http.StatusInternalServerError, "Streaming not supported")
    }

    // Create event channel
    eventChan := make(chan *nats.Msg, 100)
    defer close(eventChan)

    // Subscribe to NATS for this project
    subject := fmt.Sprintf("project.%s.>", projectID)
    sub, err := h.natsConn.ChanSubscribe(subject, eventChan)
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, "Failed to subscribe to events")
    }
    defer sub.Unsubscribe()

    // Send initial connection event
    fmt.Fprintf(c.Response().Writer, "event: connected\n")
    fmt.Fprintf(c.Response().Writer, "data: {\"project_id\": \"%s\"}\n\n", projectID)
    flusher.Flush()

    // Keepalive ticker (30 seconds)
    keepalive := time.NewTicker(30 * time.Second)
    defer keepalive.Stop()

    // Context for cancellation
    ctx := c.Request().Context()

    for {
        select {
        case msg := <-eventChan:
            // Parse NATS message
            var event SSEEvent
            if err := json.Unmarshal(msg.Data, &event); err != nil {
                continue
            }

            // Generate event ID if not present
            if event.ID == "" {
                event.ID = uuid.New().String()
            }

            // Serialize event data
            data, err := json.Marshal(event.Data)
            if err != nil {
                continue
            }

            // Send SSE event
            fmt.Fprintf(c.Response().Writer, "id: %s\n", event.ID)
            fmt.Fprintf(c.Response().Writer, "event: %s\n", event.Event)
            fmt.Fprintf(c.Response().Writer, "data: %s\n\n", data)
            flusher.Flush()

        case <-keepalive.C:
            // Send keepalive comment
            fmt.Fprintf(c.Response().Writer, ": keepalive\n\n")
            flusher.Flush()

        case <-ctx.Done():
            // Client disconnected
            return nil
        }
    }
}

// Helper: Check project access
func (h *Handler) hasProjectAccess(userID, projectID string) bool {
    var count int
    h.db.QueryRow(`
        SELECT COUNT(*)
        FROM project_members
        WHERE project_id = $1 AND user_id = $2
    `, projectID, userID).Scan(&count)
    return count > 0
}
```

### Backend: SSE Notification Service

```go
package services

import (
    "encoding/json"
    "fmt"
    "time"

    "github.com/google/uuid"
    "github.com/nats-io/nats.go"
)

// NotificationService handles sending notifications via NATS
type NotificationService struct {
    natsConn *nats.Conn
}

// NotificationType represents the type of notification
type NotificationType string

const (
    NotificationTypeItemCreated   NotificationType = "item.created"
    NotificationTypeItemUpdated   NotificationType = "item.updated"
    NotificationTypeItemDeleted   NotificationType = "item.deleted"
    NotificationTypeTestCompleted NotificationType = "test.completed"
    NotificationTypeMention       NotificationType = "mention"
)

// Notification represents a user notification
type Notification struct {
    ID        uuid.UUID        `json:"id"`
    Type      NotificationType `json:"type"`
    ProjectID uuid.UUID        `json:"project_id"`
    UserID    uuid.UUID        `json:"user_id"`
    Title     string           `json:"title"`
    Message   string           `json:"message"`
    Link      string           `json:"link"`
    Read      bool             `json:"read"`
    CreatedAt time.Time        `json:"created_at"`
}

// SendNotification publishes a notification to NATS
func (s *NotificationService) SendNotification(notification *Notification) error {
    if notification.ID == uuid.Nil {
        notification.ID = uuid.New()
    }
    if notification.CreatedAt.IsZero() {
        notification.CreatedAt = time.Now()
    }

    // Serialize notification
    data, err := json.Marshal(notification)
    if err != nil {
        return fmt.Errorf("failed to marshal notification: %w", err)
    }

    // Publish to NATS
    subject := fmt.Sprintf("project.%s.notification", notification.ProjectID)
    if err := s.natsConn.Publish(subject, data); err != nil {
        return fmt.Errorf("failed to publish notification: %w", err)
    }

    return nil
}

// Usage example
func (h *Handler) CreateItem(c echo.Context) error {
    // ... create item logic ...

    // Send notification
    notification := &Notification{
        Type:      NotificationTypeItemCreated,
        ProjectID: item.ProjectID,
        UserID:    user.ID,
        Title:     "New Item Created",
        Message:   fmt.Sprintf("%s created item: %s", user.Name, item.Title),
        Link:      fmt.Sprintf("/projects/%s/items/%s", item.ProjectID, item.ID),
    }

    if err := h.notificationService.SendNotification(notification); err != nil {
        // Log error but don't fail the request
        log.Printf("Failed to send notification: %v", err)
    }

    return c.JSON(http.StatusCreated, item)
}
```

### Frontend: React SSE Hook

```typescript
import { useEffect, useState, useRef, useCallback } from 'react';

interface SSEOptions {
    onMessage?: (event: MessageEvent) => void;
    onError?: (error: Event) => void;
    onOpen?: () => void;
    reconnect?: boolean;
    reconnectInterval?: number;
}

type SSEStatus = 'connecting' | 'open' | 'closed' | 'error';

export function useSSE(url: string, options: SSEOptions = {}) {
    const {
        onMessage,
        onError,
        onOpen,
        reconnect = true,
        reconnectInterval = 5000,
    } = options;

    const [status, setStatus] = useState<SSEStatus>('connecting');
    const [lastEventId, setLastEventId] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);

    const connect = useCallback(() => {
        // Close existing connection
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        // Build URL with Last-Event-ID if available
        const urlWithEventId = lastEventId
            ? `${url}${url.includes('?') ? '&' : '?'}lastEventId=${lastEventId}`
            : url;

        // Create new EventSource
        const eventSource = new EventSource(urlWithEventId);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            setStatus('open');
            onOpen?.();
        };

        eventSource.onmessage = (event) => {
            if (event.lastEventId) {
                setLastEventId(event.lastEventId);
            }
            onMessage?.(event);
        };

        eventSource.onerror = (error) => {
            setStatus('error');
            onError?.(error);

            // Attempt reconnection
            if (reconnect) {
                eventSource.close();
                setStatus('connecting');
                reconnectTimerRef.current = setTimeout(connect, reconnectInterval);
            }
        };
    }, [url, lastEventId, onMessage, onError, onOpen, reconnect, reconnectInterval]);

    // Connect on mount
    useEffect(() => {
        connect();

        // Cleanup on unmount
        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
            if (reconnectTimerRef.current) {
                clearTimeout(reconnectTimerRef.current);
            }
        };
    }, [connect]);

    const close = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        if (reconnectTimerRef.current) {
            clearTimeout(reconnectTimerRef.current);
        }
        setStatus('closed');
    }, []);

    return { status, close };
}

// Typed SSE hook for specific event types
export function useTypedSSE<T>(
    url: string,
    eventType: string,
    onData: (data: T) => void
) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<Error | null>(null);

    const { status, close } = useSSE(url, {
        onMessage: (event) => {
            if (event.type === eventType || event.type === 'message') {
                try {
                    const parsed = JSON.parse(event.data) as T;
                    setData(parsed);
                    onData(parsed);
                } catch (e) {
                    setError(e as Error);
                }
            }
        },
        onError: () => {
            setError(new Error('SSE connection error'));
        },
    });

    return { data, error, status, close };
}
```

### Frontend: Notification Component

```typescript
import { useSSE } from '@/hooks/useSSE';
import { toast } from 'sonner';

interface Notification {
    id: string;
    type: string;
    title: string;
    message: string;
    link: string;
    created_at: string;
}

export function LiveNotifications({ projectId }: { projectId: string }) {
    const { status } = useSSE(
        `/api/v1/projects/${projectId}/events/stream`,
        {
            onMessage: (event) => {
                if (event.type === 'notification') {
                    const notification: Notification = JSON.parse(event.data);

                    toast(notification.title, {
                        description: notification.message,
                        action: notification.link ? {
                            label: 'View',
                            onClick: () => window.location.href = notification.link,
                        } : undefined,
                    });
                }
            },
        }
    );

    return (
        <div className="fixed top-4 right-4">
            {status === 'open' && (
                <div className="flex items-center gap-2 text-xs text-green-600">
                    <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                    Live
                </div>
            )}
            {status === 'connecting' && (
                <div className="text-xs text-yellow-600">Connecting...</div>
            )}
            {status === 'error' && (
                <div className="text-xs text-red-600">Disconnected</div>
            )}
        </div>
    );
}
```

---

## 2. WebSocket Patterns

### Enhanced WebSocket Handler with Backpressure

```go
package websocket

import (
    "context"
    "encoding/json"
    "time"

    "github.com/google/uuid"
    "golang.org/x/net/websocket"
)

// Client with backpressure support
type Client struct {
    ID        string
    Conn      *websocket.Conn
    Send      chan *Message
    Hub       *Hub
    sendRate  *rate.Limiter // Rate limiter for send operations
}

// NewClient creates a client with rate limiting
func NewClient(conn *websocket.Conn, hub *Hub) *Client {
    return &Client{
        ID:       uuid.New().String(),
        Conn:     conn,
        Send:     make(chan *Message, 256),
        Hub:      hub,
        sendRate: rate.NewLimiter(rate.Limit(100), 200), // 100 msg/sec, burst 200
    }
}

// WritePump sends messages to WebSocket with backpressure handling
func (c *Client) WritePump() {
    ticker := time.NewTicker(30 * time.Second)
    defer func() {
        ticker.Stop()
        c.Conn.Close()
    }()

    for {
        select {
        case message, ok := <-c.Send:
            if !ok {
                // Channel closed, exit
                return
            }

            // Check rate limit
            if !c.sendRate.Allow() {
                // Drop message if rate exceeded (or queue elsewhere)
                continue
            }

            // Set write deadline
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))

            // Send message
            if err := websocket.JSON.Send(c.Conn, message); err != nil {
                return
            }

        case <-ticker.C:
            // Send ping
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
            if err := websocket.JSON.Send(c.Conn, &Message{Type: "ping"}); err != nil {
                return
            }
        }
    }
}

// Broadcast with priority
func (h *Hub) BroadcastWithPriority(message *Message, priority int) {
    h.mu.RLock()
    defer h.mu.RUnlock()

    for client := range h.clients {
        select {
        case client.Send <- message:
            // Message sent
        default:
            // Channel full
            if priority > 0 {
                // High priority: drop oldest message and send
                select {
                case <-client.Send:
                    client.Send <- message
                default:
                }
            }
            // Low priority: drop message
        }
    }
}
```

### Frontend: WebSocket Hook with Reconnection

```typescript
import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketOptions {
    reconnect?: boolean;
    reconnectAttempts?: number;
    reconnectInterval?: number;
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
}

type WebSocketStatus = 'connecting' | 'open' | 'closing' | 'closed';

export function useWebSocket<T>(
    url: string,
    onMessage: (data: T) => void,
    options: WebSocketOptions = {}
) {
    const {
        reconnect = true,
        reconnectAttempts = 5,
        reconnectInterval = 5000,
        onOpen,
        onClose,
        onError,
    } = options;

    const [status, setStatus] = useState<WebSocketStatus>('connecting');
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectCountRef = useRef(0);
    const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);

    const connect = useCallback(() => {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            setStatus('open');
            reconnectCountRef.current = 0;
            onOpen?.();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as T;
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            onError?.(error);
        };

        ws.onclose = () => {
            setStatus('closed');
            onClose?.();

            // Attempt reconnection
            if (reconnect && reconnectCountRef.current < reconnectAttempts) {
                reconnectCountRef.current++;
                const delay = reconnectInterval * Math.pow(1.5, reconnectCountRef.current - 1);

                reconnectTimerRef.current = setTimeout(() => {
                    setStatus('connecting');
                    connect();
                }, delay);
            }
        };
    }, [url, onMessage, reconnect, reconnectAttempts, reconnectInterval, onOpen, onClose, onError]);

    useEffect(() => {
        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
            if (reconnectTimerRef.current) {
                clearTimeout(reconnectTimerRef.current);
            }
        };
    }, [connect]);

    const sendMessage = useCallback((data: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        }
    }, []);

    const close = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
        }
    }, []);

    return { status, sendMessage, close };
}
```

---

## 3. Streaming JSON (NDJSON)

### Backend: Stream Large Export

```go
package handlers

import (
    "encoding/json"
    "fmt"
    "net/http"

    "github.com/labstack/echo/v4"
)

// StreamItems streams items as NDJSON
// GET /api/v1/projects/:projectId/items/stream
func (h *Handler) StreamItems(c echo.Context) error {
    projectID := c.Param("projectId")

    // Set headers
    c.Response().Header().Set("Content-Type", "application/x-ndjson")
    c.Response().Header().Set("Transfer-Encoding", "chunked")
    c.Response().WriteHeader(http.StatusOK)

    flusher, ok := c.Response().Writer.(http.Flusher)
    if !ok {
        return echo.NewHTTPError(http.StatusInternalServerError)
    }

    encoder := json.NewEncoder(c.Response().Writer)

    // Stream items in batches
    offset := 0
    batchSize := 100

    for {
        // Query batch
        items, err := h.itemRepo.GetItems(c.Request().Context(), projectID, offset, batchSize)
        if err != nil {
            return err
        }

        if len(items) == 0 {
            break
        }

        // Encode each item as NDJSON
        for _, item := range items {
            if err := encoder.Encode(item); err != nil {
                return err
            }
            flusher.Flush()
        }

        offset += batchSize

        // Check if client disconnected
        select {
        case <-c.Request().Context().Done():
            return nil
        default:
        }
    }

    return nil
}
```

### Frontend: NDJSON Consumer

```typescript
async function* streamNDJSON<T>(url: string): AsyncGenerator<T> {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                // Process remaining buffer
                if (buffer.trim()) {
                    yield JSON.parse(buffer);
                }
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');

            // Keep incomplete line in buffer
            buffer = lines.pop() || '';

            // Parse complete lines
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    yield JSON.parse(trimmed);
                }
            }
        }
    } finally {
        reader.releaseLock();
    }
}

// Usage: Export items to file
async function exportItems(projectId: string) {
    const items: Item[] = [];
    let count = 0;

    for await (const item of streamNDJSON<Item>(
        `/api/v1/projects/${projectId}/items/stream`
    )) {
        items.push(item);
        count++;

        // Update progress UI
        if (count % 100 === 0) {
            console.log(`Loaded ${count} items...`);
        }
    }

    // Download as JSON file
    const blob = new Blob([JSON.stringify(items, null, 2)], {
        type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `items-${projectId}.json`;
    a.click();
    URL.revokeObjectURL(url);
}
```

---

## 4. Database Streaming

### Cursor-Based Pagination (PostgreSQL)

```go
package repository

import (
    "context"
    "database/sql"
    "encoding/base64"
    "fmt"
    "strings"
    "time"

    "github.com/google/uuid"
)

type CursorParams struct {
    Cursor    string
    Limit     int
    Direction string // "forward" or "backward"
}

type ItemsPage struct {
    Items      []*Item `json:"items"`
    NextCursor *string `json:"next_cursor"`
    PrevCursor *string `json:"prev_cursor"`
    HasMore    bool    `json:"has_more"`
}

// GetItemsCursor retrieves items with cursor pagination
func (r *ItemRepository) GetItemsCursor(
    ctx context.Context,
    projectID uuid.UUID,
    params CursorParams,
) (*ItemsPage, error) {
    // Default limit
    if params.Limit == 0 {
        params.Limit = 50
    }
    if params.Limit > 500 {
        params.Limit = 500
    }

    // Decode cursor
    var cursorTime time.Time
    var cursorID uuid.UUID
    if params.Cursor != "" {
        decoded, err := base64.StdEncoding.DecodeString(params.Cursor)
        if err != nil {
            return nil, fmt.Errorf("invalid cursor: %w", err)
        }
        parts := strings.Split(string(decoded), "|")
        if len(parts) != 2 {
            return nil, fmt.Errorf("invalid cursor format")
        }
        cursorTime, _ = time.Parse(time.RFC3339, parts[0])
        cursorID, _ = uuid.Parse(parts[1])
    }

    // Build query
    query := `
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM items
        WHERE project_id = $1
    `
    args := []interface{}{projectID}
    argPos := 1

    // Add cursor condition
    if params.Cursor != "" {
        if params.Direction == "backward" {
            query += fmt.Sprintf(
                " AND (created_at > $%d OR (created_at = $%d AND id > $%d))",
                argPos+1, argPos+1, argPos+2,
            )
        } else {
            query += fmt.Sprintf(
                " AND (created_at < $%d OR (created_at = $%d AND id < $%d))",
                argPos+1, argPos+1, argPos+2,
            )
        }
        args = append(args, cursorTime, cursorID)
        argPos += 2
    }

    // Order and limit
    query += " ORDER BY created_at DESC, id DESC"
    query += fmt.Sprintf(" LIMIT $%d", argPos+1)
    args = append(args, params.Limit+1) // Fetch extra to check hasMore

    // Execute
    rows, err := r.db.QueryContext(ctx, query, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var items []*Item
    for rows.Next() {
        var item Item
        err := rows.Scan(
            &item.ID,
            &item.Title,
            &item.Description,
            &item.Status,
            &item.Priority,
            &item.CreatedAt,
            &item.UpdatedAt,
        )
        if err != nil {
            return nil, err
        }
        items = append(items, &item)
    }

    // Check for more items
    hasMore := len(items) > params.Limit
    if hasMore {
        items = items[:params.Limit]
    }

    // Build cursors
    var nextCursor, prevCursor *string
    if hasMore {
        lastItem := items[len(items)-1]
        cursor := encodeCursor(lastItem.CreatedAt, lastItem.ID)
        nextCursor = &cursor
    }
    if params.Cursor != "" && len(items) > 0 {
        firstItem := items[0]
        cursor := encodeCursor(firstItem.CreatedAt, firstItem.ID)
        prevCursor = &cursor
    }

    return &ItemsPage{
        Items:      items,
        NextCursor: nextCursor,
        PrevCursor: prevCursor,
        HasMore:    hasMore,
    }, nil
}

func encodeCursor(t time.Time, id uuid.UUID) string {
    cursor := fmt.Sprintf("%s|%s", t.Format(time.RFC3339), id.String())
    return base64.StdEncoding.EncodeToString([]byte(cursor))
}
```

---

## 5. Frontend Consumption

### Infinite Scroll with TanStack Query

```typescript
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';

interface ItemsPage {
    items: Item[];
    next_cursor?: string;
    has_more: boolean;
}

function useInfiniteItems(projectId: string) {
    return useInfiniteQuery({
        queryKey: ['items', projectId, 'infinite'],
        queryFn: async ({ pageParam }: { pageParam?: string }) => {
            const url = new URL(
                `/api/v1/projects/${projectId}/items`,
                window.location.origin
            );
            if (pageParam) {
                url.searchParams.set('cursor', pageParam);
            }
            url.searchParams.set('limit', '50');

            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to fetch items');
            return res.json() as Promise<ItemsPage>;
        },
        getNextPageParam: (lastPage) =>
            lastPage.has_more ? lastPage.next_cursor : undefined,
        staleTime: 5 * 60 * 1000,
    });
}

function InfiniteItemsList({ projectId }: { projectId: string }) {
    const parentRef = useRef<HTMLDivElement>(null);
    const {
        data,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
        isLoading,
    } = useInfiniteItems(projectId);

    const items = useMemo(
        () => data?.pages.flatMap((page) => page.items) ?? [],
        [data]
    );

    const virtualizer = useVirtualizer({
        count: hasNextPage ? items.length + 1 : items.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 60,
        overscan: 5,
    });

    useEffect(() => {
        const [lastItem] = [...virtualizer.getVirtualItems()].reverse();

        if (
            lastItem &&
            lastItem.index >= items.length - 10 &&
            hasNextPage &&
            !isFetchingNextPage
        ) {
            fetchNextPage();
        }
    }, [
        hasNextPage,
        fetchNextPage,
        items.length,
        isFetchingNextPage,
        virtualizer.getVirtualItems(),
    ]);

    if (isLoading) {
        return <Skeleton count={10} />;
    }

    return (
        <div ref={parentRef} className="h-full overflow-auto">
            <div style={{ height: virtualizer.getTotalSize() }}>
                {virtualizer.getVirtualItems().map((virtualRow) => (
                    <div
                        key={virtualRow.index}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: `${virtualRow.size}px`,
                            transform: `translateY(${virtualRow.start}px)`,
                        }}
                    >
                        {virtualRow.index >= items.length ? (
                            <Skeleton />
                        ) : (
                            <ItemRow item={items[virtualRow.index]} />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
```

---

## 6. Error Handling

### Backend: Graceful Stream Errors

```go
func (h *Handler) StreamWithRecovery(c echo.Context) error {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Recovered from panic in stream: %v", r)
        }
    }()

    // ... streaming logic ...

    for {
        select {
        case event := <-eventChan:
            if err := sendEvent(c, event); err != nil {
                // Log but continue streaming
                log.Printf("Failed to send event: %v", err)
                continue
            }

        case <-ctx.Done():
            return nil
        }
    }
}
```

### Frontend: Error Recovery

```typescript
function useResilientSSE(url: string) {
    const [error, setError] = useState<Error | null>(null);
    const [retryCount, setRetryCount] = useState(0);

    const { status } = useSSE(url, {
        onError: (err) => {
            setError(new Error('Connection failed'));
            setRetryCount(prev => prev + 1);

            // Max 5 retries
            if (retryCount >= 5) {
                toast.error('Failed to maintain connection', {
                    description: 'Please refresh the page',
                });
            }
        },
        reconnect: retryCount < 5,
    });

    return { status, error, retryCount };
}
```

---

## 7. Testing Strategies

### Backend: SSE Test

```go
func TestSSEStream(t *testing.T) {
    e := echo.New()
    req := httptest.NewRequest(http.MethodGet, "/stream", nil)
    rec := httptest.NewRecorder()
    c := e.NewContext(req, rec)

    go func() {
        handler.StreamEvents(c)
    }()

    time.Sleep(100 * time.Millisecond)

    assert.Equal(t, "text/event-stream", rec.Header().Get("Content-Type"))
    assert.Contains(t, rec.Body.String(), "data:")
}
```

### Frontend: WebSocket Test

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { WS } from 'jest-websocket-mock';

test('useWebSocket connects and receives messages', async () => {
    const server = new WS('ws://localhost:1234');
    const onMessage = vi.fn();

    const { result } = renderHook(() =>
        useWebSocket('ws://localhost:1234', onMessage)
    );

    await server.connected;

    server.send(JSON.stringify({ type: 'test', data: 'hello' }));

    await waitFor(() => {
        expect(onMessage).toHaveBeenCalledWith({ type: 'test', data: 'hello' });
    });

    expect(result.current.status).toBe('open');

    server.close();
});
```

---

## Best Practices

1. **Always use context cancellation** - Respect client disconnections
2. **Rate limit outgoing messages** - Prevent overwhelming clients
3. **Use keepalive/heartbeat** - Detect dead connections early
4. **Implement backpressure** - Drop messages if client can't keep up
5. **Log errors but continue** - Don't break stream on single error
6. **Test with slow clients** - Simulate network issues
7. **Monitor connection count** - Track active streams
8. **Set timeouts** - Prevent infinite hangs

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **SSE Connections** | 1,000+ | Per server |
| **WebSocket Connections** | 10,000+ | Per server |
| **Message Latency** | <50ms | 95th percentile |
| **Memory per Connection** | <50KB | SSE/WebSocket |
| **Throughput** | 1,000 msg/sec | Per connection |

---

## Next Steps

1. Implement SSE endpoints for notifications
2. Add cursor-based pagination to all list endpoints
3. Integrate NDJSON export for large datasets
4. Add monitoring for streaming connections
5. Create E2E tests for streaming features
