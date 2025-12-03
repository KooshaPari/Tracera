# NATS Technical Architecture for Trace
## Distributed Event Coordination & Agent Orchestration

**Document Version**: 1.0.0
**Date**: 2025-11-20
**Purpose**: Detailed NATS integration design for 1000+ agent orchestration

---

## 1. Executive Summary

This document provides implementation-level details for integrating NATS as the event coordination layer for the trace multi-view PM system. NATS will handle:

- **Event Distribution**: Pub/Sub for item changes across 16 views
- **Task Orchestration**: JetStream work queues for DAG execution
- **State Management**: KV store for distributed state
- **Agent Coordination**: Request/Reply for agent synchronization
- **Audit Trail**: JetStream persistence for immutable event log

### Why NATS Over Redis

| Feature | NATS JetStream | Redis | Winner |
|---------|----------------|-------|--------|
| Message Delivery | At-least-once, exactly-once | At-most-once | **NATS** |
| Persistence | Built-in JetStream | Requires AOF/RDB | **NATS** |
| Horizontal Scaling | Native clustering | Complex sharding | **NATS** |
| Work Queues | Pull consumers, queue groups | Requires Lua scripts | **NATS** |
| Request/Reply | Built-in pattern | Pub/Sub workaround | **NATS** |
| Operational Complexity | Lower | Higher | **NATS** |
| Perfect for DAG Coordination | ✅ | ❌ | **NATS** |

---

## 2. NATS Cluster Architecture

### 2.1 Cluster Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        trace Clients                             │
│  (CLI, TUI, Agent Workers, Verification Services)                │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼────────┐ ┌───▼────────┐
│  NATS Node 1    │ │  NATS      │ │  NATS      │
│  (Leader)       │ │  Node 2    │ │  Node 3    │
│  - JetStream    │ │  - JetStream│ │  - JetStream│
│  - KV Store     │ │  - KV Store │ │  - KV Store │
└────────┬────────┘ └───┬────────┘ └───┬────────┘
         │               │               │
         │    Cluster Gossip Protocol    │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼────────────────┐
         │    JetStream Storage Backend    │
         │    (File-based, replicated)     │
         └─────────────────────────────────┘
```

### 2.2 Configuration

```yaml
# nats-server.conf
port: 4222
server_name: trace-nats-1

# Cluster configuration for HA
cluster {
  name: trace-cluster
  listen: 0.0.0.0:6222
  routes: [
    nats://trace-nats-1:6222
    nats://trace-nats-2:6222
    nats://trace-nats-3:6222
  ]
}

# JetStream configuration
jetstream {
  store_dir: /data/jetstream
  max_memory_store: 1GB
  max_file_store: 10GB
}

# Monitoring
http_port: 8222

# Logging
debug: false
trace: false
logfile: /var/log/nats/nats-server.log
```

---

## 3. JetStream Stream Design

### 3.1 Stream Hierarchy

```
TRACE
├── TRACE_EVENTS          # All item change events
│   ├── TRACE_EVENTS.feature.*
│   ├── TRACE_EVENTS.code.*
│   ├── TRACE_EVENTS.test.*
│   └── ... (all 16 views)
│
├── TRACE_COMMITS         # Version control commits
│   ├── TRACE_COMMITS.created
│   ├── TRACE_COMMITS.merged
│   └── TRACE_COMMITS.tagged
│
├── TRACE_TASKS           # Work queue for DAG tasks
│   ├── TRACE_TASKS.execution.*
│   ├── TRACE_TASKS.verification.*
│   └── TRACE_TASKS.analysis.*
│
├── TRACE_VERIFICATION    # Verification results
│   ├── TRACE_VERIFICATION.nl_assertion
│   ├── TRACE_VERIFICATION.formal
│   └── TRACE_VERIFICATION.hybrid
│
└── TRACE_AUDIT           # Immutable audit trail
    ├── TRACE_AUDIT.proofs
    └── TRACE_AUDIT.approvals
