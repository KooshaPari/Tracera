/**
 * CreateItemDialog Tests
 *
 * Tests for the unified multi-step item creation dialog
 */

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CreateItemDialog } from "./CreateItemDialog";

describe("CreateItemDialog", () => {
	const defaultProps = {
		open: true,
		onOpenChange: vi.fn(),
		projectId: "test-project-123",
		defaultView: "TEST" as const,
	};

	it("renders type selection dialog when open", () => {
		render(<CreateItemDialog {...defaultProps} />);

		expect(screen.getByText("Create New Item")).toBeInTheDocument();
		expect(
			screen.getByText("Select the type of item you want to create"),
		).toBeInTheDocument();
	});

	it("does not render when closed", () => {
		render(<CreateItemDialog {...defaultProps} open={false} />);

		expect(screen.queryByText("Create New Item")).not.toBeInTheDocument();
	});

	it("calls onOpenChange when cancel is clicked", () => {
		const onOpenChange = vi.fn();
		render(<CreateItemDialog {...defaultProps} onOpenChange={onOpenChange} />);

		const cancelButton = screen.getByText("Cancel");
		fireEvent.click(cancelButton);

		expect(onOpenChange).toHaveBeenCalledWith(false);
	});

	it("shows type selector for TEST view", () => {
		render(<CreateItemDialog {...defaultProps} defaultView="TEST" />);

		// ItemTypeSelector should render test-related types
		// This is a basic check - more detailed tests should be in ItemTypeSelector.test.tsx
		expect(screen.getByText("Create New Item")).toBeInTheDocument();
	});

	// Note: Testing the full flow (select type -> show form) requires
	// mocking the type-specific forms, which is beyond the scope of this basic test
});
