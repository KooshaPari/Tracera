type UserMetadata = Record<string, unknown>;

interface User {
  avatar?: string | undefined;
  email: string;
  id: string;
  metadata?: UserMetadata | undefined;
  name?: string | undefined;
  role?: string | undefined;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  expiresIn?: number | undefined;
  refreshToken?: string | undefined;
  token: string;
  user: User;
}

interface RefreshTokenRequest {
  refreshToken: string;
}

interface AuthKitAuthorizeResponse {
  authorization_url: string;
  state: string;
}

interface AuthKitCallbackRequest {
  code: string;
  state: string;
}

interface AuthKitCallbackResponse {
  access_token: string;
  refresh_token: string;
  token: string;
  user: User;
}

interface AuthKitRefreshResponse {
  access_token: string;
  refresh_token: string;
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
  avatar?: string | undefined;
  metadata?: UserMetadata | undefined;
  name?: string | undefined;
}

type AuthErrorDetails = Record<string, unknown>;

type AuthErrorConstructorArgs = [
  message: string,
  statusCode: number,
  code?: string,
  details?: AuthErrorDetails,
];

class AuthError extends Error {
  public code?: string | undefined;
  public details?: AuthErrorDetails | undefined;
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
  AuthKitAuthorizeResponse,
  AuthKitCallbackRequest,
  AuthKitCallbackResponse,
  AuthKitRefreshResponse,
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
