# Vercel AI SDK v6 - Practical Quick Start Guide

## 5-Minute Chatbot Setup

### Step 1: Install Dependencies

```bash
npm install ai @ai-sdk/react @ai-sdk/openai zod
```

### Step 2: Create API Route (`app/api/chat/route.ts`)

```typescript
import { streamText, convertToModelMessages } from 'ai';
import { openai } from '@ai-sdk/openai';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o-mini'),
    messages: await convertToModelMessages(messages),
    system: 'You are a helpful assistant.',
  });

  return result.toUIMessageStreamResponse();
}
```

### Step 3: Create Chat Component (`app/chat/page.tsx`)

```typescript
'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export default function Chat() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, status } = useChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    await sendMessage({ text: input });
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs px-4 py-2 rounded ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {msg.parts?.map((part, i) => part.type === 'text' && <span key={i}>{part.text}</span>)}
            </div>
          </div>
        ))}
        {status === 'streaming' && <p className="text-gray-500">AI is typing...</p>}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message..."
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

### Step 4: Set Environment Variable

```env
# .env.local
OPENAI_API_KEY=sk_...
```

**Done!** Your chatbot is running. Visit `/chat` to test.

---

## Core APIs in 60 Seconds

### generateText() - Simple Output
```typescript
import { generateText } from 'ai';

const { text } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Explain quantum computing',
});

console.log(text);
```

### streamText() - Real-Time Streaming
```typescript
import { streamText } from 'ai';

