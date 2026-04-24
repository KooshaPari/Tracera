// Export all API utilities
import type {
  Agent,
  Item,
  ItemStatus,
  Link,
  LinkType,
  Mutation,
  PaginatedResponse,
  Priority,
  Project,
  ViewType,
} from '@tracertm/types';

import type {
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
} from './api/auth';

import { agentApi } from './api/agent';
import {
  AuthError,
  authApi,
  getAuthErrorMessage,
  isAuthError,
  loginWithCodeAndToast,
  redirectToAuthKitWithToast,
  shouldLogoutOnError,
} from './api/auth';
import { client } from './api/client';
import { componentLibraryApi } from './api/component-library';

type ClientExports = typeof client;

const clientExports: ClientExports = client;

export type {
  Agent,
  AuthErrorDetails,
  AuthResponse,
  ChangePasswordRequest,
  Link,
  LinkType,
  LoginRequest,
  Mutation,
  Item,
  ItemStatus,
  PaginatedResponse,
  Priority,
  Project,
  RefreshTokenRequest,
  ResetPasswordConfirm,
  ResetPasswordRequest,
  UpdateUserProfileRequest,
  User,
  UserMetadata,
  ViewType,
};

export const {
  API_BASE_URL,
  ApiError,
  apiClient,
  getAuthHeaders,
  getBackendURL,
  handleApiResponse,
  safeApiCall,
  validateSession,
} = clientExports;

export {
  AuthError,
  authApi,
  componentLibraryApi,
  getAuthErrorMessage,
  isAuthError,
  loginWithCodeAndToast,
  redirectToAuthKitWithToast,
  shouldLogoutOnError,
};
export const { createAgentSession } = agentApi;