```

### 3.2 Stream Configurations

```python
# Stream configurations
STREAM_CONFIGS = {
    'TRACE_EVENTS': {
        'subjects': ['TRACE_EVENTS.>'],
        'retention': 'limits',  # Retain based on limits
        'max_age': timedelta(days=365),  # 1 year retention
        'storage': 'file',  # File-based storage
        'replicas': 3,  # 3-way replication for HA
        'max_msgs': 10_000_000,
        'max_bytes': 10 * 1024 * 1024 * 1024,  # 10 GB
        'discard': 'old',  # Discard old when limit reached
        'duplicate_window': timedelta(minutes=2)  # Deduplication
    },
    'TRACE_COMMITS': {
        'subjects': ['TRACE_COMMITS.>'],
        'retention': 'limits',
        'max_age': None,  # Keep forever
        'storage': 'file',
        'replicas': 3,
        'max_msgs': 1_000_000,
        'max_bytes': 1 * 1024 * 1024 * 1024,  # 1 GB
        'discard': 'old'
    },
    'TRACE_TASKS': {
        'subjects': ['TRACE_TASKS.>'],
        'retention': 'work_queue',  # Work queue retention
        'max_age': timedelta(hours=24),  # Tasks older than 24h deleted
        'storage': 'file',
        'replicas': 3,
        'max_msgs': 100_000,
        'max_bytes': 100 * 1024 * 1024,  # 100 MB
        'discard': 'old'
    },
    'TRACE_VERIFICATION': {
        'subjects': ['TRACE_VERIFICATION.>'],
        'retention': 'limits',
        'max_age': timedelta(days=90),
        'storage': 'file',
        'replicas': 3,
        'max_msgs': 1_000_000,
        'discard': 'old'
    },
    'TRACE_AUDIT': {
        'subjects': ['TRACE_AUDIT.>'],
        'retention': 'limits',
        'max_age': None,  # Keep forever
        'storage': 'file',
        'replicas': 3,
        'max_msgs': 10_000_000,
        'max_bytes': 5 * 1024 * 1024 * 1024,  # 5 GB
        'discard': 'new'  # Never discard - fail if full
    }
}

class NATSStreamManager:
    """Manage JetStream streams for trace"""

    async def initialize_streams(self):
        """Create all required streams"""
        js = self.nats.jetstream()

        for stream_name, config in STREAM_CONFIGS.items():
            try:
                await js.add_stream(
                    name=stream_name,
                    subjects=config['subjects'],
                    retention=config['retention'],
                    max_age=config['max_age'],
                    storage=config['storage'],
                    num_replicas=config['replicas'],
                    max_msgs=config['max_msgs'],
                    max_bytes=config['max_bytes'],
                    discard=config['discard'],
                    duplicate_window=config.get('duplicate_window', timedelta(minutes=2))
                )
                logger.info(f"Stream {stream_name} created successfully")
            except Exception as e:
                logger.error(f"Failed to create stream {stream_name}: {e}")
```

---

## 4. Message Schemas

### 4.1 Event Message Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum

class EventType(str, Enum):
    """Event types for TRACE_EVENTS stream"""
    ITEM_CREATED = "item.created"
    ITEM_UPDATED = "item.updated"
    ITEM_DELETED = "item.deleted"
    LINK_CREATED = "link.created"
    LINK_DELETED = "link.deleted"
    ATTRIBUTE_CHANGED = "attribute.changed"

class EventMessage(BaseModel):
    """Schema for events published to TRACE_EVENTS"""
    event_id: UUID = Field(description="Unique event identifier")
    event_type: EventType
    aggregate_id: UUID = Field(description="ID of item that changed")
    aggregate_type: str = Field(description="View type (feature, code, etc)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    author: str = Field(description="User or agent that made change")
    commit_id: Optional[str] = Field(description="Commit hash if committed")

    # Event payload
    data: Dict[str, Any] = Field(description="Change details")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Causality tracking
    causation_id: Optional[UUID] = Field(description="Command that caused this event")
    correlation_id: Optional[UUID] = Field(description="Trace across related events")

    # Versioning
    version: int = Field(description="Event version for schema evolution")

class EventPublisher:
    """Publish events to NATS"""

    async def publish_event(self, event: EventMessage):
        """Publish event with deduplication"""
        subject = f"TRACE_EVENTS.{event.aggregate_type}.{event.event_type}"

        # Serialize to msgpack for efficiency
        payload = msgpack.packb(event.dict())

        # Publish with message ID for deduplication
        await self.js.publish(
            subject=subject,
            payload=payload,
            headers={
                'Nats-Msg-Id': str(event.event_id),  # Deduplication
                'Content-Type': 'application/msgpack',
                'Event-Type': event.event_type,
                'Aggregate-Type': event.aggregate_type
            }
        )
```

