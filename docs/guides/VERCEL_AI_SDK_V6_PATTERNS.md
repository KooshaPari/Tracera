# Vercel AI SDK v6 - Advanced Patterns & Architecture

## Architecture Patterns

### Pattern 1: Layered Service Architecture

```
Frontend (useChat hook)
    ↓
Transport Layer (/api/chat)
    ↓
Business Logic Layer (Services)
    ↓
Data Layer (DB, APIs)
    ↓
LLM Provider (OpenAI, Anthropic, etc.)
```

**Implementation:**

```typescript
// lib/services/chat.service.ts
import { streamText, convertToModelMessages } from 'ai';
import { openai } from '@ai-sdk/openai';

export class ChatService {
  async streamChat(
    messages: any[],
    options?: { system?: string; tools?: any }
  ) {
    return streamText({
      model: openai(process.env.OPENAI_MODEL || 'gpt-4o'),
      messages: await convertToModelMessages(messages),
      system: options?.system,
      tools: options?.tools,
    });
  }
}

// app/api/chat/route.ts
import { ChatService } from '@/lib/services/chat.service';

const chatService = new ChatService();

export async function POST(req: Request) {
  const { messages, tools } = await req.json();

  try {
    const result = await chatService.streamChat(messages, {
      system: 'You are a helpful assistant.',
      tools,
    });

    return result.toUIMessageStreamResponse();
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
    });
  }
}
```

---

### Pattern 2: Multi-Provider Router

Route requests to different providers based on context:

```typescript
// lib/models/provider-router.ts
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { google } from '@ai-sdk/google';
import type { LanguageModel } from 'ai';

interface ModelConfig {
  provider: 'openai' | 'anthropic' | 'google';
  name: string;
  cost: number;
  speed: number; // 1-10
}

const models: Record<string, ModelConfig> = {
  'gpt-4o': {
    provider: 'openai',
    name: 'gpt-4o',
    cost: 0.015,
    speed: 8,
  },
  'claude-3-5-sonnet': {
    provider: 'anthropic',
    name: 'claude-3-5-sonnet-20241022',
    cost: 0.003,
    speed: 7,
  },
  'gemini-2.0-flash': {
    provider: 'google',
    name: 'gemini-2.0-flash',
    cost: 0.001,
    speed: 9,
  },
};

export class ProviderRouter {
  selectModel(
    preference: 'speed' | 'cost' | 'quality'
  ): LanguageModel {
    const sorted = Object.values(models).sort((a, b) => {
      if (preference === 'speed') return b.speed - a.speed;
      if (preference === 'cost') return a.cost - b.cost;
      return 0; // Quality = default first
    });

    const selected = sorted[0];

    switch (selected.provider) {
      case 'openai':
        return openai(selected.name);
      case 'anthropic':
        return anthropic(selected.name);
      case 'google':
        return google(selected.name);
    }
  }

  getByName(name: string): LanguageModel {
    const config = models[name];
    if (!config) throw new Error(`Unknown model: ${name}`);

    switch (config.provider) {
      case 'openai':
        return openai(config.name);
      case 'anthropic':
        return anthropic(config.name);
      case 'google':
        return google(config.name);
    }
  }
}

// Usage
const router = new ProviderRouter();
const fastModel = router.selectModel('speed');
const cheapModel = router.selectModel('cost');
const gpt = router.getByName('gpt-4o');
```

---

### Pattern 3: Tool Registry

Centralized tool management:

```typescript
// lib/tools/registry.ts
import { tool } from 'ai';
import { z } from 'zod';

export interface ToolDefinition {
  name: string;
  description: string;
  execute: (args: any) => Promise<any>;
  inputSchema: z.ZodSchema;
  needsApproval?: boolean;
}

export class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();

  register(definition: ToolDefinition) {
    this.tools.set(definition.name, definition);
  }

  getAll() {
    const result: Record<string, any> = {};

    this.tools.forEach((def) => {
      result[def.name] = tool({
        description: def.description,
        inputSchema: def.inputSchema,
        needsApproval: def.needsApproval,
        execute: def.execute,
      });
    });

    return result;
  }

  get(name: string) {
    const def = this.tools.get(name);
    if (!def) throw new Error(`Tool not found: ${name}`);

    return tool({
      description: def.description,
      inputSchema: def.inputSchema,
      execute: def.execute,
    });
  }
}

// lib/tools/index.ts
import { ToolRegistry } from './registry';
import { z } from 'zod';

export const toolRegistry = new ToolRegistry();

// Register tools
toolRegistry.register({
  name: 'getWeather',
  description: 'Get current weather for a location',
  inputSchema: z.object({
    location: z.string(),
    unit: z.enum(['celsius', 'fahrenheit']).default('fahrenheit'),
  }),
  execute: async ({ location, unit }) => {
    // Fetch from weather API
    return { temperature: 72, unit, location };
  },
});

toolRegistry.register({
  name: 'sendEmail',
  description: 'Send an email',
  needsApproval: true,
  inputSchema: z.object({
    to: z.string().email(),
    subject: z.string(),
    body: z.string(),
  }),
  execute: async ({ to, subject, body }) => {
    // Send email
    return { success: true };
  },
});

// Usage
const allTools = toolRegistry.getAll();
const weatherTool = toolRegistry.get('getWeather');
```

