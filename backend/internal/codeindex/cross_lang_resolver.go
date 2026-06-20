package codeindex

import (
	"context"
	"regexp"
	"strconv"
	"strings"

	"github.com/google/uuid"
)

const (
	apiMatchMinCount        = 2
	apiAxiosMatchMinCount   = 3
	apiHandlerConfidence    = 0.9
	apiTypeRefConfidence    = 0.7
	apiPathPrefixConfidence = 0.7
)

// CrossLangResolver resolves references between different programming languages
type CrossLangResolver struct {
	repo Repository
}

// NewCrossLangResolver creates a new cross-language resolver
func NewCrossLangResolver(repo Repository) *CrossLangResolver {
	return &CrossLangResolver{repo: repo}
}

// CrossLangRef represents a cross-language reference
type CrossLangRef struct {
	SourceID   uuid.UUID `json:"source_id"`
	SourceLang Language  `json:"source_lang"`
	TargetID   uuid.UUID `json:"target_id"`
	TargetLang Language  `json:"target_lang"`
	RefType    string    `json:"ref_type"` // api_call, import, type_ref
	Confidence float64   `json:"confidence"`
	Evidence   string    `json:"evidence"`
}

// ResolveAPIReferences finds backend handlers for frontend API calls
func (resolver *CrossLangResolver) ResolveAPIReferences(
	ctx context.Context,
	projectID uuid.UUID,
	entity *CodeEntity,
) ([]CrossLangRef, error) {
	var refs []CrossLangRef

	// Look for fetch/axios calls in TypeScript/JavaScript
	if entity.Language != LanguageTypeScript && entity.Language != LanguageJavaScript {
		return refs, nil
	}

	// Extract API paths from calls
	apiPaths := resolver.extractAPIPaths(entity.Content)

	for _, apiPath := range apiPaths {
		// Find matching backend handlers
		handlers, err := resolver.repo.FindByAPIPath(ctx, projectID, apiPath.Path)
		if err != nil {
			continue
		}

		for _, handler := range handlers {
			refs = append(refs, CrossLangRef{
				SourceID:   entity.ID,
				SourceLang: entity.Language,
				TargetID:   handler.ID,
				TargetLang: handler.Language,
				RefType:    "api_call",
				Confidence: apiHandlerConfidence,
				Evidence:   apiPath.Method + " " + apiPath.Path,
			})
		}
	}

	return refs, nil
}

// APIPath represents an extracted API path
type APIPath struct {
	Method string
	Path   string
	Line   int
}

type apiPathMatchers struct {
	fetch *regexp.Regexp
	axios *regexp.Regexp
	api   *regexp.Regexp
}

// extractAPIPaths extracts API paths from frontend code
func (resolver *CrossLangResolver) extractAPIPaths(content string) []APIPath {
	lines := strings.Split(content, "\n")

	matchers := apiPathMatchers{
		fetch: regexp.MustCompile(`fetch\s*\(\s*['"\x60]([^'"\x60]+)['"\x60]`),
		axios: regexp.MustCompile(`axios\.(get|post|put|patch|delete)\s*\(\s*['"\x60]([^'"\x60]+)['"\x60]`),
		api:   regexp.MustCompile(`['"\x60](/api/[^'"\x60]+)['"\x60]`),
	}

	seen := make(map[string]bool)
	paths := make([]APIPath, 0, len(lines))

	for lineNum, line := range lines {
		paths = append(
			paths,
			extractLineAPIPaths(line, lineNum+1, matchers, seen)...,
		)
	}

	return paths
}

func extractLineAPIPaths(line string, lineNum int, matchers apiPathMatchers, seen map[string]bool) []APIPath {
	paths := make([]APIPath, 0, apiMatchMinCount)

	if matches := matchers.fetch.FindStringSubmatch(line); len(matches) >= apiMatchMinCount {
		addAPIPath(&paths, seen, APIPath{
			Method: detectFetchMethod(line),
			Path:   matches[1],
			Line:   lineNum,
		})
	}

	if matches := matchers.axios.FindStringSubmatch(line); len(matches) >= apiAxiosMatchMinCount {
		addAPIPath(&paths, seen, APIPath{
			Method: strings.ToUpper(matches[1]),
			Path:   matches[2],
			Line:   lineNum,
		})
	}

	if matches := matchers.api.FindStringSubmatch(line); len(matches) >= apiMatchMinCount {
		addAPIPath(&paths, seen, APIPath{
			Path: matches[1],
			Line: lineNum,
		})
	}

	return paths
}

