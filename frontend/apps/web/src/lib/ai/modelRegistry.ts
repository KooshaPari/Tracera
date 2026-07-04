/**
 * Static AI Model Registry for TraceRTM
 *
 * CLI providers don't support dynamic model listing, so we maintain a static registry.
 * Update this file when new models become available.
 */

import type { AIModel, AIProvider, AIProviderConfig } from './types';

/** All available AI providers and their models. Keep IDs in sync with backend (ai_service, chat schema). Model IDs must match provider APIs exactly. */
export const AI_PROVIDERS: AIProviderConfig[] = [
  {
    id: 'claude',
    name: 'Claude (Anthropic)',
    enabled: true,
    models: [
      {
        id: 'claude-sonnet-4-5-20250929',
        name: 'Claude Sonnet 4.5',
        provider: 'claude',
        description: 'Recommended: best balance of intelligence, speed, and cost',
        contextWindow: 200000,
        maxOutput: 65536,
      },
      {
        id: 'claude-sonnet-4-20250514',
        name: 'Claude Sonnet 4',
        provider: 'claude',
        description: 'Backend default; fast, balanced for most tasks',
        contextWindow: 200000,
        maxOutput: 8192,
      },
      {
        id: 'claude-haiku-4-5-20251001',
        name: 'Claude Haiku 4.5',
        provider: 'claude',
        description: 'Fastest model with near-frontier intelligence',
        contextWindow: 200000,
        maxOutput: 65536,
      },
      {
        id: 'claude-opus-4-5-20251101',
        name: 'Claude Opus 4.5',
        provider: 'claude',
        description: 'Premium model for maximum intelligence',
        contextWindow: 200000,
        maxOutput: 65536,
      },
      {
        id: 'claude-opus-4-20250514',
        name: 'Claude Opus 4',
        provider: 'claude',
        description: 'Most capable for complex reasoning',
        contextWindow: 200000,
        maxOutput: 8192,
      },
      {
        id: 'claude-3-5-haiku-20241022',
        name: 'Claude 3.5 Haiku',
        provider: 'claude',
        description: 'Legacy fast model for quick tasks',
        contextWindow: 200000,
        maxOutput: 8192,
      },
    ],
  },
  {
    id: 'codex',
    name: 'OpenAI',
    enabled: false, // Enable when API key is configured
    models: [
      {
        id: 'gpt-5.2',
        name: 'GPT-5.2',
        provider: 'codex',
        description: 'Best for coding and agentic tasks',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-5.2-pro',
        name: 'GPT-5.2 pro',
        provider: 'codex',
        description: 'Smarter and more precise than GPT-5.2',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-5-mini',
        name: 'GPT-5 mini',
        provider: 'codex',
        description: 'Faster, cost-efficient for well-defined tasks',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-5-nano',
        name: 'GPT-5 nano',
        provider: 'codex',
        description: 'Fastest, most cost-efficient GPT-5',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-4.1',
        name: 'GPT-4.1',
        provider: 'codex',
        description: 'Smartest non-reasoning model',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-4o',
        name: 'GPT-4o',
        provider: 'codex',
        description: 'Fast, intelligent, flexible',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'gpt-4o-mini',
        name: 'GPT-4o mini',
        provider: 'codex',
        description: 'Fast, affordable for focused tasks',
        contextWindow: 128000,
        maxOutput: 16384,
      },
      {
        id: 'o3',
        name: 'o3',
        provider: 'codex',
        description: 'Reasoning model for complex tasks (succeeded by GPT-5)',
        contextWindow: 200000,
        maxOutput: 100000,
      },
      {
        id: 'o4-mini',
        name: 'o4 mini',
        provider: 'codex',
        description: 'Fast, cost-efficient reasoning (succeeded by GPT-5 mini)',
        contextWindow: 128000,
        maxOutput: 65536,
      },
    ],
  },
  {
    id: 'gemini',
    name: 'Gemini (Google)',
    enabled: false, // Enable when API key is configured
    models: [
      {
        id: 'gemini-3-pro-preview',
        name: 'Gemini 3 Pro',
        provider: 'gemini',
        description: 'Most capable; multimodal, agentic, reasoning',
        contextWindow: 1048576,
        maxOutput: 65536,
      },
      {
        id: 'gemini-3-flash-preview',
        name: 'Gemini 3 Flash',
        provider: 'gemini',
        description: 'Balanced speed, scale, and intelligence',
        contextWindow: 1048576,
        maxOutput: 65536,
      },
      {
        id: 'gemini-2.5-flash',
        name: 'Gemini 2.5 Flash',
        provider: 'gemini',
        description: 'Best price-performance; thinking, agentic',
        contextWindow: 1048576,
        maxOutput: 65536,
      },
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro',
        provider: 'gemini',
        description: 'State-of-the-art thinking; long context',
        contextWindow: 1048576,
        maxOutput: 65536,
      },
      {
        id: 'gemini-2.5-flash-lite',
        name: 'Gemini 2.5 Flash-Lite',
        provider: 'gemini',
        description: 'Fastest flash; cost-efficient, high throughput',
        contextWindow: 1048576,
        maxOutput: 65536,
      },
      {
        id: 'gemini-2.0-flash',
        name: 'Gemini 2.0 Flash',
        provider: 'gemini',
        description: '1M context; native tool use',
        contextWindow: 1048576,
        maxOutput: 8192,
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        provider: 'gemini',
        description: 'Advanced reasoning, long context',
        contextWindow: 2000000,
        maxOutput: 8192,
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        provider: 'gemini',
        description: 'Fast with long context',
        contextWindow: 1000000,
        maxOutput: 8192,
      },
    ],
  },
];

/** Get all enabled providers */
export function getEnabledProviders(): AIProviderConfig[] {
  return AI_PROVIDERS.filter((p) => p.enabled);
}

/** Get all available models from enabled providers */
export function getAvailableModels(): AIModel[] {
  return getEnabledProviders().flatMap((p) => p.models);
}

/** Get provider by ID */
export function getProvider(providerId: AIProvider): AIProviderConfig | undefined {
  return AI_PROVIDERS.find((p) => p.id === providerId);
}

/** Get model by ID */
export function getModel(modelId: string): AIModel | undefined {
  return AI_PROVIDERS.flatMap((p) => p.models).find((m) => m.id === modelId);
}

/** Get default model (Claude Sonnet) */
export function getDefaultModel(): AIModel {
  const claudeProvider = AI_PROVIDERS.find((p) => p.id === 'claude');
  const model = claudeProvider?.models[0] ?? AI_PROVIDERS[0]?.models[0];
  if (!model) {
    throw new Error('No AI models configured');
  }
  return model;
}

/** Group models by provider for UI display */
export function getModelsGroupedByProvider(): Map<AIProviderConfig, AIModel[]> {
  const grouped = new Map<AIProviderConfig, AIModel[]>();
  for (const provider of getEnabledProviders()) {
    grouped.set(provider, provider.models);
  }
  return grouped;
}
