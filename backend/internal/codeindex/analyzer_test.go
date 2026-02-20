package codeindex

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewAnalyzer(t *testing.T) {
	analyzer := NewAnalyzer()
	assert.NotNil(t, analyzer)
	assert.NotNil(t, analyzer.parser)
}

func TestAnalyzer_AnalyzeFile_TypeScript(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export function getUserName(id: string): string {
  const user = getUser(id);
  return user.name;
}

export const MyComponent: React.FC = () => {
  return <div>Hello</div>;
};

export class UserService {
  async fetchUser(id: string) {
    return await fetch('/api/users/' + id);
  }
}

export interface User {
  id: string;
  name: string;
}

export type UserId = string;`

	analysis, err := analyzer.AnalyzeFile("src/user.ts", tsCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Equal(t, "src/user.ts", analysis.FilePath)
	assert.Equal(t, LanguageTypeScript, analysis.Language)
	assert.NotEmpty(t, analysis.ContentHash)

	// Check symbols extraction
	assert.NotEmpty(t, analysis.Symbols, "Should extract symbols")

	// Find function
	foundFunc := findSymbol(analysis.Symbols, "getUserName", SymbolTypeFunction)
	assert.NotNil(t, foundFunc, "Should find getUserName function")
	assert.True(t, foundFunc.IsExported, "getUserName should be exported")

	// Find component
	foundComponent := findSymbol(analysis.Symbols, "MyComponent", SymbolTypeComponent)
	assert.NotNil(t, foundComponent, "Should find MyComponent")
	assert.True(t, foundComponent.IsExported, "MyComponent should be exported")

	// Find class
	foundClass := findSymbol(analysis.Symbols, "UserService", SymbolTypeClass)
	assert.NotNil(t, foundClass, "Should find UserService class")

	// Find interface
	foundInterface := findSymbol(analysis.Symbols, "User", SymbolTypeInterface)
	assert.NotNil(t, foundInterface, "Should find User interface")

	// Find type
	foundType := findSymbol(analysis.Symbols, "UserId", SymbolTypeType)
	assert.NotNil(t, foundType, "Should find UserId type")
}

func TestAnalyzer_AnalyzeFile_TypeScriptCalls(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export function processUser(id: string) {
  const user = getUser(id);
  const profile = await fetchProfile(user.id);
  saveCache(user, profile);
  return transform(user, profile);
}`

	analysis, err := analyzer.AnalyzeFile("src/processor.ts", tsCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)

	// Check calls extraction
	assert.NotEmpty(t, analysis.Calls, "Should extract calls")

	// Verify specific calls
	callNames := make(map[string]bool)
	for _, call := range analysis.Calls {
		callNames[call.TargetName] = true
	}

	assert.True(t, callNames["getUser"], "Should find getUser call")
	assert.True(t, callNames["fetchProfile"], "Should find fetchProfile call")
	assert.True(t, callNames["saveCache"], "Should find saveCache call")
}

func findSymbol(symbols []SymbolInfo, name string, symbolType SymbolType) *SymbolInfo {
	for i := range symbols {
		if symbols[i].Name == name && symbols[i].Type == symbolType {
			return &symbols[i]
		}
	}
	return nil
}