### 4.2 Task Message Schema

```python
class TaskType(str, Enum):
    """Task types for TRACE_TASKS stream"""
    EXECUTION = "execution"       # Execute code/command
    VERIFICATION = "verification" # Verify acceptance criterion
    ANALYSIS = "analysis"         # Analyze code/metrics
    SYNTHESIS = "synthesis"       # Generate artifacts

class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"  # Execute immediately
    HIGH = "high"         # Execute soon
    NORMAL = "normal"     # Standard priority
    LOW = "low"          # Execute when idle

class TaskMessage(BaseModel):
    """Schema for tasks published to TRACE_TASKS"""
    task_id: UUID
    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL

    # Task definition
    operation: str = Field(description="Operation to execute")
    params: Dict[str, Any] = Field(description="Operation parameters")

    # Dependencies
    depends_on: List[UUID] = Field(default_factory=list, description="Task IDs this depends on")

    # Execution metadata
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=300)
    assigned_agent: Optional[str] = Field(description="Agent ID if pre-assigned")

    # Context
    context: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: UUID = Field(description="Trace related tasks")

class TaskPublisher:
    """Publish tasks for distributed execution"""

    async def schedule_task(self, task: TaskMessage):
        """Schedule task for execution"""
        subject = f"TRACE_TASKS.{task.task_type}.{task.priority}"

        payload = msgpack.packb(task.dict())

        # Publish with expected stream for acknowledgment tracking
        ack = await self.js.publish(
            subject=subject,
            payload=payload,
            stream='TRACE_TASKS'
        )

        # Store task in KV for status tracking
        await self.js.kv.put(
            bucket='task_status',
            key=str(task.task_id),
            value=msgpack.packb({
                'status': 'scheduled',
                'published_at': datetime.utcnow().isoformat(),
                'sequence': ack.seq
            })
        )
```

### 4.3 Verification Message Schema

```python
class VerificationStatus(str, Enum):
    """Verification status"""
    PASS = "pass"
    FAIL = "fail"
    UNCERTAIN = "uncertain"
    ERROR = "error"

class VerificationMessage(BaseModel):
    """Schema for verification results"""
    verification_id: UUID
    criterion_id: str
    story_id: str

    # Result
    status: VerificationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

    # Method used
    method: str = Field(description="nl_assertion, formal, hybrid")

    # Proof
    proof_hash: str
    signature: str
    merkle_proof: Optional[List[Tuple[str, str]]]

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    verifier: str = Field(description="Agent or system that verified")
    duration_ms: int

class VerificationPublisher:
    """Publish verification results"""

    async def publish_result(self, result: VerificationMessage):
        """Publish verification result with proof"""
        subject = f"TRACE_VERIFICATION.{result.method}"

        payload = msgpack.packb(result.dict())

        # Publish to verification stream
        await self.js.publish(
            subject=subject,
            payload=payload,
            stream='TRACE_VERIFICATION'
        )

        # Also publish to audit stream for immutability
        await self.js.publish(
            subject='TRACE_AUDIT.proofs',
            payload=payload,
            stream='TRACE_AUDIT'
        )
```

