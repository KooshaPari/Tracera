# Kimaki Codebase Analysis - Consolidation Opportunities with Pheno-SDK

## Executive Summary

Kimaki is a Discord bot for agent orchestration with voice capabilities, built in **TypeScript/JavaScript** (30,328 LOC across 115 source files). The codebase demonstrates sophisticated patterns in multi-provider voice processing, real-time communication, and multi-agent coordination. PhenoSDK is a Python framework (186,641 LOC) providing enterprise infrastructure, observability, resilience, and database layers.

**Key Finding**: These are fundamentally different technology stacks (TS/JS vs Python) serving different domains, but several architectural patterns and concepts could be consolidated at the abstraction level.

---

## 1. Codebase Overview

### Metrics
- **Total TypeScript/JavaScript Source Files**: 115
- **Total Lines of Code**: 30,328
- **Main Modules**: 2 (discord, liveapi)
- **Primary Purpose**: Real-time Discord bot with voice pipelines, multi-agent orchestration, and multi-provider audio processing

### Directory Structure
```
kimaki/
├── discord/src/                      # Main bot implementation (72 files, ~25KB LOC)
│   ├── providers/                    # 18 provider implementations (STT/TTS)
│   ├── core/                         # Agent registry, context managers, conversation rules
│   ├── multi-agent/                  # Agent coordination & roles
│   ├── communication/                # Discord, Telegram adapters + gateway
│   ├── audio/                        # Audio processing, VAD, speaker diarization
│   ├── voice/                        # Voice pipelines (universal, Apple)
│   ├── monitoring/                   # Health checks, voice metrics
│   ├── proactive/                    # Notifications, webhooks
│   ├── scheduling/                   # Daily scrum cron jobs
│   ├── collaboration/                # Autonomous vs moderated modes
│   ├── config/                       # Bot configuration
│   ├── commands/                     # CLI command handlers
│   ├── genai.ts                      # Google Gemini integration
│   └── cli.ts                        # 72KB CLI orchestration file
├── liveapi/src/                      # Browser-side realtime client (20 files, ~5KB LOC)
│   ├── live-api-client.ts            # Gemini Live API client
│   ├── audio-*.ts                    # Audio recording/streaming/resampling
│   ├── react.ts                      # React integration
│   └── worklets/                     # Audio worklets (Web Audio API)
└── liveapi/                          # Configuration for liveapi package
```

### Tech Stack
- **Framework**: Discord.js, node-telegram-bot-api
- **CLI**: cac (lightweight CLI framework)
- **UI**: @clack/prompts (terminal UI)
- **Database**: better-sqlite3 (local SQLite)
- **Async Runtime**: Standard Node.js async/await
- **Audio Processing**: Web Audio API worklets
- **Testing**: vitest
- **Package Manager**: pnpm workspaces

---

## 2. Pattern Identification & Analysis

### 2.1 Configuration Patterns (YAML/env vars)

**Location**: `discord/src/config/bot-config.ts`

**Pattern Type**: Structured configuration with environment variable loader

```typescript
export interface BotConfig {
  voice: VoiceConfig
  apiKeys: { gemini?, groq?, cerebras?, deepgram?, ... }
  features: { multiAgent, dailyScrum, proactiveNotifications, ... }
  telegram?: { botToken }
  multiAgent?: { defaultMode, enabledAgents }
  dailyScrum?: { schedule, participants, duration }
}

// Loaded from env vars:
export function loadConfigFromEnv(): BotConfig { ... }
export function validateConfig(config: BotConfig): { valid, errors }
export function getProviderConfig(architecture): { stt, tts, description, cost }
```

**Key Features**:
- Type-safe config with interfaces
- Environment variable binding
- Preset-based architecture selection (7 presets: gemini-live, apple-free, groq-deepgram, etc.)
- Fallback chain support (LLM provider fallback)
- Validation with error reporting

**Estimated LOC**: ~300 lines  
**Consolidation Match**: **PHENO-SDK: pheno.config** (PhenoConfig class)

