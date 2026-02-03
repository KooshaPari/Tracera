type UserMetadata = Record<string, unknown>;

type User = {
	avatar?: string;
	email: string;
	id: string;
	metadata?: UserMetadata;
	name?: string;
	role?: string;
};

type LoginRequest = {
	email: string;
	password: string;
};

type AuthResponse = {
	expiresIn?: number;
	refreshToken?: string;
	token: string;
	user: User;
};

type RefreshTokenRequest = {
	refreshToken: string;
};

type ChangePasswordRequest = {
	confirmPassword: string;
	currentPassword: string;
	newPassword: string;
};

type ResetPasswordRequest = {
	email: string;
};

type ResetPasswordConfirm = {
	confirmPassword: string;
	newPassword: string;
	token: string;
};

type UpdateUserProfileRequest = {
	avatar?: string;
	metadata?: UserMetadata;
	name?: string;
};

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
		this.name = "AuthError";
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
