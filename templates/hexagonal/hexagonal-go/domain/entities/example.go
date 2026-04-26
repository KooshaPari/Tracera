package entities

// Example is a sample domain entity
type Example struct {
	*Entity
	Name        string
	Description string
	Active      bool
}

// NewExample creates a new example entity
func NewExample(name, description string) *Example {
	return &Example{
		Entity:      NewEntity(),
		Name:        name,
		Description: description,
		Active:      true,
	}
}

// Validate performs domain validation
func (e *Example) Validate() error {
	if e.Name == "" {
		return errNameRequired
	}
	if len(e.Name) > 100 {
		return errNameTooLong
	}
	return nil
}

// Deactivate marks the example as inactive
func (e *Example) Deactivate() {
	e.Active = false
	e.Touch()
}

// Domain errors
var (
	errNameRequired = &domainError{"name", "NAME_REQUIRED", "name is required"}
	errNameTooLong  = &domainError{"name", "NAME_TOO_LONG", "name must be less than 100 characters"}
)

type domainError struct {
	field, code, message string
}

func (e *domainError) Error() string {
	return e.field + ": " + e.message
}
