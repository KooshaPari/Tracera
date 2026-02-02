/**
 * Type definitions for jest-axe with Vitest
 */
declare global {
	namespace Vi {
		interface Matchers<R = unknown> {
			toHaveNoViolations(): R;
		}
	}
}

export {};
