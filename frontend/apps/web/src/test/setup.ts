import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { toHaveNoViolations } from "jest-axe";
import { afterEach, beforeEach } from "vitest";
import { expect } from "vitest";

expect.extend({ toHaveNoViolations });

afterEach(() => {
	cleanup();
});

beforeEach(() => {
	globalThis.user = userEvent.setup();
});