---

## 5. Consumer Patterns

### 5.1 Push Consumer (Real-Time Event Subscribers)

```python
class EventStreamSubscriber:
    """Subscribe to events for real-time updates"""

    async def subscribe_to_view(
        self,
        view_type: ViewType,
        callback: Callable[[EventMessage], Awaitable[None]]
    ):
        """
        Subscribe to all events for a specific view

        Use push consumer for real-time updates in UI/CLI
        """
        subject = f"TRACE_EVENTS.{view_type}.>"

        # Create push consumer
        consumer = await self.js.subscribe(
            subject=subject,
            stream='TRACE_EVENTS',
            durable=f"ui_subscriber_{view_type}",
            deliver_policy='last',  # Start from latest
            flow_control=True,
            idle_heartbeat=timedelta(seconds=30)
        )

        # Process messages
        async for msg in consumer.messages:
            try:
                # Deserialize
                event_data = msgpack.unpackb(msg.data)
                event = EventMessage(**event_data)

                # Invoke callback
                await callback(event)

                # Ack message
                await msg.ack()

            except Exception as e:
                logger.error(f"Failed to process event: {e}")
                await msg.nak(delay=5)  # Retry after 5 seconds

# Usage
async def on_feature_updated(event: EventMessage):
    """Handle feature update events"""
    print(f"Feature {event.aggregate_id} updated: {event.data}")

subscriber = EventStreamSubscriber(nats_client)
await subscriber.subscribe_to_view(ViewType.FEATURE, on_feature_updated)
```

### 5.2 Pull Consumer (Worker Pool for Tasks)

```python
class TaskWorkerPool:
    """Worker pool for executing tasks from TRACE_TASKS queue"""

    def __init__(self, num_workers: int = 10):
        self.num_workers = num_workers
        self.workers: List[asyncio.Task] = []

    async def start(self):
        """Start worker pool"""
        # Create durable pull consumer
        consumer_config = {
            'durable_name': 'task_worker_pool',
            'deliver_policy': 'all',
            'ack_policy': 'explicit',
            'ack_wait': timedelta(minutes=5),  # 5 min to complete
            'max_deliver': 3,  # Max 3 attempts
            'filter_subject': 'TRACE_TASKS.>',
        }

        consumer = await self.js.pull_subscribe(
            subject='TRACE_TASKS.>',
            stream='TRACE_TASKS',
            **consumer_config
        )

        # Start worker coroutines
        for i in range(self.num_workers):
            worker = asyncio.create_task(
                self._worker_loop(f"worker-{i}", consumer)
            )
            self.workers.append(worker)

        logger.info(f"Started {self.num_workers} task workers")

    async def _worker_loop(self, worker_id: str, consumer):
        """Worker loop: fetch and execute tasks"""
        while True:
            try:
                # Fetch next batch (1 task at a time for this worker)
                msgs = await consumer.fetch(batch=1, timeout=30)

                for msg in msgs:
                    await self._process_task(worker_id, msg)

            except asyncio.TimeoutError:
                # No tasks available - continue waiting
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)

    async def _process_task(self, worker_id: str, msg):
        """Process a single task"""
        try:
            # Deserialize task
            task_data = msgpack.unpackb(msg.data)
            task = TaskMessage(**task_data)

            logger.info(f"Worker {worker_id} processing task {task.task_id}")

            # Update status to in_progress
            await self.js.kv.put(
                bucket='task_status',
                key=str(task.task_id),
                value=msgpack.packb({
                    'status': 'in_progress',
                    'worker_id': worker_id,
                    'started_at': datetime.utcnow().isoformat()
                })
            )

            # Execute task with timeout
            result = await asyncio.wait_for(
                self._execute_task(task),
                timeout=task.timeout_seconds
            )

            # Update status to completed
            await self.js.kv.put(
                bucket='task_status',
                key=str(task.task_id),
                value=msgpack.packb({
                    'status': 'completed',
                    'result': result,
                    'completed_at': datetime.utcnow().isoformat()
                })
            )

            # Publish result
            await self.js.publish(
                subject=f"TRACE_EVENTS.task.completed",
                payload=msgpack.packb({
                    'task_id': str(task.task_id),
                    'result': result
                })
            )

            # Ack message
            await msg.ack()

        except asyncio.TimeoutError:
            logger.error(f"Task {task.task_id} timed out")
            await msg.nak(delay=60)  # Retry after 1 minute
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            await msg.nak(delay=30)  # Retry after 30 seconds

    async def _execute_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Execute task based on type"""
        if task.task_type == TaskType.EXECUTION:
            return await self._execute_code(task)
        elif task.task_type == TaskType.VERIFICATION:
            return await self._verify_criterion(task)
        elif task.task_type == TaskType.ANALYSIS:
            return await self._analyze_code(task)
        elif task.task_type == TaskType.SYNTHESIS:
            return await self._synthesize_artifact(task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
```

