# Vercel AI SDK Community Providers for CLI Tools: Comprehensive Research

## Executive Summary

The Vercel AI SDK ecosystem includes three primary CLI-integrated provider implementations (Codex CLI, Claude Code, and Gemini CLI) that extend the Language Model Specification V3 to enable autonomous tool execution through command-line interfaces. These providers differ significantly in their approach to model listing, tool execution strategies, and authentication mechanisms. While none currently support dynamic model discovery through APIs, each offers distinct integration patterns suitable for different use cases. The underlying Language Model Specification V3 provides a standardized interface enabling custom providers following established patterns.

## Research Objectives

This research answers the following questions:
1. How do CLI-based providers (Codex CLI, Claude Code, Gemini CLI) integrate with the Vercel AI SDK?
2. What models does each provider expose and how are they accessed?
3. What are the capabilities and limitations of each implementation?
4. What standardized patterns exist for implementing custom providers?
5. How can new CLI tool providers be developed following ACP standards?

## Methodology

Research was conducted through:
- Official Vercel AI SDK documentation at ai-sdk.dev
- Community provider documentation pages
- Web search for current implementation details and patterns
- Analysis of provider installation, configuration, and API interfaces
- Review of Language Model Specification V3 documentation

---

## Part 1: Codex CLI Provider

### Installation and Configuration

**Package Installation:**
```bash
npm install ai-sdk-provider-codex-cli ai
```

For AI SDK v5 compatibility:
```bash
npm install ai-sdk-provider-codex-cli@ai-sdk-v5 ai@^5.0.0
```

**Basic Configuration:**
```typescript
import { codexCli } from 'ai-sdk-provider-codex-cli';

// Use default instance
const model = codexCli('gpt-5.2-codex');

// Or customize defaults
const customProvider = codexCli({
  reasoningEffort: 'high',
  approvalMode: 'on-request',
  sandboxMode: 'workspace-write',
  verbose: true,
});
```

### Available Models

**Current Generation (Recommended):**
- `gpt-5.2-codex` - Latest agentic coding model for real-world engineering
- `gpt-5.2` - General purpose model
- `gpt-5.1-codex-max` - Supports extended reasoning (xhigh)
- `gpt-5.1-codex-mini` - Lightweight, cost-effective variant

**Legacy Models:**
- `gpt-5.1`
- `gpt-5.1-codex`
- `gpt-5`
- `gpt-5-codex`
- `gpt-5-codex-mini`

### Configuration Options

The Codex CLI provider supports granular control over execution behavior:

| Option | Type | Purpose | Values |
|--------|------|---------|--------|
| `reasoningEffort` | string | Control reasoning depth | 'none', 'low', 'medium', 'high', 'xhigh' |
| `approvalMode` | string | Tool execution policy | 'untrusted', 'on-failure', 'on-request', 'never' |
| `sandboxMode` | string | Sandbox restrictions | 'read-only', 'workspace-write', 'danger-full-access' |
| `mcpServers` | array | MCP server connections | Array of server configs |
| `verbose` | boolean | Enable detailed logging | true/false |
| `logger` | object | Custom logger instance | Winston/Pino compatible |

### Dynamic Model Listing

**Status:** NOT SUPPORTED

The Codex CLI provider documentation does not provide APIs for dynamically discovering available models. Models must be hardcoded or maintained as constants in your application.

**Recommendation:** Maintain a static configuration file:
```typescript
const CODEX_MODELS = {
  'gpt-5.2-codex': { tier: 'premium', reasoning: true },
  'gpt-5.2': { tier: 'standard', reasoning: true },
  'gpt-5.1-codex-max': { tier: 'premium', reasoning: true },
  'gpt-5.1-codex-mini': { tier: 'lite', reasoning: false },
} as const;
```

### Key Limitations

1. **No AI SDK Custom Tools Support** - Does not support Zod schemas for custom tools. Instead, Codex CLI executes its own autonomous tools.
2. **No Tool Streaming** - Tool execution cannot be streamed; results arrive as complete events.
3. **Environment Requirements:**
   - Node.js 18 or higher
   - Codex CLI installed globally on the system
   - Authentication via `codex login`
4. **Tool Approval Overhead** - In `on-request` mode, requires user confirmation for each tool execution
5. **No Dynamic Model Discovery** - Must hardcode available models