**Pheno-SDK Equivalent**:
```python
from pheno.config import Config, ConfigLoader
config = Config.from_env()
config.validate()
```

**Savings**: 200 LOC (replace custom validation with SDK validation)

---

### 2.2 HTTP Client Usage & API Integration

**Locations**: 
- `discord/src/genai.ts` (Google Gemini API)
- `discord/src/openai-realtime.ts` (OpenAI Realtime API)
- `liveapi/src/live-api-client.ts` (Browser Gemini Live client)

**Pattern Type**: Provider-based HTTP clients with streaming support

```typescript
// genai.ts - Google Gemini integration
class GeminiClient {
  async transcribeAudio(audioBuffer): Promise<string>
  async streamText(prompt): Promise<ReadableStream>
  async generateAudio(text): Promise<Buffer>
}

// live-api-client.ts - WebSocket streaming
class LiveAPIClient {
  private ws: WebSocket
  async connect(apiKey: string)
  async sendAudio(audioChunk: Uint8Array)
  onMessage(handler: (msg) => void)
}
```

**Key Features**:
- Multiple provider clients (Groq, Deepgram, Cartesia, OpenAI, Cerebras, Azure, Google)
- Streaming support for real-time audio
- Error handling with provider-specific logic
- Fallback mechanisms (provider failover)

**Estimated LOC**: ~2,500 lines (18 provider files)  
**Consolidation Match**: **PHENO-SDK: pheno.clients.base** + **pheno.adapters**

**Pheno-SDK Equivalent**:
```python
from pheno.clients import BaseHTTPClient, RetryPolicy
from pheno.adapters import ProviderAdapter

class GroqAdapter(ProviderAdapter):
    async def transcribe(self, audio): ...
    async def stream_response(self, prompt): ...
```

**Savings**: 1,500+ LOC (centralized HTTP retry/timeout logic)

---

### 2.3 Logging & Observability

**Location**: `discord/src/logger.ts`

**Pattern Type**: Simple logger factory with prefixing

```typescript
export function createLogger(prefix: string) {
  return {
    log: (...args) => log.info(`[${prefix}] ${args.join(' ')}`),
    error: (...args) => log.error(`[${prefix}] ${args.join(' ')}`),
    warn: (...args) => log.warn(`[${prefix}] ${args.join(' ')}`),
    debug: (...args) => log.info(`[${prefix}] ${args.join(' ')}`),
  }
}
```

**Key Features**:
- Context-aware logging with prefixes
- Centralized log formatting
- Multiple log levels
- Basic structured logging (prefixes only)

**Estimated LOC**: ~20 lines  
**Consolidation Match**: **PHENO-SDK: pheno.logging** + **pheno.observability**

**Pheno-SDK Equivalent**:
```python
from pheno.observability import get_logger, configure_observability

logger = get_logger(__name__)
logger.info("message", extra={"context": "value"})
```

**Pheno Advantage**: 
- Full OpenTelemetry integration
- Distributed tracing
- Metrics collection
- Automatic instrumentation

**Savings**: Eliminate custom logging logic, use pheno observability

---

### 2.4 Health Checks & Monitoring

**Location**: `discord/src/monitoring/health-check.ts`, `discord/src/monitoring/voice-metrics.ts`

**Pattern Type**: Periodic health checks with status aggregation

```typescript
export class HealthChecker {
  private healthResults: Map<string, HealthCheckResult> = new Map()
  
  start({ intervalMs = 60000 })
  async checkProvider(provider: string): Promise<HealthCheckResult>
  getSystemHealth(): SystemHealth
  getUnhealthyProviders(): string[]
}

export interface HealthCheckResult {
  status: 'healthy' | 'degraded' | 'unhealthy'
  provider: string
  latency: number
  timestamp: Date
}
```

**Key Features**:
- Interval-based health checks (60s default)
- Per-provider latency measurement
- Aggregate system health determination
- Unhealthy provider tracking

**Estimated LOC**: ~200 lines  
**Consolidation Match**: **PHENO-SDK: pheno.resilience.health_checks** + **pheno.ports**

