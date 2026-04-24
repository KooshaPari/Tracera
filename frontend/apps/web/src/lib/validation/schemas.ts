import { z } from 'zod';

// Common validators

export const uuidSchema = z.string().uuid('Invalid UUID format');

export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Invalid email format')
  .max(255, 'Email is too long');

export const urlSchema = z.string().url('Invalid URL format').max(2000, 'URL is too long');

export const optionalUrlSchema = z
  .string()
  .url('Invalid URL format')
  .max(2000, 'URL is too long')
  .optional()
  .or(z.literal(''));

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password is too long')
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
    'Password must contain at least one uppercase letter, one lowercase letter, and one number',
  );

export const slugSchema = z
  .string()
  .min(1, 'Slug is required')
  .max(100, 'Slug is too long')
  .regex(
    /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    'Slug can only contain lowercase letters, numbers, and hyphens',
  );

// Text field validators with length limits
export const shortTextSchema = z
  .string()
  .min(1, 'This field is required')
  .max(200, 'Text is too long (max 200 characters)')
  .transform((val) => val.trim());

export const mediumTextSchema = z
  .string()
  .min(1, 'This field is required')
  .max(500, 'Text is too long (max 500 characters)')
  .transform((val) => val.trim());

export const longTextSchema = z
  .string()
  .max(2000, 'Text is too long (max 2000 characters)')
  .optional()
  .transform((val) => (val ? val.trim() : ''));

export const veryLongTextSchema = z
  .string()
  .max(5000, 'Text is too long (max 5000 characters)')
  .optional()
  .transform((val) => (val ? val.trim() : ''));

// Enum validators

export const itemTypeSchema = z.enum([
  'feature',
  'task',
  'bug',
  'epic',
  'story',
  'requirement',
  'test',
  'module',
  'file',
  'function',
  'class',
  'suite',
  'case',
  'scenario',
  'endpoint',
  'schema',
  'model',
  'table',
  'column',
  'index',
  'screen',
  'component',
  'flow',
  'guide',
  'reference',
  'tutorial',
  'changelog',
  'environment',
  'release',
  'config',
]);

export const itemStatusSchema = z.enum(['todo', 'in_progress', 'done', 'blocked', 'cancelled']);

export const prioritySchema = z.enum(['low', 'medium', 'high', 'critical']);

export const viewTypeSchema = z.enum([
  'FEATURE',
  'CODE',
  'TEST',
  'API',
  'DATABASE',
  'WIREFRAME',
  'DOCUMENTATION',
  'DEPLOYMENT',
]);

export const linkTypeSchema = z.enum([
  'depends_on',
  'blocks',
  'relates_to',
  'implements',
  'tests',
  'documents',
  'parent_of',
  'child_of',
  'same_as',
  'represents',
  'manifests_as',
  'alternative_to',
  'originates_from',
  'derived_from',
  'evolves_into',
  'supersedes',
  'deprecates',
  'fulfills',
  'verifies',
  'validates',
  'mitigates',
  'addresses',
  'references',
  'mentions',
  'part_of',
  'composed_of',
  'related_to',
  'associated_with',
]);

// Item schemas

export const createItemSchema = z.object({
  title: shortTextSchema,
  description: longTextSchema,
  view: viewTypeSchema,
  type: itemTypeSchema,
  status: itemStatusSchema,
  priority: prioritySchema,
  projectId: uuidSchema,
  parentId: uuidSchema.optional().or(z.literal('')),
  owner: z.string().max(255).optional(),
  metadata: z.record(z.string(), z.unknown()).optional(),
});

export const updateItemSchema = createItemSchema.partial().extend({
  id: uuidSchema,
});

export const itemFiltersSchema = z.object({
  projectId: uuidSchema.optional(),
  type: itemTypeSchema.optional(),
  status: itemStatusSchema.optional(),
  priority: prioritySchema.optional(),
  search: z.string().max(200).optional(),
  limit: z.number().int().min(1).max(1000).default(100),
  offset: z.number().int().min(0).default(0),
});

// Link schemas

export const createLinkSchema = z.object({
  sourceId: uuidSchema,
  targetId: uuidSchema,
  type: linkTypeSchema,
  projectId: uuidSchema,
  metadata: z.record(z.string(), z.unknown()).optional(),
});

export const updateLinkSchema = createLinkSchema.partial().extend({
  id: uuidSchema,
});

// Project schemas

export const createProjectSchema = z.object({
  name: z
    .string()
    .min(1, 'Project name is required')
    .max(100, 'Project name is too long')
    .transform((val) => val.trim()),
  description: longTextSchema,
  metadata: z.record(z.string(), z.unknown()).optional(),
});

export const updateProjectSchema = createProjectSchema.partial().extend({
  id: uuidSchema,
});