---

## 6. KV Store Usage

### 6.1 State Management

```python
class DistributedStateManager:
    """Manage distributed state using NATS KV"""

    async def initialize_buckets(self):
        """Create KV buckets for different state types"""
        buckets = {
            'task_status': {
                'ttl': timedelta(hours=24),  # Tasks cleaned up after 24h
                'max_value_size': 10 * 1024,  # 10KB max
                'history': 5,  # Keep 5 versions
                'replicas': 3
            },
            'agent_presence': {
                'ttl': timedelta(minutes=5),  # Heartbeat-based
                'max_value_size': 1 * 1024,  # 1KB max
                'history': 1,  # Only current
                'replicas': 3
            },
            'execution_state': {
                'ttl': timedelta(hours=1),
                'max_value_size': 100 * 1024,  # 100KB max
                'history': 10,  # Keep 10 versions
                'replicas': 3
            },
            'cache': {
                'ttl': timedelta(minutes=15),  # Short-lived cache
                'max_value_size': 1 * 1024 * 1024,  # 1MB max
                'history': 1,
                'replicas': 1  # No replication for cache
            }
        }

        for bucket_name, config in buckets.items():
            await self.js.create_key_value(
                bucket=bucket_name,
                ttl=config['ttl'],
                max_value_size=config['max_value_size'],
                history=config['history'],
                replicas=config['replicas']
            )

    async def set_agent_presence(self, agent_id: str, info: Dict[str, Any]):
        """Register agent presence (heartbeat)"""
        await self.js.kv.put(
            bucket='agent_presence',
            key=agent_id,
            value=msgpack.packb({
                'agent_id': agent_id,
                'status': 'active',
                'last_heartbeat': datetime.utcnow().isoformat(),
                **info
            })
        )

    async def get_active_agents(self) -> List[str]:
        """Get list of active agents"""
        keys = await self.js.kv.keys(bucket='agent_presence')
        return keys
```

### 6.2 Distributed Locking

```python
class DistributedLock:
    """Distributed lock using NATS KV"""

    def __init__(self, lock_name: str, ttl: timedelta = timedelta(seconds=30)):
        self.lock_name = lock_name
        self.ttl = ttl
        self.lock_id = str(uuid4())

    async def __aenter__(self):
        """Acquire lock"""
        acquired = False
        while not acquired:
            try:
                # Try to create lock key
                await self.js.kv.create(
                    bucket='locks',
                    key=self.lock_name,
                    value=msgpack.packb({
                        'lock_id': self.lock_id,
                        'acquired_at': datetime.utcnow().isoformat(),
                        'acquired_by': os.getpid()
                    })
                )
                acquired = True
            except nats.js.errors.KeyExistsError:
                # Lock already held - wait and retry
                await asyncio.sleep(0.1)

        # Start heartbeat to maintain lock
        self.heartbeat_task = asyncio.create_task(self._heartbeat())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock"""
        # Cancel heartbeat
        self.heartbeat_task.cancel()

        # Delete lock key
        await self.js.kv.delete(
            bucket='locks',
            key=self.lock_name
        )

    async def _heartbeat(self):
        """Maintain lock with periodic updates"""
        while True:
            await asyncio.sleep(self.ttl.total_seconds() / 2)
            try:
                await self.js.kv.put(
                    bucket='locks',
                    key=self.lock_name,
                    value=msgpack.packb({
                        'lock_id': self.lock_id,
                        'heartbeat_at': datetime.utcnow().isoformat()
                    })
                )
            except Exception as e:
                logger.error(f"Failed to heartbeat lock {self.lock_name}: {e}")
                break

# Usage
async with DistributedLock('commit_graph') as lock:
    # Perform critical section
    await update_commit_graph()
```

