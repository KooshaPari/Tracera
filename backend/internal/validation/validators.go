package validation

import (
	"errors"
	"fmt"
	"mime/multipart"
	"net/mail"
	"regexp"
	"strings"
	"sync"
	"unicode/utf8"
)

// Filename length limits
const maxFilenameLength = 255

// String validators

// ValidateStringLength validates string length constraints
func ValidateStringLength(s string, minLen, maxLen int, fieldName string) error {
	length := utf8.RuneCountInString(s)
	if length < minLen {
		return fmt.Errorf("%s must be at least %d characters long", fieldName, minLen)
	}
	if maxLen > 0 && length > maxLen {
		return fmt.Errorf("%s must be at most %d characters long", fieldName, maxLen)
	}
	return nil
}

// ValidateNonEmpty validates that a string is not empty after trimming
func ValidateNonEmpty(s string, fieldName string) error {
	trimmed := strings.TrimSpace(s)
	if trimmed == "" {
		return fmt.Errorf("%s cannot be empty", fieldName)
	}
	return nil
}

// ValidateRequiredString validates and sanitizes a required string field
func ValidateRequiredString(s string, fieldName string, minLen, maxLen int) (string, error) {
	// Trim whitespace
	trimmed := strings.TrimSpace(s)

	// Check if empty
	if trimmed == "" {
		return "", fmt.Errorf("%s is required", fieldName)
	}

	// Validate length
	if err := ValidateStringLength(trimmed, minLen, maxLen, fieldName); err != nil {
		return "", err
	}

	return trimmed, nil
}

// ValidateOptionalString validates and sanitizes an optional string field
func ValidateOptionalString(s string, fieldName string, maxLen int) (string, error) {
	trimmed := strings.TrimSpace(s)

	// Empty is valid for optional fields
	if trimmed == "" {
		return "", nil
	}

	// Validate length
	if err := ValidateStringLength(trimmed, 0, maxLen, fieldName); err != nil {
		return "", err
	}

	return trimmed, nil
}

// ValidatePattern validates that a string matches a regex pattern
func ValidatePattern(s string, pattern *regexp.Regexp, fieldName string, description string) error {
	if !pattern.MatchString(s) {
		return fmt.Errorf("%s must match pattern: %s", fieldName, description)
	}
	return nil
}

// Email validators

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

// ValidateEmail validates email format using both regex and Go's mail parser
func ValidateEmail(email string) error {
	trimmed := strings.TrimSpace(email)

	if trimmed == "" {
		return errors.New("email is required")
	}

	// Use Go's mail.ParseAddress for RFC 5322 compliance
	_, err := mail.ParseAddress(trimmed)
	if err != nil {
		return fmt.Errorf("invalid email format: %s", trimmed)
	}

	// Additional regex check for common patterns
	if !emailRegex.MatchString(trimmed) {
		return fmt.Errorf("invalid email format: %s", trimmed)
	}

	return nil
}

// Numeric validators

// ValidateIntRange validates that an integer is within a specified range
func ValidateIntRange(value int, minVal, maxVal int, fieldName string) error {
	if value < minVal {
		return fmt.Errorf("%s must be at least %d", fieldName, minVal)
	}
	if value > maxVal {
		return fmt.Errorf("%s must be at most %d", fieldName, maxVal)
	}
	return nil
}

// ValidateInt32Range validates that an int32 is within a specified range
func ValidateInt32Range(value int32, minVal, maxVal int32, fieldName string) error {
	if value < minVal {
		return fmt.Errorf("%s must be at least %d", fieldName, minVal)
	}
	if value > maxVal {
		return fmt.Errorf("%s must be at most %d", fieldName, maxVal)
	}
	return nil
}

// ValidatePositiveInt validates that an integer is positive (> 0)
func ValidatePositiveInt(value int, fieldName string) error {
	if value <= 0 {
		return fmt.Errorf("%s must be a positive number", fieldName)
	}
	return nil
}

// ValidateNonNegativeInt validates that an integer is non-negative (>= 0)
func ValidateNonNegativeInt(value int, fieldName string) error {
	if value < 0 {
		return fmt.Errorf("%s cannot be negative", fieldName)
	}
	return nil
}

// URL and path validators

var urlRegex = regexp.MustCompile(`^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+$`)

// ValidateURL validates URL format
func ValidateURL(url string) error {
	trimmed := strings.TrimSpace(url)

	if trimmed == "" {
		return errors.New("URL is required")
	}

	if !urlRegex.MatchString(trimmed) {
		return fmt.Errorf("invalid URL format: %s", trimmed)
	}

	return nil
}

