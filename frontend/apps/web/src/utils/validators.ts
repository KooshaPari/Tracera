// Validation utilities

const MAX_ITEM_TITLE_LENGTH = 200;
const MAX_PROJECT_NAME_LENGTH = 50;
const MIN_PROJECT_NAME_LENGTH = 3;
const MAX_DESCRIPTION_LENGTH = 500;

export const isEmail = (email: string): boolean => {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return emailRegex.test(email);
};

export const isUrl = (url: string): boolean => URL.canParse(url);

export const isValidProjectName = (name: string): boolean => {
	const nameRegex = new RegExp(
		`^[a-zA-Z0-9\\s-_]{${MIN_PROJECT_NAME_LENGTH},${MAX_PROJECT_NAME_LENGTH}}$`,
	);
	return nameRegex.test(name);
};

export const isValidItemTitle = (title: string): boolean =>
	title.length > 0 && title.length <= MAX_ITEM_TITLE_LENGTH;

export const isValidId = (id: string): boolean => {
	const uuidRegex =
		/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
	const simpleIdRegex = /^[a-zA-Z0-9_-]+$/;
	return uuidRegex.test(id) || simpleIdRegex.test(id);
};

export const isNumeric = (value: string): boolean =>
	!Number.isNaN(Number.parseFloat(value)) && Number.isFinite(Number(value));

export const isInRange = (
	value: number,
	min: number,
	max: number,
): boolean => value >= min && value <= max;

export const hasMinLength = (text: string, min: number): boolean =>
	text.length >= min;

export const hasMaxLength = (text: string, max: number): boolean =>
	text.length <= max;

export const matchesPattern = (text: string, pattern: RegExp): boolean =>
	pattern.test(text);

// Complex validation
export interface ValidationResult {
	valid: boolean;
	errors: string[];
}

export const validateProject = (data: {
	description?: string;
	name?: string;
}): ValidationResult => {
	const errors: string[] = [];

	if (!data.name) {
		errors.push("Project name is required");
	} else if (!isValidProjectName(data.name)) {
		errors.push(
			`Project name must be ${MIN_PROJECT_NAME_LENGTH}-${MAX_PROJECT_NAME_LENGTH} characters (letters, numbers, spaces, hyphens, underscores)`,
		);
	}

	if (data.description && data.description.length > MAX_DESCRIPTION_LENGTH) {
		errors.push(`Description must be less than ${MAX_DESCRIPTION_LENGTH} characters`);
	}

	return {
		errors,
		valid: errors.length === 0,
	};
};

export const validateItem = (data: {
	priority?: string;
	status?: string;
	title?: string;
	type?: string;
	view?: string;
}): ValidationResult => {
	const errors: string[] = [];

	if (!data.title) {
		errors.push("Item title is required");
	} else if (!isValidItemTitle(data.title)) {
		errors.push(`Item title must be 1-${MAX_ITEM_TITLE_LENGTH} characters`);
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
		errors,
		valid: errors.length === 0,
	};
};

export const validateLink = (data: {
	sourceId?: string;
	targetId?: string;
	type?: string;
}): ValidationResult => {
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
		errors,
		valid: errors.length === 0,
	};
};
