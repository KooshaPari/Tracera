# Vercel AI SDK v6 - Comprehensive Research Document

## Executive Summary

The Vercel AI SDK v6 is a production-ready, open-source TypeScript toolkit for building AI-powered applications across multiple platforms (React, Next.js, Vue, Svelte, Node.js, etc.). The SDK abstracts away vendor-specific API differences across 40+ language model providers (OpenAI, Anthropic, Google, Mistral, etc.), enabling rapid development of streaming chat interfaces, autonomous agents, and generative AI features. Version 6 introduces significant enhancements including a unified Agent framework, enhanced tool capabilities with approval workflows, comprehensive MCP (Model Context Protocol) support, and developer tools for debugging LLM interactions.

**Key Strengths:**
- Unified API across 40+ LLM providers eliminates vendor lock-in
- Built-in streaming support with real-time UI updates via `useChat` hook
- Multi-step agent workflows with tool calling and structured output generation
- Framework-agnostic with optimized integrations for Next.js, Vue, Svelte, Svelte Kit, Expo
- Comprehensive error handling, telemetry, and debugging capabilities
- Transport-based architecture (v5+) decoupling from input state management

---

## Research Objectives

This research answers the following critical questions:

1. **What are the core APIs and architectural patterns needed to build chat applications?**
2. **How does the provider system work and can models be dynamically listed/selected?**
3. **What UI patterns and streaming mechanisms are recommended for chat interfaces?**
4. **What advanced features are available (tools, agents, structured output, MCP)?**
5. **What are the best practices for production deployment and performance optimization?**
6. **How does the SDK handle complex workflows (tool calling, multi-step generation, approval workflows)?**

---

## Methodology

Research was conducted through:

1. **Official Documentation Analysis** - Comprehensive review of ai-sdk.dev documentation
2. **Blog Post Analysis** - Vercel's official AI SDK v6 release announcement and guides
3. **Academy Content** - Practical implementations from Vercel Academy
4. **Community Resources** - LogRocket, DEV Community, Codecademy guides
5. **API Reference Study** - Detailed examination of useChat, streamText, generateText APIs

---

## Detailed Findings

### 1. CORE ARCHITECTURE & LIBRARIES

The AI SDK is organized into three interconnected libraries:

#### A. AI SDK Core
**Purpose:** Server-side language model interactions and business logic

**Primary APIs:**

| API | Purpose | Use Case | Returns |
|-----|---------|----------|---------|
| `generateText()` | Complete text generation without streaming | Batch processing, automation, non-interactive tasks | Full text + token usage + finish reason |
| `streamText()` | Real-time text generation with streaming | Chat applications, interactive scenarios | Async iterable of text chunks + full stream |
| `generateObject()` | Structured data generation (no streaming) | Extract data into JSON schema format | Typed object conforming to schema |
| `streamObject()` | Streaming structured data generation | Progressive data extraction | Streamed object parts |
| `embed()` / `embedMany()` | Vector embeddings for semantic search | RAG, similarity search, clustering | Vector arrays |
| `generateImage()` | Image generation and editing | Content creation, image-to-image | Image data |
| `transcribeAudio()` | Speech-to-text conversion | Voice input processing | Transcribed text |
| `createProviderRegistry()` | Multi-provider configuration | Enable dynamic provider switching | Registry instance |

**Key Parameters (Common across APIs):**
```typescript
{
  model: LanguageModel;           // Model instance (e.g., openai('gpt-4o'))
  prompt?: string | Message[];     // Text or conversation messages
  messages?: Message[];            // Chat message array
  system?: string;                 // System prompt/instructions
  tools?: Record<string, Tool>;    // External functions model can call
  toolChoice?: 'auto' | 'none' | 'required' | string; // Tool execution control
  temperature?: number;            // 0-2, controls randomness
  topP?: number;                   // Nucleus sampling (0-1)
  topK?: number;                   // Top-K sampling
  maxTokens?: number;              // Output length limit
  stopSequences?: string[];        // Stop generation at these tokens
  output?: 'text' | 'object' | 'array' | 'choice' | 'json'; // Output format
  seed?: number;                   // Deterministic generation
}
```

#### B. AI SDK UI
**Purpose:** Framework-agnostic React/Vue/Svelte hooks for chat interfaces

**Primary Hook:** `useChat()`

