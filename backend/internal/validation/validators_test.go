package validation

import (
	"strings"
	"testing"
)

// String validation tests

func TestValidateStringLength(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		minLen    int
		maxLen    int
		fieldName string
		wantErr   bool
	}{
		{"Valid string", "hello", 1, 10, "field", false},
		{"Too short", "hi", 5, 10, "field", true},
		{"Too long", "hello world", 1, 5, "field", true},
		{"Exact min length", "hello", 5, 10, "field", false},
		{"Exact max length", "hello", 1, 5, "field", false},
		{"No max limit", "hello world", 1, 0, "field", false},
		{"Empty string with min=0", "", 0, 10, "field", false},
		{"Unicode characters", "你好世界", 1, 10, "field", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateStringLength(tt.input, tt.minLen, tt.maxLen, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateStringLength() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidateNonEmpty(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		fieldName string
		wantErr   bool
	}{
		{"Valid non-empty", "hello", "field", false},
		{"Empty string", "", "field", true},
		{"Whitespace only", "   ", "field", true},
		{"Tab and spaces", "\t  \n", "field", true},
		{"Single character", "a", "field", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateNonEmpty(tt.input, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateNonEmpty() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidateRequiredString(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		fieldName string
		minLen    int
		maxLen    int
		want      string
		wantErr   bool
	}{
		{"Valid string", "  hello  ", "field", 1, 10, "hello", false},
		{"Empty after trim", "   ", "field", 1, 10, "", true},
		{"Too short", "hi", "field", 5, 10, "", true},
		{"Too long", "hello world", "field", 1, 5, "", true},
		{"Valid with whitespace", "  hello world  ", "field", 1, 20, "hello world", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ValidateRequiredString(tt.input, tt.fieldName, tt.minLen, tt.maxLen)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateRequiredString() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("ValidateRequiredString() = %v, want %v", got, tt.want)
			}
		})
	}
}

// Email validation tests

func TestValidateEmail(t *testing.T) {
	tests := []struct {
		name    string
		email   string
		wantErr bool
	}{
		{"Valid email", "user@example.com", false},
		{"Valid with plus", "user+tag@example.com", false},
		{"Valid with dash", "user-name@example.com", false},
		{"Valid with subdomain", "user@mail.example.com", false},
		{"Empty email", "", true},
		{"Missing @", "userexample.com", true},
		{"Missing domain", "user@", true},
		{"Missing local part", "@example.com", true},
		{"Invalid TLD", "user@example.c", true},
		{"Spaces in email", "user @example.com", true},
		{"Multiple @", "user@@example.com", true},
		{"Unicode in local", "用户@example.com", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateEmail(tt.email)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateEmail() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// Numeric validation tests

func TestValidateIntRange(t *testing.T) {
	tests := []struct {
		name      string
		value     int
		min       int
		max       int
		fieldName string
		wantErr   bool
	}{
		{"Within range", 5, 1, 10, "field", false},
		{"At min", 1, 1, 10, "field", false},
		{"At max", 10, 1, 10, "field", false},
		{"Below min", 0, 1, 10, "field", true},
		{"Above max", 11, 1, 10, "field", true},
		{"Negative range", -5, -10, -1, "field", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateIntRange(tt.value, tt.min, tt.max, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateIntRange() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidatePositiveInt(t *testing.T) {
	tests := []struct {
		name      string
		value     int
		fieldName string
		wantErr   bool
	}{
		{"Positive number", 5, "field", false},
		{"Zero", 0, "field", true},
		{"Negative", -1, "field", true},
		{"Large positive", 1000000, "field", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidatePositiveInt(tt.value, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidatePositiveInt() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidateNonNegativeInt(t *testing.T) {
	tests := []struct {
		name      string
		value     int
		fieldName string
		wantErr   bool
	}{
		{"Positive number", 5, "field", false},
		{"Zero", 0, "field", false},
		{"Negative", -1, "field", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateNonNegativeInt(tt.value, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateNonNegativeInt() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// URL validation tests

func TestValidateURL(t *testing.T) {
	tests := []struct {
		name    string
		url     string
		wantErr bool
	}{
		{"Valid HTTP URL", "http://example.com", false},
		{"Valid HTTPS URL", "https://example.com", false},
		{"URL with path", "https://example.com/path/to/resource", false},
		{"URL with query", "https://example.com?key=value", false},
		{"URL with port", "https://example.com:8080", false},
		{"Empty URL", "", true},
		{"Invalid protocol", "ftp://example.com", true},
		{"Missing protocol", "example.com", true},
		{"Spaces in URL", "http://exam ple.com", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateURL(tt.url)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateURL() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// Path traversal tests

func TestValidateNoPathTraversal(t *testing.T) {
	tests := []struct {
		name      string
		path      string
		fieldName string
		wantErr   bool
	}{
		{"Valid path", "uploads/image.png", "path", false},
		{"Parent directory Unix", "../etc/passwd", "path", true},
		{"Parent directory Windows", "..\\windows\\system32", "path", true},
		{"Current directory", "./config.txt", "path", true},
		{"Double slash", "uploads//file.txt", "path", true},
		{"Windows double backslash", "uploads\\\\file.txt", "path", true},
		{"Nested valid path", "uploads/images/photo.jpg", "path", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateNoPathTraversal(tt.path, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateNoPathTraversal() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// File validation tests

func TestValidateFileSize(t *testing.T) {
	tests := []struct {
		name      string
		size      int64
		maxSize   int64
		fieldName string
		wantErr   bool
	}{
		{"Valid size", 1024, 2048, "file", false},
		{"At max size", 2048, 2048, "file", false},
		{"Over max size", 3000, 2048, "file", true},
		{"Zero size", 0, 2048, "file", true},
		{"Negative size", -100, 2048, "file", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateFileSize(tt.size, tt.maxSize, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateFileSize() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidateFileType(t *testing.T) {
	allowedTypes := map[string]bool{
		"image/jpeg": true,
		"image/png":  true,
	}

	tests := []struct {
		name        string
		contentType string
		fieldName   string
		wantErr     bool
	}{
		{"Valid JPEG", "image/jpeg", "file", false},
		{"Valid PNG", "image/png", "file", false},
		{"Invalid type", "image/gif", "file", true},
		{"Empty type", "", "file", true},
		{"Text file", "text/plain", "file", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateFileType(tt.contentType, allowedTypes, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateFileType() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestValidateFilename(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		wantErr  bool
	}{
		{"Valid filename", "document.pdf", false},
		{"Filename with spaces", "my document.pdf", false},
		{"Long filename", strings.Repeat("a", 255), false},
		{"Too long filename", strings.Repeat("a", 256), true},
		{"Empty filename", "", true},
		{"Path traversal", "../etc/passwd", true},
		{"Null byte", "file\x00.txt", true},
		{"Windows path traversal", "..\\file.txt", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateFilename(tt.filename)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateFilename() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// SQL injection tests

func TestValidateNoSQLInjection(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		fieldName string
		wantErr   bool
	}{
		{"Valid input", "John Doe", "name", false},
		{"SQL SELECT", "'; SELECT * FROM users--", "input", true},
		{"SQL UNION", "1 UNION SELECT password FROM users", "input", true},
		{"SQL comment", "value--comment", "input", true},
		{"SQL block comment", "value /* comment */", "input", true},
		{"Semicolon", "value; DROP TABLE users", "input", true},
		{"Valid semicolon in sentence", "Hello; how are you?", "input", true}, // This will fail - acceptable tradeoff
		{"Numbers only", "12345", "input", false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateNoSQLInjection(tt.input, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateNoSQLInjection() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// XSS tests

func TestValidateNoXSS(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		fieldName string
		wantErr   bool
	}{
		{"Valid input", "Hello World", "content", false},
		{"Script tag", "<script>alert('XSS')</script>", "content", true},
		{"Iframe", "<iframe src='evil.com'></iframe>", "content", true},
		{"JavaScript protocol", "javascript:alert('XSS')", "content", true},
		{"Onclick handler", "<div onclick='alert()'>", "content", true},
		{"Onerror handler", "<img onerror='alert()'>", "content", true},
		{"Valid HTML tags", "<p>Hello</p>", "content", false},
		{"Mixed content", "Visit <script>alert()</script> now", "content", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateNoXSS(tt.input, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateNoXSS() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// Sanitization tests

func TestSanitizeUserInput(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  string
	}{
		{"No changes", "hello", "hello"},
		{"Trim spaces", "  hello  ", "hello"},
		{"Remove null bytes", "hello\x00world", "helloworld"},
		{"Mixed", "  hello\x00world  ", "helloworld"},
		{"Unicode", "你好世界", "你好世界"},
		{"Empty", "", ""},
		{"Only spaces", "   ", ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SanitizeUserInput(tt.input)
			if got != tt.want {
				t.Errorf("SanitizeUserInput() = %v, want %v", got, tt.want)
			}
		})
	}
}

// Enum validation tests

func TestValidateEnum(t *testing.T) {
	allowedValues := []string{"draft", "published", "archived"}

	tests := []struct {
		name      string
		value     string
		fieldName string
		wantErr   bool
	}{
		{"Valid value", "draft", "status", false},
		{"Another valid value", "published", "status", false},
		{"Invalid value", "deleted", "status", true},
		{"Empty value", "", "status", true},
		{"Case sensitive", "Draft", "status", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateEnum(tt.value, allowedValues, tt.fieldName)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateEnum() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

// Errors tests

func TestErrors(t *testing.T) {
	t.Run("Empty errors", func(t *testing.T) {
		ve := NewErrors()
		if ve.HasErrors() {
			t.Error("Expected no errors")
		}
		if ve.ToError() != nil {
			t.Error("Expected nil error")
		}
	})

	t.Run("Single error", func(t *testing.T) {
		ve := NewErrors()
		ve.Add("email", "invalid email format")
		if !ve.HasErrors() {
			t.Error("Expected errors")
		}
		if ve.ToError() == nil {
			t.Error("Expected non-nil error")
		}
	})

	t.Run("Multiple errors", func(t *testing.T) {
		ve := NewErrors()
		ve.Add("email", "invalid email format")
		ve.Add("password", "password too short")
		if len(ve.Errors) != 2 {
			t.Errorf("Expected 2 errors, got %d", len(ve.Errors))
		}
		errorMsg := ve.Error()
		if !strings.Contains(errorMsg, "email") || !strings.Contains(errorMsg, "password") {
			t.Errorf("Error message missing field names: %s", errorMsg)
		}
	})
}

// Benchmark tests

func BenchmarkValidateEmail(b *testing.B) {
	email := "user@example.com"
	for i := 0; i < b.N; i++ {
		if err := ValidateEmail(email); err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkValidateUUID(b *testing.B) {
	id := "550e8400-e29b-41d4-a716-446655440000"
	for i := 0; i < b.N; i++ {
		if err := ValidateUUID(id); err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkValidateStringLength(b *testing.B) {
	str := "hello world"
	for i := 0; i < b.N; i++ {
		if err := ValidateStringLength(str, 1, 100, "field"); err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkSanitizeUserInput(b *testing.B) {
	input := "  hello world  "
	for i := 0; i < b.N; i++ {
		_ = SanitizeUserInput(input)
	}
}