func TestAnalyzer_AnalyzeFile_TypeScriptAsync(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export async function fetchData() {
  const result = await fetch('/api/data');
  return await result.json();
}`

	analysis, err := analyzer.AnalyzeFile("src/async.ts", tsCode)
	require.NoError(t, err)

	var foundAsyncFunc *SymbolInfo
	for i := range analysis.Symbols {
		if analysis.Symbols[i].Name == "fetchData" {
			foundAsyncFunc = &analysis.Symbols[i]
			break
		}
	}
	assert.NotNil(t, foundAsyncFunc)
	assert.True(t, foundAsyncFunc.IsAsync, "fetchData should be marked as async")
}

func TestAnalyzer_AnalyzeFile_TypeScriptHooks(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export const useAuth = () => {
  const [user, setUser] = useState(null);
  return { user, setUser };
};

export const useUser = (id: string) => {
  const user = useAuth();
  return user;
};`

	analysis, err := analyzer.AnalyzeFile("src/hooks.ts", tsCode)
	require.NoError(t, err)

	var foundUseAuth *SymbolInfo
	var foundUseUser *SymbolInfo

	for i := range analysis.Symbols {
		if analysis.Symbols[i].Name == "useAuth" {
			foundUseAuth = &analysis.Symbols[i]
		}
		if analysis.Symbols[i].Name == "useUser" {
			foundUseUser = &analysis.Symbols[i]
		}
	}

	// Note: The arrow function pattern matcher doesn't detect hooks yet,
	// they are detected as constants and then upgraded to hooks via const pattern
	assert.NotNil(t, foundUseAuth)
	assert.True(t, foundUseAuth.IsExported, "useAuth should be exported")
	assert.NotNil(t, foundUseUser)
	assert.True(t, foundUseUser.IsExported, "useUser should be exported")
}

