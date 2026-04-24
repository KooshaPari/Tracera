package docindex

import (
	"bytes"
	"regexp"
	"strings"

	"github.com/yuin/goldmark"
	meta "github.com/yuin/goldmark-meta"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/text"
)

const (
	frontmatterStartOffset = 3
	frontmatterDelimiter   = "---"
	sectionLevelCount      = 7
	maxHeadingLevel        = 6
	fileRefConfidence      = 0.9
)

// Parser parses markdown documents into structured sections
type Parser struct {
	md goldmark.Markdown
}

// NewParser creates a new markdown parser
func NewParser() *Parser {
	md := goldmark.New(
		goldmark.WithExtensions(
			extension.GFM, // GitHub Flavored Markdown
			extension.Table,
			extension.Strikethrough,
			extension.TaskList,
			meta.Meta, // YAML frontmatter
		),
		goldmark.WithParserOptions(
			parser.WithAutoHeadingID(),
		),
	)
	return &Parser{md: md}
}

// Parse parses a markdown document and extracts its structure
func (p *Parser) Parse(filePath string, content []byte) (*Document, error) {
	doc := &Document{
		FilePath:      filePath,
		RawContent:    string(content),
		Sections:      make([]*Section, 0),
		CodeRefs:      make([]CodeRef, 0),
		APIRefs:       make([]APIRef, 0),
		InternalLinks: make([]InternalLink, 0),
	}

	// Parse the markdown
	reader := text.NewReader(content)
	root := p.md.Parser().Parse(reader)

	// Extract frontmatter
	doc.Frontmatter = p.extractFrontmatter(content)
	if title, ok := doc.Frontmatter["title"].(string); ok {
		doc.Title = title
	}

	// Extract sections from AST
	doc.Sections = p.extractSections(root, content)

	// Set document title from first h1 if not in frontmatter
	if doc.Title == "" && len(doc.Sections) > 0 {
		doc.Title = doc.Sections[0].Title
	}

	return doc, nil
}

// extractFrontmatter extracts YAML frontmatter from markdown
func (p *Parser) extractFrontmatter(content []byte) map[string]any {
	// Check for frontmatter delimiter
	if !bytes.HasPrefix(content, []byte(frontmatterDelimiter)) {
		return nil
	}

	// Find end delimiter
	end := bytes.Index(content[frontmatterStartOffset:], []byte("\n"+frontmatterDelimiter))
	if end == -1 {
		return nil
	}

	// Parse with goldmark-meta
	ctx := parser.NewContext()
	reader := text.NewReader(content)
	p.md.Parser().Parse(reader, parser.WithContext(ctx))

	metaData := meta.Get(ctx)
	return metaData
}

// buildSectionPath builds the dotted section number path from counters up to the given level.
func buildSectionPath(counters []int, level int) string {
	var pathParts []string
	for i := 1; i <= level; i++ {
		if counters[i] > 0 {
			pathParts = append(pathParts, string(rune('0'+counters[i])))
		}
	}
	return strings.Join(pathParts, ".")
}

// insertSection inserts a section into the hierarchy and updates the stack.
func insertSection(section *Section, sections *[]*Section, stack *[]*Section) {
	for len(*stack) > 0 && (*stack)[len(*stack)-1].Level >= section.Level {
		*stack = (*stack)[:len(*stack)-1]
	}
	if len(*stack) == 0 {
		*sections = append(*sections, section)
	} else {
		parent := (*stack)[len(*stack)-1]
		parent.Children = append(parent.Children, section)
	}
	*stack = append(*stack, section)
}

// extractSections extracts hierarchical sections from the AST
func (p *Parser) extractSections(root ast.Node, source []byte) []*Section {
	var sections []*Section
	var stack []*Section
	counters := make([]int, sectionLevelCount)

	if err := ast.Walk(root, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if !entering {
			return ast.WalkContinue, nil
		}
		heading, ok := n.(*ast.Heading)
		if !ok {
			return ast.WalkContinue, nil
		}

		level := heading.Level
		counters[level]++
		for i := level + 1; i <= maxHeadingLevel; i++ {
			counters[i] = 0
		}

		section := &Section{
			Title:     p.headingText(heading, source),
			Level:     level,
			StartLine: p.getLineNumber(source, heading.Lines().At(0).Start),
			Path:      buildSectionPath(counters, level),
			Children:  make([]*Section, 0),
		}
		insertSection(section, &sections, &stack)

		return ast.WalkContinue, nil
	}); err != nil {
		return sections
	}

	p.extractSectionContent(sections, source)
	return sections
}

func (p *Parser) headingText(heading *ast.Heading, source []byte) string {
	lines := heading.Lines()
	var builder strings.Builder
	for i := 0; i < lines.Len(); i++ {
		segment := lines.At(i)
		builder.Write(segment.Value(source))
	}
	return strings.TrimSpace(builder.String())
}

// getLineNumber returns the 1-based line number for a byte offset
func (p *Parser) getLineNumber(source []byte, offset int) int {
	return bytes.Count(source[:offset], []byte("\n")) + 1
}

// extractSectionContent extracts the text content for each section
func (p *Parser) extractSectionContent(sections []*Section, source []byte) {
	lines := strings.Split(string(source), "\n")

	var extractContent func(sections []*Section, endLine int)
	extractContent = func(sections []*Section, parentEndLine int) {
		for i, section := range sections {
			// Determine end line
			var endLine int
			if i+1 < len(sections) {
				endLine = sections[i+1].StartLine - 1
			} else {
				endLine = parentEndLine
			}
			section.EndLine = endLine

			// Extract content (lines between heading and next section)
			if section.StartLine < endLine && section.StartLine <= len(lines) {
				contentLines := lines[section.StartLine:min(endLine, len(lines))]
				section.Content = strings.TrimSpace(strings.Join(contentLines, "\n"))
				section.RawMarkdown = lines[section.StartLine-1] + "\n" + section.Content
			}

			// Process children
			if len(section.Children) > 0 {
				extractContent(section.Children, endLine)
			}
		}
	}

	extractContent(sections, len(lines))
}

// ExtractCodeRefs extracts code references from text content
func (p *Parser) ExtractCodeRefs(content string) []CodeRef {
	var refs []CodeRef

	// Pattern for inline code
	inlineCode := regexp.MustCompile("`([^`]+)`")
	matches := inlineCode.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		code := content[match[2]:match[3]]
		ref := p.classifyCodeRef(code, match[0], match[1])
		if ref != nil {
			refs = append(refs, *ref)
		}
	}

	// Pattern for file paths
	filePath := regexp.MustCompile(`(?:^|[\s(])([a-zA-Z0-9_\-./]+\.(ts|tsx|js|jsx|go|py|md|json|yaml|yml))(?:[\s):]|$)`)
	matches = filePath.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		path := content[match[2]:match[3]]
		refs = append(refs, CodeRef{
			Type:        "file",
			Name:        path,
			FilePath:    path,
			StartOffset: match[2],
			EndOffset:   match[3],
			Confidence:  fileRefConfidence,
		})
	}

	return refs
}
