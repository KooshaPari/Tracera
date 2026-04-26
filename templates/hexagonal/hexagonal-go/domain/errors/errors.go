package errors

import "errors"

// Domain errors - use sentinel errors for known conditions
var (
    ErrNotFound          = errors.New("entity not found")
    ErrAlreadyExists     = errors.New("entity already exists")
    ErrInvalidInput      = errors.New("invalid input")
    ErrConcurrency       = errors.New("concurrency conflict")
    ErrDomainViolation   = errors.New("domain business rule violation")
)

// DomainError wraps domain errors with context
type DomainError struct {
    Err       error
    Field     string
    Code      string
    Message   string
}

func (e *DomainError) Error() string {
    if e.Field != "" {
        return e.Field + ": " + e.Message
    }
    return e.Message
}

func (e *DomainError) Unwrap() error {
    return e.Err
}

// NewDomainError creates a new domain error
func NewDomainError(err error, field, code, message string) *DomainError {
    return &DomainError{
        Err:     err,
        Field:   field,
        Code:    code,
        Message: message,
    }
}
