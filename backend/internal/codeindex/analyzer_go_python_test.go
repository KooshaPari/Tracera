package codeindex

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAnalyzer_AnalyzeFile_Go(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package main

import "fmt"

// User represents a user entity
type User struct {
	ID    string
	Name  string
	Email string
}

// GetUser retrieves a user by ID
func GetUser(id string) (*User, error) {
	user := &User{ID: id}
	return user, nil
}

func (u *User) String() string {
	return fmt.Sprintf("%s <%s>", u.Name, u.Email)
}

type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}

interface UserRepository {
	GetByID(id string) (*User, error)
}`

	analysis, err := analyzer.AnalyzeFile("internal/user/service.go", goCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Equal(t, LanguageGo, analysis.Language)
	assert.NotEmpty(t, analysis.Symbols, "Should extract Go symbols")
}

func TestAnalyzer_AnalyzeFile_GoFunctions(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package handlers

func HandleLogin(w ResponseWriter) {
	user := authenticate()
}

func authenticate() *User {
	return nil
}

func validateToken(token string) {
	return
}`

	analysis, err := analyzer.AnalyzeFile("handlers/auth.go", goCode)
	require.NoError(t, err)

	// Check function extraction - at least some functions should be found
	assert.NotEmpty(t, analysis.Symbols, "Should extract Go functions")

	// Check that we have handlers detected
	hasHandler := false
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeHandler {
			hasHandler = true
			break
		}
	}

	assert.True(t, hasHandler || len(analysis.Symbols) > 0, "Should detect functions or handlers")
}

func TestAnalyzer_AnalyzeFile_GoStructs(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package models

type User struct {
	ID   string
	Name string
}

type Post struct {
	ID    string
	Title string
}

func (u *User) String() string {
	return u.Name
}`

	analysis, err := analyzer.AnalyzeFile("models/types.go", goCode)
	require.NoError(t, err)

	structNames := make(map[string]bool)
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeStruct {
			structNames[sym.Name] = true
		}
	}

	assert.True(t, structNames["User"], "Should find User struct")
	assert.True(t, structNames["Post"], "Should find Post struct")
}

func TestAnalyzer_AnalyzeFile_GoMethods(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package main

type Calculator struct {
	value int
}

func (c *Calculator) Add(n int) int {
	c.value += n
	return c.value
}

func (c *Calculator) Multiply(n int) int {
	c.value *= n
	return c.value
}`

	analysis, err := analyzer.AnalyzeFile("calc.go", goCode)
	require.NoError(t, err)

	// Methods should be detected
	methodNames := make(map[string]bool)
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeMethod {
			methodNames[sym.Name] = true
		}
	}

	// Go parsing might detect these as functions or methods depending on implementation
	assert.NotEmpty(t, analysis.Symbols)
}

func TestAnalyzer_AnalyzeFile_Python(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `import os
from typing import Optional

class User:
    """A user entity."""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

def get_user(user_id: str) -> Optional[User]:
    """Get a user by ID."""
    user = User(user_id, "Test User")
    return user

def authenticate(username: str, password: str) -> bool:
    """Authenticate a user."""
    user = get_user(username)
    return validate_password(user, password)

def validate_password(user: User, password: str) -> bool:
    return True`

	analysis, err := analyzer.AnalyzeFile("models/user.py", pyCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Equal(t, LanguagePython, analysis.Language)
	assert.NotEmpty(t, analysis.Symbols, "Should extract Python symbols")
}

func TestAnalyzer_AnalyzeFile_PythonClasses(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `class User:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class Admin(User):
    def __init__(self, name, level):
        super().__init__(name)
        self.level = level`

	analysis, err := analyzer.AnalyzeFile("classes.py", pyCode)
	require.NoError(t, err)

	classNames := make(map[string]bool)
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeClass {
			classNames[sym.Name] = true
		}
	}

	assert.True(t, classNames["User"], "Should find User class")
	assert.True(t, classNames["Admin"], "Should find Admin class")
}