### Integration Pattern

```typescript
import { codexCli } from 'ai-sdk-provider-codex-cli';
import { generateText } from 'ai';

const { text } = await generateText({
  model: codexCli('gpt-5.2-codex'),
  prompt: 'Implement a TypeScript function that validates email addresses',
  reasoningEffort: 'high',
});

console.log(text);
```

### Use Cases

- Advanced agentic coding workflows requiring extended reasoning
- Autonomous tool execution with user approval gates
- Integration with existing Codex CLI setups
- Projects requiring xhigh reasoning effort on complex problems

---

## Part 2: Claude Code Provider

### Installation and Configuration

**Package Installation:**
```bash
npm install ai-sdk-provider-claude-code ai
```

Version compatibility by AI SDK version:
```bash
# AI SDK v5
npm install ai-sdk-provider-claude-code@ai-sdk-v5 ai@^5.0.0

# AI SDK v4
npm install ai-sdk-provider-claude-code@ai-sdk-v4 ai@^4.0.0
```

**Basic Configuration:**
```typescript
import { createClaudeCode } from 'ai-sdk-provider-claude-code';

// Default instance with all tools enabled
const claudeCode = createClaudeCode();

// Custom configuration with tool restrictions
const customClaudeCode = createClaudeCode({
  allowedTools: ['Read', 'Write', 'Edit', 'Bash'],
  disallowedTools: ['RiskyOperation'],
  permissionMode: 'default',
  workingDirectory: '/projects/my-app',
});
```

### Available Models

The Claude Code provider exposes three model shortcuts:

| Shortcut | Full Identifier | Use Case | Performance |
|----------|-----------------|----------|-------------|
| `opus` | `claude-opus-4-5-*` | Most capable, highest quality | Slowest |
| `sonnet` | `claude-sonnet-4-5-20250514` | Balanced performance/cost | Medium |
| `haiku` | `claude-haiku-4-5-*` | Fastest, most cost-effective | Fastest |

**Example identifiers:**
- `claude-opus-4-5` (latest Opus)
- `claude-sonnet-4-5-20250514` (specific version)
- `claude-haiku-4-5-20251001` (specific version)

### Model Capabilities

All Claude Code models support:
- Image input processing
- Object generation
- MCP server integration
- Autonomous tool execution (no Zod schemas required)

**NOT Supported:**
- AI SDK custom tools with Zod schemas
- Native tool streaming (tools execute autonomously)

### Configuration Options

```typescript
const config = {
  // Tool management
  allowedTools: ['Read', 'Write', 'Edit', 'Bash', 'Glob'],
  disallowedTools: ['DangerousTool'],

  // Permission handling
  permissionMode: 'default',  // or 'strict', 'permissive'

  // MCP servers
  mcpServers: [
    { name: 'filesystem', command: 'mcp-server-filesystem' }
  ],

  // Execution constraints
  conversationTurnLimit: 50,
  workingDirectory: '/path/to/project',

  // Logging and debugging
  verbose: true,
  logger: customLogger,
};
```

### Dynamic Model Listing

**Status:** NOT SUPPORTED

The Claude Code provider does not provide APIs for discovering available models. The three shortcuts (opus, sonnet, haiku) are the documented interface.

**Workaround - Model Registry:**
```typescript
const CLAUDE_MODELS = {
  opus: {
    fullId: 'claude-opus-4-5-20251101',
    capabilities: ['images', 'objects', 'tools'],
    latency: 'high',
  },
  sonnet: {
    fullId: 'claude-sonnet-4-5-20250514',
    capabilities: ['images', 'objects', 'tools'],
    latency: 'medium',
  },
  haiku: {
    fullId: 'claude-haiku-4-5-20251001',
    capabilities: ['images', 'objects', 'tools'],
    latency: 'low',
  },
} as const;
```

### Authentication Requirements

Claude Code provider requires:
1. **Claude CLI Authentication:** `claude login` must be executed
2. **Subscription:** Claude Pro or Max subscription
3. **Environment:** Node.js 18 or higher
4. **System Dependency:** Claude Code CLI installed globally

### Integration Patterns