Imports vary by framework:
```typescript
// React
import { useChat } from '@ai-sdk/react';

// Vue
import { Chat } from '@ai-sdk/vue';

// Svelte
import { Chat } from '@ai-sdk/svelte';

// Angular
import { Chat } from '@ai-sdk/angular';
```

#### C. AI SDK RSC
**Purpose:** React Server Components with streaming and generative UI

Enables streaming React components directly from language models for advanced generative UI patterns.

---

### 2. THE useChat HOOK - COMPLETE API REFERENCE

The `useChat()` hook is the foundation for building conversational interfaces.

#### Initialization Parameters

```typescript
const chat = useChat({
  // Core configuration
  id?: string;                          // Unique chat identifier (auto-generated)
  chat?: Chat;                          // Existing Chat instance
  messages?: UIMessage[];               // Initial message array
  transport?: ChatTransport;            // Message transport layer

  // Request customization
  prepareSendMessagesRequest?: (options) => void;      // Modify requests
  prepareReconnectToStreamRequest?: (options) => void; // Customize reconnection
  headers?: Record<string, string>;     // Custom HTTP headers
  credentials?: 'include' | 'same-origin' | 'omit';   // CORS credentials
  body?: Record<string, any>;           // Additional request body data
  fetch?: typeof fetch;                 // Custom fetch implementation

  // Schema & metadata
  messageMetadataSchema?: z.ZodSchema;  // Validation for message metadata
  dataPartSchemas?: Record<string, z.ZodSchema>; // Data part validation
  generateId?: () => string;            // Custom ID generation

  // Callbacks
  onToolCall?: (event: ToolCallEvent) => void;     // Tool invocation handler
  onFinish?: (completion: {              // Completion callback
    message: UIMessage;
    finishReason: FinishReason;
    usage: { inputTokens: number; outputTokens: number };
  }) => void;
  onError?: (error: Error) => void;     // Error handler
  onData?: (data: any) => void;         // Data part handler
  sendAutomaticallyWhen?: (responses: any[]) => boolean; // Resubmit logic

  // Advanced
  experimental_throttle?: number;       // Update throttling (ms)
  resume?: boolean;                     // Resume interrupted streams
});
```

#### Return Values (State & Actions)

```typescript
const {
  // State
  id: string;                           // Chat identifier
  messages: UIMessage[];                // Message array with parts
  status: 'ready' | 'submitted' | 'streaming' | 'error'; // Request status
  error: Error | null;                  // Current error

  // Actions
  sendMessage: (options: {
    text?: string;
    parts?: MessagePart[];
  }) => Promise<void>;                  // Send message

  regenerate: () => Promise<void>;      // Recreate last assistant message
  stop: () => void;                     // Abort streaming
  resumeStream: () => void;             // Resume interrupted stream

  addToolOutput: (options: {            // Register tool execution result
    toolCallId: string;
    output: any;
  }) => void;

  addToolApprovalResponse: (options: {  // Tool approval response
    toolCallId: string;
    approved: boolean;
  }) => void;

  setMessages: (messages: UIMessage[]) => void; // Update local state
  clearError: () => void;               // Clear error state
} = useChat(config);
```

#### Message Structure (UIMessage)

```typescript
interface UIMessage {
  id: string;                    // Unique identifier
  role: 'user' | 'assistant';    // Message author
  parts: MessagePart[];          // Message content
  metadata?: Record<string, any>; // Custom metadata
}

type MessagePart =
  | { type: 'text'; text: string }
  | { type: 'tool-call'; toolCallId: string; toolName: string; args: any }
  | { type: 'tool-result'; toolCallId: string; result: any }
  | { type: 'reasoning'; reasoning: string };
```

#### Status Lifecycle

| Status | Meaning | When to Show |
|--------|---------|-------------|
| `ready` | Ready for new input | No loading state |
| `submitted` | Message sent, waiting for response | Loading spinner |
| `streaming` | Response streaming in | Allow abort/stop button |
| `error` | Request failed | Error message + retry option |

---

### 3. STREAMING IMPLEMENTATION - CORE APIS

#### streamText() - Complete Reference

