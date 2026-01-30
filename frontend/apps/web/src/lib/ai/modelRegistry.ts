/**
 * Static AI Model Registry for TraceRTM
 *
 * CLI providers don't support dynamic model listing, so we maintain a static registry.
 * Update this file when new models become available.
 */

import type { AIModel, AIProvider, AIProviderConfig } from "./types";

/** All available AI providers and their models */
export const AI_PROVIDERS: AIProviderConfig[] = [
	{
		id: "claude",
		name: "Claude (Anthropic)",
		enabled: true,
		models: [
			{
				id: "claude-sonnet-4-20250514",
				name: "Claude Sonnet 4",
				provider: "claude",
				description: "Fast, balanced model for most tasks",
				contextWindow: 200000,
				maxOutput: 8192,
			},
			{
				id: "claude-opus-4-20250514",
				name: "Claude Opus 4",
				provider: "claude",
				description: "Most capable model for complex reasoning",
				contextWindow: 200000,
				maxOutput: 8192,
			},
			{
				id: "claude-3-5-haiku-20241022",
				name: "Claude 3.5 Haiku",
				provider: "claude",
				description: "Fastest model for quick tasks",
				contextWindow: 200000,
				maxOutput: 8192,
			},
		],
	},
	{
		id: "codex",
		name: "OpenAI Codex",
		enabled: false, // Enable when API key is configured
		models: [
			{
				id: "gpt-4o",
				name: "GPT-4o",
				provider: "codex",
				description: "Latest multimodal model",
				contextWindow: 128000,
				maxOutput: 16384,
			},
			{
				id: "gpt-4-turbo",
				name: "GPT-4 Turbo",
				provider: "codex",
				description: "Fast GPT-4 variant",
				contextWindow: 128000,
				maxOutput: 4096,
			},
		],
	},
	{
		id: "gemini",
		name: "Gemini (Google)",
		enabled: false, // Enable when API key is configured
		models: [
			{
				id: "gemini-2.0-flash",
				name: "Gemini 2.0 Flash",
				provider: "gemini",
				description: "Fast, efficient model",
				contextWindow: 1000000,
				maxOutput: 8192,
			},
			{
				id: "gemini-1.5-pro",
				name: "Gemini 1.5 Pro",
				provider: "gemini",
				description: "Advanced reasoning model",
				contextWindow: 2000000,
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
export function getProvider(
	providerId: AIProvider,
): AIProviderConfig | undefined {
	return AI_PROVIDERS.find((p) => p.id === providerId);
}

/** Get model by ID */
export function getModel(modelId: string): AIModel | undefined {
	return AI_PROVIDERS.flatMap((p) => p.models).find((m) => m.id === modelId);
}

/** Get default model (Claude Sonnet) */
export function getDefaultModel(): AIModel {
	const claudeProvider = AI_PROVIDERS.find((p) => p.id === "claude");
	const model = claudeProvider?.models[0] ?? AI_PROVIDERS[0]?.models[0];
	if (!model) {
		throw new Error("No AI models configured");
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