**Basic Text Generation:**
```typescript
import { claudeCode } from 'ai-sdk-provider-claude-code';
import { generateText } from 'ai';

const { text } = await generateText({
  model: claudeCode('sonnet'),
  prompt: 'Create a comprehensive API documentation',
});
```

**Autonomous Tool Execution:**
```typescript
const { text } = await generateText({
  model: claudeCode('opus'),
  prompt: 'Analyze the codebase in /src and generate a summary',
  allowedTools: ['Read', 'Glob', 'Bash'],
});
```

**Image Processing:**
```typescript
const { text } = await generateText({
  model: claudeCode('sonnet'),
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'image',
          image: buffer, // or base64 string
        },
        {
          type: 'text',
          text: 'Describe this image',
        },
      ],
    },
  ],
});
```

### Use Cases

- Full-stack development workflows requiring code analysis and generation
- Multi-turn conversations with persistent context
- Image-based code review and documentation
- Projects leveraging Claude's extended reasoning capabilities
- Teams already invested in Claude Pro/Max subscriptions

### Comparative Advantages

- **vs. Codex CLI:** Faster iteration, simpler setup, broader tool ecosystem
- **vs. Gemini CLI:** Better code generation, more mature integration
- **Disadvantage:** Requires paid subscription (Claude Pro/Max)

---

## Part 3: Gemini CLI Provider

### Installation and Configuration

**Package Installation:**
```bash
npm install ai-sdk-provider-gemini-cli
```

**Version Compatibility:**
- v2.x → AI SDK v6
- v1.x → AI SDK v5
- v0.x → AI SDK v4

**Basic Configuration:**
```typescript
import { createGeminiProvider } from 'ai-sdk-provider-gemini-cli';

const gemini = createGeminiProvider({
  authType: 'oauth-personal',
});

const model = gemini('gemini-3-pro-preview');
```

### Available Models

**Preview Models (Latest):**
- `gemini-3-pro-preview` - Advanced reasoning capabilities
- `gemini-3-flash-preview` - Optimized for speed with preview features

**Production Models:**
- `gemini-2.5-pro` - Advanced general-purpose model
- `gemini-2.5-flash` - Fast, cost-effective production model

**Feature Matrix:**

| Model | Reasoning | Output Tokens | Status | Recommended For |
|-------|-----------|----------------|--------|-----------------|
| gemini-3-pro-preview | Enhanced | 64K | Preview | Research, complex reasoning |
| gemini-3-flash-preview | Standard | 64K | Preview | Experimentation |
| gemini-2.5-pro | Standard | 32K | Production | General tasks |
| gemini-2.5-flash | Standard | 32K | Production | Speed-critical tasks |

### Authentication Strategies

The Gemini CLI provider supports four authentication approaches:

**1. OAuth (Recommended):**
```typescript
const gemini = createGeminiProvider({
  authType: 'oauth-personal',
  // Uses local CLI authentication flow
});
```

**2. API Key:**
```typescript
const gemini = createGeminiProvider({
  authType: 'api-key',
  apiKey: process.env.GOOGLE_AI_STUDIO_KEY,
});
```
Obtain key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**3. Vertex AI:**
```typescript
const gemini = createGeminiProvider({
  authType: 'vertex-ai',
  projectId: 'my-gcp-project',
  location: 'us-central1',
});
```

**4. Google Auth Library:**
```typescript
const gemini = createGeminiProvider({
  authType: 'google-auth',
  googleAuthInstance: existingAuthClient,
});
```

### Model Configuration

```typescript
const model = gemini('gemini-3-pro-preview', {
  temperature: 0.7,
  topK: 40,
  topP: 0.95,
  maxOutputTokens: 2048,
  thinkingConfig: {
    thinkingLevel: 'medium',  // 'low', 'medium', 'high'
  },
});
```

### Supported Features

All Gemini models enable:
- Image input (base64-encoded only, NOT URLs)
- Object generation
- Tool usage
- Tool streaming

**Important Limitation:** Images must be base64-encoded; URL-based image loading is not supported.

### Dynamic Model Listing

**Status:** NOT SUPPORTED

The Gemini CLI provider documentation lists only predefined models. There is no API for discovering available models dynamically.

