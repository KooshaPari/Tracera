import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MobileMenu } from "@/components/mobile";

// Mock dependencies
vi.mock("@tanstack/react-router", () => ({
	useNavigate: vi.fn(() => vi.fn()),
	useLocation: vi.fn(() => ({
		pathname: "/",
	})),
}));

vi.mock("@/stores/authStore", () => ({
	useAuthStore: vi.fn(() => ({
		user: {
			name: "Test User",
			email: "test@example.com",
			role: "user",
		},
		logout: vi.fn(),
	})),
}));

describe("MobileMenu", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders hamburger button", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		expect(button).toBeInTheDocument();
	});

	it("has minimum 44x44px touch target for hamburger button", () => {
		const { container } = render(<MobileMenu />);

		const button = container.querySelector("button");
		expect(button).toHaveClass("h-11", "w-11");
		// 44px = h-11 and w-11 in tailwind
	});

	it("toggles menu visibility when button is clicked", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");

		// Menu should be closed initially
		let menuPanel = document.getElementById("mobile-menu");
		expect(menuPanel).toHaveClass("-translate-x-full");

		// Click to open
		fireEvent.click(button);
		menuPanel = document.getElementById("mobile-menu");
		expect(menuPanel).toHaveClass("translate-x-0");
	});

	it("displays user information in menu", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		fireEvent.click(button);

		expect(screen.getByText("Test User")).toBeInTheDocument();
		expect(screen.getByText("test@example.com")).toBeInTheDocument();
	});

	it("closes menu when backdrop is clicked", () => {
		const { container } = render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		fireEvent.click(button);

		const backdrop = container.querySelector(".bg-black/50");
		if (backdrop) {
			fireEvent.click(backdrop);
		}

		const menuPanel = document.getElementById("mobile-menu");
		expect(menuPanel).toHaveClass("-translate-x-full");
	});

	it("closes menu when escape key is pressed", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		fireEvent.click(button);

		fireEvent.keyDown(window, { key: "Escape" });

		const menuPanel = document.getElementById("mobile-menu");
		expect(menuPanel).toHaveClass("-translate-x-full");
	});

	it("has minimum 52px height for menu items", () => {
		const { container } = render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		fireEvent.click(button);

		const menuItems = container.querySelectorAll(".min-h-\\[52px\\]");
		expect(menuItems.length).toBeGreaterThan(0);
	});

	it("renders accessibility attributes", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		expect(button).toHaveAttribute("aria-expanded", "false");
		expect(button).toHaveAttribute("aria-controls", "mobile-menu");
	});

	it("displays logout button with proper styling", () => {
		render(<MobileMenu />);

		const button = screen.getByLabelText("Open menu");
		fireEvent.click(button);

		const logoutButton = screen.getByText("Log out").closest("button");
		expect(logoutButton).toHaveClass("min-h-[52px]");
		expect(logoutButton).toHaveClass("text-destructive");
	});

	it("hides menu on desktop (md: breakpoint)", () => {
		render(<MobileMenu />);

		const button = screen.getByRole("button", {
			name: /open menu|close menu/i,
		});
		expect(button).toHaveClass("md:hidden");
	});
});
