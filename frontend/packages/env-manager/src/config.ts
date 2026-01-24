/**
 * Configuration loader for TraceRTM frontend
 */

import { EnvManager } from "./index";

export interface FrontendConfig {
	// Application
	appEnv: "development" | "staging" | "production";
	appDebug: boolean;

	// API
	apiUrl: string;
	wsUrl: string;
	apiTimeout: number;
	apiRetries: number;

	// Authentication
	workosClientId: string;
	supabaseUrl: string;
	supabaseAnonKey: string;

	// Features
	enableAnalytics: boolean;
	enableSentry: boolean;
	enableDatadog: boolean;

	// Logging
	logLevel: "debug" | "info" | "warn" | "error";
	logFormat: "json" | "text";

	// UI
	theme: "light" | "dark" | "auto";
	locale: string;
}

export function loadFrontendConfig(envManager?: EnvManager): FrontendConfig {
	const env = envManager || new EnvManager();

	const config: FrontendConfig = {
		// Application
		appEnv:
			(env.get("VITE_ENVIRONMENT", "development") as any) || "development",
		appDebug: env.getBoolean("VITE_DEBUG", false),

		// API
		apiUrl: env.getRequired("VITE_API_URL"),
		wsUrl: env.getRequired("VITE_WS_URL"),
		apiTimeout: env.getNumber("VITE_API_TIMEOUT", 30000) || 30000,
		apiRetries: env.getNumber("VITE_API_RETRIES", 3) || 3,

		// Authentication
		workosClientId: env.getRequired("VITE_WORKOS_CLIENT_ID"),
		supabaseUrl: env.get("VITE_SUPABASE_URL") || "",
		supabaseAnonKey: env.get("VITE_SUPABASE_ANON_KEY") || "",

		// Features
		enableAnalytics: env.getBoolean("VITE_ENABLE_ANALYTICS", true),
		enableSentry: env.getBoolean("VITE_ENABLE_SENTRY", false),
		enableDatadog: env.getBoolean("VITE_ENABLE_DATADOG", false),

		// Logging
		logLevel: (env.get("VITE_LOG_LEVEL", "info") as any) || "info",
		logFormat: (env.get("VITE_LOG_FORMAT", "json") as any) || "json",

		// UI
		theme: (env.get("VITE_THEME", "auto") as any) || "auto",
		locale: env.get("VITE_LOCALE") || "en-US",
	};

	return config;
}

export function validateFrontendConfig(config: FrontendConfig): void {
	const errors: string[] = [];

	if (!config.apiUrl) {
		errors.push("VITE_API_URL is required");
	}

	if (!config.wsUrl) {
		errors.push("VITE_WS_URL is required");
	}

	if (!config.workosClientId) {
		errors.push("VITE_WORKOS_CLIENT_ID is required");
	}

	if (config.apiTimeout < 1000) {
		errors.push("VITE_API_TIMEOUT must be at least 1000ms");
	}

	if (config.apiRetries < 0) {
		errors.push("VITE_API_RETRIES must be non-negative");
	}

	if (!["development", "staging", "production"].includes(config.appEnv)) {
		errors.push(`Invalid VITE_ENVIRONMENT: ${config.appEnv}`);
	}

	if (!["debug", "info", "warn", "error"].includes(config.logLevel)) {
		errors.push(`Invalid VITE_LOG_LEVEL: ${config.logLevel}`);
	}

	if (!["light", "dark", "auto"].includes(config.theme)) {
		errors.push(`Invalid VITE_THEME: ${config.theme}`);
	}

	if (errors.length > 0) {
		throw new Error(`Configuration validation failed:\n${errors.join("\n")}`);
	}
}

// Export singleton instance
export const frontendConfig = loadFrontendConfig();