---

## 7. DAG Execution with NATS

### 7.1 Complete DAG Execution System

```python
class NATSDAGExecutor:
    """Execute task DAGs using NATS for coordination"""

    async def execute_dag(
        self,
        dag: TaskDAG,
        max_parallel: int = 10
    ) -> DAGExecutionResult:
        """
        Execute DAG with dependency resolution

        Architecture:
        1. Store DAG metadata in KV
        2. Publish ready tasks to work queue
        3. Workers pull and execute tasks
        4. On completion, check for newly ready tasks
        5. Repeat until DAG complete
        """
        execution_id = uuid4()

        # Store DAG in KV
        await self._store_dag(execution_id, dag)

        # Initialize execution state
        state = ExecutionState(
            execution_id=execution_id,
            dag=dag,
            completed=set(),
            failed=set(),
            in_progress=set()
        )

        # Store initial state
        await self._update_state(state)

        # Publish ready tasks
        ready_tasks = dag.get_ready_tasks()
        for task_id in ready_tasks:
            await self._schedule_task(execution_id, task_id, state)

        # Subscribe to completion events
        completion_sub = await self.nats.subscribe(
            f"TRACE_EVENTS.task.completed.{execution_id}"
        )

        # Wait for completion
        async for msg in completion_sub.messages:
            completion_data = msgpack.unpackb(msg.data)
            task_id = UUID(completion_data['task_id'])

            # Update state
            state.completed.add(task_id)
            state.in_progress.discard(task_id)
            await self._update_state(state)

            # Check for newly ready tasks
            newly_ready = dag.get_newly_ready_tasks(
                completed=state.completed,
                failed=state.failed
            )

            for new_task_id in newly_ready:
                await self._schedule_task(execution_id, new_task_id, state)

            # Check if complete
            if state.is_complete():
                break

        return DAGExecutionResult(
            execution_id=execution_id,
            success=len(state.failed) == 0,
            completed=state.completed,
            failed=state.failed,
            duration=state.elapsed_time()
        )

    async def _schedule_task(
        self,
        execution_id: UUID,
        task_id: UUID,
        state: ExecutionState
    ):
        """Schedule task for execution"""
        task = state.dag.get_task(task_id)

        # Create task message
        task_msg = TaskMessage(
            task_id=task_id,
            task_type=task.type,
            priority=task.priority,
            operation=task.operation,
            params=task.params,
            depends_on=task.dependencies,
            correlation_id=execution_id
        )

        # Publish to work queue
        await self.task_publisher.schedule_task(task_msg)

        # Update state
        state.in_progress.add(task_id)
        await self._update_state(state)
```

### 7.2 Dependency Resolution