func addAPIPath(paths *[]APIPath, seen map[string]bool, apiPath APIPath) {
	if apiPath.Path == "" {
		return
	}

	key := apiPath.Path + ":" + strconv.Itoa(apiPath.Line)
	if seen[key] {
		return
	}
	seen[key] = true
	*paths = append(*paths, apiPath)
}

func detectFetchMethod(line string) string {
	if !strings.Contains(line, "method:") {
		return "GET"
	}

	switch {
	case strings.Contains(line, "'POST'") || strings.Contains(line, `"POST"`):
		return "POST"
	case strings.Contains(line, "'PUT'") || strings.Contains(line, `"PUT"`):
		return "PUT"
	case strings.Contains(line, "'DELETE'") || strings.Contains(line, `"DELETE"`):
		return "DELETE"
	default:
		return "GET"
	}
}

// ResolveTypeReferences finds type definitions across languages
func (resolver *CrossLangResolver) ResolveTypeReferences(
	ctx context.Context,
	projectID uuid.UUID,
	entity *CodeEntity,
) ([]CrossLangRef, error) {
	var refs []CrossLangRef

	// Look for type references in the entity
	typeRefs := resolver.extractTypeReferences(entity)

	for _, typeRef := range typeRefs {
		// Search for matching types in other languages
		matches, err := resolver.repo.FindBySymbolName(ctx, projectID, typeRef)
		if err != nil {
			continue
		}

		for _, match := range matches {
			// Only include cross-language matches
			if match.Language == entity.Language {
				continue
			}

			refs = append(refs, CrossLangRef{
				SourceID:   entity.ID,
				SourceLang: entity.Language,
				TargetID:   match.ID,
				TargetLang: match.Language,
				RefType:    "type_ref",
				Confidence: apiTypeRefConfidence,
				Evidence:   "Type reference: " + typeRef,
			})
		}
	}

	return refs, nil
}

// extractTypeReferences extracts type references from code
func (resolver *CrossLangResolver) extractTypeReferences(entity *CodeEntity) []string {
	var types []string
	seen := make(map[string]bool)

	resolver.appendSignatureTypes(entity.Signature, seen, &types)
	resolver.appendReferenceTypes(entity.References, seen, &types)

	return types
}

func (resolver *CrossLangResolver) appendSignatureTypes(
	signature string,
	seen map[string]bool,
	types *[]string,
) {
	if signature == "" {
		return
	}
	typePattern := regexp.MustCompile(`[A-Z][a-zA-Z0-9]+`)
	matches := typePattern.FindAllString(signature, -1)
	for _, match := range matches {
		resolver.appendTypeMatch(match, seen, types)
	}
}

func (resolver *CrossLangResolver) appendReferenceTypes(
	references []SymbolRef,
	seen map[string]bool,
	types *[]string,
) {
	for _, ref := range references {
		if ref.RefType != "extends" && ref.RefType != "implements" {
			continue
		}
		resolver.appendTypeMatch(ref.SymbolName, seen, types)
	}
}

func (resolver *CrossLangResolver) appendTypeMatch(
	match string,
	seen map[string]bool,
	types *[]string,
) {
	if seen[match] || isCommonType(match) {
		return
	}
	*types = append(*types, match)
	seen[match] = true
}

func isCommonType(name string) bool {
	common := map[string]bool{
		"String": true, "Int": true, "Float": true, "Bool": true, "Boolean": true,
		"Array": true, "Object": true, "Map": true, "Set": true, "List": true,
		"Error": true, "Promise": true, "Context": true, "Request": true, "Response": true,
	}
	return common[name]
}
