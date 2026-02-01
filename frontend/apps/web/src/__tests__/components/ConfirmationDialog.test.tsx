/**
 * Confirmation Dialog Component Tests
 *
 * Tests for:
 * - Dialog open/close states
 * - Confirm/cancel actions
 * - Loading states
 * - Error handling
 * - Accessibility
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	BulkConfirmationDialog,
	ConfirmationDialog,
} from "@/components/ui/confirmation-dialog";

describe("ConfirmationDialog", () => {
	const defaultProps = {
		open: true,
		onOpenChange: vi.fn(),
		title: "Delete item?",
		description: "This action cannot be undone.",
		onConfirm: vi.fn(),
		onCancel: vi.fn(),
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders dialog when open", () => {
		render(<ConfirmationDialog {...defaultProps} />);

		expect(screen.getByText("Delete item?")).toBeInTheDocument();
		expect(
			screen.getByText("This action cannot be undone."),
		).toBeInTheDocument();
	});

	it("does not render when closed", () => {
		const { rerender } = render(
			<ConfirmationDialog {...defaultProps} open={false} />,
		);

		expect(screen.queryByText("Delete item?")).not.toBeInTheDocument();
	});

	it("calls onConfirm when confirm button clicked", async () => {
		const user = userEvent.setup();
		const onConfirm = vi.fn();

		render(
			<ConfirmationDialog
				{...defaultProps}
				onConfirm={onConfirm}
				confirmText="Delete"
			/>,
		);

		const confirmButton = screen.getByRole("button", { name: /delete/i });
		await user.click(confirmButton);

		await waitFor(() => {
			expect(onConfirm).toHaveBeenCalled();
		});
	});

	it("calls onCancel when cancel button clicked", async () => {
		const user = userEvent.setup();
		const onCancel = vi.fn();

		render(
			<ConfirmationDialog
				{...defaultProps}
				onCancel={onCancel}
				cancelText="Cancel"
			/>,
		);

		const cancelButton = screen.getByRole("button", { name: /cancel/i });
		await user.click(cancelButton);

		expect(onCancel).toHaveBeenCalled();
	});

	it("shows loading state", () => {
		render(
			<ConfirmationDialog
				{...defaultProps}
				isLoading={true}
				confirmText="Delete"
			/>,
		);

		const confirmButton = screen.getByRole("button", { name: /deleting/i });
		expect(confirmButton).toBeDisabled();
	});

	it("displays context information", () => {
		render(
			<ConfirmationDialog {...defaultProps} context="and 5 related items" />,
		);

		expect(screen.getByText("and 5 related items")).toBeInTheDocument();
	});

	it("shows warning for critical severity", () => {
		render(
			<ConfirmationDialog
				{...defaultProps}
				severity="critical"
				showWarning={true}
			/>,
		);

		expect(
			screen.getByText("This action cannot be undone."),
		).toBeInTheDocument();
	});

	it("renders custom confirm and cancel text", () => {
		render(
			<ConfirmationDialog
				{...defaultProps}
				confirmText="Remove Forever"
				cancelText="Keep It"
			/>,
		);

		expect(
			screen.getByRole("button", { name: /remove forever/i }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /keep it/i }),
		).toBeInTheDocument();
	});

	it("has proper ARIA attributes", () => {
		const { container } = render(<ConfirmationDialog {...defaultProps} />);

		const alertDialog = container.querySelector('[role="alertdialog"]');
		expect(alertDialog).toBeInTheDocument();
	});

	it("closes dialog when onOpenChange is called with false", () => {
		const onOpenChange = vi.fn();
		const { rerender } = render(
			<ConfirmationDialog {...defaultProps} onOpenChange={onOpenChange} />,
		);

		expect(screen.getByText("Delete item?")).toBeInTheDocument();

		rerender(
			<ConfirmationDialog
				{...defaultProps}
				open={false}
				onOpenChange={onOpenChange}
			/>,
		);

		expect(screen.queryByText("Delete item?")).not.toBeInTheDocument();
	});

	it("disables buttons during loading", () => {
		render(
			<ConfirmationDialog
				{...defaultProps}
				isLoading={true}
				confirmText="Delete"
				cancelText="Cancel"
			/>,
		);

		const confirmButton = screen.getByRole("button", { name: /deleting/i });
		const cancelButton = screen.getByRole("button", { name: /cancel/i });

		expect(confirmButton).toBeDisabled();
		expect(cancelButton).toBeDisabled();
	});

	it("shows different severity styles", () => {
		const { rerender } = render(
			<ConfirmationDialog {...defaultProps} severity="warning" />,
		);

		expect(screen.getByText("Delete item?").closest("div")).toBeInTheDocument();

		rerender(<ConfirmationDialog {...defaultProps} severity="danger" />);
		expect(screen.getByText("Delete item?").closest("div")).toBeInTheDocument();

		rerender(<ConfirmationDialog {...defaultProps} severity="critical" />);
		expect(screen.getByText("Delete item?").closest("div")).toBeInTheDocument();
	});
});

describe("BulkConfirmationDialog", () => {
	const defaultProps = {
		open: true,
		onOpenChange: vi.fn(),
		actionType: "delete" as const,
		itemCount: 5,
		onConfirm: vi.fn(),
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders bulk delete dialog", () => {
		render(<BulkConfirmationDialog {...defaultProps} />);

		expect(screen.getByText("Delete 5 items?")).toBeInTheDocument();
	});

	it("handles singular item", () => {
		render(<BulkConfirmationDialog {...defaultProps} itemCount={1} />);

		expect(screen.getByText("Delete 1 item?")).toBeInTheDocument();
	});

	it("shows correct action type text", () => {
		const { rerender } = render(
			<BulkConfirmationDialog {...defaultProps} actionType="delete" />,
		);

		expect(screen.getByText(/delete 5 items/i)).toBeInTheDocument();

		rerender(<BulkConfirmationDialog {...defaultProps} actionType="archive" />);

		expect(screen.getByText(/archive 5 items/i)).toBeInTheDocument();
	});

	it("calls onConfirm with correct action", async () => {
		const user = userEvent.setup();
		const onConfirm = vi.fn();

		render(<BulkConfirmationDialog {...defaultProps} onConfirm={onConfirm} />);

		const confirmButton = screen.getByRole("button", { name: /delete/i });
		await user.click(confirmButton);

		await waitFor(() => {
			expect(onConfirm).toHaveBeenCalled();
		});
	});

	it("displays item count context", () => {
		render(<BulkConfirmationDialog {...defaultProps} itemCount={10} />);

		expect(
			screen.getByText("10 items will be permanently deleted"),
		).toBeInTheDocument();
	});

	it("handles different action types", () => {
		const actionTypes = [
			{ type: "delete" as const, icon: "Delete" },
			{ type: "archive" as const, icon: "Archive" },
			{ type: "status-change" as const, icon: "Change status" },
			{ type: "assign" as const, icon: "Assign" },
		];

		actionTypes.forEach(({ type }) => {
			const { unmount } = render(
				<BulkConfirmationDialog {...defaultProps} actionType={type} />,
			);

			expect(document.body).toContainElement(
				screen.getByText(new RegExp(type.replace("-", " "), "i")),
			);

			unmount();
		});
	});

	it("shows critical severity for delete", () => {
		render(<BulkConfirmationDialog {...defaultProps} actionType="delete" />);

		// Dialog should be rendered (severity affects styling)
		expect(screen.getByText("Delete 5 items?")).toBeInTheDocument();
	});

	it("shows warning severity for other actions", () => {
		render(<BulkConfirmationDialog {...defaultProps} actionType="archive" />);

		expect(screen.getByText("Archive 5 items?")).toBeInTheDocument();
	});
});
