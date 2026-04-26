package errors

import "errors"

var (
	ErrNotFound       = errors.New("entity not found")
	ErrAlreadyExists  = errors.New("entity already exists")
	ErrInvalidInput   = errors.New("invalid input")
	ErrConcurrency    = errors.New("concurrency conflict")
)

type DomainError struct {
	Err     error
	Field   string
	Code    string
	Message string
}

func (e *DomainError) Error() string {
	return e.Message
}

func (e *DomainError) Unwrap() error {
	return e.Err
}
