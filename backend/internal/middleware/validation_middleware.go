package middleware

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/validation"
)

// DefaultRequestSizeLimit sets a maximum size for request bodies (default 10MB)
const (
	DefaultRequestSizeLimit = 10 * 1024 * 1024
	validationMaxLimit      = 1000
)

// RequestSizeLimiter middleware limits the size of incoming requests
func RequestSizeLimiter(maxSize int64) echo.MiddlewareFunc {
	if maxSize <= 0 {
		maxSize = DefaultRequestSizeLimit
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			req := c.Request()

			// Check Content-Length header if present
			if req.ContentLength > maxSize {
				return echo.NewHTTPError(
					http.StatusRequestEntityTooLarge,
					"request body too large (max "+strconv.FormatInt(maxSize, 10)+" bytes)",
				)
			}

			// Limit the request body reader
			req.Body = http.MaxBytesReader(c.Response(), req.Body, maxSize)

			return next(c)
		}
	}
}

// QueryParamValidator validates common query parameters
func QueryParamValidator() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Validate limit parameter if present
			if err := validateLimitParam(c); err != nil {
				return err
			}

			// Validate offset parameter if present
			if err := validateOffsetParam(c); err != nil {
				return err
			}

			// Validate page parameter if present
			if err := validatePageParam(c); err != nil {
				return err
			}

			// Validate UUID parameters
			if err := validateUUIDParams(c); err != nil {
				return err
			}

			return next(c)
		}
	}
}

// validateLimitParam validates the limit query parameter
func validateLimitParam(c echo.Context) error {
	limitStr := c.QueryParam("limit")
	if limitStr == "" {
		return nil
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		return echo.NewHTTPError(
			http.StatusBadRequest,
			"invalid limit parameter: must be a number",
		)
	}
	if err := validation.ValidateIntRange(limit, 1, validationMaxLimit, "limit"); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	return nil
}

// validateOffsetParam validates the offset query parameter
func validateOffsetParam(c echo.Context) error {
	offsetStr := c.QueryParam("offset")
	if offsetStr == "" {
		return nil
	}

	offset, err := strconv.Atoi(offsetStr)
	if err != nil {
		return echo.NewHTTPError(
			http.StatusBadRequest,
			"invalid offset parameter: must be a number",
		)
	}
	if err := validation.ValidateNonNegativeInt(offset, "offset"); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	return nil
}

// validatePageParam validates the page query parameter
func validatePageParam(c echo.Context) error {
	pageStr := c.QueryParam("page")
	if pageStr == "" {
		return nil
	}

	page, err := strconv.Atoi(pageStr)
	if err != nil {
		return echo.NewHTTPError(
			http.StatusBadRequest,
			"invalid page parameter: must be a number",
		)
	}
	if err := validation.ValidatePositiveInt(page, "page"); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	return nil
}

// validateUUIDParams validates common UUID query parameters
func validateUUIDParams(c echo.Context) error {
	uuidParams := []string{"project_id", "item_id", "link_id", "user_id", "graph_id"}
	for _, param := range uuidParams {
		if id := c.QueryParam(param); id != "" {
			if err := validation.ValidateUUID(id); err != nil {
				return echo.NewHTTPError(
					http.StatusBadRequest,
					"invalid "+param+": "+err.Error(),
				)
			}
		}
	}
	return nil
}

// PathParamValidator validates path parameters
func PathParamValidator(paramName string, validator func(string) error) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			value := c.Param(paramName)
			if value == "" {
				return echo.NewHTTPError(
					http.StatusBadRequest,
					paramName+" parameter is required",
				)
			}

			if err := validator(value); err != nil {
				return echo.NewHTTPError(
					http.StatusBadRequest,
					"invalid "+paramName+": "+err.Error(),
				)
			}

			return next(c)
		}
	}
}

// UUIDPathValidator validates that a path parameter is a valid UUID
func UUIDPathValidator(paramName string) echo.MiddlewareFunc {
	return PathParamValidator(paramName, validation.ValidateUUID)
}

// SanitizeInputPlaceholder middleware is a placeholder for input sanitization
// Note: Actual sanitization should happen at the struct binding level
// Use SanitizeInput() from security.go for actual sanitization
func SanitizeInputPlaceholder() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Placeholder - use SanitizeInput() from security.go for actual sanitization
			return next(c)
		}
	}
}

// validateMultipartFiles validates all files in a multipart form against size and type constraints.
func validateMultipartFiles(c echo.Context, maxSize int64, allowedTypes map[string]bool) error {
	form, parseErr := c.MultipartForm()
	if parseErr != nil {
		// Not a multipart request, skip validation - this is expected for non-multipart requests
		return nil //nolint:nilerr // intentionally ignoring parseErr for non-multipart requests
	}
	for _, files := range form.File {
		for _, file := range files {
			if err := validation.ValidateUploadedFile(file, maxSize, allowedTypes); err != nil {
				return echo.NewHTTPError(http.StatusBadRequest, err.Error())
			}
		}
	}
	return nil
}

// FileUploadValidator creates middleware to validate file uploads
func FileUploadValidator(maxSize int64, allowedTypes map[string]bool) echo.MiddlewareFunc {
	if maxSize <= 0 {
		maxSize = validation.MaxFileSize
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if err := validateMultipartFiles(c, maxSize, allowedTypes); err != nil {
				return err
			}
			return next(c)
		}
	}
}

// ContentTypeValidator validates that the request has an expected content type
func ContentTypeValidator(allowedTypes ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Skip for GET requests
			if c.Request().Method == http.MethodGet {
				return next(c)
			}

			contentType := c.Request().Header.Get("Content-Type")
			if contentType == "" {
				return echo.NewHTTPError(
					http.StatusBadRequest,
					"Content-Type header is required",
				)
			}

			// Check if content type is in allowed list
			for _, allowed := range allowedTypes {
				if contentType == allowed || len(contentType) > len(allowed) && contentType[:len(allowed)] == allowed {
					return next(c)
				}
			}

			return echo.NewHTTPError(
				http.StatusUnsupportedMediaType,
				"unsupported content type: "+contentType,
			)
		}
	}
}

// ValidationErrorResponse represents a validation error response
type ValidationErrorResponse struct {
	Error  string             `json:"error"`
	Errors []validation.Error `json:"errors,omitempty"`
}

// ValidateRequestBody validates a request body against a custom validator function
func ValidateRequestBody(validator func(c echo.Context) error) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if err := validator(c); err != nil {
				ve := &validation.Errors{}
				if errors.As(err, &ve) {
					return c.JSON(http.StatusBadRequest, ValidationErrorResponse{
						Error:  "validation failed",
						Errors: ve.Errors,
					})
				}
				return echo.NewHTTPError(http.StatusBadRequest, err.Error())
			}
			return next(c)
		}
	}
}

// HeaderValidator validates required headers
func HeaderValidator(requiredHeaders ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			for _, header := range requiredHeaders {
				if c.Request().Header.Get(header) == "" {
					return echo.NewHTTPError(
						http.StatusBadRequest,
						"missing required header: "+header,
					)
				}
			}
			return next(c)
		}
	}
}
