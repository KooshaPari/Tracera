# SSE Notifications Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐         ┌──────────────────┐                    │
│  │  React Hook    │────────>│  SSE Client      │                    │
│  │useNotifications│         │ (sse-client.ts)  │                    │
│  └────────────────┘         └──────────────────┘                    │
│         │                            │                               │
│         │ Initial Fetch              │ Persistent Connection         │
│         │ (REST API)                 │ (Server-Sent Events)          │
│         │                            │                               │
│         v                            v                               │
│  ┌────────────────────────────────────────────────┐                 │
│  │           React Query Cache                    │                 │
│  │  (Automatic updates from SSE events)           │                 │
│  └────────────────────────────────────────────────┘                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP/SSE
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                       SERVER LAYER (Go)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │              Echo HTTP Server                          │         │
│  │                                                         │         │
│  │  ┌──────────────────────────────────────────────────┐ │         │
│  │  │     Notification Handler                         │ │         │
│  │  │                                                   │ │         │
│  │  │  GET  /notifications         (List)              │ │         │
│  │  │  GET  /notifications/stream  (SSE) ◄─────┐       │ │         │
│  │  │  POST /notifications/:id/read (Mark Read)│       │ │         │
│  │  │  POST /notifications/read-all (Mark All) │       │ │         │
│  │  │  DELETE /notifications/:id    (Delete)   │       │ │         │
│  │  │  POST /notifications          (Create)   │       │ │         │
│  │  └──────────────────────────────────────────┘       │ │         │
│  │                       │                              │ │         │
│  └───────────────────────┼──────────────────────────────┘ │         │
│                          │                                 │         │
│                          v                                 │         │
│  ┌─────────────────────────────────────────────────────┐  │         │
│  │         Notification Service                        │  │         │
│  │                                                      │  │         │
│  │  • Create/Read/Update/Delete                        │  │         │
│  │  • Subscription Management (in-memory)              │  │         │
│  │  • Event Broadcasting                               │  │         │
│  │  • Auto Cleanup (expired notifications)             │  │         │
│  │                                                      │  │         │
│  │  ┌──────────────────────────────────────┐           │  │         │
│  │  │  Subscribers Map                     │           │  │         │
│  │  │  userID -> subscriberID -> channel   │           │  │         │
│  │  └──────────────────────────────────────┘           │  │         │
│  │                                                      │  │         │
│  └──────────────┬──────────────────┬────────────────────┘  │         │
│                 │                  │                        │         │
│                 v                  v                        │         │
│    ┌────────────────────┐  ┌──────────────────┐            │         │
│    │   PostgreSQL       │  │  Redis Pub/Sub   │            │         │
│    │   (GORM)           │  │                  │            │         │
│    │                    │  │  Channels:       │            │         │
│    │  notifications     │  │  notify:user-123 │            │         │
│    │  ├─ id (PK)        │  │  notify:user-456 │            │         │
│    │  ├─ user_id (idx)  │  │  ...             │            │         │
│    │  ├─ type           │  └──────────────────┘            │         │
│    │  ├─ title          │                                  │         │
│    │  ├─ message        │                                  │         │
│    │  ├─ link           │                                  │         │
│    │  ├─ read_at        │                                  │         │
│    │  ├─ created_at(idx)│                                  │         │
│    │  └─ expires_at(idx)│                                  │         │
│    └────────────────────┘                                  │         │
│                                                             │         │
└─────────────────────────────────────────────────────────────┘         │

```

## Event Flow

### 1. New Notification Creation

```
┌─────────┐      ┌─────────────┐      ┌──────────┐      ┌───────┐      ┌────────┐
│ Service │─────>│ Notification│─────>│PostgreSQL│      │ Redis │      │ Client │
│ (Create)│      │  Service    │      │          │      │Pub/Sub│      │ (SSE)  │
└─────────┘      └─────────────┘      └──────────┘      └───────┘      └────────┘
                        │                   │                 │              │
                        │ 1. Insert         │                 │              │
                        ├──────────────────>│                 │              │
                        │                   │                 │              │
                        │ 2. Publish Event  │                 │              │
                        ├───────────────────────────────────>│              │
                        │                   │                 │              │
                        │ 3. Broadcast      │                 │              │
                        ├─────────────────────────────────────────────────>│
                        │                   │                 │              │
                        │                   │                 │ 4. Update UI │
                        │                   │                 │<─────────────┤
```

### 2. SSE Connection Lifecycle

```
Client                  Server               Notification Service
  │                       │                          │
  │ 1. GET /stream        │                          │
  ├──────────────────────>│                          │
  │                       │                          │
  │                       │ 2. Subscribe             │
  │                       ├─────────────────────────>│
  │                       │                          │
  │                       │ 3. Return subscriber ID  │
  │                       │<─────────────────────────┤
  │                       │                          │
  │ 4. event: connected   │                          │
  │<──────────────────────┤                          │
  │                       │                          │
  │                       │ 5. Listen for events     │
  │                       │<─────────────────────────┤
  │                       │                          │
  │ 6. event: notification│                          │
  │<──────────────────────┤                          │
  │                       │                          │
  │ 7. event: ping (30s)  │                          │
  │<──────────────────────┤                          │
  │                       │                          │
  │ ... (repeated)        │                          │
  │                       │                          │
  │ 8. Close connection   │                          │
  ├──────────────────────>│                          │
  │                       │                          │
  │                       │ 9. Unsubscribe           │
  │                       ├─────────────────────────>│
  │                       │                          │