**Alternative:** Maintain a versioned model registry:
```typescript
const GEMINI_MODELS = {
  'gemini-3-pro-preview': {
    status: 'preview',
    maxTokens: 64000,
    thinkingSupport: true,
  },
  'gemini-3-flash-preview': {
    status: 'preview',
    maxTokens: 64000,
    thinkingSupport: false,
  },
  'gemini-2.5-pro': {
    status: 'production',
    maxTokens: 32000,
    thinkingSupport: false,
  },
  'gemini-2.5-flash': {
    status: 'production',
    maxTokens: 32000,
    thinkingSupport: false,
  },
} as const;
```

### Integration Pattern

**Basic Usage:**
```typescript
import { createGeminiProvider } from 'ai-sdk-provider-gemini-cli';
import { generateText } from 'ai';

const gemini = createGeminiProvider({ authType: 'oauth-personal' });

const { text } = await generateText({
  model: gemini('gemini-2.5-pro'),
  prompt: 'Explain quantum computing in simple terms',
});

console.log(text);
```

**With Extended Thinking:**
```typescript
const { text } = await generateText({
  model: gemini('gemini-3-pro-preview', {
    thinkingConfig: { thinkingLevel: 'high' },
  }),
  prompt: 'Design a distributed system architecture for a social network',
});
```

**With Base64 Images:**
```typescript
import fs from 'fs';
import path from 'path';

const imageBuffer = fs.readFileSync('/path/to/image.jpg');
const base64Image = imageBuffer.toString('base64');

const { text } = await generateText({
  model: gemini('gemini-2.5-pro'),
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'image',
          image: base64Image,
          mimeType: 'image/jpeg',
        },
        {
          type: 'text',
          text: 'What is shown in this image?',
        },
      ],
    },
  ],
});
```

### Use Cases

- Multimodal AI workflows with image processing (note: base64 requirement)
- Preview access to latest Google research (gemini-3-* models)
- Extended thinking problems requiring deliberate reasoning
- GCP-integrated environments (Vertex AI option)
- Cost-optimized inference (gemini-2.5-flash)

### Advantages and Trade-offs

**Advantages:**
- Latest preview models with cutting-edge reasoning
- Production-ready models (gemini-2.5)
- Extended thinking support
- Multiple authentication options

**Disadvantages:**
- Base64-only image encoding (no URL support)
- API key requirement (vs. OAuth in other providers)
- Preview models may change behavior between releases

---

## Part 4: Custom Provider Implementation Pattern (ACP Standard)

### Language Model Specification V3 Overview

The AI SDK provides a standardized Language Model Specification V3 that defines how providers interact with language models. This specification ensures interoperability across the ecosystem.

**Core Principle:** "You can write your own provider that adheres to the specification and it will be compatible with the AI SDK."

### Provider Architecture

Three main interfaces form the foundation:

```typescript
// 1. Provider Factory
interface ProviderV3 {
  languageModel(modelId: string): LanguageModelV3;
  textEmbeddings?(modelId: string): EmbeddingModelV3;
  imageGeneration?(modelId: string): ImageModelV3;
}

// 2. Language Model Interface
interface LanguageModelV3 {
  specificationVersion: 'V3';
  modelId: string;
  doGenerate(request: GenerateRequest): Promise<GenerateResult>;
  doStream(request: GenerateRequest): Stream<StreamPart>;
  supportedUrls?: string[];
}

// 3. Specialized Interfaces
interface EmbeddingModelV3 {
  specificationVersion: 'V3';
  doEmbed(request: EmbedRequest): Promise<EmbedResult>;
}

interface ImageModelV3 {
  specificationVersion: 'V3';
  doGenerateImage(request: GenerateImageRequest): Promise<GenerateImageResult>;
}
```

### Step-by-Step Implementation

#### Step 1: Create Provider Entry Point

```typescript
// src/index.ts
import { ProviderV3, LanguageModelV3 } from '@ai-sdk/provider';

export interface MyProviderConfig {
  apiKey?: string;
  baseUrl?: string;
  headers?: Record<string, string>;
}

export function createMyProvider(config: MyProviderConfig = {}): ProviderV3 {
  const apiKey = config.apiKey || process.env.MY_PROVIDER_API_KEY;

  if (!apiKey) {
    throw new Error('MyProvider API key is required');
  }

  return {
    languageModel(modelId: string): LanguageModelV3 {
      return new MyLanguageModel(modelId, apiKey, config);
    },
  };
}

// Convenience export
export const myProvider = createMyProvider();
```