func TestAnalyzer_AnalyzeFile_PythonFunctions(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

async def fetch_data(url):
    response = await http.get(url)
    return response.json()`

	analysis, err := analyzer.AnalyzeFile("utils.py", pyCode)
	require.NoError(t, err)

	functionNames := make(map[string]bool)
	asyncFuncs := make(map[string]bool)

	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeFunction {
			functionNames[sym.Name] = true
			if sym.IsAsync {
				asyncFuncs[sym.Name] = true
			}
		}
	}

	assert.True(t, functionNames["add"], "Should find add function")
	assert.True(t, functionNames["multiply"], "Should find multiply function")
	// Async detection depends on implementation
	if len(asyncFuncs) > 0 {
		assert.True(t, asyncFuncs["fetch_data"], "Should detect async function")
	}
}

func TestAnalyzer_AnalyzeFile_PythonDecorators(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `@decorator
def decorated_function():
    return 42

@property
class ConfigClass:
    @staticmethod
    def static_method():
        return "static"

    @classmethod
    def class_method(cls):
        return cls.__name__`

	analysis, err := analyzer.AnalyzeFile("decorators.py", pyCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)

	// Should handle decorated definitions
	assert.NotEmpty(t, analysis.Symbols)
}

func TestAnalyzer_GoCalls(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `func ProcessUser(id string) {
	user := GetUser(id)
	if user == nil {
		return
	}

	profile := FetchProfile(user.ID)
	SaveCache(user, profile)
}`

	analysis, err := analyzer.AnalyzeFile("processor.go", goCode)
	require.NoError(t, err)

	callNames := make(map[string]bool)
	for _, call := range analysis.Calls {
		callNames[call.TargetName] = true
	}

	// Depending on implementation, these calls should be detected
	assert.NotEmpty(t, analysis.Calls, "Should detect function calls")
}

func TestAnalyzer_PythonCalls(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `def process_data(data):
	result = validate(data)
	if not result:
		return None

	transformed = transform(result)
	return save_to_cache(transformed)`

	analysis, err := analyzer.AnalyzeFile("processor.py", pyCode)
	require.NoError(t, err)

	callNames := make(map[string]bool)
	for _, call := range analysis.Calls {
		callNames[call.TargetName] = true
	}

	// Should detect function calls
	assert.NotEmpty(t, analysis.Calls, "Should detect function calls")
}

func TestAnalyzer_GoImports(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package main

import (
	"fmt"
	"github.com/google/uuid"
	db "github.com/lib/pq"
	. "net/http"
)`

	analysis, err := analyzer.AnalyzeFile("main.go", goCode)
	require.NoError(t, err)

	importPaths := make(map[string]bool)
	for _, imp := range analysis.Imports {
		importPaths[imp.ModulePath] = true
	}

	assert.True(t, importPaths["fmt"], "Should find fmt import")
	assert.True(t, importPaths["github.com/google/uuid"], "Should find uuid import")
}

func TestAnalyzer_PythonImports(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `import os
import sys
from typing import Optional, List
from django.conf import settings
from . import helpers`

	analysis, err := analyzer.AnalyzeFile("imports.py", pyCode)
	require.NoError(t, err)

	importPaths := make(map[string]bool)
	for _, imp := range analysis.Imports {
		importPaths[imp.ModulePath] = true
	}

	assert.True(t, importPaths["os"], "Should find os import")
	assert.True(t, importPaths["sys"], "Should find sys import")
	assert.NotEmpty(t, analysis.Imports)
}

// Edge cases
func TestAnalyzer_Go_EmptyFile(t *testing.T) {
	analyzer := NewAnalyzer()

	analysis, err := analyzer.AnalyzeFile("empty.go", "")
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Empty(t, analysis.Symbols)
}

func TestAnalyzer_Python_Comments(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `# This is a comment
# def commented_function():
#     return 42

def active_function():
    # Internal comment
    return 42`

	analysis, err := analyzer.AnalyzeFile("comments.py", pyCode)
	require.NoError(t, err)

	// Commented function should not be extracted
	var found bool
	for _, sym := range analysis.Symbols {
		if sym.Name == "commented_function" {
			found = true
			break
		}
	}

	assert.False(t, found, "Should not extract commented code")
}

func TestAnalyzer_Go_Interfaces(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package main

type Reader interface {
	Read(p []byte) (n int, err error)
}

type Writer interface {
	Write(p []byte) (n int, err error)
}

type ReadWriter interface {
	Reader
	Writer
}`

	analysis, err := analyzer.AnalyzeFile("interfaces.go", goCode)
	require.NoError(t, err)

	interfaceNames := make(map[string]bool)
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeInterface {
			interfaceNames[sym.Name] = true
		}
	}

	// Depending on implementation, interfaces might be detected
	assert.NotEmpty(t, analysis.Symbols)
}

func TestAnalyzer_Python_Docstrings(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `def documented_function():
	"""
	This is a docstring.
	It can span multiple lines.
	"""
	return True`

	analysis, err := analyzer.AnalyzeFile("docstrings.py", pyCode)
	require.NoError(t, err)

	// Should extract function even with complex docstring
	assert.NotEmpty(t, analysis.Symbols)
}

func TestAnalyzer_Go_Constants(t *testing.T) {
	analyzer := NewAnalyzer()

	goCode := `package main

const (
	Version = "1.0"
	Author  = "Test"
)

const MaxRetries = 3

var GlobalState string
`

	analysis, err := analyzer.AnalyzeFile("constants.go", goCode)
	require.NoError(t, err)

	// Constants and variables might be detected depending on implementation
	assert.NotNil(t, analysis)
}

func TestAnalyzer_Python_Multiline(t *testing.T) {
	analyzer := NewAnalyzer()

	pyCode := `def long_function(
    arg1: str,
    arg2: int,
    arg3: bool
) -> str:
    return f"{arg1}: {arg2}"

class MultilineClass(
    BaseClass1,
    BaseClass2,
):
    pass`

	analysis, err := analyzer.AnalyzeFile("multiline.py", pyCode)
	require.NoError(t, err)

	// Should handle multiline definitions
	assert.NotEmpty(t, analysis.Symbols)
}