```typescript
import { streamText } from 'ai';

const result = streamText({
  model: openai('gpt-4o'),
  messages: [
    { role: 'user', content: 'Explain quantum computing' }
  ],
  system: 'You are an expert physicist.',

  // Access streamed content
  onChunk: ({ chunk }) => {
    // Handle each chunk
  },
});

// Multiple ways to consume the stream

// 1. Text-only stream (most common)
for await (const chunk of result.textStream) {
  console.log(chunk); // Individual text deltas
}

// 2. Full stream (includes tool calls, reasoning, etc.)
for await (const event of result.fullStream) {
  if (event.type === 'text-delta') console.log(event.delta);
  if (event.type === 'tool-call') console.log(event.toolCall);
}

// 3. Promise-based access (await for completion)
const text = await result.text;          // Full generated text
const usage = await result.usage;        // Token consumption
const finishReason = await result.finishReason; // 'stop', 'length', etc.
const toolCalls = await result.toolCalls;       // Function invocations
```

**Return Object Properties:**

| Property | Type | Availability | Use Case |
|----------|------|--------------|----------|
| `textStream` | AsyncIterable<string> | Immediate | Stream text deltas progressively |
| `fullStream` | AsyncIterable<Event> | Immediate | Access tool calls, reasoning, errors |
| `text` | Promise<string> | Awaitable | Get complete response after streaming |
| `usage` | Promise<{ inputTokens, outputTokens }> | Awaitable | Track token consumption |
| `finishReason` | Promise<FinishReason> | Awaitable | Determine completion reason |
| `toolCalls` | Promise<ToolCall[]> | Awaitable | Access executed tool invocations |
| `toolResults` | Promise<any[]> | Awaitable | Get tool execution results |

#### generateText() - Non-Streaming Alternative

```typescript
import { generateText } from 'ai';

const { text, toolCalls, usage, finishReason } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Explain quantum computing',
  // Returns complete result (no streaming)
});
```

**Key Differences:**
- `streamText()`: Returns readable stream, better for interactive UX
- `generateText()`: Returns complete result, better for automation

---

### 4. PROVIDER SYSTEM - HOW IT WORKS

#### Provider Abstraction Architecture

The AI SDK solves vendor lock-in by providing a standardized interface:

```
Your Code (unified API)
    ↓
AI SDK Provider Layer (abstraction)
    ↓
Multiple Providers:
├── OpenAI
├── Anthropic
├── Google
├── Mistral
├── Groq
└── 35+ more...
```

#### Creating Language Model Instances

```typescript
// Using AI Gateway (default, no setup needed)
import { openai } from '@ai-sdk/openai';
const model = openai('gpt-4o');

// Using direct provider packages
import { anthropic } from '@ai-sdk/anthropic';
const model = anthropic('claude-3-5-sonnet-20241022');

import { google } from '@ai-sdk/google';
const model = google('gemini-2.0-flash');

// All models use the same API:
const result = await generateText({ model, prompt: '...' });
```

#### Multi-Provider Configuration

```typescript
import { createProviderRegistry } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

// Create registry for dynamic provider selection
const registry = createProviderRegistry({
  providers: {
    openai: openai({ apiKey: process.env.OPENAI_API_KEY }),
    anthropic: anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }),
  },
});

// Use by ID:
const model = registry.languageModel('openai', 'gpt-4o');
```

#### Supported Providers (40+)

**Official & Widely Used:**
- OpenAI (GPT-4o, o1, etc.)
- Anthropic (Claude 3.5 Sonnet, etc.)
- Google (Gemini 2.0, etc.)
- Mistral AI
- Groq
- DeepSeek
- xAI (Grok)
- Cohere
- Perplexity

**Enterprise & Specialized:**
- Amazon Bedrock
- Azure OpenAI
- Databricks Foundation Models
- Together AI
- Replicate
- Fireworks AI

**Community & Self-Hosted:**
- Ollama (local models)
- OpenRouter (multi-provider)
- Portkey
- LM Studio
- OpenAI-compatible endpoints

#### Listing Available Models

While the SDK doesn't provide a built-in dynamic model discovery API, you can:

1. **Hardcode supported models** (most common):
```typescript
const models = [
  'gpt-4o',
  'gpt-4-turbo',
  'gpt-4o-mini',
  'claude-3-5-sonnet-20241022',
  'claude-3-opus-20250219',
];
```

2. **Use provider APIs directly**:
```typescript
// OpenAI
const { data } = await openai.models.list();

// Anthropic
const models = ANTHROPIC_MODELS; // From documentation
```