// ValidateOptionalURL validates optional URL format
func ValidateOptionalURL(url string) error {
	trimmed := strings.TrimSpace(url)

	// Empty is valid for optional URLs
	if trimmed == "" {
		return nil
	}

	return ValidateURL(trimmed)
}

// ValidateNoPathTraversal validates that a path doesn't contain path traversal sequences
func ValidateNoPathTraversal(path string, fieldName string) error {
	dangerous := []string{
		"../",
		"..\\",
		"./",
		".\\",
		"//",
		"\\\\",
	}

	for _, pattern := range dangerous {
		if strings.Contains(path, pattern) {
			return fmt.Errorf("%s contains invalid path sequences", fieldName)
		}
	}

	return nil
}

// File upload validators

const (
	// MaxFileSize is the default maximum upload size (10MB).
	MaxFileSize = 10 * 1024 * 1024 // 10MB default
	// MaxImageSize is the maximum upload size for images (5MB).
	MaxImageSize = 5 * 1024 * 1024 // 5MB for images
	// MaxDocumentSize is the maximum upload size for documents (20MB).
	MaxDocumentSize = 20 * 1024 * 1024 // 20MB for documents
	// MaxVideoSize is the maximum upload size for videos (100MB).
	MaxVideoSize = 100 * 1024 * 1024 // 100MB for videos
)

// Lazy-initialized immutable lookup tables and regex patterns for validation.
// These are package-level to enable sync.Once initialization.
//
//nolint:gochecknoglobals // lazy-initialized immutable lookup tables and regex patterns
var (
	allowedImageTypes    map[string]bool
	imageTypesOnce       sync.Once
	allowedDocumentTypes map[string]bool
	docTypesOnce         sync.Once
	sqlInjectionPatterns []*regexp.Regexp
	sqlInjectionOnce     sync.Once
	xssPatterns          []*regexp.Regexp
	xssOnce              sync.Once
)

// GetAllowedImageTypes returns the allowed image MIME types
func GetAllowedImageTypes() map[string]bool {
	return getAllowedImageTypes()
}

func getAllowedImageTypes() map[string]bool {
	imageTypesOnce.Do(func() {
		allowedImageTypes = map[string]bool{
			"image/jpeg":    true,
			"image/png":     true,
			"image/gif":     true,
			"image/webp":    true,
			"image/svg+xml": true,
		}
	})
	return allowedImageTypes
}

// getAllowedDocumentTypes returns the allowed document MIME types (lazy init)
func getAllowedDocumentTypes() map[string]bool {
	docTypesOnce.Do(func() {
		allowedDocumentTypes = map[string]bool{
			"application/pdf":  true,
			"application/json": true,
			"text/plain":       true,
			"text/markdown":    true,
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document": true, // .docx
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":       true, // .xlsx
		}
	})
	return allowedDocumentTypes
}

// GetAllowedDocumentTypes returns the allowed document MIME types
func GetAllowedDocumentTypes() map[string]bool {
	return getAllowedDocumentTypes()
}

// ValidateFileSize validates file size against a maximum
func ValidateFileSize(size int64, maxSize int64, fieldName string) error {
	if size <= 0 {
		return fmt.Errorf("%s is empty", fieldName)
	}

	if size > maxSize {
		return fmt.Errorf("%s exceeds maximum size of %d bytes", fieldName, maxSize)
	}

	return nil
}

// ValidateFileType validates file MIME type against allowed types
func ValidateFileType(contentType string, allowedTypes map[string]bool, fieldName string) error {
	if contentType == "" {
		return fmt.Errorf("%s content type is missing", fieldName)
	}

	if !allowedTypes[contentType] {
		return fmt.Errorf("%s has invalid content type: %s", fieldName, contentType)
	}

	return nil
}

// ValidateUploadedFile validates a multipart file upload
func ValidateUploadedFile(file *multipart.FileHeader, maxSize int64, allowedTypes map[string]bool) error {
	if file == nil {
		return errors.New("file is required")
	}

	// Validate file size
	if err := ValidateFileSize(file.Size, maxSize, "file"); err != nil {
		return err
	}

	// Validate content type
	contentType := file.Header.Get("Content-Type")
	if err := ValidateFileType(contentType, allowedTypes, "file"); err != nil {
		return err
	}

	// Validate filename
	if err := ValidateFilename(file.Filename); err != nil {
		return err
	}

	return nil
}