func TestAnalyzer_AnalyzeFile_JavaScript(t *testing.T) {
	analyzer := NewAnalyzer()

	jsCode := `function add(a, b) {
  return a + b;
}

const multiply = (x, y) => x * y;

module.exports = { add, multiply };`

	analysis, err := analyzer.AnalyzeFile("src/math.js", jsCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Equal(t, LanguageJavaScript, analysis.Language)
	assert.NotEmpty(t, analysis.Symbols)
}

func TestAnalyzer_AnalyzeFile_UnsupportedLanguage(t *testing.T) {
	analyzer := NewAnalyzer()

	analysis, err := analyzer.AnalyzeFile("README.md", "# Documentation")
	assert.Nil(t, analysis)
	assert.NoError(t, err) // Should handle gracefully
}

func TestAnalyzer_AnalyzeFile_EmptyFile(t *testing.T) {
	analyzer := NewAnalyzer()

	analysis, err := analyzer.AnalyzeFile("src/empty.ts", "")
	require.NoError(t, err)
	assert.NotNil(t, analysis)
	assert.Empty(t, analysis.Symbols)
	assert.Empty(t, analysis.Calls)
}

func TestAnalyzer_ExtractTSSymbols_ExportedVsPrivate(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export function publicFunc() {}
function privateFunc() {}
export const publicConst = 42;
const privateConst = 42;`

	symbols := analyzer.extractTSSymbols(tsCode)

	exportedCount := 0
	privateCount := 0
	for _, sym := range symbols {
		if sym.IsExported {
			exportedCount++
		} else {
			privateCount++
		}
	}

	assert.Equal(t, 2, exportedCount, "Should have 2 exported symbols")
	assert.Equal(t, 2, privateCount, "Should have 2 private symbols")
}

func TestAnalyzer_ExtractTSCalls_FilterKeywords(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `if (condition()) {
  for (let i = 0; i < 10; i++) {
    doSomething();
  }
}`

	calls := analyzer.extractTSCalls(tsCode)

	// Keywords like if, for should be filtered out
	for _, call := range calls {
		assert.NotEqual(t, "if", call.TargetName)
		assert.NotEqual(t, "for", call.TargetName)
	}

	// But actual calls should be found
	found := false
	for _, call := range calls {
		if call.TargetName == "doSomething" {
			found = true
			break
		}
	}
	assert.True(t, found, "Should find doSomething call")
}

func TestAnalyzer_ExtractTSCalls_MethodChains(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `const result = user.getProfile().getSettings().getSecurity();
logger.info('done');`

	calls := analyzer.extractTSCalls(tsCode)

	// Method chains should be captured
	callNames := make(map[string]bool)
	for _, call := range calls {
		callNames[call.TargetName] = true
	}

	assert.True(t, callNames["user.getProfile"], "Should find user.getProfile call")
	assert.True(t, callNames["logger.info"], "Should find logger.info call")
}

func TestAnalyzer_HashContent(t *testing.T) {
	analyzer := NewAnalyzer()

	content1 := "const x = 42;"
	content2 := "const x = 42;"
	content3 := "const x = 43;"

	hash1 := analyzer.hashContent(content1)
	hash2 := analyzer.hashContent(content2)
	hash3 := analyzer.hashContent(content3)

	assert.Equal(t, hash1, hash2, "Same content should produce same hash")
	assert.NotEqual(t, hash1, hash3, "Different content should produce different hash")
	assert.Len(t, hash1, 64, "SHA256 hash should be 64 characters")
}

func TestAnalyzer_AnalyzeFile_WithAnnotations(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `// @trace-implements(login-flow)
export function loginUser(email: string) {
  // @canonical(AuthService)
  return authenticate(email);
}`

	analysis, err := analyzer.AnalyzeFile("src/auth.ts", tsCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)

	// Annotations should be extracted
	assert.NotEmpty(t, analysis.Annotations)
	assert.Equal(t, "trace_implements", analysis.Annotations[0].Name)
	assert.Equal(t, "login-flow", analysis.Annotations[0].Value)
}

func TestAnalyzer_AnalyzeFile_WithImports(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `import { useState } from 'react';
import * as utils from './utils';
import axios from 'axios';

export function MyComponent() {
  const [state, setState] = useState(null);
  return utils.render();
}`

	analysis, err := analyzer.AnalyzeFile("src/component.tsx", tsCode)
	require.NoError(t, err)
	assert.NotNil(t, analysis)

	// Imports should be extracted
	assert.NotEmpty(t, analysis.Imports)

	// Verify imports
	importPaths := make(map[string]bool)
	for _, imp := range analysis.Imports {
		importPaths[imp.ModulePath] = true
	}

	assert.True(t, importPaths["react"], "Should find react import")
	assert.True(t, importPaths["./utils"], "Should find utils import")
	assert.True(t, importPaths["axios"], "Should find axios import")
}

func TestAnalyzer_AnalyzeFile_LineNumbers(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `// Line 1

export function test() {  // Line 3
  return 42;
}`

	analysis, err := analyzer.AnalyzeFile("src/test.ts", tsCode)
	require.NoError(t, err)

	var testFunc *SymbolInfo
	for i := range analysis.Symbols {
		if analysis.Symbols[i].Name == "test" {
			testFunc = &analysis.Symbols[i]
			break
		}
	}

	assert.NotNil(t, testFunc)
	assert.Equal(t, 3, testFunc.StartLine, "Function should start at line 3")
}

// Test edge cases
func TestAnalyzer_EdgeCase_NestedFunctions(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `export function outer() {
  function inner() {
    return 42;
  }
  return inner();
}`

	analysis, err := analyzer.AnalyzeFile("src/nested.ts", tsCode)
	require.NoError(t, err)

	// Should find both functions
	funcNames := make(map[string]bool)
	for _, sym := range analysis.Symbols {
		if sym.Type == SymbolTypeFunction {
			funcNames[sym.Name] = true
		}
	}

	assert.True(t, funcNames["outer"], "Should find outer function")
	assert.True(t, funcNames["inner"], "Should find inner function")
}

func TestAnalyzer_EdgeCase_MultilineStrings(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := "export function query() {\n  const sql = `\n    SELECT * FROM users\n    WHERE id = $1\n  `;\n  return db.query(sql);\n}"

	analysis, err := analyzer.AnalyzeFile("src/query.ts", tsCode)
	require.NoError(t, err)

	var found bool
	for _, sym := range analysis.Symbols {
		if sym.Name == "query" {
			found = true
			break
		}
	}
	assert.True(t, found, "Should handle multiline strings")
}

func TestAnalyzer_EdgeCase_CommentedCode(t *testing.T) {
	analyzer := NewAnalyzer()

	tsCode := `// export function commented() {
//   return 42;
// }

export function active() {
  return 42;
}`

	analysis, err := analyzer.AnalyzeFile("src/commented.ts", tsCode)
	require.NoError(t, err)

	// Should only find active function, not commented one
	var found bool
	for _, sym := range analysis.Symbols {
		if sym.Name == "commented" {
			found = true
			break
		}
	}
	assert.False(t, found, "Should not extract commented code")
}
