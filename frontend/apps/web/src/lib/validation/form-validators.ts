import { z } from 'zod';

/**
 * Common form validation utilities
 */

// UUID validation
export const isValidUUID = (value: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(value);
};

export const validateUUID = (value: string): string | undefined => {
  if (!value) return 'UUID is required';
  if (!isValidUUID(value)) return 'Invalid UUID format';
  return undefined;
};

// Email validation
export const isValidEmail = (value: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(value);
};

export const validateEmail = (value: string): string | undefined => {
  if (!value) return 'Email is required';
  if (!isValidEmail(value.trim())) return 'Invalid email format';
  if (value.length > 255) return 'Email is too long';
  return undefined;
};

// URL validation
export const isValidURL = (value: string): boolean => {
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch (error) {
    return false;
  }
};

export const validateURL = (value: string, required = true): string | undefined => {
  if (!value) {
    return required ? 'URL is required' : undefined;
  }
  if (!isValidURL(value.trim())) return 'Invalid URL format';
  if (value.length > 2000) return 'URL is too long';
  return undefined;
};

// String length validation
export const validateLength = (
  value: string,
  min: number,
  max: number,
  fieldName = 'This field',
): string | undefined => {
  const trimmed = value.trim();
  if (trimmed.length < min) {
    return `${fieldName} must be at least ${min} characters`;
  }
  if (trimmed.length > max) {
    return `${fieldName} must be at most ${max} characters`;
  }
  return undefined;
};

export const validateRequired = (
  value: string | undefined | null,
  fieldName = 'This field',
): string | undefined => {
  const trimmed = value?.trim() || '';
  if (!trimmed) {
    return `${fieldName} is required`;
  }
  return undefined;
};

// Number validation
export const validateNumberRange = (
  value: number,
  min: number,
  max: number,
  fieldName = 'This field',
): string | undefined => {
  if (value < min) {
    return `${fieldName} must be at least ${min}`;
  }
  if (value > max) {
    return `${fieldName} must be at most ${max}`;
  }
  return undefined;
};

export const validatePositiveNumber = (
  value: number,
  fieldName = 'This field',
): string | undefined => {
  if (value <= 0) {
    return `${fieldName} must be a positive number`;
  }
  return undefined;
};

// Password validation
export const validatePasswordStrength = (password: string): string | undefined => {
  if (!password) return 'Password is required';
  if (password.length < 8) return 'Password must be at least 8 characters';
  if (password.length > 128) return 'Password is too long';
  if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter';
  if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter';
  if (!/\d/.test(password)) return 'Password must contain at least one number';
  return undefined;
};

export const validatePasswordMatch = (
  password: string,
  confirmPassword: string,
): string | undefined => {
  if (password !== confirmPassword) return "Passwords don't match";
  return undefined;
};

// File validation
export const validateFileSize = (file: File, maxSizeBytes: number): string | undefined => {
  if (file.size > maxSizeBytes) {
    const maxSizeMB = maxSizeBytes / (1024 * 1024);
    return `File size must be less than ${maxSizeMB}MB`;
  }
  return undefined;
};

export const validateFileType = (file: File, allowedTypes: string[]): string | undefined => {
  if (!allowedTypes.includes(file.type)) {
    return `File type ${file.type} is not allowed`;
  }
  return undefined;
};

export const validateImageFile = (file: File): string | undefined => {
  const allowedTypes = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'image/gif',
    'image/svg+xml',
  ];
  const maxSize = 5 * 1024 * 1024; // 5MB

  const typeError = validateFileType(file, allowedTypes);
  if (typeError) return typeError;

  const sizeError = validateFileSize(file, maxSize);
  if (sizeError) return sizeError;

  return undefined;
};

// Filename validation
export const validateFilename = (filename: string): string | undefined => {
  if (!filename) return 'Filename is required';
  if (filename.includes('..')) return 'Filename contains invalid characters';
  if (filename.includes('/') || filename.includes('\\'))
    return 'Filename cannot contain path separators';
  if (filename.includes('\0')) return 'Filename contains invalid characters';
  if (filename.length > 255) return 'Filename is too long';
  return undefined;
};

// Path traversal validation
export const hasPathTraversal = (path: string): boolean => {
  const dangerous = ['../', '..\\', './', '.\\', '//', '\\\\'];
  return dangerous.some((pattern) => path.includes(pattern));
};

export const validateNoPathTraversal = (path: string, fieldName = 'Path'): string | undefined => {
  if (hasPathTraversal(path)) {
    return `${fieldName} contains invalid path sequences`;
  }
  return undefined;
};