// ValidateFilename validates a filename for security issues
func ValidateFilename(filename string) error {
	if filename == "" {
		return errors.New("filename is required")
	}

	// Check for path traversal
	if err := ValidateNoPathTraversal(filename, "filename"); err != nil {
		return err
	}

	// Check for null bytes
	if strings.Contains(filename, "\x00") {
		return errors.New("filename contains invalid characters")
	}

	// Validate length
	if err := ValidateStringLength(filename, 1, maxFilenameLength, "filename"); err != nil {
		return err
	}

	return nil
}

// SQL injection prevention

// getSQLInjectionPatterns returns the SQL injection detection patterns (lazy init)
func getSQLInjectionPatterns() []*regexp.Regexp {
	sqlInjectionOnce.Do(func() {
		sqlInjectionPatterns = []*regexp.Regexp{
			regexp.MustCompile(`(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)\s`),
			regexp.MustCompile(`--`),
			regexp.MustCompile(`/\*`),
			regexp.MustCompile(`\*/`),
			regexp.MustCompile(`;`),
		}
	})
	return sqlInjectionPatterns
}

// GetSQLInjectionPatterns returns the SQL injection detection patterns
func GetSQLInjectionPatterns() []*regexp.Regexp {
	return getSQLInjectionPatterns()
}

// getXSSPatterns returns the XSS detection patterns (lazy init)
func getXSSPatterns() []*regexp.Regexp {
	xssOnce.Do(func() {
		xssPatterns = []*regexp.Regexp{
			regexp.MustCompile(`(?i)<script[^>]*>.*?</script>`),
			regexp.MustCompile(`(?i)<iframe[^>]*>.*?</iframe>`),
			regexp.MustCompile(`(?i)javascript:`),
			regexp.MustCompile(`(?i)on\w+\s*=`), // Event handlers like onclick, onerror
		}
	})
	return xssPatterns
}

// GetXSSPatterns returns the XSS detection patterns
func GetXSSPatterns() []*regexp.Regexp {
	return getXSSPatterns()
}

// ValidateNoSQLInjection validates that a string doesn't contain SQL injection patterns
// Note: This is a basic check. Use parameterized queries as primary defense.
func ValidateNoSQLInjection(input string, fieldName string) error {
	for _, pattern := range getSQLInjectionPatterns() {
		if pattern.MatchString(input) {
			return fmt.Errorf("%s contains invalid characters or patterns", fieldName)
		}
	}
	return nil
}

// ValidateNoXSS validates that a string doesn't contain XSS patterns
// Note: This is a basic check. Use proper HTML sanitization for user content.
func ValidateNoXSS(input string, fieldName string) error {
	for _, pattern := range getXSSPatterns() {
		if pattern.MatchString(input) {
			return fmt.Errorf("%s contains potentially dangerous content", fieldName)
		}
	}
	return nil
}

// SanitizeUserInput performs basic sanitization on user input
func SanitizeUserInput(input string) string {
	// Trim whitespace
	sanitized := strings.TrimSpace(input)

	// Remove null bytes
	sanitized = strings.ReplaceAll(sanitized, "\x00", "")

	// Normalize unicode
	sanitized = strings.ToValidUTF8(sanitized, "")

	return sanitized
}

// Enum validators

// ValidateEnum validates that a value is one of the allowed enum values
func ValidateEnum(value string, allowedValues []string, fieldName string) error {
	for _, allowed := range allowedValues {
		if value == allowed {
			return nil
		}
	}

	return fmt.Errorf("%s must be one of: %s", fieldName, strings.Join(allowedValues, ", "))
}

// Multi-field validators

// Error represents a structured validation error.
type Error struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// Errors represents multiple validation errors.
type Errors struct {
	Errors []Error `json:"errors"`
}

// Error implements the error interface
func (ve Errors) Error() string {
	if len(ve.Errors) == 0 {
		return "validation failed"
	}

	messages := make([]string, len(ve.Errors))
	for i, err := range ve.Errors {
		messages[i] = err.Field + ": " + err.Message
	}

	return strings.Join(messages, "; ")
}

// NewErrors creates a new Errors instance.
func NewErrors() *Errors {
	return &Errors{
		Errors: make([]Error, 0),
	}
}

// Add adds a validation error
func (ve *Errors) Add(field, message string) {
	ve.Errors = append(ve.Errors, Error{
		Field:   field,
		Message: message,
	})
}

// HasErrors returns true if there are validation errors
func (ve *Errors) HasErrors() bool {
	return len(ve.Errors) > 0
}

// ToError converts to error if there are errors, returns nil otherwise
func (ve *Errors) ToError() error {
	if ve.HasErrors() {
		return ve
	}
	return nil
}