const result = streamText({
  model: openai('gpt-4o'),
  messages: [{ role: 'user', content: 'Hello!' }],
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

### generateObject() - Structured Data
```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const { object } = await generateObject({
  model: openai('gpt-4o'),
  prompt: 'Extract sentiment from: "Great product!"',
  schema: z.object({
    sentiment: z.enum(['positive', 'negative', 'neutral']),
    confidence: z.number().min(0).max(1),
  }),
});

console.log(object); // { sentiment: 'positive', confidence: 0.95 }
```

### useChat() - React Hook
```typescript
import { useChat } from '@ai-sdk/react';

export function Chat() {
  const { messages, sendMessage, status } = useChat();

  return (
    <>
      {messages.map(msg => (
        <div key={msg.id}>{msg.role}: {msg.parts}</div>
      ))}
      <button onClick={() => sendMessage({ text: 'Hi' })}>
        Send
      </button>
    </>
  );
}
```

---

## Using Tools (Function Calling)

### Define Tool
```typescript
import { tool } from 'ai';
import { z } from 'zod';

const getWeather = tool({
  description: 'Get weather for a location',
  inputSchema: z.object({
    location: z.string(),
  }),
  execute: async ({ location }) => {
    // Real implementation
    return `72°F in ${location}`;
  },
});
```

### Use in API Route
```typescript
export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages: await convertToModelMessages(messages),
    tools: { getWeather },
    toolChoice: 'auto', // Let model decide when to use
  });

  return result.toUIMessageStreamResponse();
}
```

### Handle in useChat
```typescript
const { messages } = useChat({
  onToolCall: (event) => {
    console.log(`Tool called: ${event.tool.name}`);
    console.log(`Args: ${JSON.stringify(event.args)}`);
  },
});
```

---

## Multi-Provider Setup

### Using AI Gateway (No Setup)
```typescript
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

// Just use directly
const gpt = openai('gpt-4o');
const claude = anthropic('claude-3-5-sonnet-20241022');
```

### Dynamic Provider Selection
```typescript
const providers = {
  openai: openai('gpt-4o'),
  anthropic: anthropic('claude-3-5-sonnet-20241022'),
  google: google('gemini-2.0-flash'),
};

const selectedProvider = providers[process.env.PREFERRED_PROVIDER];

const result = streamText({
  model: selectedProvider,
  messages,
});
```

### Fallback Models
```typescript
const result = streamText({
  model: openai('gpt-4o'),
  fallbackModels: [
    openai('gpt-4-turbo'),
    anthropic('claude-3-opus-20250219'),
  ],
  // Tries first model, falls back if unavailable
});
```

---

## useChat Hook Configuration

### Basic Setup
```typescript
const {
  messages,           // Array of UIMessage
  sendMessage,        // Send new message
  status,             // 'ready' | 'submitted' | 'streaming' | 'error'
  error,              // Error object
  stop,               // Abort streaming
  regenerate,         // Retry last message
  clearError,         // Reset error
} = useChat({
  id: 'chat-1',       // Optional: custom chat ID
  initialMessages: [], // Start with messages
  api: '/api/chat',   // Endpoint (default)
});
```

### Advanced Options
```typescript
const chat = useChat({
  // Callbacks
  onFinish: (completion) => {
    console.log('Finish reason:', completion.finishReason);
    console.log('Tokens:', completion.usage);
  },

  onError: (error) => {
    console.error('Chat error:', error);
  },

  onToolCall: (event) => {
    console.log('Tool:', event.tool.name, 'Args:', event.args);
  },

  // Performance
  experimental_throttle: 50, // Update UI max every 50ms

  // Custom headers
  headers: {
    'X-Custom-Header': 'value',
  },
});
```

### Message Structure
```typescript
interface UIMessage {
  id: string;                    // Unique ID
  role: 'user' | 'assistant';    // Sender
  parts: MessagePart[];          // Content
}

type MessagePart =
  | { type: 'text'; text: string }
  | { type: 'tool-call'; toolCallId: string; toolName: string; args: any }
  | { type: 'tool-result'; toolCallId: string; result: any };
```

---

## Structured Output Example

### Chat with JSON Response
```typescript
// API route
export async function POST(req: Request) {
  const result = streamText({
    model: openai('gpt-4o'),
    messages: await convertToModelMessages(messages),
    system: 'You are a helpful assistant.',
    output: 'object', // Generate JSON at end
    schema: z.object({
      mainPoints: z.array(z.string()),
      summary: z.string(),
    }),
  });

  return result.toUIMessageStreamResponse();
}

// Component
const { messages } = useChat();

messages.forEach(msg => {
  msg.parts?.forEach(part => {
    if (part.type === 'text') {
      // Try parsing as JSON
      const parsed = JSON.parse(part.text);
      console.log('Main points:', parsed.mainPoints);
    }
  });
});
```

---

## Common Patterns

### Streaming with Status Indication
```typescript
const { messages, status, stop } = useChat();

return (
  <>
    {status === 'submitted' && <p>Sending...</p>}
    {status === 'streaming' && <p>AI is thinking... <button onClick={stop}>Stop</button></p>}
    {status === 'error' && <p>Something went wrong</p>}
    {messages.map(/* ... */)}
  </>
);
```

### Message Regeneration
```typescript
const { messages, regenerate } = useChat();

function retryLastMessage() {
  regenerate();
}
```

### Error Handling
```typescript
const { error, clearError, regenerate } = useChat({
  onError: (error) => {
    console.error('Error:', error);
    // Show user-friendly message
  },
});

return (
  <>
    {error && (
      <div>
        <p>{error.message}</p>
        <button onClick={() => clearError()}>Dismiss</button>
        <button onClick={() => regenerate()}>Retry</button>
      </div>
    )}
  </>
);
```

### Conversation Persistence
```typescript
import { useEffect } from 'react';

const { messages } = useChat();

// Save to localStorage
useEffect(() => {
  if (messages.length > 0) {
    localStorage.setItem('chat', JSON.stringify(messages));
  }
}, [messages]);

// Load on init
const [initialMessages] = useState(() => {
  const saved = localStorage.getItem('chat');
  return saved ? JSON.parse(saved) : [];
});

const chat = useChat({ initialMessages });
```

---

## Key Configuration Parameters

### streamText() Options
```typescript
streamText({
  model: openai('gpt-4o'),
  messages,

  // Content
  system: 'You are helpful...',      // System prompt
  prompt: 'Hello',                    // Alternative to messages

  // Generation control
  temperature: 0.7,                   // 0-2 (0=deterministic, 2=random)
  topP: 0.9,                          // Nucleus sampling
  topK: 40,                           // Top-K sampling
  maxTokens: 1024,                    // Output length limit
  seed: 42,                           // Deterministic output
  stopSequences: ['END'],             // Stop tokens

  // Tools & output
  tools: { /* ... */ },               // Available functions
  toolChoice: 'auto',                 // 'auto' | 'none' | 'required'
  output: 'text',                     // 'text' | 'object' | 'array'

  // Advanced
  onChunk: ({ chunk }) => {},         // Each chunk received
  headers: { /* ... */ },             // Custom headers
});
```

### useChat() Options
```typescript
useChat({
  api: '/api/chat',                   // Endpoint
  id: 'chat-1',                       // Chat identifier
  messages: [],                        // Initial messages

  headers: { /* ... */ },             // Custom headers
  credentials: 'include',             // CORS

  onToolCall: (event) => {},         // Tool invocation
  onFinish: (completion) => {},      // Generation complete
  onError: (error) => {},             // Error occurred

  experimental_throttle: 50,          // Update throttle (ms)
  resume: false,                      // Resume interrupted stream
});
```

---

## Debugging & DevTools

### Enable Logging
```typescript
const result = streamText({
  model: openai('gpt-4o'),
  messages,
  onChunk: ({ chunk }) => {
    console.log('Chunk:', chunk);
  },
});

// Log token usage
const usage = await result.usage;
console.log(`Tokens: ${usage.inputTokens} in, ${usage.outputTokens} out`);
```

### Inspect Tool Calls
```typescript
onToolCall: (event) => {
  console.log({
    tool: event.tool.name,
    args: event.args,
    toolCallId: event.toolCallId,
  });
}
```

### Check Finish Reason
```typescript
onFinish: (completion) => {
  console.log('Finish reason:', completion.finishReason);
  // 'stop' | 'length' | 'content-filter' | 'tool-calls' | 'error' | 'other'
}
```

---

## Performance Tips

### Optimize Streaming
```typescript
// 1. Throttle updates to prevent UI thrashing
const chat = useChat({
  experimental_throttle: 50, // Update max every 50ms
});

// 2. Use appropriate models for responsiveness
// Fast: gpt-4o-mini, claude-3-5-haiku
// Slow: o1, reasoning models (10-15s delay)

// 3. Limit token output
streamText({
  model: openai('gpt-4o'),
  messages,
  maxTokens: 1024, // Prevent long responses
});
```

### Manage Conversation Size
```typescript
// Truncate old messages
function truncateMessages(messages, maxCount = 20) {
  return messages.slice(-maxCount);
}

// Or implement message summarization
const { messages } = useChat();
const recentMessages = messages.slice(-10);
const olderMessages = messages.slice(0, -10);

// Summarize older messages into context
const summary = await generateText({
  model: openai('gpt-4o'),
  prompt: `Summarize this conversation:\n${olderMessages}`,
});
```

---

## Migration from v5 to v6

### Main Changes
```typescript
// OLD (v5)
import { convertToCoreMessages } from 'ai';
const msgs = convertToCoreMessages(uiMessages);

// NEW (v6)
import { convertToModelMessages } from 'ai';
const msgs = await convertToModelMessages(uiMessages);
```

### Auto-Migrate Code
```bash
npx @ai-sdk/codemod v6
```

---

## Troubleshooting

### Issue: Messages not streaming
**Solution:** Ensure `maxDuration` is set in API route:
```typescript
export const maxDuration = 30;
```

### Issue: Tools not being called
**Solution:** Ensure model supports tools and toolChoice is set:
```typescript
streamText({
  model: openai('gpt-4o'),
  tools: { /* ... */ },
  toolChoice: 'auto', // Must specify
});
```

### Issue: State not updating in useChat
**Solution:** Ensure component has `'use client'` directive:
```typescript
'use client'; // Required for client-side hooks

import { useChat } from '@ai-sdk/react';
```

### Issue: Streaming stops after timeout
**Solution:** Increase `maxDuration`:
```typescript
export const maxDuration = 60; // Up to 900 on Pro
```

---

## Resources

- [Docs](https://ai-sdk.dev/docs)
- [Examples](https://github.com/vercel/ai/tree/main/examples)
- [GitHub](https://github.com/vercel/ai)
- [Academy](https://vercel.com/academy/ai-sdk)

---

## Complete Working Example

### File Structure
```
app/
├── api/
│   └── chat/
│       └── route.ts
├── chat/
│   └── page.tsx
└── layout.tsx
```

### `app/api/chat/route.ts`
```typescript
import { streamText, convertToModelMessages } from 'ai';
import { openai } from '@ai-sdk/openai';

export const maxDuration = 30;

export async function POST(request: Request) {
  const { messages } = await request.json();

  const result = streamText({
    model: openai('gpt-4o-mini'),
    system: 'You are a helpful assistant. Answer concisely.',
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

### `app/chat/page.tsx`
```typescript
'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { messages, sendMessage, status, error } = useChat();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    await sendMessage({ text: input });
    setInput('');
  }

  return (
    <div className="flex flex-col w-full h-screen max-w-2xl mx-auto">
      <header className="bg-gray-100 p-4 border-b">
        <h1 className="text-2xl font-bold">AI Chat</h1>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-md px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-black'
              }`}
            >
              {msg.parts?.map((part, i) =>
                part.type === 'text' ? (
                  <p key={i}>{part.text}</p>
                ) : null
              )}
            </div>
          </div>
        ))}

        {status === 'streaming' && (
          <div className="text-gray-500 text-sm italic">
            AI is thinking...
          </div>
        )}

        {error && (
          <div className="text-red-500 text-sm bg-red-50 p-2 rounded">
            {error.message}
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t p-4 flex gap-2 bg-gray-50"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 border rounded px-3 py-2"
          disabled={status === 'streaming'}
        />
        <button
          type="submit"
          disabled={status === 'streaming' || !input.trim()}
          className="bg-blue-500 text-white px-6 py-2 rounded disabled:bg-gray-400"
        >
          {status === 'streaming' ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
```

### `.env.local`
```
OPENAI_API_KEY=sk_...
```

**Run:** `npm run dev` → Visit `http://localhost:3000/chat`

Done! You have a fully functional chatbot.