**Pheno-SDK Equivalent**:
```python
from pheno.ports import HealthCheckPort
from pheno.resilience import HealthCheckManager

class ProviderHealthCheck(HealthCheckPort):
    async def check(self) -> HealthStatus: ...
```

**Savings**: 150 LOC (use SDK health check framework)

---

### 2.5 Provider Failover & Resilience

**Location**: `discord/src/providers/provider-failover.ts`

**Pattern Type**: Circuit breaker + provider selection with cooldown

```typescript
export class ProviderFailover {
  private failedProviders: Map<string, number> = new Map()
  private config: FailoverConfig = {
    maxRetries: 3,
    retryDelay: 1000,
    autoFailover: true,
    cooldownPeriod: 60000
  }
  
  getNextAvailableProvider(): string | null
  registerProvider(config: ProviderConfig)
  markProviderFailed(name: string)
  resetProvider(name: string)
}
```

**Key Features**:
- Priority-based provider ordering
- Cooldown period for failed providers
- Automatic failover with retry configuration
- Per-provider enabled/disabled state

**Estimated LOC**: ~150 lines  
**Consolidation Match**: **PHENO-SDK: pheno.resilience.circuit_breaker** + **pheno.resilience.failover**

**Pheno-SDK Equivalent**:
```python
from pheno.resilience import CircuitBreaker, Fallback, RetryPolicy

@fallback_to(backup_provider)
@retry_policy(max_retries=3, backoff=exponential)
async def call_provider(provider: str): ...
```

**Savings**: 100+ LOC (use SDK decorators instead of manual logic)

---

### 2.6 Session & State Management

**Location**: `discord/src/communication/gateway.ts`, `discord/src/core/project-context-manager.ts`

**Pattern Type**: In-memory session store with context preservation

```typescript
export class CommunicationGateway {
  private sessions: Map<string, Session> = new Map()
  
  getSession(userId: string, channelType: ChannelType): Session | undefined
  createSession(userId: string, channelType: ChannelType): Session
  updateSession(userId, channelType, updates)
  endSession(userId, channelType)
  cleanupInactiveSessions(maxInactiveMinutes)
}

export interface Session {
  id: string
  userId: string
  channelType: ChannelType
  conversationHistory: Array<{ role, content, timestamp }>
  state: { isActive, lastActivity, voiceCallActive }
}
```

**Key Features**:
- Map-based session storage
- Automatic session creation
- Conversation history tracking
- Inactive session cleanup
- Session state management

**Estimated LOC**: ~300 lines  
**Consolidation Match**: **PHENO-SDK: pheno.database + pheno.core.shared.cache** or **pheno.storage**

**Pheno-SDK Equivalent**:
```python
from pheno.database import Session as DBSession
from pheno.core.shared.cache import cached, CacheManager

@cached(ttl=3600)
async def get_session(user_id: str) -> Session: ...
```

**Savings**: 200 LOC (use SDK database/cache layer instead of Map)

---

### 2.7 CLI Argument Parsing

**Location**: `discord/src/cli.ts` (72KB!)

**Pattern Type**: Full CLI orchestration with setup workflows

```typescript
const cli = cac('kimaki')

cli.command('session list', 'List all sessions')
cli.command('session create', 'Create a new session')
cli.command('project list', 'List all projects')
cli.command('project add', 'Add a new project')

// Setup workflows:
- Voice architecture selection
- Provider credential configuration
- Environment variable generation
- Health checks
- OAuth automation
- CICD setup
```

**Key Features**:
- cac-based command structure
- Interactive prompts for setup
- Multi-step workflows
- Credential validation
- Environment file generation
- Browser automation for OAuth

**Estimated LOC**: ~2,000 (including setup utilities)  
**Consolidation Match**: **PHENO-SDK: pheno.cli**

**Pheno-SDK Equivalent**:
```python
from pheno.cli import Command, CLIApp
from pheno.cli.setup import SetupWizard

app = CLIApp()
@app.command()
async def session_list(): ...
```

**Savings**: 1,500+ LOC (use SDK CLI framework)

---

