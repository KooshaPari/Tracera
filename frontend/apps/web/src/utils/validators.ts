// Validation utilities

const MAX_ITEM_TITLE_LENGTH = Number('200');
const MAX_PROJECT_NAME_LENGTH = Number('50');
const MIN_PROJECT_NAME_LENGTH = Number('3');
const MAX_DESCRIPTION_LENGTH = Number('500');

const isEmail = function isEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const isUrl = function isUrl(url: string): boolean {
  return URL.canParse(url);
};

const isValidProjectName = function isValidProjectName(name: string): boolean {
  const nameRegex = new RegExp(
    `^[a-zA-Z0-9\\s_-]{${MIN_PROJECT_NAME_LENGTH},${MAX_PROJECT_NAME_LENGTH}}$`,
  );
  return nameRegex.test(name);
};

const isValidItemTitle = function isValidItemTitle(title: string): boolean {
  return title.length > 0 && title.length <= MAX_ITEM_TITLE_LENGTH;
};

const isValidId = function isValidId(id: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const simpleIdRegex = /^[a-zA-Z0-9_-]+$/;
  return uuidRegex.test(id) || simpleIdRegex.test(id);
};

const isNumeric = function isNumeric(value: string): boolean {
  return !Number.isNaN(Number.parseFloat(value)) && Number.isFinite(Number(value));
};

const isInRange = function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
};

const hasMinLength = function hasMinLength(text: string, min: number): boolean {
  return text.length >= min;
};

const hasMaxLength = function hasMaxLength(text: string, max: number): boolean {
  return text.length <= max;
};

const matchesPattern = function matchesPattern(text: string, pattern: RegExp): boolean {
  return pattern.test(text);
};

// Complex validation
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

const validateProject = function validateProject(data: {
  description?: string;
  name?: string;
}): ValidationResult {
  const errors: string[] = [];

  if (!data.name) {
    errors.push('Project name is required');
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

const validateItem = function validateItem(data: {
  priority?: string;
  status?: string;
  title?: string;
  type?: string;
  view?: string;
}): ValidationResult {
  const errors: string[] = [];

  if (!data.title) {
    errors.push('Item title is required');
  } else if (!isValidItemTitle(data.title)) {
    errors.push(`Item title must be 1-${MAX_ITEM_TITLE_LENGTH} characters`);
  }

  if (!data.view) {
    errors.push('View type is required');
  }

  if (!data.type) {
    errors.push('Item type is required');
  }

  if (!data.status) {
    errors.push('Status is required');
  }

  if (!data.priority) {
    errors.push('Priority is required');
  }

  return {
    errors,
    valid: errors.length === 0,
  };
};

const validateLink = function validateLink(data: {
  sourceId?: string;
  targetId?: string;
  type?: string;
}): ValidationResult {
  const errors: string[] = [];

  if (!data.sourceId) {
    errors.push('Source item is required');
  }

  if (!data.targetId) {
    errors.push('Target item is required');
  }

  if (data.sourceId === data.targetId) {
    errors.push('Source and target cannot be the same item');
  }

  if (!data.type) {
    errors.push('Link type is required');
  }

  return {
    errors,
    valid: errors.length === 0,
  };
};

export {
  hasMaxLength,
  hasMinLength,
  isEmail,
  isInRange,
  isNumeric,
  isUrl,
  isValidId,
  isValidItemTitle,
  isValidProjectName,
  matchesPattern,
  validateItem,
  validateLink,
  validateProject,
};
