type UserMetadata = Record<string, unknown>;

interface User {
  avatar?: string;
  email: string;
  id: string;
  metadata?: UserMetadata;
  name?: string;
  role?: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  expiresIn?: number;
  refreshToken?: string;
  token: string;
  user: User;
}

interface RefreshTokenRequest {
  refreshToken: string;
}

interface ChangePasswordRequest {
  confirmPassword: string;
  currentPassword: string;
  newPassword: string;
}

interface ResetPasswordRequest {
  email: string;
}

interface ResetPasswordConfirm {
  confirmPassword: string;
  newPassword: string;
  token: string;
}

interface UpdateUserProfileRequest {
  avatar?: string;
  metadata?: UserMetadata;
  name?: string;
}

type AuthErrorDetails = Record<string, unknown>;

type AuthErrorConstructorArgs = [
  message: string,
  statusCode: number,
  code?: string,
  details?: AuthErrorDetails,
];

class AuthError extends Error {
  public code?: string;
  public details?: AuthErrorDetails;
  public statusCode: number;

  public constructor(...args: AuthErrorConstructorArgs) {
    const [message, statusCode, code, details] = args;
    super(message);
    this.code = code;
    this.details = details;
    this.name = 'AuthError';
    this.statusCode = statusCode;
    Object.setPrototypeOf(this, AuthError.prototype);
  }
}

export type {
  AuthErrorConstructorArgs,
  AuthErrorDetails,
  AuthResponse,
  ChangePasswordRequest,
  LoginRequest,
  RefreshTokenRequest,
  ResetPasswordConfirm,
  ResetPasswordRequest,
  UpdateUserProfileRequest,
  User,
  UserMetadata,
};

export { AuthError };