### 2.8 Database & Persistence

**Location**: Direct sqlite3 usage in `cli.ts` and `discordBot.ts`

**Pattern Type**: SQLite direct usage (better-sqlite3)

```typescript
const db = new Database('kimaki.db')
db.exec('CREATE TABLE IF NOT EXISTS ...')
db.prepare('SELECT * FROM sessions WHERE ...').all()
db.prepare('INSERT INTO ...').run(values)
```

**Key Features**:
- Direct SQL execution
- No ORM
- Synchronous operations
- File-based persistence

**Estimated LOC**: ~400 lines (scattered across multiple files)  
**Consolidation Match**: **PHENO-SDK: pheno.database** (SQLAlchemy-based with migrations)

**Pheno-SDK Equivalent**:
```python
from pheno.database import session, Session as DBSession
from sqlalchemy.orm import declarative_base

class KimakaSession(DBSession):
    __tablename__ = "sessions"
    user_id: str
    channel_type: str
```

**Savings**: 300 LOC (ORM + migrations + connection pooling)

---

### 2.9 Multi-Agent Coordination

**Location**: `discord/src/multi-agent/` (3 files), `discord/src/core/agent-registry.ts`

**Pattern Type**: Agent registry with collaboration rules

```typescript
export class AgentRegistry {
  private agents: Map<string, AgentRegistration> = new Map()
  private projectAgents: Map<string, Set<string>> = new Map()
  
  register(agent: AgentRegistration)
  getAgentsForProject(projectId: string): AgentRegistration[]
  getAvailableAgents(): AgentRegistration[]
}

export interface AgentRegistration extends AgentConfig {
  projects: Array<{ projectId, role, permissions, joinedAt }>
  availability: { schedule, timezone, officeHours, isAvailable }
  collaborationRules: { canInitiateWith, mustConsultWith, ignoreAgents }
  metrics: { totalConversations, averageResponseTime, successRate }
}
```

**Key Features**:
- Agent registration and indexing
- Project-based agent assignment
- Availability scheduling (cron-based)
- Collaboration rules engine
- Performance metrics tracking

**Estimated LOC**: ~400 lines  
**Consolidation Match**: **PHENO-SDK: pheno.domain** + **pheno.workflow**

**Unique to Kimaki**: Voice-based agent coordination specific to Discord

**Savings**: 150 LOC (use SDK domain models)

---

### 2.10 Real-Time Voice Streaming

**Location**: `discord/src/voice/`, `liveapi/src/live-api-client.ts`

**Pattern Type**: WebSocket + Web Audio API integration

```typescript
// Server side (discord/src/voice-pipeline-universal.ts)
export class VoicePipeline {
  private audioBuffer: Buffer[] = []
  async processAudioChunk(chunk: Buffer): Promise<string>
  async transcribeAndRespond(audio: Buffer): Promise<string>
}

// Client side (liveapi/src/live-api-client.ts)
export class LiveAPIClient {
  private ws: WebSocket
  async sendAudio(chunk: Uint8Array)
  onAudioResponse(handler: (audio: AudioData) => void)
}
```

**Key Features**:
- Streaming audio input
- Real-time transcription
- Buffering and chunking
- Audio format conversion
- WebSocket connection management

**Estimated LOC**: ~800 lines  
**Consolidation Match**: **PHENO-SDK: pheno.adapters + pheno.clients**

**Unique to Kimaki**: Discord voice channel integration

**Savings**: 400 LOC (use SDK WebSocket client + retry logic)

---

### 2.11 Testing Framework

**Location**: `discord/src/**/*.test.ts`

**Pattern Type**: vitest-based unit tests

```typescript
describe('GeminiClient', () => {
  it('should transcribe audio', async () => {
    const client = new GeminiClient(apiKey)
    const result = await client.transcribe(mockAudio)
    expect(result).toBe('expected text')
  })
})
```

**Key Features**:
- vitest test runner
- Unit tests for providers
- Inline snapshots (genai-to-ui-message.test.ts has 30K LOC of snapshots!)
- Mock objects

