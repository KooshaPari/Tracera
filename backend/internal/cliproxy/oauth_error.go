package cliproxy

import "net/http"

// NewOAuthError creates an RFC 6749-compatible error response.
func NewOAuthError(code, description, state string) *OAuthErrorResponse {
	return &OAuthErrorResponse{
		ErrorCode:        code,
		ErrorDescription: description,
		State:            state,
		StatusCode:       statusCodeForOAuthError(code),
		ErrorURI:         "",
	}
}

func statusCodeForOAuthError(code string) int {
	switch code {
	case "invalid_request", "invalid_client", "invalid_grant", "unsupported_grant_type", "invalid_scope":
		return http.StatusBadRequest
	case "invalid_code":
		return http.StatusBadRequest
	case "unauthorized_client":
		return http.StatusUnauthorized
	default:
		return http.StatusInternalServerError
	}
}