#### Step 2: Implement LanguageModelV3

```typescript
// src/language-model.ts
import {
  LanguageModelV3,
  StreamPart,
  GenerateRequest,
  GenerateResult,
  APICallError,
  TooManyRequestsError,
} from '@ai-sdk/provider';

class MyLanguageModel implements LanguageModelV3 {
  specificationVersion = 'V3' as const;
  modelId: string;
  private apiKey: string;
  private baseUrl: string;

  constructor(
    modelId: string,
    apiKey: string,
    config: MyProviderConfig
  ) {
    this.modelId = modelId;
    this.apiKey = apiKey;
    this.baseUrl = config.baseUrl || 'https://api.myprovider.com/v1';
  }

  async doGenerate(request: GenerateRequest): Promise<GenerateResult> {
    // Convert AI SDK format to provider API format
    const messages = request.messages.map(msg =>
      this.convertMessage(msg)
    );

    try {
      const response = await fetch(
        `${this.baseUrl}/completions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: this.modelId,
            messages,
            temperature: request.temperature,
            max_tokens: request.maxTokens,
            stop: request.stopSequences,
          }),
        }
      );

      if (!response.ok) {
        if (response.status === 429) {
          throw new TooManyRequestsError({
            retryAfterSeconds: parseInt(
              response.headers.get('retry-after') || '60'
            ),
          });
        }
        throw new APICallError({
          statusCode: response.status,
          responseBody: await response.text(),
        });
      }

      const data = await response.json();

      return {
        rawCall: { rawRequestBody: JSON.stringify(messages) },
        finishReason: this.mapFinishReason(data.stop_reason),
        usage: {
          promptTokens: data.usage.prompt_tokens,
          completionTokens: data.usage.completion_tokens,
        },
        text: data.choices[0].message.content,
      };
    } catch (error) {
      if (error instanceof APICallError) throw error;
      throw new APICallError({
        statusCode: 500,
        responseBody: JSON.stringify(error),
      });
    }
  }

  async doStream(
    request: GenerateRequest
  ): Promise<ReadableStream<StreamPart>> {
    const messages = request.messages.map(msg =>
      this.convertMessage(msg)
    );

    const response = await fetch(
      `${this.baseUrl}/completions/stream`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.modelId,
          messages,
          stream: true,
        }),
      }
    );

    if (!response.ok) {
      throw new APICallError({
        statusCode: response.status,
        responseBody: await response.text(),
      });
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    return new ReadableStream<StreamPart>({
      async start(controller) {
        controller.enqueue({
          type: 'stream-start',
        } as const);

        try {
          let buffer = '';
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (!line.startsWith('data: ')) continue;

              const data = JSON.parse(line.slice(6));
              const content = data.choices[0].delta.content;

              if (content) {
                controller.enqueue({
                  type: 'text-delta',
                  textDelta: content,
                } as const);
              }
            }
          }

          controller.enqueue({
            type: 'finish',
            finishReason: 'stop',
          } as const);
        } catch (error) {
          controller.error(error);
        } finally {
          controller.close();
        }
      },
    });
  }

  private convertMessage(msg: any): any {
    // Convert AI SDK message format to provider API format
    return {
      role: msg.role,
      content: msg.content.map((c: any) => {
        if (c.type === 'text') {
          return { type: 'text', text: c.text };
        } else if (c.type === 'tool-call') {
          return {
            type: 'tool_use',
            id: c.toolUseId,
            name: c.toolName,
            input: c.toolInput,
          };
        }
        return c;
      }),
    };
  }

  private mapFinishReason(stopReason: string): 'stop' | 'length' | 'tool-calls' | 'content-filter' | 'other' {
    const map: Record<string, any> = {
      'stop': 'stop',
      'max_tokens': 'length',
      'tool_calls': 'tool-calls',
      'content_policy': 'content-filter',
    };
    return map[stopReason] ?? 'other';
  }
}
```

#### Step 3: Content Types Supported

The Language Model Specification V3 supports five distinct content generation types:

```typescript
// Stream parts your model can emit
type StreamPart =
  // Initialization
  | { type: 'stream-start' }

  // Text generation
  | { type: 'text-delta'; textDelta: string }

  // Tool calls
  | { type: 'tool-call-delta'; toolCallId: string; toolName: string; argsTextDelta: string }
  | { type: 'tool-call'; toolCallId: string; toolName: string; args: unknown }

  // File outputs (images, audio, documents)
  | { type: 'file'; mimeType: string; data: Uint8Array }

  // Extended reasoning (chain-of-thought)
  | { type: 'thinking-delta'; thinkingDelta: string }

  // Source attribution
  | { type: 'source'; sourceId: string; url: string }

  // Completion
  | { type: 'finish'; finishReason: 'stop' | 'length' | 'tool-calls' | 'content-filter' | 'other' };