**Estimated LOC**: ~400 lines of actual test code  
**Consolidation Match**: **PHENO-SDK: pheno.testing**

**Savings**: 150 LOC (use SDK test utilities)

---

### 2.12 Async Patterns

**Pattern Type**: Native TypeScript async/await (good baseline)

**Key Features**:
- Promise-based async operations
- Error handling with try/catch
- Promise.all for concurrent operations
- Proper cleanup in finally blocks

**Assessment**: Modern and idiomatic; well-structured async code

**Consolidation Match**: **PHENO-SDK: pheno.infra.async_utils** (advanced patterns)

**Unique Opportunities**:
- Add pheno's `TaskPool` for concurrent provider calls
- Use pheno's `BackgroundTask` for async cleanup

---

### 2.13 Authentication & Security Patterns

**Location**: `discord/src/setup/`, `discord/src/communication/discord-adapter.ts`

**Pattern Type**: API key management + OAuth

**Key Features**:
- Environment-based API key storage
- Provider-specific key validation
- OAuth automation for setup
- Credential validation at startup

**Estimated LOC**: ~600 lines  
**Consolidation Match**: **PHENO-SDK: pheno.auth + pheno.credentials**

**Pheno-SDK Advantage**:
- Hierarchical credential scoping (org:project:env:resource)
- Automatic fallback resolution
- Encryption at rest
- Audit logging

**Savings**: 400 LOC (use SDK credential broker)

---

### 2.14 MCP (Model Context Protocol) Patterns

**Location**: None directly, but referenced as future capability

**Assessment**: Kimaki doesn't implement MCP, but pheno-sdk has extensive MCP support

**Consolidation Opportunity**: MCP server integration for future agent capabilities

---

## 3. Consolidation Opportunities Summary

### High-Priority Consolidation (200+ LOC savings each)

| Pattern | Kimaki LOC | Pheno-SDK Module | Savings | Complexity |
|---------|-----------|------------------|---------|-----------|
| HTTP Clients & Adapters | 2,500 | pheno.clients + pheno.adapters | 1,500 | Medium |
| CLI Framework | 2,000 | pheno.cli | 1,500 | High |
| Database & ORM | 400 | pheno.database | 300 | Medium |
| Configuration | 300 | pheno.config | 200 | Low |
| Session/State Mgmt | 300 | pheno.database + pheno.core.shared.cache | 200 | Medium |
| Auth & Credentials | 600 | pheno.auth + pheno.credentials | 400 | Medium |
| **Subtotal** | **6,100** | | **4,100** | |

### Medium-Priority Consolidation (100-200 LOC savings each)

| Pattern | Kimaki LOC | Pheno-SDK Module | Savings | Complexity |
|---------|-----------|------------------|---------|-----------|
| Health Checks | 200 | pheno.resilience.health_checks | 150 | Low |
| Provider Failover | 150 | pheno.resilience | 100 | Low |
| Logging | 20 | pheno.logging | - | N/A |
| Testing | 400 | pheno.testing | 150 | Low |
| **Subtotal** | **770** | | **400** | |

### Unique/Non-Consolidatable Patterns

| Pattern | Kimaki LOC | Reason |
|---------|-----------|--------|
| Discord Bot Logic | 5,000+ | Discord.js-specific, voice integration |
| Voice Pipelines | 800 | Real-time audio processing (could use adapters) |
| Provider Implementations | 2,500 | Provider-specific APIs vary; use SDK adapters for 1,500 LOC savings |
| Multi-Agent Orchestration | 400 | Domain-specific; only core registry could be simplified |
| **Total Unique** | **8,700** | |

### Total Estimated Savings

- **Directly Consolidatable**: 4,500 LOC (~15% of codebase)
- **Partially Consolidatable**: 2,000 LOC (via adapters/wrappers)
- **Not Consolidatable**: 8,700 LOC (Discord-specific, domain-specific)
- **Existing Shared**: 15,128 LOC (tests, snapshots, configuration)

**Total Potential Reduction**: 6,500 LOC (~21% code reduction)

---