```python
class DAGDependencyResolver:
    """Resolve task dependencies using NATS KV"""

    async def check_dependencies_ready(
        self,
        task_id: UUID,
        dependencies: List[UUID]
    ) -> bool:
        """Check if all dependencies are completed"""
        for dep_id in dependencies:
            status = await self.js.kv.get(
                bucket='task_status',
                key=str(dep_id)
            )

            if not status:
                return False

            status_data = msgpack.unpackb(status.value)
            if status_data['status'] != 'completed':
                return False

        return True

    async def get_dependency_results(
        self,
        dependencies: List[UUID]
    ) -> Dict[UUID, Any]:
        """Get results from dependency tasks"""
        results = {}

        for dep_id in dependencies:
            status = await self.js.kv.get(
                bucket='task_status',
                key=str(dep_id)
            )

            if status:
                status_data = msgpack.unpackb(status.value)
                results[dep_id] = status_data.get('result')

        return results
```

---

## 8. Request/Reply for Coordination

### 8.1 Agent Coordination Pattern

```python
class AgentCoordinator:
    """Coordinate agents using request/reply pattern"""

    async def request_agent_action(
        self,
        agent_id: str,
        action: str,
        params: Dict[str, Any],
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Send request to specific agent and wait for reply

        Subject pattern: agent.{agent_id}.{action}
        """
        subject = f"agent.{agent_id}.{action}"

        request_data = msgpack.packb({
            'action': action,
            'params': params,
            'request_id': str(uuid4()),
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            # Send request and wait for reply
            response = await self.nats.request(
                subject=subject,
                payload=request_data,
                timeout=timeout_seconds
            )

            return msgpack.unpackb(response.data)

        except asyncio.TimeoutError:
            raise AgentTimeoutError(f"Agent {agent_id} did not respond")

class AgentService:
    """Agent that handles requests"""

    async def start(self, agent_id: str):
        """Start agent and listen for requests"""
        # Subscribe to agent-specific subject
        await self.nats.subscribe(
            subject=f"agent.{agent_id}.>",
            cb=self._handle_request
        )

    async def _handle_request(self, msg):
        """Handle incoming request"""
        request_data = msgpack.unpackb(msg.data)

        # Extract action
        action = request_data['action']
        params = request_data['params']

        # Execute action
        try:
            result = await self._execute_action(action, params)

            # Send reply
            response = msgpack.packb({
                'success': True,
                'result': result
            })

        except Exception as e:
            response = msgpack.packb({
                'success': False,
                'error': str(e)
            })

        # Reply to original subject
        await msg.respond(response)
```

---

## 9. Performance Optimization

### 9.1 Message Batching

```python
class BatchPublisher:
    """Batch messages for efficient publishing"""

    def __init__(self, max_batch_size: int = 100, flush_interval: float = 1.0):
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.pending: List[Tuple[str, bytes]] = []
        self.flush_task = None

    async def publish(self, subject: str, payload: bytes):
        """Add message to batch"""
        self.pending.append((subject, payload))

        if len(self.pending) >= self.max_batch_size:
            await self._flush()
        elif not self.flush_task:
            self.flush_task = asyncio.create_task(self._auto_flush())

    async def _flush(self):
        """Flush pending messages"""
        if not self.pending:
            return

        # Publish all pending messages
        for subject, payload in self.pending:
            await self.js.publish(subject, payload)

        self.pending.clear()

        if self.flush_task:
            self.flush_task.cancel()
            self.flush_task = None

    async def _auto_flush(self):
        """Auto-flush after interval"""
        await asyncio.sleep(self.flush_interval)
        await self._flush()
```

### 9.2 Connection Pooling

```python
class NATSConnectionPool:
    """Pool of NATS connections for high throughput"""

    def __init__(self, servers: List[str], pool_size: int = 10):
        self.servers = servers
        self.pool_size = pool_size
        self.connections: List[nats.NATS] = []
        self.current_index = 0

    async def initialize(self):
        """Create connection pool"""
        for i in range(self.pool_size):
            nc = await nats.connect(servers=self.servers)
            self.connections.append(nc)

    def get_connection(self) -> nats.NATS:
        """Get connection from pool (round-robin)"""
        conn = self.connections[self.current_index]
        self.current_index = (self.current_index + 1) % self.pool_size
        return conn
```

---

## 10. Monitoring & Observability