```

### 3. Multi-Instance Scaling

```
┌─────────────────────────────────────────────────────────────────┐
│                     Load Balancer                                │
└─────────────────────────────────────────────────────────────────┘
                     │                    │
        ┌────────────┴────────┐  ┌────────┴────────────┐
        │                     │  │                      │
┌───────▼────────┐    ┌───────▼────────┐  ┌───────────▼────────┐
│  Server 1      │    │  Server 2      │  │  Server 3          │
│                │    │                │  │                    │
│ SSE Clients:   │    │ SSE Clients:   │  │ SSE Clients:       │
│ • user-123     │    │ • user-456     │  │ • user-789         │
│ • user-111     │    │ • user-222     │  │ • user-333         │
└────────┬───────┘    └────────┬───────┘  └────────┬───────────┘
         │                     │                    │
         └─────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Redis Pub/Sub     │
                    │                     │
                    │ Channels:           │
                    │ • notifications:*   │
                    │                     │
                    │ All servers         │
                    │ receive all events  │
                    │ and broadcast to    │
                    │ their local clients │
                    └─────────────────────┘
```

## Reconnection Flow

```
Client SSE Library                   Server
      │                                │
      │ 1. Initial Connect             │
      ├───────────────────────────────>│
      │                                │
      │ 2. Connection Established      │
      │<───────────────────────────────┤
      │                                │
      │ 3. Network Error! ✗            │
      │                                │
      │ 4. Reconnect (delay: 1s)       │
      ├───────────────────────────────>│
      │                                │
      │ 5. Failed! ✗                   │
      │                                │
      │ 6. Reconnect (delay: 2s)       │
      ├───────────────────────────────>│
      │                                │
      │ 7. Failed! ✗                   │
      │                                │
      │ 8. Reconnect (delay: 4s)       │
      ├───────────────────────────────>│
      │                                │
      │ 9. Success! ✓                  │
      │<───────────────────────────────┤
      │                                │
      │ Reset delay to 1s              │
      │                                │
```

## Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      Notification Lifecycle                     │
└────────────────────────────────────────────────────────────────┘

1. CREATE
   System/Admin ──> POST /notifications ──> Service.Create()
                                              │
                                              ├──> DB.Insert()
                                              │
                                              ├──> Redis.Publish()
                                              │
                                              └──> SSE.Broadcast() ──> All Clients

2. READ
   Client ──> GET /notifications ──> Service.List() ──> DB.Query()
                                                         │
                                                         └──> Filter by user_id

3. UPDATE (Mark as Read)
   Client ──> POST /notifications/:id/read ──> Service.MarkAsRead()
                                                 │
                                                 ├──> DB.Update()
                                                 │
                                                 ├──> Redis.Publish()
                                                 │
                                                 └──> SSE.Broadcast() ──> All Clients

4. DELETE
   Client ──> DELETE /notifications/:id ──> Service.Delete()
                                              │
                                              ├──> DB.Delete()
                                              │
                                              ├──> Redis.Publish()
                                              │
                                              └──> SSE.Broadcast() ──> All Clients

5. STREAM (Real-time)
   Client ──> GET /notifications/stream ──> Handler.StreamNotifications()
                                              │
                                              ├──> Service.Subscribe()
                                              │
                                              └──> Keep connection open
                                                   │
                                                   └──> Send events as they occur
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Components                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  NotificationBell.tsx                                             │
│  └──> useNotifications()                                          │
│        ├──> Initial fetch (REST)                                  │
│        ├──> SSE connection (real-time)                            │
│        └──> React Query cache (auto-update)                       │
│                                                                   │
│  NotificationPanel.tsx                                            │
│  └──> useNotifications()                                          │
│        └──> Same cache, instant sync                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ Shared Cache
                               │
┌─────────────────────────────────────────────────────────────────┐
│                  React Query QueryClient                         │
│                                                                   │
│  ["notifications"] = [                                            │
│    { id: "1", title: "...", read_at: null },                     │
│    { id: "2", title: "...", read_at: "2026-02-01..." },          │
│    ...                                                            │
│  ]                                                                │
│                                                                   │
│  Auto-updated by SSE events                                      │
│  No manual invalidation needed                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Legend

- `───>` : HTTP Request
- `<───` : HTTP Response
- `━━━>` : SSE Stream
- `├──>` : Internal Method Call
- `└──>` : Final Action
- `◄───` : Persistent Connection
- `✗` : Failed
- `✓` : Success

## Key Architectural Decisions

1. **Redis Pub/Sub**: Enables horizontal scaling across multiple server instances
2. **In-Memory Subscriptions**: Fast local broadcasting without database queries
3. **SSE over WebSocket**: Simpler protocol, built-in browser support, automatic reconnection
4. **React Query Cache**: Automatic state management, no manual synchronization
5. **Exponential Backoff**: Prevents server overload during outages
6. **Keep-Alive Pings**: Maintains connection through proxies and firewalls