```

### Publishing Your Provider

After development:

1. **Create an NPM Package:**
```json
{
  "name": "ai-sdk-provider-myprovider",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "peerDependencies": {
    "ai": "^6.0.0"
  },
  "dependencies": {
    "@ai-sdk/provider": "^1.0.0"
  }
}
```

2. **Publish to NPM:**
```bash
npm publish
```

3. **Submit Documentation PR:**
Submit a PR to the Vercel AI SDK repository to add documentation to the Community Providers section. Use existing provider docs as templates.

### Example: Complete Simple Provider

```typescript
// simple-provider/src/index.ts
import { ProviderV3, LanguageModelV3, APICallError } from '@ai-sdk/provider';

class SimpleLanguageModel implements LanguageModelV3 {
  specificationVersion = 'V3' as const;
  modelId = 'simple-model';

  async doGenerate(request: any) {
    // Minimal implementation
    return {
      finishReason: 'stop',
      usage: { promptTokens: 0, completionTokens: 0 },
      text: 'Hello from SimpleProvider',
    };
  }

  async doStream(request: any) {
    return new ReadableStream({
      start(controller) {
        controller.enqueue({ type: 'stream-start' });
        controller.enqueue({ type: 'text-delta', textDelta: 'Hello' });
        controller.enqueue({ type: 'text-delta', textDelta: ' from ' });
        controller.enqueue({ type: 'text-delta', textDelta: 'SimpleProvider' });
        controller.enqueue({ type: 'finish', finishReason: 'stop' });
        controller.close();
      },
    });
  }
}

export function createSimpleProvider(): ProviderV3 {
  return {
    languageModel(): LanguageModelV3 {
      return new SimpleLanguageModel();
    },
  };
}

export const simpleProvider = createSimpleProvider();
```

---

## Part 5: ACP Provider Pattern

### What is ACP?

**ACP (AI Community Providers)** is not a specific pattern, but rather a community-driven approach to extending the Vercel AI SDK. The ecosystem includes a reference provider: `@mcpc-tech/acp-ai-provider`.

### ACP Standard Characteristics

1. **Open-Source Implementation** - ACP providers follow the Language Model Specification V3
2. **Community Maintenance** - Third-party developers maintain providers
3. **Interoperability** - All ACP providers work with the same AI SDK API
4. **Vendor-Agnostic** - Your code remains independent of provider choice

### Building an ACP-Compatible Provider

To create an ACP provider:

```typescript
// 1. Implement Language Model Specification V3
// 2. Export a factory function
export function createYourProvider(config): ProviderV3 { ... }

// 3. Support standardized configuration
// 4. Handle errors consistently
// 5. Publish as @your-org/ai-sdk-provider-name

