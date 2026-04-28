"""
Test suite for Pheno SDK exception hierarchy.

Tests all exception types, error handling utilities, and backward compatibility.
"""

import pytest

from pheno.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleViolation,
    CheckConstraintError,
    ConfigurationError,
    DatabaseConnectionError,
    DatabaseError,
    DomainError,
    EntityNotFoundError,
    ErrorCategory,
    FieldValidationError,
    ForeignKeyError,
    IntegrationError,
    InternalError,
    InvalidCredentialsError,
    InvalidStateTransitionError,
    MissingConfigurationError,
    NetworkError,
    NotFoundError,
    NotNullConstraintError,
    PermissionDeniedError,
    PhenoException,
    RateLimitError,
    SchemaValidationError,
    TokenExpiredError,
    UnauthorizedAccessError,
    UniqueConstraintError,
    ValidationError,
    create_internal_error,
    is_retryable,
    normalize_error,
    normalize_postgres_error,
)


class TestPhenoException:
    """Test base PhenoException class."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = PhenoException(
            "Test error",
            component="test",
            operation="test_op",
        )

        assert str(exc) == "PHENO_ERROR: Test error"
        assert exc.message == "Test error"
        assert exc.error_code == "PHENO_ERROR"
        assert exc.category == ErrorCategory.INTERNAL
        assert exc.status == 500
        assert exc.context.component == "test"
        assert exc.context.operation == "test_op"

    def test_custom_error_code(self):
        """Test exception with custom error code."""
        exc = PhenoException(
            "Test error",
            error_code="CUSTOM_ERROR",
            component="test",
        )

        assert exc.error_code == "CUSTOM_ERROR"
        assert str(exc) == "CUSTOM_ERROR: Test error"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        exc = PhenoException(
            "Test error",
            component="test",
            operation="test_op",
            details={"key": "value"},
        )

        result = exc.to_dict()

        assert result["message"] == "Test error"
        assert result["error_code"] == "PHENO_ERROR"
        assert result["category"] == "internal"
        assert result["status"] == 500
        assert result["component"] == "test"
        assert result["operation"] == "test_op"
        assert result["details"] == {"key": "value"}
        assert "error_id" in result
        assert "timestamp" in result

    def test_to_http_response(self):
        """Test conversion to HTTP response format."""
        exc = PhenoException(
            "Test error",
            error_code="TEST_ERROR",
            details={"key": "value"},
        )

        result = exc.to_http_response()

        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test error"
        assert result["error"]["details"] == {"key": "value"}
        assert "error_id" in result["error"]
        assert "timestamp" in result["error"]


class TestValidationErrors:
    """Test validation error types."""

    def test_validation_error(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid input")

        assert exc.category == ErrorCategory.VALIDATION
        assert exc.status == 400
        assert exc.error_code == "VALIDATION_ERROR"

    def test_field_validation_error(self):
        """Test field-specific validation error."""
        exc = FieldValidationError(
            field="email",
            message="Invalid email format",
        )

        assert exc.field == "email"
        assert exc.message == "Invalid email format"
        assert exc.context.details["field"] == "email"
        assert exc.error_code == "FIELD_VALIDATION_ERROR"

    def test_schema_validation_error(self):
        """Test schema validation error."""
        exc = SchemaValidationError("Schema validation failed")

        assert exc.error_code == "SCHEMA_VALIDATION_ERROR"
        assert exc.category == ErrorCategory.VALIDATION


class TestResourceErrors:
    """Test resource/entity error types."""

    def test_not_found_error(self):
        """Test basic not found error."""
        exc = NotFoundError("Resource not found")

        assert exc.category == ErrorCategory.RESOURCE_NOT_FOUND
        assert exc.status == 404
        assert exc.error_code == "NOT_FOUND"

    def test_entity_not_found_error(self):
        """Test entity not found error."""
        exc = EntityNotFoundError(
            entity_type="User",
            entity_id="123",
        )

        assert exc.entity_type == "User"
        assert exc.entity_id == "123"
        assert "User with ID 123 not found" in exc.message
        assert exc.context.details["entity_type"] == "User"
        assert exc.context.details["entity_id"] == "123"
        assert exc.error_code == "ENTITY_NOT_FOUND"


class TestAuthenticationErrors:
    """Test authentication error types."""

    def test_authentication_error(self):
        """Test basic authentication error."""
        exc = AuthenticationError("Authentication failed")

        assert exc.category == ErrorCategory.AUTHENTICATION
        assert exc.status == 401
        assert exc.error_code == "AUTHENTICATION_ERROR"

    def test_invalid_credentials_error(self):
        """Test invalid credentials error."""
        exc = InvalidCredentialsError("Invalid username or password")

        assert exc.error_code == "INVALID_CREDENTIALS"
        assert exc.status == 401

    def test_token_expired_error(self):
        """Test token expired error."""
        exc = TokenExpiredError("Token has expired")

        assert exc.error_code == "TOKEN_EXPIRED"


class TestAuthorizationErrors:
    """Test authorization error types."""

    def test_authorization_error(self):
        """Test basic authorization error."""
        exc = AuthorizationError("Access denied")

        assert exc.category == ErrorCategory.AUTHORIZATION
        assert exc.status == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"

    def test_permission_denied_error(self):
        """Test permission denied error."""
        exc = PermissionDeniedError(
            table="users",
            operation="delete",
            reason="insufficient privileges",
        )

        assert exc.table == "users"
        assert exc.operation == "delete"
        assert exc.reason == "insufficient privileges"
        assert "Permission denied for delete on users" in exc.message
        assert exc.error_code == "PERMISSION_DENIED"

    def test_permission_denied_simple(self):
        """Test permission denied with simple message."""
        exc = PermissionDeniedError("Access denied")

        assert exc.message == "Access denied"


class TestDatabaseErrors:
    """Test database error types."""

    def test_database_error(self):
        """Test basic database error."""
        exc = DatabaseError("Database operation failed")

        assert exc.category == ErrorCategory.DATABASE
        assert exc.status == 500
        assert exc.error_code == "DATABASE_ERROR"

    def test_unique_constraint_error(self):
        """Test unique constraint violation."""
        exc = UniqueConstraintError()

        assert exc.message == "Duplicate value"
        assert exc.constraint_type == "unique"
        assert exc.error_code == "UNIQUE_CONSTRAINT"
        assert exc.status == 409

    def test_foreign_key_error(self):
        """Test foreign key constraint violation."""
        exc = ForeignKeyError()

        assert exc.message == "Referenced item not found"
        assert exc.constraint_type == "foreign_key"
        assert exc.error_code == "FOREIGN_KEY"

    def test_check_constraint_error(self):
        """Test check constraint violation."""
        exc = CheckConstraintError()

        assert exc.message == "Validation rule failed"
        assert exc.constraint_type == "check"
        assert exc.error_code == "CHECK_CONSTRAINT"

    def test_not_null_constraint_error(self):
        """Test not null constraint violation."""
        exc = NotNullConstraintError()

        assert exc.message == "Required field missing"
        assert exc.constraint_type == "not_null"
        assert exc.error_code == "NOT_NULL"


class TestConfigurationErrors:
    """Test configuration error types."""

    def test_configuration_error(self):
        """Test basic configuration error."""
        exc = ConfigurationError("Invalid configuration")

        assert exc.category == ErrorCategory.CONFIGURATION
        assert exc.status == 500
        assert exc.error_code == "CONFIGURATION_ERROR"

    def test_missing_configuration_error(self):
        """Test missing configuration error."""
        exc = MissingConfigurationError("DATABASE_URL")

        assert exc.config_key == "DATABASE_URL"
        assert "Missing required configuration: DATABASE_URL" in exc.message
        assert exc.error_code == "MISSING_CONFIGURATION"


class TestIntegrationErrors:
    """Test integration/external service error types."""

    def test_integration_error(self):
        """Test basic integration error."""
        exc = IntegrationError("External service failed")

        assert exc.category == ErrorCategory.EXTERNAL_SERVICE
        assert exc.error_code == "INTEGRATION_ERROR"

    def test_api_error(self):
        """Test API error."""
        exc = APIError(
            "API request failed",
            api_name="stripe",
            api_status=503,
        )

        assert exc.api_name == "stripe"
        assert exc.api_status == 503
        assert exc.context.details["api_name"] == "stripe"
        assert exc.context.details["api_status"] == 503
        assert exc.error_code == "API_ERROR"


class TestBusinessLogicErrors:
    """Test business logic error types."""

    def test_business_rule_violation(self):
        """Test business rule violation."""
        exc = BusinessRuleViolation("Cannot delete active user")

        assert exc.category == ErrorCategory.BUSINESS_RULE
        assert exc.status == 422
        assert exc.error_code == "BUSINESS_RULE_VIOLATION"

    def test_invalid_state_transition_error(self):
        """Test invalid state transition."""
        exc = InvalidStateTransitionError(
            "Invalid state transition",
            from_state="pending",
            to_state="completed",
        )

        assert exc.from_state == "pending"
        assert exc.to_state == "completed"
        assert exc.context.details["from_state"] == "pending"
        assert exc.context.details["to_state"] == "completed"
        assert exc.error_code == "INVALID_STATE_TRANSITION"

    def test_domain_error(self):
        """Test domain error."""
        exc = DomainError("Domain rule violated")

        assert exc.error_code == "DOMAIN_ERROR"
        assert exc.category == ErrorCategory.BUSINESS_RULE


class TestRetryability:
    """Test retryability detection."""

    def test_retryable_errors(self):
        """Test that retryable errors are detected."""
        assert is_retryable(NetworkError("Network error"))
        assert is_retryable(RateLimitError())
        assert is_retryable(IntegrationError("External service error"))
        assert is_retryable(DatabaseConnectionError("Connection failed"))
        assert is_retryable(ConnectionError())
        assert is_retryable(TimeoutError())

    def test_non_retryable_errors(self):
        """Test that non-retryable errors are detected."""
        assert not is_retryable(ValidationError("Invalid input"))
        assert not is_retryable(NotFoundError("Not found"))
        assert not is_retryable(AuthenticationError("Auth failed"))
        assert not is_retryable(AuthorizationError("Access denied"))
        assert not is_retryable(BusinessRuleViolation("Rule violated"))


class TestPostgresErrorNormalization:
    """Test PostgreSQL error normalization."""

    def test_unique_constraint_normalization(self):
        """Test unique constraint error normalization."""
        error = Exception("duplicate key value violates unique constraint 23505")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, UniqueConstraintError)
        assert normalized.message == "Duplicate value"
        assert normalized.status == 409

    def test_foreign_key_normalization(self):
        """Test foreign key error normalization."""
        error = Exception("violates foreign key constraint 23503")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, ForeignKeyError)
        assert normalized.message == "Referenced item not found"

    def test_check_constraint_normalization(self):
        """Test check constraint error normalization."""
        error = Exception("violates check constraint 23514")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, CheckConstraintError)
        assert normalized.message == "Validation rule failed"

    def test_not_null_normalization(self):
        """Test not null constraint error normalization."""
        error = Exception("null value in column violates not-null constraint 23502")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, NotNullConstraintError)
        assert normalized.message == "Required field missing"

    def test_permission_denied_normalization(self):
        """Test permission denied error normalization."""
        error = Exception("permission denied for table 42501")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, PermissionDeniedError)
        assert normalized.message == "Permission denied"
        assert normalized.status == 403

    def test_rls_violation_normalization(self):
        """Test RLS policy violation normalization."""
        error = Exception("new row violates row-level security policy for table projects")
        normalized = normalize_postgres_error(error)

        assert isinstance(normalized, UnauthorizedAccessError)
        assert "organization" in normalized.message.lower()


class TestErrorHandlers:
    """Test error handling utilities."""

    def test_normalize_error_with_pheno_exception(self):
        """Test normalizing a PhenoException returns it unchanged."""
        exc = ValidationError("Invalid input")
        normalized = normalize_error(exc)

        assert normalized is exc

    def test_normalize_error_with_string(self):
        """Test normalizing a string error."""
        normalized = normalize_error("Error message", component="test")

        assert isinstance(normalized, InternalError)
        assert normalized.message == "Internal server error"

    def test_create_internal_error(self):
        """Test creating internal error."""
        exc = create_internal_error(
            "Internal error",
            component="test",
            operation="test_op",
            details={"key": "value"},
        )

        assert isinstance(exc, InternalError)
        assert exc.message == "Internal error"
        assert exc.status == 500
        assert exc.context.component == "test"
        assert exc.context.operation == "test_op"
        assert exc.context.details == {"key": "value"}


class TestBackwardCompatibility:
    """Test backward compatibility."""

    def test_api_error_format(self):
        """Test legacy API error format."""
        exc = PhenoException(
            "Test error",
            error_code="TEST_ERROR",
            status=400,
            details={"key": "value"},
        )

        api_error = exc.to_api_error()

        assert api_error["code"] == "TEST_ERROR"
        assert api_error["message"] == "Test error"
        assert api_error["status"] == 400
        assert api_error["details"] == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
