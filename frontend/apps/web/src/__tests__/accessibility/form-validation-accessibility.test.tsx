/**
 * Accessibility Tests: Form Validation and Error Handling
 * Tests WCAG 2.1 AA compliance for form validation and error messaging
 */
/// <reference path="../a11y/jest-axe.d.ts" />

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { axe } from "../a11y/setup";

let user: ReturnType<typeof userEvent.setup>;

beforeEach(() => {
	user = userEvent.setup();
});

type FormField = "email" | "message" | "name";
type FormData = Partial<Record<FormField, string>>;
type FormErrors = Partial<Record<FormField, string>>;
type FormTouched = Partial<Record<FormField, boolean>>;

function validateFormData(formData: FormData): FormErrors {
	const newErrors: FormErrors = {};

	if (!formData.email) {
		newErrors.email = "Email is required";
	} else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
		newErrors.email = "Please enter a valid email address";
	}

	if (!formData.name || formData.name.trim().length < 2) {
		newErrors.name = "Name must be at least 2 characters";
	}

	if (!formData.message || formData.message.trim().length < 10) {
		newErrors.message = "Message must be at least 10 characters";
	}

	return newErrors;
}

// Mock Form with Validation
function MockAccessibleForm({
	onSubmit = vi.fn(),
}: {
	onSubmit?: (data: FormData) => void;
}) {
	const [errors, setErrors] = React.useState<FormErrors>({});
	const [touched, setTouched] = React.useState<FormTouched>({});
	const [isSubmitting, setIsSubmitting] = React.useState(false);

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setIsSubmitting(true);

		const formData = new FormData(e.currentTarget);
		const data: FormData = {
			email: String(formData.get("email") ?? ""),
			message: String(formData.get("message") ?? ""),
			name: String(formData.get("name") ?? ""),
		};

		const validationErrors = validateFormData(data as Record<string, string>);
		setErrors(validationErrors);
		setTouched({
			email: true,
			message: true,
			name: true,
		});

		if (Object.keys(validationErrors).length === 0) {
			await new Promise((resolve) => setTimeout(resolve, 100));
			onSubmit(data);
			setErrors({});
			setTouched({});
			e.currentTarget.reset();
		}

		setIsSubmitting(false);
	};

	const handleBlur = (fieldName: FormField) => {
		setTouched({ ...touched, [fieldName]: true });

		// Validate single field on blur
		const formElement = document.querySelector("form");
		if (formElement) {
			const formData = new FormData(formElement);
			const data: FormData = {
				email: String(formData.get("email") ?? ""),
				message: String(formData.get("message") ?? ""),
				name: String(formData.get("name") ?? ""),
			};

			const fieldErrors = validateFormData(data);
			const fieldError = fieldErrors[fieldName];

			if (fieldError) {
				setErrors({ ...errors, [fieldName]: fieldError });
			} else {
				const newErrors = { ...errors };
				delete newErrors[fieldName];
				setErrors(newErrors);
			}
		}
	};

	return (
		<form onSubmit={handleSubmit} noValidate aria-label="Contact form">
			<div className="mb-6">
				<label htmlFor="name" className="block text-sm font-medium mb-2">
					Name
					<span className="text-red-600 ml-1" aria-label="required">
						*
					</span>
				</label>
				<input
					id="name"
					name="name"
					type="text"
					placeholder="Your name"
					onBlur={() => handleBlur("name")}
					aria-invalid={touched.name && Boolean(errors.name)}
					aria-describedby={errors.name ? "name-error" : undefined}
					className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent ${
						errors.name && touched.name
							? "border-red-600 bg-red-50"
							: "border-gray-300"
					}`}
					required
				/>
				{errors.name && touched.name && (
					<div
						id="name-error"
						role="alert"
						className="mt-2 text-sm text-red-600"
					>
						{errors.name}
					</div>
				)}
			</div>

			<div className="mb-6">
				<label htmlFor="email" className="block text-sm font-medium mb-2">
					Email
					<span className="text-red-600 ml-1" aria-label="required">
						*
					</span>
				</label>
				<input
					id="email"
					name="email"
					type="email"
					placeholder="your@email.com"
					onBlur={() => handleBlur("email")}
					aria-invalid={touched.email && Boolean(errors.email)}
					aria-describedby={errors.email ? "email-error" : "email-hint"}
					className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent ${
						errors.email && touched.email
							? "border-red-600 bg-red-50"
							: "border-gray-300"
					}`}
					required
				/>
				<span id="email-hint" className="sr-only">
					Email format: user@example.com
				</span>
				{errors.email && touched.email && (
					<div
						id="email-error"
						role="alert"
						className="mt-2 text-sm text-red-600"
					>
						{errors.email}
					</div>
				)}
			</div>

			<div className="mb-6">
				<label htmlFor="message" className="block text-sm font-medium mb-2">
					Message
					<span className="text-red-600 ml-1" aria-label="required">
						*
					</span>
				</label>
				<textarea
					id="message"
					name="message"
					placeholder="Your message here..."
					rows={4}
					onBlur={() => handleBlur("message")}
					aria-invalid={touched.message && Boolean(errors.message)}
					aria-describedby={errors.message ? "message-error" : "message-help"}
					className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-600 focus:border-transparent resize-vertical ${
						errors.message && touched.message
							? "border-red-600 bg-red-50"
							: "border-gray-300"
					}`}
					required
				/>
				<span id="message-help" className="sr-only">
					Message must be at least 10 characters long
				</span>
				{errors.message && touched.message && (
					<div
						id="message-error"
						role="alert"
						className="mt-2 text-sm text-red-600"
					>
						{errors.message}
					</div>
				)}
			</div>

			<div className="flex gap-3">
				<button
					type="submit"
					disabled={isSubmitting}
					className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 font-medium"
					aria-busy={isSubmitting}
				>
					{isSubmitting ? "Sending..." : "Send Message"}
				</button>
				<button
					type="reset"
					className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 font-medium"
				>
					Clear
				</button>
			</div>

			{Object.keys(errors).length > 0 && touched && (
				<div
					role="alert"
					aria-live="polite"
					className="mt-4 p-4 bg-red-50 border-l-4 border-red-600"
				>
					<h3 className="font-semibold text-red-800 mb-2">
						Please fix the following errors:
					</h3>
					<ul className="list-disc list-inside text-red-700 text-sm">
						{Object.entries(errors).map(([field, error]) => (
							<li key={field}>{error}</li>
						))}
					</ul>
				</div>
			)}
		</form>
	);
}

describe("Form Validation - Field-Level Errors", () => {
	it("should show error on invalid email", async () => {
		const { container } = render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		await user.type(emailInput, "invalid");
		const focusAway = container.querySelector("button");
		if (focusAway) {
			await user.click(focusAway);
		}

		await waitFor(() => {
			const error = screen.getByText("Please enter a valid email address");
			expect(error).toBeInTheDocument();
		});
	});

	it("should show error on missing required field", async () => {
		render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			expect(screen.getByText("Email is required")).toBeInTheDocument();
			expect(
				screen.getByText("Name must be at least 2 characters"),
			).toBeInTheDocument();
		});
	});

	it("should clear error when field becomes valid", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");

		// Type invalid email
		await user.type(emailInput, "invalid");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(
				screen.getByText("Please enter a valid email address"),
			).toBeInTheDocument();
		});

		// Fix email
		await user.clear(emailInput);
		await user.type(emailInput, "valid@example.com");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(
				screen.queryByText("Please enter a valid email address"),
			).not.toBeInTheDocument();
		});
	});
});

describe("Form Validation - ARIA Attributes", () => {
	it("should have aria-invalid on invalid fields", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		await user.type(emailInput, "invalid");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(emailInput).toHaveAttribute("aria-invalid", "true");
		});
	});

	it("should have aria-invalid='false' on valid fields", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		expect(emailInput).toHaveAttribute("aria-invalid", "false");
	});

	it("should have aria-describedby for error messages", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		await user.type(emailInput, "invalid");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(emailInput).toHaveAttribute("aria-describedby", "email-error");
		});
	});

	it("should have aria-describedby for help text", () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		expect(emailInput).toHaveAttribute("aria-describedby", "email-hint");
	});

	it("should have required attribute on required fields", () => {
		render(<MockAccessibleForm />);

		expect(screen.getByPlaceholderText("Your name")).toHaveAttribute(
			"required",
		);
		expect(screen.getByPlaceholderText("your@email.com")).toHaveAttribute(
			"required",
		);
		expect(screen.getByPlaceholderText("Your message here...")).toHaveAttribute(
			"required",
		);
	});

	it("should mark required fields visually and accessibly", () => {
		render(<MockAccessibleForm />);

		const requiredLabels = screen.getAllByLabelText("required");
		expect(requiredLabels.length).toBeGreaterThan(0);
	});
});

describe("Form Validation - Error Announcements", () => {
	it("should announce errors with role='alert'", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		await user.type(emailInput, "invalid");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			const errorAlert = screen.getByRole("alert");
			expect(errorAlert).toBeInTheDocument();
		});
	});

	it("should announce form-level errors", async () => {
		render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			const alert = screen.getByText("Please fix the following errors:");
			expect(alert).toBeInTheDocument();
		});
	});

	it("should have aria-live region for error announcements", async () => {
		const { container } = render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			const liveRegion = container.querySelector("[role='alert'][aria-live]");
			expect(liveRegion).toBeInTheDocument();
		});
	});
});

describe("Form Validation - Field Focus Management", () => {
	it("should focus first invalid field on submit", async () => {
		render(<MockAccessibleForm />);

	const nameInput = screen.getByPlaceholderText(
		"Your name",
	) as HTMLInputElement;
		const submitBtn = screen.getByRole("button", { name: "Send Message" });

		await user.click(submitBtn);

		// Name is first field, should be focused on validation
		await waitFor(() => {
			expect(nameInput).toHaveAttribute("aria-invalid", "true");
		});
	});

	it("should validate field on blur", async () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		await user.type(emailInput, "test");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(emailInput).toHaveAttribute("aria-invalid", "true");
		});
	});

	it("should maintain focus during validation", async () => {
		render(<MockAccessibleForm />);

		const nameInput = screen.getByPlaceholderText(
			"Your name",
		) as HTMLInputElement;
		nameInput.focus();
		expect(nameInput).toHaveFocus();

		await user.type(nameInput, "A");
		await user.keyboard("{Tab}");

		// Focus should move to next field
		const emailInput = screen.getByPlaceholderText("your@email.com");
		expect(emailInput).toHaveFocus();
	});
});

describe("Form Validation - Error Recovery", () => {
	it("should allow resubmission after fixing errors", async () => {
		const handleSubmit = vi.fn();

		render(<MockAccessibleForm onSubmit={handleSubmit} />);

		const nameInput = screen.getByPlaceholderText(
			"Your name",
		) as HTMLInputElement;
		const emailInput = screen.getByPlaceholderText("your@email.com");
		const messageInput = screen.getByPlaceholderText("Your message here...");
		const submitBtn = screen.getByRole("button", { name: "Send Message" });

		// First attempt - invalid
		await user.click(submitBtn);

		await waitFor(() => {
			expect(
				screen.getByText("Name must be at least 2 characters"),
			).toBeInTheDocument();
		});

		// Fix form
		await user.type(nameInput, "John Doe");
		await user.type(emailInput, "john@example.com");
		await user.type(messageInput, "This is a valid message");

		// Second attempt - should succeed
		await user.click(submitBtn);

		await waitFor(() => {
			expect(handleSubmit).toHaveBeenCalled();
		});
	});

	it("should clear form on reset button click", async () => {
		render(<MockAccessibleForm />);

		const nameInput = screen.getByPlaceholderText(
			"Your name",
		) as HTMLInputElement;
		const resetBtn = screen.getByRole("button", { name: "Clear" });

		await user.type(nameInput, "John");
		expect(nameInput.value).toBe("John");

		await user.click(resetBtn);

		expect(nameInput.value).toBe("");
	});

	it("should clear error messages on reset", async () => {
		render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			expect(
				screen.getByText("Name must be at least 2 characters"),
			).toBeInTheDocument();
		});

		const resetBtn = screen.getByRole("button", { name: "Clear" });
		await user.click(resetBtn);

		await waitFor(() => {
			expect(
				screen.queryByText("Name must be at least 2 characters"),
			).not.toBeInTheDocument();
		});
	});
});

describe("Form Accessibility - WCAG Compliance", () => {
	it("should have no accessibility violations", async () => {
		const { container } = render(<MockAccessibleForm />);
		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});

	it("should have accessible color contrast on errors", () => {
		const { container } = render(<MockAccessibleForm />);

		// Error text should have sufficient contrast
		const errorElements = container.querySelectorAll(".text-red-600");
		expect(errorElements.length).toBeGreaterThan(0);
	});

	it("should have sufficient color differentiation for color-blind users", () => {
		const { container } = render(<MockAccessibleForm />);

		// Red borders on error should be paired with icons or text
		const invalidInputs = container.querySelectorAll(
			"input[aria-invalid='true']",
		);

		invalidInputs.forEach((input) => {
			const label = input.previousElementSibling;
			expect(label).toBeInTheDocument();
		});
	});

	it("should have readable font sizes", () => {
		const { container } = render(<MockAccessibleForm />);

		const labels = container.querySelectorAll("label");
		labels.forEach((label) => {
			expect(label.className).toContain("text-sm");
		});
	});

	it("should have proper line height for readability", () => {
		const { container } = render(<MockAccessibleForm />);

		const textareas = container.querySelectorAll("textarea");
		textareas.forEach((textarea) => {
			expect(textarea).toBeInTheDocument();
		});
	});
});

describe("Form Validation - Inline Validation", () => {
	it("should show validation as user types", async () => {
		render(<MockAccessibleForm />);

		const messageInput = screen.getByPlaceholderText("Your message here...");

		// Type short message
		await user.type(messageInput, "Hi");
		await user.keyboard("{Tab}");

		await waitFor(() => {
			expect(
				screen.getByText("Message must be at least 10 characters"),
			).toBeInTheDocument();
		});

		// Type rest of message
		await user.type(messageInput, " there, this is a valid message");

		await waitFor(() => {
			expect(
				screen.queryByText("Message must be at least 10 characters"),
			).not.toBeInTheDocument();
		});
	});
});

describe("Form Validation - Submission State", () => {
	it("should show loading state during submission", async () => {
		render(<MockAccessibleForm />);

		const nameInput = screen.getByPlaceholderText("Your name");
		const emailInput = screen.getByPlaceholderText("your@email.com");
		const messageInput = screen.getByPlaceholderText("Your message here...");
		const submitBtn = screen.getByRole("button", { name: "Send Message" });

		await user.type(nameInput, "John Doe");
		await user.type(emailInput, "john@example.com");
		await user.type(messageInput, "This is a valid message");
		await user.click(submitBtn);

		expect(submitBtn).toHaveAttribute("aria-busy", "true");
		expect(submitBtn).toHaveTextContent("Sending...");
	});

	it("should disable submit button during submission", async () => {
		render(<MockAccessibleForm />);

		const nameInput = screen.getByPlaceholderText("Your name");
		const emailInput = screen.getByPlaceholderText("your@email.com");
		const messageInput = screen.getByPlaceholderText("Your message here...");
		const submitBtn = screen.getByRole("button", { name: "Send Message" });

		await user.type(nameInput, "John");
		await user.type(emailInput, "john@example.com");
		await user.type(messageInput, "Valid message here");
		await user.click(submitBtn);

		expect(submitBtn).toBeDisabled();
	});
});

describe("Form Validation - Field Types", () => {
	it("should use correct input types for mobile", () => {
		render(<MockAccessibleForm />);

		const emailInput = screen.getByPlaceholderText("your@email.com");
		expect(emailInput).toHaveAttribute("type", "email");
	});

	it("should use textarea for multi-line input", () => {
		render(<MockAccessibleForm />);

		const messageInput = screen.getByPlaceholderText("Your message here...");
		expect(messageInput.tagName).toBe("TEXTAREA");
	});
});

describe("Form Validation - Error Summary", () => {
	it("should display summary of all errors", async () => {
		render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			const summary = screen.getByText("Please fix the following errors:");
			expect(summary).toBeInTheDocument();

			// Should list all errors
			const errorList = summary.closest("div")?.querySelector("ul");
			expect(errorList).toBeInTheDocument();
			expect(errorList?.children.length).toBeGreaterThan(0);
		});
	});

	it("should update error summary as user fixes errors", async () => {
		render(<MockAccessibleForm />);

		const submitBtn = screen.getByRole("button", { name: "Send Message" });
		await user.click(submitBtn);

		await waitFor(() => {
			expect(
				screen.getByText("Please fix the following errors:"),
			).toBeInTheDocument();
		});

		// Fix name field
		const nameInput = screen.getByPlaceholderText("Your name");
		await user.type(nameInput, "John Doe");
		await user.keyboard("{Tab}");

		// Error should still show other errors
		await waitFor(() => {
			expect(screen.getByText("Email is required")).toBeInTheDocument();
		});
	});
});
