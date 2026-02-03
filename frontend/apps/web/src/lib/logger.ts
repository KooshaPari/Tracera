/**
 * Centralized logging utility for the application.
 *
 * Features:
 * - Development-only debug/info logging
 * - Production-safe error/warn logging
 * - Consistent log formatting
 * - Security: prevents sensitive data leakage in production
 */

type LogLevel = "debug" | "info" | "warn" | "error";

class Logger {
	private isDev = import.meta.env.DEV;

	/**
	 * Debug level logging - only visible in development
	 * Use for detailed debugging information
	 */
	debug(...args: any[]) {
		if (this.isDev) {
			console.debug("[DEBUG]", ...args);
		}
	}

	/**
	 * Info level logging - only visible in development
	 * Use for general informational messages
	 */
	info(...args: any[]) {
		if (this.isDev) {
			console.info("[INFO]", ...args);
		}
	}

	/**
	 * Warning level logging - visible in all environments
	 * Use for non-critical issues that should be monitored
	 */
	warn(...args: any[]) {
		console.warn("[WARN]", ...args);
	}

	/**
	 * Error level logging - visible in all environments
	 * Use for errors that need attention
	 */
	error(...args: any[]) {
		console.error("[ERROR]", ...args);
	}

	/**
	 * Table logging - only visible in development
	 * Use for displaying tabular data
	 */
	table(data: any, columns?: string[]) {
		if (this.isDev) {
			console.table(data, columns);
		}
	}

	/**
	 * Group logging - only visible in development
	 * Use for grouping related log messages
	 */
	group(label: string) {
		if (this.isDev) {
			console.group(label);
		}
	}

	/**
	 * Collapsed group logging - only visible in development
	 */
	groupCollapsed(label: string) {
		if (this.isDev) {
			console.groupCollapsed(label);
		}
	}

	/**
	 * End group logging - only visible in development
	 */
	groupEnd() {
		if (this.isDev) {
			console.groupEnd();
		}
	}

	/**
	 * Time tracking - only visible in development
	 */
	time(label: string) {
		if (this.isDev) {
			console.time(label);
		}
	}

	/**
	 * End time tracking - only visible in development
	 */
	timeEnd(label: string) {
		if (this.isDev) {
			console.timeEnd(label);
		}
	}
}

export const logger = new Logger();