3. **Implement provider-specific endpoints** for model discovery.

#### Model Fallback Strategy

```typescript
const result = await streamText({
  model: openai('gpt-4o'),
  fallbackModels: [
    openai('gpt-4-turbo'),
    anthropic('claude-3-opus-20250219'),
  ],
  // Tries gpt-4o first, falls back if unavailable
});
```

---

### 5. TOOLS & TOOL CALLING

#### Defining Tools

Tools enable language models to call external functions. Define using Zod for validation:

```typescript
import { tool } from 'ai';
import { z } from 'zod';

const tools = {
  getWeather: tool({
    description: 'Get current weather for a location',
    inputSchema: z.object({
      location: z.string().describe('City name, e.g., "San Francisco"'),
      unit: z.enum(['celsius', 'fahrenheit']).optional().default('fahrenheit'),
    }),
    execute: async ({ location, unit }) => {
      // Fetch real data
      return `It's 72°F in ${location}`;
    },
  }),

  sendEmail: tool({
    description: 'Send an email message',
    needsApproval: true, // Require human approval before execution
    inputSchema: z.object({
      to: z.string().email(),
      subject: z.string(),
      body: z.string(),
    }),
    inputExample: {
      to: 'user@example.com',
      subject: 'Meeting Tomorrow',
      body: 'Are you available tomorrow at 2pm?',
    },
    execute: async ({ to, subject, body }) => {
      // Send email
      return { success: true };
    },
  }),
};
```

#### Using Tools in streamText

```typescript
const result = streamText({
  model: openai('gpt-4o'),
  messages: [
    { role: 'user', content: 'What\'s the weather in San Francisco?' }
  ],
  tools,
  toolChoice: 'auto', // Let model decide
  // Alternatives: 'none', 'required', or specific tool name
});

// Handle tool calls
for await (const event of result.fullStream) {
  if (event.type === 'tool-call') {
    const { toolName, args } = event.toolCall;
    console.log(`Calling ${toolName}:`, args);
  }
}
```

#### Tool Execution Approval Workflow

For sensitive operations (emails, payments, deletes):

```typescript
// Client-side with useChat
const { messages, addToolOutput, addToolApprovalResponse } = useChat();

// Listen for tool calls
onToolCall: async (event) => {
  if (event.tool.needsApproval) {
    // Show approval dialog
    const approved = await showApprovalDialog(event);

    if (approved) {
      const result = await executeToolWithApproval(event.tool, event.args);
      addToolOutput({ toolCallId: event.toolCallId, output: result });
    } else {
      addToolApprovalResponse({
        toolCallId: event.toolCallId,
        approved: false
      });
    }
  }
};
```

#### Multi-Step Tool Loops

Execute tools iteratively for complex workflows:

```typescript
import { streamText, stepCountIs } from 'ai';

const result = streamText({
  model: openai('gpt-4o'),
  messages,
  tools,
  stopWhen: stepCountIs(5), // Allow up to 5 tool calls before output
});

// Model can now:
// 1. Call weather tool → get result
// 2. Call calendar tool → get result
// 3. Call email tool → send message
// 4. Generate final response
```

---

### 6. STRUCTURED OUTPUT

#### Generating Structured Data

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const schema = z.object({
  sentiment: z.enum(['positive', 'negative', 'neutral']),
  score: z.number().min(0).max(1),
  keywords: z.array(z.string()),
});

const { object } = await generateObject({
  model: openai('gpt-4o'),
  prompt: 'Analyze the sentiment of this review: "Amazing product!"',
  schema,
  output: 'object',
});

// object is typed: { sentiment: string; score: number; keywords: string[] }
```

#### Streaming Structured Output

```typescript
import { streamObject } from 'ai';

const result = streamObject({
  model: openai('gpt-4o'),
  prompt: 'Extract product information...',
  schema: z.object({
    name: z.string(),
    price: z.number(),
    features: z.array(z.string()),
  }),
});

// Stream partial objects
for await (const event of result.partialStream) {
  console.log('Partial:', event.value); // Incomplete object as it streams
}

const finalObject = await result.object; // Complete object
```

#### Combining Tools + Structured Output (AI SDK v6)

A key v6 feature: execute tools, then generate structured output at the end:

```typescript
const result = streamText({
  model: openai('gpt-4o'),
  messages,
  tools, // Can execute tools
  output: 'object', // Generate structured output at end
  schema: z.object({
    summary: z.string(),
    actionItems: z.array(z.string()),
  }),
  stopWhen: stepCountIs(5), // Allow enough steps for both tools + output
});

// Tool execution → Structured output generation (counts as final step)
```

**Important:** When using tools with structured output, the output generation counts as an additional step, so adjust `stopWhen` accordingly.

---

### 7. AGENTS FRAMEWORK (NEW IN V6)

#### Basic Agent Definition

```typescript
import { Agent } from 'ai';

const agent = new Agent({
  model: openai('gpt-4o'),
  name: 'Research Assistant',
  description: 'Researches topics and generates summaries',
  instructions: `You are a helpful research assistant.
    Use available tools to find information and provide
    detailed summaries to the user.`,
  tools,
});

// Execute agent
const result = await agent.run({
  messages: [
    { role: 'user', content: 'Research AI market size' }
  ],
});
```

#### ToolLoopAgent for Iterative Execution

```typescript
import { ToolLoopAgent } from 'ai';

const agent = new ToolLoopAgent({
  model: openai('gpt-4o'),
  tools,
  maxIterations: 10,
});

const result = await agent.run({
  userMessage: 'Get weather for 3 cities and summarize',
});

// Agent automatically:
// 1. Calls tools sequentially
// 2. Stops when reaching maxIterations or satisfactory response
// 3. Returns final response
```

---

### 8. MODEL CONTEXT PROTOCOL (MCP) INTEGRATION

MCP v6 now supports:

- **OAuth Authentication** - Secure provider authentication
- **Resource Access** - Access files, databases, external systems
- **Prompt Templates** - Reusable prompt components
- **Elicitation** - Server-initiated user input requests
- **Tool Definitions** - MCP-defined tools exposed to models

```typescript
import { createMCPClient } from 'ai/mcp';

const client = createMCPClient({
  url: 'stdio://python -m myserver',
  tools: true,
  resources: true,
});

const result = await streamText({
  model: openai('gpt-4o'),
  messages,
  tools: client.tools, // Use MCP-provided tools
});
```

---

### 9. NEXT.JS INTEGRATION - COMPLETE EXAMPLE

#### Backend Route Handler

Create `app/api/chat/route.ts`:

```typescript
import { streamText, convertToModelMessages } from 'ai';
import { openai } from '@ai-sdk/openai';

export const maxDuration = 30; // Allow 30-second streaming

export async function POST(req: Request) {
  const { messages } = await req.json();

  try {
    const result = streamText({
      model: openai('gpt-4o'),
      messages: await convertToModelMessages(messages),
      system: 'You are a helpful assistant.',
    });

    // Convert to Server-Sent Events stream
    return result.toUIMessageStreamResponse();
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({
        error: 'Failed to process chat request',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
```

#### Frontend Chat Component

Create `app/chat/page.tsx`:

```typescript
'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, status } = useChat();

  return (
    <div className="flex flex-col w-full max-w-2xl mx-auto">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-300 text-black'
              }`}
            >
              {message.parts?.map((part, i) =>
                part.type === 'text' ? (
                  <span key={`${message.id}-${i}`}>{part.text}</span>
                ) : null
              )}
            </div>
          </div>
        ))}

        {status === 'streaming' && (
          <div className="text-gray-500 text-sm">AI is typing...</div>
        )}
      </div>

      {/* Input form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!input.trim()) return;

          sendMessage({ text: input });
          setInput('');
        }}
        className="border-t p-4 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 border rounded px-3 py-2"
          disabled={status === 'streaming'}
        />
        <button
          type="submit"
          disabled={status === 'streaming'}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

**Key Points:**
- `maxDuration = 30` allows streaming responses up to 30 seconds
- `convertToModelMessages()` transforms UI messages to model format
- `toUIMessageStreamResponse()` converts result to SSE stream
- `useChat` manages state and streaming automatically
- `parts` array supports different message types (text, tool-calls, etc.)

---

### 10. BEST PRACTICES FOR PRODUCTION

#### Performance & Streaming

1. **Use `experimental_throttle` for high-frequency updates:**
```typescript
const { messages } = useChat({
  experimental_throttle: 50, // Update UI max every 50ms
});
```

2. **Respect token limits for real-time responsiveness:**
   - Fast models: gpt-4o-mini, claude-3-5-haiku (immediate)
   - Slow models: o1, reasoning models (10-15 second delays)
   - Choose based on UX requirements

3. **Set appropriate maxTokens to prevent overruns:**
```typescript
const result = streamText({
  model: openai('gpt-4o'),
  messages,
  maxTokens: 1024, // Prevent excessively long responses
});
```

#### Error Handling

1. **Implement graceful error boundaries:**
```typescript
const { error, clearError, regenerate } = useChat({
  onError: (error) => {
    console.error('Chat error:', error);
    // Show user-friendly message
  },
});
```

2. **Use fallback models for resilience:**
```typescript
const result = await streamText({
  model: openai('gpt-4o'),
  fallbackModels: [
    openai('gpt-4-turbo'),
    anthropic('claude-3-opus-20250219'),
  ],
});
```

#### Security & Privacy

1. **Store API keys in environment variables:**
```typescript
// .env.local
OPENAI_API_KEY=sk_...
ANTHROPIC_API_KEY=sk-ant-...
```

2. **Use server-side API routes for sensitive operations:**
   - Never expose API keys to client
   - Validate requests server-side
   - Sanitize user inputs

3. **Implement authentication for multi-user systems:**
```typescript
export async function POST(req: Request) {
  const user = await validateAuth(req);
  if (!user) return new Response('Unauthorized', { status: 401 });

  // Process request for authenticated user
}
```

#### State Management & Persistence

1. **Persist conversation history:**
```typescript
useEffect(() => {
  if (messages.length > 0) {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }
}, [messages]);

// Load on init
const [messages, setMessages] = useState(() => {
  const saved = localStorage.getItem('chatHistory');
  return saved ? JSON.parse(saved) : [];
});
```

2. **Implement proper message cleanup:**
```typescript
const { setMessages } = useChat();

function clearChat() {
  setMessages([]);
  localStorage.removeItem('chatHistory');
}
```

#### Tool Execution Best Practices

1. **Validate tool inputs strictly:**
```typescript
const tool = tool({
  inputSchema: z.object({
    amount: z.number().positive().max(10000),
    email: z.string().email(),
  }),
  // Zod validation enforced before execution
});
```

2. **Implement timeout handling:**
```typescript
const execute = async (args: any) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  try {
    const result = await fetchData(args, { signal: controller.signal });
    return result;
  } finally {
    clearTimeout(timeout);
  }
};
```

3. **Log tool usage for auditing:**
```typescript
onToolCall: async (event) => {
  console.log(`[AUDIT] Tool: ${event.tool.name}`, {
    args: event.args,
    timestamp: new Date(),
    userId: user.id,
  });
};
```

#### Monitoring & Debugging

1. **Use built-in DevTools (new in v6):**
```typescript
import { DebugStream } from 'ai/debug';

const debug = new DebugStream();
const result = await streamText({
  model: openai('gpt-4o'),
  messages,
});

// Inspect calls
debug.logCalls(result);
```

2. **Track token usage:**
```typescript
const { usage } = await result;
console.log(`Input: ${usage.inputTokens}, Output: ${usage.outputTokens}`);
```

3. **Monitor streaming delays:**
```typescript
const startTime = Date.now();
for await (const chunk of result.textStream) {
  const elapsed = Date.now() - startTime;
  console.log(`Chunk at ${elapsed}ms:`, chunk);
}
```

---

## KEY APIS QUICK REFERENCE

### Text Generation APIs

```typescript
// Simple text generation (no streaming)
import { generateText } from 'ai';
const { text } = await generateText({ model, prompt });

// Streaming text generation (interactive)
import { streamText } from 'ai';
const result = streamText({ model, messages });
for await (const chunk of result.textStream) { /* ... */ }

// Structured data generation
import { generateObject } from 'ai';
const { object } = await generateObject({ model, prompt, schema });

// Streaming structured data
import { streamObject } from 'ai';
const result = streamObject({ model, prompt, schema });
```

### UI Hook APIs

```typescript
// React chat interface
import { useChat } from '@ai-sdk/react';
const { messages, sendMessage, status } = useChat();

// Vue chat
import { Chat } from '@ai-sdk/vue';
const chat = new Chat({ /* config */ });

