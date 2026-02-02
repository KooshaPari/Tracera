/**
 * Validation utilities and schemas
 *
 * This module provides comprehensive validation for all forms and API requests.
 *
 * @module validation
 */

// Export all schemas
export * from "./schemas";

// Export all validators
export * from "./form-validators";

// Re-export commonly used types
export type {
	CreateItemInput,
	UpdateItemInput,
	CreateLinkInput,
	UpdateLinkInput,
	CreateProjectInput,
	UpdateProjectInput,
	LoginInput,
	RegisterInput,
	SearchInput,
	PaginationInput,
} from "./schemas";