## 4. Unique Patterns in Kimaki Worth Extracting

### 4.1 Voice Pipeline Architecture
Multi-provider voice handling with intelligent fallback. Could become a reusable **VoicePipelineKit** in pheno-sdk.

### 4.2 Multi-Agent Collaboration Framework
Agent availability scheduling, role-based permissions, and coordination rules. Could become **AgentOrchestrationKit**.

### 4.3 Real-Time Audio Streaming
WebSocket + buffering + transcription coordination. Could become **RealtimeAudioKit**.

### 4.4 Provider Failover Strategy
Sophisticated provider selection with health-aware fallback chains. Already good pattern; could be documented in pheno-sdk.

---

## 5. Dependencies on Other Kush Projects

### Current Dependencies
- **agentapi**: Not directly referenced in source code
- **opencode-openai-codex-auth**: Imported as `@opencode-ai/sdk` for code execution
- **router**: No direct reference
- **others**: No direct reference

### Potential Integration Points
1. **crun**: Both could share config/observability infrastructure
2. **pheno-sdk**: Central hub for shared patterns
3. **bloc**: Testing utilities could be shared

---

## 6. Migration Complexity Assessment

### Complexity Factors

**Easy Migrations** (1-2 days each):
- Configuration loader (pheno.config)
- Logging setup (pheno.logging)
- Health checks (pheno.resilience)

**Medium Migrations** (3-5 days each):
- Session management → database layer
- Provider HTTP clients → pheno.adapters
- CLI framework migration

**Hard Migrations** (1-2 weeks):
- Full database migration (schema design + migration generation)
- CLI workflow adaptation (cac → pheno.cli)

---

## 7. Recommendations

### Priority 1: Configuration & Observability
**Why**: Foundation for all other improvements
**Action**: Migrate config loading and logging to pheno-sdk
**Timeline**: 2 days
**Savings**: 150 LOC

### Priority 2: HTTP Clients & Adapters
**Why**: Large code base, high duplication across providers
**Action**: Create unified adapter pattern using pheno.clients + pheno.adapters
**Timeline**: 1 week
**Savings**: 1,500 LOC

### Priority 3: Database & Session Management
**Why**: Currently uses manual Map + SQLite
**Action**: Migrate to pheno.database with SQLAlchemy
**Timeline**: 1 week
**Savings**: 500 LOC

### Priority 4: CLI Framework
**Why**: 72KB monolithic file, difficult to maintain
**Action**: Restructure using pheno.cli
**Timeline**: 2 weeks
**Savings**: 1,500 LOC

### Priority 5: Auth & Credentials
**Why**: Manual key management is error-prone
**Action**: Use pheno.auth + pheno.credentials
**Timeline**: 3 days
**Savings**: 400 LOC

---

## 8. Risk Assessment

### High Risk
- Voice integration disruption: Discord.js has specific expectations
- Real-time streaming: Performance-critical code
- **Mitigation**: Keep voice pipelines, only refactor infrastructure around them

### Medium Risk
- Multi-agent coordination: Domain-specific logic
- **Mitigation**: Extract only generic parts (registry, scheduling)

### Low Risk
- Configuration: Straightforward mapping
- HTTP clients: Can be done incrementally
- CLI: Can be tested in parallel

---

## 9. Conclusion

Kimaki and Pheno-SDK operate in **different technology stacks** (TS/JS vs Python) but share **common architectural patterns**. The most realistic consolidation strategy is:

1. **Extract reusable patterns** from Kimaki into language-agnostic documentation
2. **Create TypeScript/JavaScript equivalents** of pheno-sdk concepts where beneficial
3. **Share infrastructure** (config, logging, observability) via shared SDKs
4. **Keep domain-specific code** (Discord integration, voice pipelines) separate

**Estimated Effort**: 4-6 weeks to consolidate 6,500 LOC (21% reduction)  
**Estimated ROI**: Improved maintainability, shared testing utilities, unified observability

**Recommendation**: Start with **Priority 1** (config/observability), then move to **Priority 2** (HTTP adapters) for maximum impact.