// Svelte chat
import { Chat } from '@ai-sdk/svelte';
```

### Provider APIs

```typescript
// Create model instance
import { openai } from '@ai-sdk/openai';
const model = openai('gpt-4o');

// Multi-provider
import { createProviderRegistry } from 'ai';
const registry = createProviderRegistry({ providers: { /* ... */ } });
```

### Tool APIs

```typescript
// Define tool
import { tool } from 'ai';
const myTool = tool({
  description: '...',
  inputSchema: z.object({ /* ... */ }),
  execute: async (args) => { /* ... */ },
});

// Use in generation
streamText({
  model,
  messages,
  tools: { myTool },
  toolChoice: 'auto',
});
```

---

## COMMON MIGRATION PATTERNS (From v5 to v6)

### Deprecated: convertToCoreMessages()
```typescript
// OLD (v5)
const messages = convertToCoreMessages(uiMessages);

// NEW (v6)
const messages = convertToModelMessages(uiMessages);
```

### Automatic Migration
```bash
npx @ai-sdk/codemod v6
```

---

## LIMITATIONS & CONSIDERATIONS

1. **Dynamic Model Discovery:** No built-in API to list available models from providers. Must hardcode or use provider-specific endpoints.

2. **State Management:** v5+ removed internal input state from useChat. Must manage input separately using useState.

3. **Real-Time Performance:** Reasoning models (o1) introduce 10-15 second delays—not suitable for conversational UX.

4. **Token Limits:** Long conversations accumulate tokens. Implement truncation for large message histories.

5. **Tool Availability:** Not all models support all tools equally. Claude and GPT-4 have best tool support.

6. **Streaming Throttling:** High-frequency updates can cause performance issues. Use `experimental_throttle`.

---

## RECOMMENDED ARCHITECTURE

### Monorepo Structure
```
project/
├── packages/
│   ├── ui/          # React components with useChat
│   ├── api/         # Next.js route handlers with streamText
│   └── shared/      # Types, schemas, utilities
├── app/
│   ├── api/chat/
│   │   └── route.ts # POST /api/chat
│   └── chat/
│       └── page.tsx # Chat interface
└── .env.local       # API keys
```

### Recommended Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Framework | Next.js App Router | Excellent AI SDK integration |
| Language | TypeScript | Type safety for schemas |
| Validation | Zod | Tool input validation |
| Styling | Tailwind CSS | Rapid UI development |
| Database | PostgreSQL + Prisma | Message persistence |
| Deployment | Vercel | Native AI SDK support |

---

## RESOURCES & REFERENCES

### Official Documentation
- [AI SDK Main Site](https://ai-sdk.dev)
- [AI SDK Docs](https://ai-sdk.dev/docs)
- [Vercel AI Blog](https://vercel.com/blog/ai-sdk-6)
- [GitHub Repository](https://github.com/vercel/ai)

### Learning Resources
- [Vercel Academy](https://vercel.com/academy/ai-sdk)
- [LogRocket Guide](https://blog.logrocket.com/nextjs-vercel-ai-sdk-streaming/)
- [DEV Community Guides](https://dev.to/pockit_tools/vercel-ai-sdk-complete-guide-building-production-ready-ai-chat-apps-with-nextjs-4cp6)

### Example Code
- [Official Templates](https://vercel.com/templates)
- [GitHub Examples](https://github.com/vercel/ai/tree/main/examples)

---

## CONCLUSION

The Vercel AI SDK v6 provides a comprehensive, production-ready foundation for building AI applications. Its key strengths—provider abstraction, built-in streaming, agent framework, and tool orchestration—make it the leading choice for TypeScript-based AI development. The v6 release significantly enhances agent capabilities and MCP integration while maintaining backward compatibility.

For teams building conversational AI, the combination of `useChat` + `streamText` + tools creates a powerful pattern requiring minimal boilerplate. The framework's flexibility supports everything from simple chatbots to complex autonomous agents with human-in-the-loop approval workflows.

**Recommended next steps:**
1. Review the [official Getting Started guide](https://ai-sdk.dev/docs/getting-started) for your framework
2. Implement a basic chatbot following the [Basic Chatbot tutorial](https://vercel.com/academy/ai-sdk/basic-chatbot)
3. Extend with tools for domain-specific functionality
4. Deploy to Vercel for seamless integration and monitoring