### 10.1 Metrics Collection

```python
class NATSMetricsCollector:
    """Collect NATS metrics for monitoring"""

    async def collect_stream_metrics(self) -> Dict[str, Any]:
        """Collect JetStream metrics"""
        metrics = {}

        for stream_name in ['TRACE_EVENTS', 'TRACE_COMMITS', 'TRACE_TASKS']:
            stream_info = await self.js.stream_info(stream_name)

            metrics[stream_name] = {
                'messages': stream_info.state.messages,
                'bytes': stream_info.state.bytes,
                'first_seq': stream_info.state.first_seq,
                'last_seq': stream_info.state.last_seq,
                'consumer_count': stream_info.state.consumer_count,
                'first_ts': stream_info.state.first_ts,
                'last_ts': stream_info.state.last_ts
            }

        return metrics

    async def collect_kv_metrics(self) -> Dict[str, Any]:
        """Collect KV bucket metrics"""
        metrics = {}

        for bucket_name in ['task_status', 'agent_presence', 'execution_state']:
            status = await self.js.kv.status(bucket_name)

            metrics[bucket_name] = {
                'values': status.values,
                'history': status.history,
                'ttl': status.ttl
            }

        return metrics
```

---

## 11. Deployment Configurations

### 11.1 Local Development

```bash
# Start single NATS server with JetStream
nats-server -js -m 8222

# Or with Docker
docker run -p 4222:4222 -p 8222:8222 nats:latest -js -m 8222
```

### 11.2 Production Cluster

```yaml
# docker-compose.yml for 3-node cluster
version: '3.8'
services:
  nats-1:
    image: nats:latest
    command: ["-js", "-m", "8222", "--cluster_name", "trace-cluster", "--cluster", "nats://0.0.0.0:6222", "--routes", "nats://nats-2:6222,nats://nats-3:6222"]
    ports:
      - "4222:4222"
      - "8222:8222"
    volumes:
      - ./nats-data-1:/data

  nats-2:
    image: nats:latest
    command: ["-js", "-m", "8223", "--cluster_name", "trace-cluster", "--cluster", "nats://0.0.0.0:6222", "--routes", "nats://nats-1:6222,nats://nats-3:6222"]
    ports:
      - "4223:4222"
      - "8223:8222"
    volumes:
      - ./nats-data-2:/data

  nats-3:
    image: nats:latest
    command: ["-js", "-m", "8224", "--cluster_name", "trace-cluster", "--cluster", "nats://0.0.0.0:6222", "--routes", "nats://nats-1:6222,nats://nats-2:6222"]
    ports:
      - "4224:4222"
      - "8224:8222"
    volumes:
      - ./nats-data-3:/data
```

---

## 12. Summary: NATS Integration Benefits

### 12.1 For Agent Orchestration

✅ **Native Work Queues**: Pull consumers with automatic load balancing
✅ **Dependency Resolution**: KV store for task dependencies
✅ **Exactly-Once Delivery**: JetStream guarantees for critical operations
✅ **Request/Reply**: Built-in coordination between agents
✅ **Presence Tracking**: KV with TTL for agent heartbeats

### 12.2 For Event Sourcing

✅ **Immutable Event Log**: JetStream with unlimited retention
✅ **Event Replay**: Replay from any point in history
✅ **Event Deduplication**: Built-in message deduplication
✅ **Stream Replication**: 3-way replication for HA
✅ **Audit Trail**: Separate stream with no discard policy

### 12.3 For Performance

✅ **Horizontal Scaling**: Add more NATS nodes for throughput
✅ **Message Batching**: Efficient bulk operations
✅ **Connection Pooling**: Multiple connections for parallelism
✅ **Low Latency**: Sub-millisecond message delivery
✅ **High Throughput**: Millions of messages per second

This NATS-based architecture provides a production-ready foundation for orchestrating 1000+ agents with robust event coordination, distributed task execution, and immutable audit trails.
