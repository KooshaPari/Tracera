// Mock elkjs before any imports
import { vi } from "vitest";

vi.mock("elkjs", () => ({
	default: class MockELK {
		layout() {
			return Promise.resolve({ children: [], edges: [] });
		}
	},
}));

// Mock clipboard
Object.assign(navigator, {
	clipboard: {
		writeText: vi.fn(() => Promise.resolve()),
	},
});