// XSS validation
export const containsXSS = (value: string): boolean => {
  const xssPatterns = [
    /<script[^>]*>.*?<\/script>/gi,
    /<iframe[^>]*>.*?<\/iframe>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi, // Event handlers
  ];
  return xssPatterns.some((pattern) => pattern.test(value));
};

export const validateNoXSS = (value: string, fieldName = 'This field'): string | undefined => {
  if (containsXSS(value)) {
    return `${fieldName} contains potentially dangerous content`;
  }
  return undefined;
};

// SQL injection validation (basic check - server-side validation is primary)
export const containsSQLInjection = (value: string): boolean => {
  const sqlPatterns = [
    /(union|select|insert|update|delete|drop|create|alter|exec|execute)\s/gi,
    /--/g,
    /\/\*/g,
    /\*\//g,
  ];
  return sqlPatterns.some((pattern) => pattern.test(value));
};

export const validateNoSQLInjection = (
  value: string,
  fieldName = 'This field',
): string | undefined => {
  if (containsSQLInjection(value)) {
    return `${fieldName} contains invalid characters`;
  }
  return undefined;
};

// Sanitization helpers
export const sanitizeString = (value: string): string => {
  return value.trim().replace(/\0/g, '');
};

export const sanitizeHTML = (value: string): string => {
  const div = document.createElement('div');
  div.textContent = value;
  return div.innerHTML;
};

// Enum validation
export const validateEnum = <T extends string>(
  value: string,
  allowedValues: readonly T[],
  fieldName = 'This field',
): string | undefined => {
  if (!allowedValues.includes(value as T)) {
    return `${fieldName} must be one of: ${allowedValues.join(', ')}`;
  }
  return undefined;
};

// Async validators

export const createAsyncValidator = <T>(
  validator: (value: T) => Promise<boolean>,
  errorMessage: string,
) => {
  return async (value: T): Promise<string | undefined> => {
    try {
      const isValid = await validator(value);
      return isValid ? undefined : errorMessage;
    } catch (error) {
      return 'Validation error';
    }
  };
};

// Cross-field validators

export const validateConditionalRequired = (
  value: string | undefined | null,
  condition: boolean,
  fieldName = 'This field',
): string | undefined => {
  if (condition) {
    return validateRequired(value, fieldName);
  }
  return undefined;
};

export const validateDateRange = (startDate: Date, endDate: Date): string | undefined => {
  if (startDate > endDate) {
    return 'Start date must be before end date';
  }
  return undefined;
};

// Form-level validators

export type FieldValidator<T> = (value: T) => string | undefined;
export type AsyncFieldValidator<T> = (value: T) => Promise<string | undefined>;

export const combineValidators =
  <T>(...validators: FieldValidator<T>[]): FieldValidator<T> =>
  (value: T) => {
    for (const validator of validators) {
      const error = validator(value);
      if (error) return error;
    }
    return undefined;
  };

export const combineAsyncValidators =
  <T>(...validators: AsyncFieldValidator<T>[]): AsyncFieldValidator<T> =>
  async (value: T) => {
    for (const validator of validators) {
      const error = await validator(value);
      if (error) return error;
    }
    return undefined;
  };

// Validation helpers for react-hook-form

export const createZodResolver = <T extends z.ZodType>(schema: T) => {
  return async (data: unknown) => {
    try {
      const validated = await schema.parseAsync(data);
      return { values: validated, errors: {} };
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        const errors: Record<string, { type: string; message: string }> = {};
        error.issues.forEach((err: any) => {
          const path = err.path.join('.');
          errors[path] = {
            type: err.code,
            message: err.message,
          };
        });
        return { values: {}, errors };
      }
      throw error;
    }
  };
};

// Real-time validation debouncing
export const createDebouncedValidator = <T>(
  validator: (value: T) => Promise<string | undefined>,
  delay = 300,
) => {
  let timeoutId: NodeJS.Timeout;

  return (value: T): Promise<string | undefined> => {
    return new Promise((resolve) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(async () => {
        const error = await validator(value);
        resolve(error);
      }, delay);
    });
  };
};

// Validation result helpers
export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export const createValidationResult = (
  errors: Record<string, string | undefined>,
): ValidationResult => {
  const cleanedErrors: Record<string, string> = {};
  let isValid = true;

  Object.entries(errors).forEach(([key, value]) => {
    if (value) {
      cleanedErrors[key] = value;
      isValid = false;
    }
  });

  return { isValid, errors: cleanedErrors };
};