// Authentication schemas

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z
  .object({
    email: emailSchema,
    password: passwordSchema,
    name: z
      .string()
      .min(1, 'Name is required')
      .max(100, 'Name is too long')
      .transform((val) => val.trim()),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

export const changePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, 'Current password is required'),
    newPassword: passwordSchema,
    confirmPassword: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })
  .refine((data) => data.currentPassword !== data.newPassword, {
    message: 'New password must be different from current password',
    path: ['newPassword'],
  });

// User profile schemas

export const updateProfileSchema = z.object({
  name: z
    .string()
    .min(1, 'Name is required')
    .max(100, 'Name is too long')
    .transform((val) => val.trim()),
  email: emailSchema,
  avatarUrl: optionalUrlSchema,
  bio: longTextSchema,
});

// File upload schemas

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB

const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp',
  'image/gif',
  'image/svg+xml',
];

const ALLOWED_DOCUMENT_TYPES = [
  'application/pdf',
  'application/json',
  'text/plain',
  'text/markdown',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

export const imageUploadSchema = z
  .instanceof(File)
  .refine((file) => file.size <= MAX_IMAGE_SIZE, 'Image must be less than 5MB')
  .refine(
    (file) => ALLOWED_IMAGE_TYPES.includes(file.type),
    'Only JPEG, PNG, WebP, GIF, and SVG images are allowed',
  )
  .refine((file) => !file.name.includes('..') && !file.name.includes('/'), 'Invalid filename');

export const documentUploadSchema = z
  .instanceof(File)
  .refine((file) => file.size <= MAX_FILE_SIZE, 'File must be less than 10MB')
  .refine((file) => ALLOWED_DOCUMENT_TYPES.includes(file.type), 'File type not allowed')
  .refine((file) => !file.name.includes('..') && !file.name.includes('/'), 'Invalid filename');

export const avatarUploadSchema = z.object({
  file: imageUploadSchema,
});

// Graph/View schemas

export const createGraphViewSchema = z.object({
  name: shortTextSchema,
  type: z.enum(['kanban', 'timeline', 'matrix', 'graph']),
  projectId: uuidSchema,
  config: z.record(z.string(), z.unknown()).optional(),
});

export const updateGraphViewSchema = createGraphViewSchema.partial().extend({
  id: uuidSchema,
});

// Test schemas

export const createTestCaseSchema = z.object({
  title: shortTextSchema,
  description: longTextSchema,
  projectId: uuidSchema,
  itemId: uuidSchema.optional(),
  steps: z
    .array(
      z.object({
        description: mediumTextSchema,
        expected: mediumTextSchema,
        order: z.number().int().min(1),
      }),
    )
    .min(1, 'At least one test step is required'),
  priority: prioritySchema,
  status: z.enum(['draft', 'active', 'deprecated']),
});

export const updateTestCaseSchema = createTestCaseSchema.partial().extend({
  id: uuidSchema,
});

// Search schemas

export const searchSchema = z.object({
  query: z.string().min(1, 'Search query is required').max(200),
  projectId: uuidSchema.optional(),
  types: z.array(itemTypeSchema).optional(),
  limit: z.number().int().min(1).max(100).default(20),
});

// Pagination schemas

export const paginationSchema = z.object({
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(1000).default(100),
  sort: z.string().optional(),
  order: z.enum(['asc', 'desc']).default('asc'),
});

// Query parameter schemas

export const uuidParamSchema = z.object({
  id: uuidSchema,
});

export const projectParamSchema = z.object({
  projectId: uuidSchema,
});

// Integration schemas

export const githubRepoSchema = z.object({
  owner: z.string().min(1, 'Owner is required').max(100),
  repo: z.string().min(1, 'Repository is required').max(100),
  branch: z.string().max(100).optional(),
});

export const jiraIntegrationSchema = z.object({
  url: urlSchema,
  email: emailSchema,
  apiToken: z.string().min(1, 'API token is required'),
  projectKey: z.string().min(1, 'Project key is required').max(50),
});

// Webhook schemas

export const createWebhookSchema = z.object({
  url: urlSchema,
  events: z.array(z.string()).min(1, 'At least one event is required'),
  secret: z.string().min(16, 'Secret must be at least 16 characters'),
  active: z.boolean().default(true),
});

// Export type inference helpers
export type CreateItemInput = z.infer<typeof createItemSchema>;
export type UpdateItemInput = z.infer<typeof updateItemSchema>;
export type CreateLinkInput = z.infer<typeof createLinkSchema>;
export type UpdateLinkInput = z.infer<typeof updateLinkSchema>;
export type CreateProjectInput = z.infer<typeof createProjectSchema>;
export type UpdateProjectInput = z.infer<typeof updateProjectSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type SearchInput = z.infer<typeof searchSchema>;
export type PaginationInput = z.infer<typeof paginationSchema>;