---

### Pattern 4: Conversation Memory with Vector Store

Implement long-term memory using embeddings:

```typescript
// lib/memory/conversation-memory.ts
import { embed } from 'ai';
import { openai } from '@ai-sdk/openai';

interface ConversationSnapshot {
  id: string;
  summary: string;
  embedding: number[];
  timestamp: Date;
  messageCount: number;
}

export class ConversationMemory {
  private snapshots: ConversationSnapshot[] = [];

  async addSnapshot(
    conversationId: string,
    summary: string,
    messageCount: number
  ) {
    const { embedding } = await embed({
      model: openai.embedding('text-embedding-3-small'),
      value: summary,
    });

    this.snapshots.push({
      id: conversationId,
      summary,
      embedding,
      timestamp: new Date(),
      messageCount,
    });
  }

  async findRelevantSnapshots(query: string, topK: number = 3) {
    const { embedding } = await embed({
      model: openai.embedding('text-embedding-3-small'),
      value: query,
    });

    // Cosine similarity
    const similarities = this.snapshots.map((snap) => ({
      ...snap,
      similarity: this.cosineSimilarity(embedding, snap.embedding),
    }));

    return similarities
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, topK);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const dotProduct = a.reduce((sum, x, i) => sum + x * b[i], 0);
    const magnitude1 = Math.sqrt(a.reduce((sum, x) => sum + x * x, 0));
    const magnitude2 = Math.sqrt(b.reduce((sum, x) => sum + x * x, 0));
    return dotProduct / (magnitude1 * magnitude2);
  }
}
```

---

### Pattern 5: Agent Orchestration

Build complex agent workflows:

```typescript
// lib/agents/research-agent.ts
import { ToolLoopAgent } from 'ai';
import { openai } from '@ai-sdk/openai';
import { toolRegistry } from '@/lib/tools';

export class ResearchAgent {
  private agent: ToolLoopAgent;

  constructor() {
    this.agent = new ToolLoopAgent({
      model: openai('gpt-4o'),
      tools: toolRegistry.getAll(),
      maxIterations: 10,
    });
  }

  async research(query: string) {
    const result = await this.agent.run({
      userMessage: `Research and summarize information about: ${query}`,
    });

    return result;
  }
}

// Usage
const agent = new ResearchAgent();
const research = await agent.research('Quantum computing advances in 2024');
```

---

### Pattern 6: Streaming with Progress Tracking

Track long-running operations:

```typescript
// lib/streaming/progress-tracker.ts
import { streamText } from 'ai';

interface ProgressEvent {
  type: 'start' | 'progress' | 'complete' | 'error';
  progress?: number;
  stage?: string;
  data?: any;
}

export async function streamWithProgress(
  operation: () => ReturnType<typeof streamText>,
  onProgress: (event: ProgressEvent) => void
) {
  onProgress({ type: 'start' });

  try {
    const result = operation();
    let chunkCount = 0;

    for await (const chunk of result.textStream) {
      chunkCount++;

      onProgress({
        type: 'progress',
        progress: Math.min(chunkCount / 10, 0.9), // Estimate
        stage: 'Generating response',
        data: { chunksReceived: chunkCount },
      });
    }

    onProgress({ type: 'complete', progress: 1 });
    return result;
  } catch (error) {
    onProgress({
      type: 'error',
      data: { error: error.message },
    });
    throw error;
  }
}

// Client-side usage
const { addToolOutput } = useChat({
  onFinish: () => {
    setProgress(100);
  },
});
```

---

### Pattern 7: Request Caching

Prevent duplicate API calls:

```typescript
// lib/cache/response-cache.ts
import { streamText } from 'ai';
import crypto from 'crypto';

interface CacheEntry {
  text: string;
  timestamp: number;
  ttl: number;
}

export class ResponseCache {
  private cache = new Map<string, CacheEntry>();

  private getKey(messages: any[]): string {
    const content = JSON.stringify(messages);
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  get(messages: any[]): string | null {
    const key = this.getKey(messages);
    const entry = this.cache.get(key);

    if (!entry) return null;

    const age = Date.now() - entry.timestamp;
    if (age > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.text;
  }

  set(messages: any[], text: string, ttl: number = 3600000): void {
    const key = this.getKey(messages);
    this.cache.set(key, {
      text,
      timestamp: Date.now(),
      ttl,
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

// Usage in API route
const cache = new ResponseCache();

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Check cache
  const cached = cache.get(messages);
  if (cached) {
    return new Response(cached, {
      headers: { 'X-Cache': 'HIT' },
    });
  }

  // Generate new response
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });

  const fullText = await result.text;
  cache.set(messages, fullText);

  return new Response(fullText);
}
```

---

### Pattern 8: Rate Limiting

Control API usage:

```typescript
// lib/rate-limit/rate-limiter.ts
export interface RateLimitConfig {
  maxRequests: number;
  windowMs: number; // milliseconds
}

export class RateLimiter {
  private requests = new Map<string, number[]>();

  constructor(private config: RateLimitConfig) {}

  isAllowed(clientId: string): boolean {
    const now = Date.now();
    const requests = this.requests.get(clientId) || [];

    // Remove old requests outside window
    const validRequests = requests.filter((time) => now - time < this.config.windowMs);

    if (validRequests.length >= this.config.maxRequests) {
      return false;
    }

    validRequests.push(now);
    this.requests.set(clientId, validRequests);
    return true;
  }

  getRemainingRequests(clientId: string): number {
    const now = Date.now();
    const requests = this.requests.get(clientId) || [];
    const validRequests = requests.filter((time) => now - time < this.config.windowMs);
    return this.config.maxRequests - validRequests.length;
  }
}

// Middleware
import { NextRequest, NextResponse } from 'next/server';

const limiter = new RateLimiter({
  maxRequests: 10,
  windowMs: 60000, // 1 minute
});

export async function rateLimitMiddleware(req: NextRequest) {
  const clientId = req.headers.get('x-client-id') || req.ip || 'unknown';

  if (!limiter.isAllowed(clientId)) {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    );
  }

  return NextResponse.next();
}
```

---

## Advanced Patterns

### Pattern 9: Multi-Agent Conversation

Agents discussing a topic:

```typescript
// lib/agents/multi-agent-discussion.ts
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

interface Agent {
  name: string;
  role: string;
  systemPrompt: string;
}

export class MultiAgentDiscussion {
  async runDiscussion(
    agents: Agent[],
    topic: string,
    rounds: number = 3
  ) {
    const conversation: Array<{
      agent: string;
      message: string;
    }> = [];

    for (let round = 0; round < rounds; round++) {
      for (const agent of agents) {
        const previousResponses = conversation
          .slice(-2)
          .map((c) => `${c.agent}: ${c.message}`)
          .join('\n');

        const { text } = await generateText({
          model: openai('gpt-4o'),
          system: agent.systemPrompt,
          prompt: `Topic: ${topic}\n\nRecent discussion:\n${previousResponses}\n\nYour response as ${agent.name}:`,
          maxTokens: 200,
        });

        conversation.push({
          agent: agent.name,
          message: text,
        });
      }
    }

    return conversation;
  }
}

// Usage
const discussion = new MultiAgentDiscussion();
const result = await discussion.runDiscussion(
  [
    {
      name: 'Researcher',
      role: 'Research scientist',
      systemPrompt: 'You are a research scientist focused on evidence.',
    },
    {
      name: 'Philosopher',
      role: 'Philosopher',
      systemPrompt: 'You are a philosopher exploring ethical implications.',
    },
  ],
  'AI safety',
  2
);
```

---

### Pattern 10: Structured Output Pipeline

Chain structured outputs:

```typescript
// lib/pipeline/structured-pipeline.ts
import { generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

interface PipelineStep<T> {
  name: string;
  schema: z.ZodSchema<T>;
  prompt: (previousOutput: any) => string;
}

export async function runStructuredPipeline<T>(
  steps: PipelineStep<T>[]
) {
  let previousOutput: any = null;

  for (const step of steps) {
    const { object } = await generateObject({
      model: openai('gpt-4o'),
      prompt: step.prompt(previousOutput),
      schema: step.schema,
    });

    console.log(`Step: ${step.name}`, object);
    previousOutput = object;
  }

  return previousOutput;
}

// Usage
const result = await runStructuredPipeline([
  {
    name: 'Extract entities',
    schema: z.object({
      entities: z.array(
        z.object({
          name: z.string(),
          type: z.enum(['person', 'place', 'thing']),
        })
      ),
    }),
    prompt: () => 'Extract named entities from: "John went to Paris."',
  },
  {
    name: 'Analyze sentiment',
    schema: z.object({
      sentiment: z.enum(['positive', 'negative', 'neutral']),
      confidence: z.number(),
    }),
    prompt: (prevOutput) =>
      `Analyze sentiment considering these entities: ${JSON.stringify(prevOutput)}`,
  },
]);
```

---

## Performance Optimization

### Optimization 1: Message Truncation

Limit conversation history:

```typescript
// lib/utils/message-truncation.ts
export function truncateMessages(
  messages: any[],
  maxMessages: number = 20
): any[] {
  if (messages.length <= maxMessages) {
    return messages;
  }

  // Keep first (system context) + last (recent)
  const systemMessages = messages.filter((m) => m.role === 'system');
  const otherMessages = messages.filter((m) => m.role !== 'system');

  return [
    ...systemMessages,
    ...otherMessages.slice(-maxMessages),
  ];
}
```

### Optimization 2: Token Estimation

Estimate costs before generation:

```typescript
// lib/utils/token-counter.ts
export function estimateTokens(text: string): number {
  // Rough estimation: 1 token ≈ 4 characters
  return Math.ceil(text.length / 4);
}

export function estimateCost(
  inputTokens: number,
  outputTokens: number,
  provider: 'openai' | 'anthropic' = 'openai'
): number {
  const rates = {
    openai: {
      input: 0.000005, // $0.005 per 1K tokens
      output: 0.000015,
    },
    anthropic: {
      input: 0.000003, // $0.003 per 1K tokens
      output: 0.000015,
    },
  };

  const rate = rates[provider];
  return (
    (inputTokens * rate.input + outputTokens * rate.output) / 1000
  );
}
```

---

## Error Handling & Resilience

### Graceful Degradation

```typescript
// lib/resilience/fallback-service.ts
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

export async function generateWithFallback(prompt: string) {
  const providers = [
    { name: 'OpenAI', fn: () => openai('gpt-4o') },
    { name: 'Anthropic', fn: () => anthropic('claude-3-5-sonnet-20241022') },
  ];

  let lastError: Error | null = null;

  for (const provider of providers) {
    try {
      const model = provider.fn();
      const { text } = await generateText({
        model,
        prompt,
        timeout: 5000,
      });
      return { text, provider: provider.name };
    } catch (error) {
      console.error(`${provider.name} failed:`, error);
      lastError = error as Error;
      continue;
    }
  }

  throw lastError;
}
```

---

## Testing Patterns

### Mock LLM for Testing

```typescript
// lib/testing/mock-llm.ts
import { LanguageModel } from 'ai';

export function createMockLLM(responses: string[]): LanguageModel {
  let callCount = 0;

  return {
    doGenerate: async () => {
      const response = responses[callCount] || 'Mock response';
      callCount++;

      return {
        text: response,
        toolCalls: [],
        finishReason: 'stop',
        usage: {
          inputTokens: 10,
          outputTokens: 10,
        },
      };
    },
  } as any;
}

// Test
describe('Chat', () => {
  it('should respond to messages', async () => {
    const mockLLM = createMockLLM(['Hello there!', 'How can I help?']);

    const result = await generateText({
      model: mockLLM,
      prompt: 'Hi',
    });

    expect(result.text).toBe('Hello there!');
  });
});
```

---

## Summary: When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| Layered Service | Organize logic across services |
| Multi-Provider Router | Cost/speed optimization |
| Tool Registry | Centralize tool management |
| Conversation Memory | Long-term context |
| Agent Orchestration | Complex workflows |
| Progress Tracking | Long-running operations |
| Request Caching | High-traffic applications |
| Rate Limiting | Protect against abuse |
| Multi-Agent Discussion | Debate/analysis scenarios |
| Structured Pipeline | Data extraction workflows |

---

## References

- [AI SDK Documentation](https://ai-sdk.dev)
- [Advanced Patterns](https://ai-sdk.dev/docs/advanced)
- [GitHub Examples](https://github.com/vercel/ai/tree/main/examples)
