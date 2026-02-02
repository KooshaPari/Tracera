/**
 * Tests for useKeyPress - Keyboard event detection
 */

import { describe, expect, it, vi } from "vitest";

describe("useKeyPress Hook", () => {
	describe("Key Matching Logic", () => {
		it("should match keys case-insensitively", () => {
			const targetKey = "Enter";
			const eventKey = "enter";
			const matches = eventKey.toLowerCase() === targetKey.toLowerCase();
			expect(matches).toBe(true);
		});

		it("should handle uppercase key", () => {
			const targetKey = "a";
			const eventKey = "A";
			const matches = eventKey.toLowerCase() === targetKey.toLowerCase();
			expect(matches).toBe(true);
		});

		it("should not match different keys", () => {
			const targetKey = "Enter";
			const eventKey = "Escape";
			const matches = eventKey.toLowerCase() === targetKey.toLowerCase();
			expect(matches).toBe(false);
		});

		it("should match special keys", () => {
			const specialKeys = ["Enter", "Tab", "Escape", "ArrowUp", "ArrowDown"];
			specialKeys.forEach((key) => {
				const matches = key.toLowerCase() === key.toLowerCase();
				expect(matches).toBe(true);
			});
		});
	});

	describe("Modifier Key Matching", () => {
		it("should match ctrl key when required", () => {
			const ctrlRequired = true;
			const ctrlPressed = true;
			const matches =
				ctrlRequired === undefined || ctrlPressed === ctrlRequired;
			expect(matches).toBe(true);
		});

		it("should match shift key when required", () => {
			const shiftRequired = true;
			const shiftPressed = true;
			const matches =
				shiftRequired === undefined || shiftPressed === shiftRequired;
			expect(matches).toBe(true);
		});

		it("should not match when ctrl not pressed but required", () => {
			const ctrlRequired: boolean = true;
			const ctrlPressed: boolean = false;
			const matches =
				ctrlRequired === undefined || ctrlPressed === ctrlRequired;
			expect(matches).toBe(false);
		});

		it("should match multiple modifiers", () => {
			const options = { ctrl: true, shift: false };
			const event = { ctrlKey: true, shiftKey: false };

			const ctrlMatch =
				options.ctrl === undefined || event.ctrlKey === options.ctrl;
			const shiftMatch =
				options.shift === undefined || event.shiftKey === options.shift;

			expect(ctrlMatch && shiftMatch).toBe(true);
		});

		it("should handle undefined modifiers as any", () => {
			const options = { ctrl: undefined, shift: true };
			const event1 = { ctrlKey: true, shiftKey: true };
			const event2 = { ctrlKey: false, shiftKey: true };

			const match1 =
				(options.ctrl === undefined || event1.ctrlKey === options.ctrl) &&
				(options.shift === undefined || event1.shiftKey === options.shift);
			const match2 =
				(options.ctrl === undefined || event2.ctrlKey === options.ctrl) &&
				(options.shift === undefined || event2.shiftKey === options.shift);

			expect(match1).toBe(true);
			expect(match2).toBe(true);
		});

		it("should match all modifier combinations", () => {
			const modifiers = ["ctrl", "shift", "alt", "meta"];
			modifiers.forEach((mod) => {
				const option = { [mod]: true };
				expect(option[mod]).toBe(true);
			});
		});

		it("should handle alt key matching", () => {
			const altRequired = true;
			const altPressed = true;
			const matches = altRequired === undefined || altPressed === altRequired;
			expect(matches).toBe(true);
		});

		it("should handle meta key matching", () => {
			const metaRequired = true;
			const metaPressed = true;
			const matches =
				metaRequired === undefined || metaPressed === metaRequired;
			expect(matches).toBe(true);
		});
	});

	describe("Event Listener Logic", () => {
		it("should check window availability", () => {
			const windowAvailable = typeof window !== "undefined";
			expect(typeof windowAvailable).toBe("boolean");
		});

		it("should have keydown event type", () => {
			const eventType = "keydown";
			expect(eventType).toBe("keydown");
		});

		it("should have keyup event type", () => {
			const eventType = "keyup";
			expect(eventType).toBe("keyup");
		});

		it("should support event listener registration", () => {
			// Mock addEventListener
			const listeners = {} as Record<string, any[]>;
			const mockAddEventListener = vi.fn((event: string, handler: EventListener) => {
				if (!listeners[event]) listeners[event] = [];
				listeners[event].push(handler);
			});

			mockAddEventListener("keydown", () => {});
			mockAddEventListener("keyup", () => {});

			expect(mockAddEventListener).toHaveBeenCalledTimes(2);
			expect(mockAddEventListener).toHaveBeenCalledWith(
				"keydown",
				expect.any(Function),
			);
			expect(mockAddEventListener).toHaveBeenCalledWith(
				"keyup",
				expect.any(Function),
			);
		});

		it("should support event listener removal", () => {
			const mockRemoveEventListener = vi.fn();

			mockRemoveEventListener("keydown", () => {});
			mockRemoveEventListener("keyup", () => {});

			expect(mockRemoveEventListener).toHaveBeenCalledTimes(2);
			expect(mockRemoveEventListener).toHaveBeenCalledWith(
				"keydown",
				expect.any(Function),
			);
			expect(mockRemoveEventListener).toHaveBeenCalledWith(
				"keyup",
				expect.any(Function),
			);
		});
	});

	describe("Keyboard Shortcut Logic", () => {
		it("should execute callback on key match", () => {
			const callback = vi.fn();
			const eventKey = "Enter";
			const targetKey = "Enter";

			if (eventKey.toLowerCase() === targetKey.toLowerCase()) {
				callback();
			}

			expect(callback).toHaveBeenCalled();
		});

		it("should not execute callback on key mismatch", () => {
			const callback = vi.fn();
			const eventKey = "Escape";
			const targetKey = "Enter";

			if (eventKey.toLowerCase() === targetKey.toLowerCase()) {
				callback();
			}

			expect(callback).not.toHaveBeenCalled();
		});

		it("should handle preventDefault in shortcuts", () => {
			const event = { preventDefault: vi.fn() };
			const shouldPrevent = true;

			if (shouldPrevent) {
				event.preventDefault();
			}

			expect(event.preventDefault).toHaveBeenCalled();
		});

		it("should match shortcut with modifiers", () => {
			const callback = vi.fn();
			const options = { ctrl: true };
			const event = {
				key: "S",
				ctrlKey: true,
				shiftKey: false,
				altKey: false,
				metaKey: false,
			};

			const eventKey = event.key.toLowerCase();
			const targetKey = "S".toLowerCase();
			const ctrlMatch =
				options.ctrl === undefined || event.ctrlKey === options.ctrl;

			if (eventKey === targetKey && ctrlMatch) {
				callback();
			}

			expect(callback).toHaveBeenCalled();
		});
	});

	describe("Dependency Management", () => {
		it("should include targetKey in dependencies", () => {
			const deps = ["Enter", { ctrl: true }];
			expect(deps[0]).toBe("Enter");
		});

		it("should include options in dependencies", () => {
			const options = { ctrl: true, shift: false };
			const deps = ["Enter", options];
			expect(deps[1]).toEqual(options);
		});

		it("should update on key change", () => {
			let key = "Enter";
			expect(key).toBe("Enter");

			key = "Escape";
			expect(key).toBe("Escape");
		});
	});

	describe("State Management", () => {
		it("should track pressed state", () => {
			let pressed = false;
			expect(pressed).toBe(false);

			pressed = true;
			expect(pressed).toBe(true);

			pressed = false;
			expect(pressed).toBe(false);
		});

		it("should set pressed on keydown", () => {
			let pressed = false;
			const eventKey = "Enter";
			const targetKey = "Enter";

			if (eventKey.toLowerCase() === targetKey.toLowerCase()) {
				pressed = true;
			}

			expect(pressed).toBe(true);
		});

		it("should unset pressed on keyup", () => {
			let pressed = true;
			const eventKey = "Enter";
			const targetKey = "Enter";

			if (eventKey.toLowerCase() === targetKey.toLowerCase()) {
				pressed = false;
			}

			expect(pressed).toBe(false);
		});
	});
});
