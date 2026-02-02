// Validation utilities

export function isEmail(email: string): boolean {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return emailRegex.test(email);
}

export function isUrl(url: string): boolean {
	return URL.canParse(url);
}

export function isValidProjectName(name: string): boolean {
	// Must be 3-50 characters, alphanumeric with spaces, hyphens, underscores
	const nameRegex = /^[a-zA-Z0-9\s\-_]{3,50}$/;
	return nameRegex.test(name);
}

export function isValidItemTitle(title: string): boolean {
	// Must be 1-200 characters
	return title.length >= 1 && title.length <= 200;
}

export function isValidId(id: string): boolean {
	// UUIDs or simple alphanumeric IDs
	const uuidRegex =
		/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
	const simpleIdRegex = /^[a-zA-Z0-9_-]+$/;
	return uuidRegex.test(id) || simpleIdRegex.test(id);
}

export function isNumeric(value: string): boolean {
	return !Number.isNaN(parseFloat(value)) && Number.isFinite(Number(value));
}

export function isInRange(value: number, min: number, max: number): boolean {
	return value >= min && value <= max;
}

export function hasMinLength(text: string, min: number): boolean {
	return text.length >= min;
}

export function hasMaxLength(text: string, max: number): boolean {
	return text.length <= max;
}

export function matchesPattern(text: string, pattern: RegExp): boolean {
	return pattern.test(text);
}

// Complex validation
export interface ValidationResult {
	valid: boolean;
	errors: string[];
}

export function validateProject(data: {
	name?: string;
	description?: string;
}): ValidationResult {
	const errors: string[] = [];

	if (!data.name) {
		errors.push("Project name is required");
	} else if (!isValidProjectName(data.name)) {
		errors.push(
			"Project name must be 3-50 characters (letters, numbers, spaces, hyphens, underscores)",
		);
	}

	if (data.description && data.description.length > 500) {
		errors.push("Description must be less than 500 characters");
	}

	return {
		valid: errors.length === 0,
		errors,
	};
}

export function validateItem(data: {
	title?: string;
	view?: string;
	type?: string;
	status?: string;
	priority?: string;
}): ValidationResult {
	const errors: string[] = [];

	if (!data.title) {
		errors.push("Item title is required");
	} else if (!isValidItemTitle(data.title)) {
		errors.push("Item title must be 1-200 characters");
	}

	if (!data.view) {
		errors.push("View type is required");
	}

	if (!data.type) {
		errors.push("Item type is required");
	}

	if (!data.status) {
		errors.push("Status is required");
	}

	if (!data.priority) {
		errors.push("Priority is required");
	}

	return {
		valid: errors.length === 0,
		errors,
	};
}

export function validateLink(data: {
	sourceId?: string;
	targetId?: string;
	type?: string;
}): ValidationResult {
	const errors: string[] = [];

	if (!data.sourceId) {
		errors.push("Source item is required");
	}

	if (!data.targetId) {
		errors.push("Target item is required");
	}

	if (data.sourceId === data.targetId) {
		errors.push("Source and target cannot be the same item");
	}

	if (!data.type) {
		errors.push("Link type is required");
	}

	return {
		valid: errors.length === 0,
		errors,
	};
}