// 6. Optionally contribute to ACP community list
```

### ACP Community Structure

The broader ACP ecosystem includes:
- **Official AI SDK Providers** (OpenAI, Anthropic, Google, Azure)
- **OpenAI-Compatible Providers** (LM Studio, Ollama, Together AI, vLLM)
- **Community Providers** (50+ integrations)
- **Observability Partners** (14 integrations for monitoring)

### How to Contribute

1. Develop provider following Language Model Specification V3
2. Publish to NPM as `ai-sdk-provider-{name}`
3. Add comprehensive documentation
4. Submit PR to Vercel AI SDK docs with:
   - Installation instructions
   - Configuration examples
   - Model listing
   - Limitations
   - Use cases

---

## Comparative Analysis Table

| Feature | Codex CLI | Claude Code | Gemini CLI | Custom Provider |
|---------|-----------|------------|-----------|-----------------|
| **Installation Complexity** | Medium | Medium | Low | High |
| **Model Discovery** | Static list | Static shortcuts | Static list | Custom |
| **Authentication** | CLI login | CLI login | Multiple methods | Custom |
| **Tool Execution** | Autonomous | Autonomous | Streaming | Both |
| **Reasoning Support** | xhigh | High | Medium/High | Custom |
| **Image Support** | No | Yes | Yes (base64) | Custom |
| **Subscription Required** | No | Claude Pro/Max | API key only | N/A |
| **Node.js Requirement** | 18+ | 18+ | 18+ | N/A |
| **Dynamic Models** | No | No | No | Possible |
| **LMS Compliance** | V3 | V3 | V3 | V3 Required |
| **Community Tier** | Production | Production | Production | Custom |

---

## Integration Recommendations

### For Code-Heavy Workflows
**Best Choice:** Claude Code
- Strongest code generation
- Rich tool ecosystem
- Mature implementation
- Trade-off: Requires paid subscription

### For Cost-Optimized Solutions
**Best Choice:** Gemini CLI
- Free tier available (API key)
- Fast model (gemini-2.5-flash)
- Production-ready
- Trade-off: Base64 image encoding requirement

### For Advanced Reasoning
**Best Choice:** Codex CLI
- Extended xhigh reasoning
- Autonomous tool approval workflows
- Latest agentic models
- Trade-off: More overhead, fewer tools

### For Custom Requirements
**Best Choice:** Custom Provider
- Implement Language Model Specification V3
- Integrate proprietary models
- Custom tool strategies
- Investment: Moderate development effort

---

## Implementation Checklist

### For Using Existing Providers

- [ ] Install provider package (`npm install ai-sdk-provider-{name}`)
- [ ] Set up authentication (API keys, CLI login, etc.)
- [ ] Create provider instance with configuration
- [ ] Define model constants for your application
- [ ] Implement error handling and retry logic
- [ ] Test with generateText and streamText
- [ ] Monitor token usage and costs

### For Building Custom Providers

- [ ] Review Language Model Specification V3 documentation
- [ ] Create provider package structure
- [ ] Implement ProviderV3 factory
- [ ] Implement LanguageModelV3 with doGenerate and doStream
- [ ] Handle message format conversion
- [ ] Implement error mapping to standard errors
- [ ] Add streaming support
- [ ] Write comprehensive tests
- [ ] Publish to NPM
- [ ] Document installation and configuration
- [ ] Submit to Vercel AI SDK Community Providers

---

## Sources and References

- [Vercel AI SDK - Community Providers](https://ai-sdk.dev/providers/community-providers/)
- [Vercel AI SDK - Codex CLI Provider](https://ai-sdk.dev/providers/community-providers/codex-cli)
- [Vercel AI SDK - Claude Code Provider](https://ai-sdk.dev/providers/community-providers/claude-code)
- [Vercel AI SDK - Gemini CLI Provider](https://ai-sdk.dev/providers/community-providers/gemini-cli)
- [Writing a Custom Provider - AI SDK](https://ai-sdk.dev/providers/community-providers/custom-providers)
- [AI SDK - Foundations: Providers and Models](https://ai-sdk.dev/docs/foundations/providers-and-models)
- [Vercel AI SDK 6 Release Blog](https://vercel.com/blog/ai-sdk-6)
- [AI SDK Core: Providers and Models](https://ai-sdk.dev/docs/ai-sdk-core/providers-and-models)

---

## Conclusion

The Vercel AI SDK ecosystem provides three mature CLI-integrated providers (Codex CLI, Claude Code, Gemini CLI) with distinct strengths:

1. **Codex CLI** excels at advanced agentic reasoning with tool approval workflows
2. **Claude Code** offers the strongest code generation and most mature integration
3. **Gemini CLI** provides cost-optimized solutions with preview model access

None of these providers currently support dynamic model discovery through APIs; models must be maintained as static configurations in your application.

For custom requirements, the Language Model Specification V3 provides a standardized interface enabling development of custom providers that integrate seamlessly with the AI SDK ecosystem. This follows the ACP (AI Community Providers) pattern, allowing new integrations to coexist alongside official providers.

The choice between providers should be driven by specific use case requirements: code generation capability, cost constraints, authentication preferences, and feature availability (images, reasoning, streaming).
