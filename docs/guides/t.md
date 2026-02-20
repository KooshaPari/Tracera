                                                                                                         
▗ ▗   ▖ ▖  Claude Code v2.1.25                                                                           
           Opus 4.5 · Claude Max                                                                         
  ▘▘ ▝▝    ~/temp-PRODVERCEL/485/kush/trace                                                              
                                                                                                         
╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Plan to implement                                                                                     │
│                                                                                                       │
│ Multi-Dimensional Traceability Model: Unified Graph Visualization                                     │
│                                                                                                       │
│ Vision                                                                                                │
│                                                                                                       │
│ Transform the graph visualization into a multi-dimensional traceability model that unifies:           │
│ - Perspectives (stakeholder views: product, business, technical, security, etc.)                      │
│ - Dimensions (orthogonal cross-cutting concerns: maturity, complexity, coverage)                      │
│ - Canonical Concepts (abstract entities that manifest as projections in each view)                    │
│ - Code Mapping (repository indexing with AST-level granularity)                                       │
│ - Documentation Nodes (hierarchical: document → section → chunk)                                      │
│ - Automatic Journey Derivation (user flows, data paths, call chains)                                  │
│                                                                                                       │
│ The core insight: Each view is a complete dimension of the product, with nodes existing independently │
│  per view but linked as equivalents through canonical concepts.                                       │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 1: Conceptual Architecture                                                                       │
│                                                                                                       │
│ 1.1 Three-Layer Equivalence Model                                                                     │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────┐                               │
│ │                      CANONICAL LAYER                                │                               │
│ │  Abstract concepts that exist independently of any view             │                               │
│ │  e.g., "User Authentication" concept                                │                               │
│ └────────────────────────────┬────────────────────────────────────────┘                               │
│                              │ manifests_as                                                           │
│         ┌────────────────────┼────────────────────┐                                                   │
│         ▼                    ▼                    ▼                                                   │
│ ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                                             │
│ │ PRODUCT VIEW  │   │ TECHNICAL VIEW│   │ SECURITY VIEW │                                             │
│ │ "Login Feature"│   │ "AuthService" │   │ "Auth Req 2.1"│                                            │
│ │               │   │ "login()"     │   │               │                                             │
│ └───────────────┘   └───────────────┘   └───────────────┘                                             │
│         │                    │                    │                                                   │
│         └────────────────────┴────────────────────┘                                                   │
│                     equivalent_to (inferred + manual)                                                 │
│                                                                                                       │
│ Three Layers:                                                                                         │
│ 1. Canonical Concepts - Abstract, view-agnostic entities (stored)                                     │
│ 2. View Projections - Concrete nodes in each perspective (stored, linked to canonical)                │
│ 3. Inferred Equivalence - Auto-detected relationships + manual overrides                              │
│                                                                                                       │
│ 1.2 Dimension Orthogonality                                                                           │
│                                                                                                       │
│                      PERSPECTIVES (Stakeholder Views)                                                 │
│                      ─────────────────────────────────►                                               │
│                      Product │ Technical │ Security │ ...                                             │
│               ┌──────────────┼───────────┼──────────┤                                                 │
│               │              │           │          │                                                 │
│   DIMENSIONS  │  Draft       │     ●     │    ●     │                                                 │
│   (Cross-     ├──────────────┼───────────┼──────────┤                                                 │
│   cutting)    │  In Review   │     ●     │          │                                                 │
│               ├──────────────┼───────────┼──────────┤                                                 │
│       │       │  Approved    │           │    ●     │                                                 │
│       ▼       └──────────────┴───────────┴──────────┘                                                 │
│                                                                                                       │
│ Perspectives = WHO sees it (product manager, developer, security auditor)                             │
│ Dimensions = WHAT state it's in (maturity, complexity, test coverage, priority)                       │
│                                                                                                       │
│ Dimensions don't filter visibility - they annotate/color nodes within any perspective.                │
│                                                                                                       │
│ 1.3 Documentation as First-Class Nodes                                                                │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────┐                                   │
│ │                    DOCUMENTATION DIMENSION                       │                                  │
│ ├─────────────────────────────────────────────────────────────────┤                                   │
│ │                                                                 │                                   │
│ │  ┌─────────────┐                                                │                                   │
│ │  │ Document    │  README.md, API.md, ARCHITECTURE.md            │                                   │
│ │  │ (doc_root)  │                                                │                                   │
│ │  └──────┬──────┘                                                │                                   │
│ │         │                                                       │                                   │
│ │  ┌──────┴──────┐                                                │                                   │
│ │  │ Section     │  "## Authentication", "## API Endpoints"       │                                   │
│ │  │ (doc_section)                                                │                                   │
│ │  └──────┬──────┘                                                │                                   │
│ │         │                                                       │                                   │
│ │  ┌──────┴──────┐                                                │                                   │
│ │  │ Chunk       │  Paragraphs, code blocks, tables               │                                   │
│ │  │ (doc_chunk) │  AI-parsed semantic units                      │                                   │
│ │  └─────────────┘                                                │                                   │
│ │                                                                 │                                   │
│ │  Links: documents → mentions → code entities                    │                                   │
│ │         documents → describes → requirements                    │                                   │
│ │         documents → specifies → API endpoints                   │                                   │
│ └─────────────────────────────────────────────────────────────────┘                                   │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 2: Data Model Extensions                                                                         │
│                                                                                                       │
│ 2.1 Canonical Concept Entity                                                                          │
│                                                                                                       │
│ File: /frontend/packages/types/src/canonical.ts (new)                                                 │
│                                                                                                       │
│ export interface CanonicalConcept {                                                                   │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   name: string;                                                                                       │
│   description?: string;                                                                               │
│                                                                                                       │
│   // Type classification                                                                              │
│   conceptType: 'feature' | 'capability' | 'component' | 'domain' | 'integration';                     │
│                                                                                                       │
│   // Projections in each perspective                                                                  │
│   projections: {                                                                                      │
│     perspectiveId: string;                                                                            │
│     itemId: string;          // The concrete Item in that view                                        │
│     confidence: number;      // 0-1, how strongly this maps                                           │
│     source: 'manual' | 'inferred' | 'canonical';                                                      │
│   }[];                                                                                                │
│                                                                                                       │
│   // Semantic identity                                                                                │
│   keywords: string[];                                                                                 │
│   embedding?: number[];      // Vector for semantic matching                                          │
│                                                                                                       │
│   // Metadata                                                                                         │
│   createdAt: string;                                                                                  │
│   updatedAt: string;                                                                                  │
│   createdBy: 'user' | 'system';                                                                       │
│ }                                                                                                     │
│                                                                                                       │
│ 2.2 Extended Item Model                                                                               │
│                                                                                                       │
│ File: /frontend/packages/types/src/item.ts (modified)                                                 │
│                                                                                                       │
│ export interface Item {                                                                               │
│   // ... existing fields ...                                                                          │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   title: string;                                                                                      │
│   description?: string;                                                                               │
│   type: string;                                                                                       │
│   status: ItemStatus;                                                                                 │
│                                                                                                       │
│   // NEW: Canonical linkage                                                                           │
│   canonicalId?: string;              // Links to CanonicalConcept                                     │
│                                                                                                       │
│   // NEW: Perspective override                                                                        │
│   perspectives?: string[];           // Override TYPE_TO_PERSPECTIVE default                          │
│                                                                                                       │
│   // NEW: Dimension values (orthogonal to perspective)                                                │
│   dimensions?: {                                                                                      │
│     maturity?: 'draft' | 'review' | 'approved' | 'deprecated';                                        │
│     complexity?: 'low' | 'medium' | 'high' | 'critical';                                              │
│     coverage?: number;               // 0-100%                                                        │
│     priority?: 'p0' | 'p1' | 'p2' | 'p3';                                                             │
│     [key: string]: unknown;          // Extensible                                                    │
│   };                                                                                                  │
│                                                                                                       │
│   // NEW: For code entities                                                                           │
│   codeRef?: {                                                                                         │
│     repositoryId: string;                                                                             │
│     filePath: string;                                                                                 │
│     startLine: number;                                                                                │
│     endLine: number;                                                                                  │
│     language: string;                                                                                 │
│     qualifiedName: string;                                                                            │
│   };                                                                                                  │
│                                                                                                       │
│   // NEW: For documentation entities                                                                  │
│   docRef?: {                                                                                          │
│     sourceType: 'markdown' | 'wiki' | 'docstring' | 'comment';                                        │
│     sourcePath: string;                                                                               │
│     headingLevel?: number;           // 1-6 for markdown headers                                      │
│     parentDocId?: string;            // For hierarchical docs                                         │
│   };                                                                                                  │
│                                                                                                       │
│   // Existing                                                                                         │
│   metadata?: Record<string, unknown>;                                                                 │
│   parentId?: string;                                                                                  │
│   version: number;                                                                                    │
│   createdAt: string;                                                                                  │
│   updatedAt: string;                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ 2.3 Enhanced Link Types                                                                               │
│                                                                                                       │
│ File: /frontend/packages/types/src/link.ts (modified)                                                 │
│                                                                                                       │
│ export type LinkType =                                                                                │
│   // Existing                                                                                         │
│   | 'implements' | 'tests' | 'depends_on' | 'related_to' | 'blocks' | 'parent_of'                     │
│                                                                                                       │
│   // NEW: Cross-view equivalence                                                                      │
│   | 'same_as'           // Explicit: "these are the same concept"                                     │
│   | 'represents'        // "code X represents requirement Y"                                          │
│   | 'manifests_as'      // Canonical → projection                                                     │
│                                                                                                       │
│   // NEW: Documentation                                                                               │
│   | 'documents'         // "doc X documents code Y"                                                   │
│   | 'mentions'          // "doc X mentions concept Y"                                                 │
│   | 'specifies'         // "doc X specifies API Y"                                                    │
│                                                                                                       │
│   // NEW: Code relationships                                                                          │
│   | 'calls' | 'imports' | 'extends' | 'contains'                                                      │
│                                                                                                       │
│   // NEW: Navigation                                                                                  │
│   | 'navigates_to' | 'opens_modal' | 'triggers_event';                                                │
│                                                                                                       │
│ export interface Link {                                                                               │
│   // ... existing fields ...                                                                          │
│                                                                                                       │
│   // NEW: Cross-perspective indicator                                                                 │
│   crossPerspective?: boolean;        // True if source and target are in different perspectives       │
│                                                                                                       │
│   // NEW: Equivalence confidence (for same_as, represents links)                                      │
│   equivalenceConfidence?: number;    // 0-1                                                           │
│   equivalenceSource?: 'manual' | 'inferred' | 'pattern';                                              │
│ }                                                                                                     │
│                                                                                                       │
│ 2.4 Perspective Configuration (Project-Customizable)                                                  │
│                                                                                                       │
│ File: /frontend/packages/types/src/perspective.ts (modified)                                          │
│                                                                                                       │
│ export interface PerspectiveConfig {                                                                  │
│   id: string;                                                                                         │
│   projectId?: string;                // undefined = global default                                    │
│                                                                                                       │
│   // Display                                                                                          │
│   label: string;                                                                                      │
│   description: string;                                                                                │
│   icon: string;                                                                                       │
│   color: string;                                                                                      │
│                                                                                                       │
│   // Type mapping (customizable per project)                                                          │
│   includeTypes: string[];                                                                             │
│   excludeTypes?: string[];                                                                            │
│                                                                                                       │
│   // Layout preferences                                                                               │
│   defaultLayout: 'elk' | 'dagre' | 'cose' | 'breadthfirst';                                           │
│                                                                                                       │
│   // NEW: Dimension visibility                                                                        │
│   visibleDimensions?: string[];      // Which dimensions to show in this perspective                  │
│                                                                                                       │
│   // NEW: Cross-perspective settings                                                                  │
│   showCrossPerspectiveLinks?: boolean;                                                                │
│   bridgePerspectives?: string[];     // Other perspectives that commonly link to this one             │
│ }                                                                                                     │
│                                                                                                       │
│ 2.5 Database Schema Additions                                                                         │
│                                                                                                       │
│ -- Canonical concepts table                                                                           │
│ CREATE TABLE canonical_concepts (                                                                     │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│   name VARCHAR(500) NOT NULL,                                                                         │
│   description TEXT,                                                                                   │
│   concept_type VARCHAR(50) NOT NULL,                                                                  │
│   keywords TEXT[],                                                                                    │
│   embedding VECTOR(1536),            -- For semantic search                                           │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Canonical projections (many-to-many: canonical ↔ items)                                            │
│ CREATE TABLE canonical_projections (                                                                  │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   canonical_id UUID NOT NULL REFERENCES canonical_concepts(id) ON DELETE CASCADE,                     │
│   item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,                                       │
│   perspective_id VARCHAR(50) NOT NULL,                                                                │
│   confidence DECIMAL(3,2) NOT NULL DEFAULT 1.0,                                                       │
│   source VARCHAR(20) NOT NULL DEFAULT 'manual',                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   UNIQUE(canonical_id, item_id)                                                                       │
│ );                                                                                                    │
│                                                                                                       │
│ -- Documentation entities                                                                             │
│ CREATE TABLE doc_entities (                                                                           │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   repository_id UUID REFERENCES code_repositories(id),                                                │
│   item_id UUID REFERENCES items(id),         -- Links to traceability item                            │
│                                                                                                       │
│   source_type VARCHAR(50) NOT NULL,          -- markdown, wiki, docstring, comment                    │
│   source_path VARCHAR(1000) NOT NULL,                                                                 │
│   heading_level INTEGER,                                                                              │
│   parent_doc_id UUID REFERENCES doc_entities(id),                                                     │
│                                                                                                       │
│   title VARCHAR(500),                                                                                 │
│   content TEXT,                                                                                       │
│   content_hash VARCHAR(64),                                                                           │
│                                                                                                       │
│   -- Extracted entities for linking                                                                   │
│   mentioned_symbols TEXT[],                   -- Code symbols mentioned                               │
│   mentioned_concepts TEXT[],                  -- Business terms mentioned                             │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Code entities (from Part 1 plan, enhanced)                                                         │
│ CREATE TABLE code_entities (                                                                          │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   repository_id UUID NOT NULL REFERENCES code_repositories(id) ON DELETE CASCADE,                     │
│   item_id UUID REFERENCES items(id),                                                                  │
│   canonical_id UUID REFERENCES canonical_concepts(id),  -- NEW: direct canonical link                 │
│                                                                                                       │
│   entity_type VARCHAR(50) NOT NULL,                                                                   │
│   qualified_name VARCHAR(1000) NOT NULL,                                                              │
│   simple_name VARCHAR(255) NOT NULL,                                                                  │
│   file_path VARCHAR(1000) NOT NULL,                                                                   │
│   start_line INTEGER NOT NULL,                                                                        │
│   end_line INTEGER NOT NULL,                                                                          │
│   language VARCHAR(50) NOT NULL,                                                                      │
│                                                                                                       │
│   signature TEXT,                                                                                     │
│   documentation TEXT,                         -- Extracted docstring                                  │
│   visibility VARCHAR(20),                                                                             │
│                                                                                                       │
│   content_hash VARCHAR(64),                                                                           │
│   embedding VECTOR(1536),                     -- For semantic matching                                │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Project-specific perspective overrides                                                             │
│ CREATE TABLE perspective_configs (                                                                    │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│   perspective_id VARCHAR(50) NOT NULL,                                                                │
│                                                                                                       │
│   config_overrides JSONB NOT NULL DEFAULT '{}',                                                       │
│   custom_type_mapping JSONB,                  -- type → perspectives[]                                │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   UNIQUE(project_id, perspective_id)                                                                  │
│ );                                                                                                    │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 3: Equivalence Detection System                                                                  │
│                                                                                                       │
│ 3.1 Multi-Strategy Equivalence Engine                                                                 │
│                                                                                                       │
│ Location: /backend/internal/equivalence/                                                              │
│                                                                                                       │
│ equivalence/                                                                                          │
│ ├── engine.go              # Orchestrates all strategies                                              │
│ ├── strategies/                                                                                       │
│ │   ├── naming.go          # Pattern-based name matching                                              │
│ │   ├── semantic.go        # Embedding-based similarity                                               │
│ │   ├── structural.go      # Graph structure analysis                                                 │
│ │   ├── api_contract.go    # Frontend→Backend API matching                                            │
│ │   └── annotation.go      # Explicit @trace comments                                                 │
│ ├── confidence.go          # Confidence scoring                                                       │
│ └── resolver.go            # Conflict resolution                                                      │
│                                                                                                       │
│ 3.2 Detection Strategies (Ordered by Confidence)                                                      │
│ ┌─────────────────────┬────────────┬─────────────────────────────────────────────┐                    │
│ │      Strategy       │ Confidence │                How It Works                 │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Explicit Annotation │ 1.0        │ Parse @trace-implements X comments in code  │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Manual Link         │ 1.0        │ User-created same_as or represents links    │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ API Contract        │ 0.9        │ Match frontend fetch URLs to backend routes │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Shared Canonical    │ 0.9        │ Items linked to same CanonicalConcept       │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Naming Pattern      │ 0.7        │ useGetUser → GetUser → user_story:get_user  │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Semantic Similarity │ 0.6        │ Embedding cosine similarity > 0.85          │                    │
│ ├─────────────────────┼────────────┼─────────────────────────────────────────────┤                    │
│ │ Structural          │ 0.5        │ Similar graph neighborhoods                 │                    │
│ └─────────────────────┴────────────┴─────────────────────────────────────────────┘                    │
│ 3.3 Confidence Aggregation                                                                            │
│                                                                                                       │
│ function computeEquivalenceConfidence(                                                                │
│   signals: EquivalenceSignal[]                                                                        │
│ ): { confidence: number; source: string } {                                                           │
│   // Weight by source reliability                                                                     │
│   const weights = {                                                                                   │
│     'annotation': 1.0,                                                                                │
│     'manual': 1.0,                                                                                    │
│     'api_contract': 0.9,                                                                              │
│     'canonical': 0.9,                                                                                 │
│     'naming': 0.7,                                                                                    │
│     'semantic': 0.6,                                                                                  │
│     'structural': 0.5                                                                                 │
│   };                                                                                                  │
│                                                                                                       │
│   // Take highest confidence signal, boost if multiple agree                                          │
│   const sorted = signals.sort((a, b) =>                                                               │
│     weights[b.source] * b.confidence - weights[a.source] * a.confidence                               │
│   );                                                                                                  │
│                                                                                                       │
│   const primary = sorted[0];                                                                          │
│   const agreementBoost = signals.length > 1 ? 0.1 : 0;                                                │
│                                                                                                       │
│   return {                                                                                            │
│     confidence: Math.min(1.0, primary.confidence + agreementBoost),                                   │
│     source: primary.source                                                                            │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 4: Documentation Indexing                                                                        │
│                                                                                                       │
│ 4.1 Markdown Parser                                                                                   │
│                                                                                                       │
│ Location: /backend/internal/docindex/                                                                 │
│                                                                                                       │
│ type DocParser struct {                                                                               │
│     mdParser  goldmark.Markdown                                                                       │
│     codeLinker *CodeLinker                                                                            │
│     conceptExtractor *ConceptExtractor                                                                │
│ }                                                                                                     │
│                                                                                                       │
│ type ParsedDocument struct {                                                                          │
│     Path     string                                                                                   │
│     Title    string                                                                                   │
│     Sections []ParsedSection                                                                          │
│     CodeRefs []CodeReference      // Links to code entities                                           │
│     Concepts []ConceptMention     // Business terms mentioned                                         │
│ }                                                                                                     │
│                                                                                                       │
│ type ParsedSection struct {                                                                           │
│     ID           string                                                                               │
│     HeadingLevel int                                                                                  │
│     Title        string                                                                               │
│     Content      string                                                                               │
│     Chunks       []SemanticChunk   // AI-parsed meaningful units                                      │
│     ParentID     string                                                                               │
│     Children     []ParsedSection                                                                      │
│ }                                                                                                     │
│                                                                                                       │
│ type SemanticChunk struct {                                                                           │
│     ID      string                                                                                    │
│     Type    string  // paragraph, code_block, table, definition, example                              │
│     Content string                                                                                    │
│     CodeRefs []string                                                                                 │
│ }                                                                                                     │
│                                                                                                       │
│ 4.2 Document-to-Code Linking                                                                          │
│                                                                                                       │
│ type CodeLinker struct {                                                                              │
│     codeEntities map[string]CodeEntity  // qualified_name → entity                                    │
│ }                                                                                                     │
│                                                                                                       │
│ func (l *CodeLinker) ExtractCodeReferences(content string) []CodeReference {                          │
│     refs := []CodeReference{}                                                                         │
│                                                                                                       │
│     // 1. Inline code: `AuthService.login()`                                                          │
│     inlineCodePattern := regexp.MustCompile("`([^`]+)`")                                              │
│                                                                                                       │
│     // 2. Code blocks with file references                                                            │
│     codeBlockPattern := regexp.MustCompile("```(\\w+)?\\n([\\s\\S]*?)```")                            │
│                                                                                                       │
│     // 3. Explicit links: [AuthService](src/auth/service.ts)                                          │
│     linkPattern := regexp.MustCompile("\\[([^\\]]+)\\]\\(([^)]+)\\)")                                 │
│                                                                                                       │
│     // Match against known code entities                                                              │
│     for _, match := range inlineCodePattern.FindAllString(content, -1) {                              │
│         symbol := strings.Trim(match, "`")                                                            │
│         if entity, ok := l.codeEntities[symbol]; ok {                                                 │
│             refs = append(refs, CodeReference{                                                        │
│                 Symbol: symbol,                                                                       │
│                 EntityID: entity.ID,                                                                  │
│                 Confidence: 0.9,                                                                      │
│             })                                                                                        │
│         }                                                                                             │
│     }                                                                                                 │
│                                                                                                       │
│     return refs                                                                                       │
│ }                                                                                                     │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 5: UI Dimension - Page Decomposition & Component Library                                         │
│                                                                                                       │
│ The UI dimension is a complete perspective representing the application's interface layer, with its   │
│ own hierarchical decomposition and bidirectional traceability to code, requirements, and design.      │
│                                                                                                       │
│ 5.1 UI Hierarchy Model (Page → Element Decomposition)                                                 │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────┐                       │
│ │                         UI DIMENSION HIERARCHY                               │                      │
│ ├─────────────────────────────────────────────────────────────────────────────┤                       │
│ │                                                                             │                       │
│ │  LEVEL 0   ┌─────────────────────────────────────────────────────────────┐  │                       │
│ │  (Site)    │  APPLICATION / SITE                                         │  │                       │
│ │            │  "TracerTM Web App"                                          │  │                      │
│ │            └───────────────────────────┬─────────────────────────────────┘  │                       │
│ │                                        │                                    │                       │
│ │  LEVEL 1   ┌──────────┬───────────┬────┴────┬──────────┬─────────────────┐  │                       │
│ │  (Route)   │ /login   │ /dashboard│ /graph  │ /settings│ /projects/:id   │  │                       │
│ │            │ (page)   │ (page)    │ (page)  │ (page)   │ (page)          │  │                       │
│ │            └────┬─────┴─────┬─────┴────┬────┴────┬─────┴────────┬────────┘  │                       │
│ │                 │           │          │         │              │           │                       │
│ │  LEVEL 2   ┌────┴───┐  ┌────┴───┐  ┌───┴───┐  ┌──┴──┐      ┌───┴────┐     │                         │
│ │  (Layout)  │ Auth   │  │ Main   │  │ Graph │  │ Settings │ │ Detail │     │                         │
│ │            │ Layout │  │ Layout │  │ Layout│  │ Layout   │ │ Layout │     │                         │
│ │            └────┬───┘  └────┬───┘  └───┬───┘  └────┬─────┘ └────┬───┘     │                         │
│ │                 │           │          │           │            │          │                        │
│ │  LEVEL 3   ┌────┴───────────┴────┐  ┌──┴───┐  ┌────┴────┐                  │                        │
│ │  (Section) │ Hero │ Form │ Footer│  │Canvas│  │ Sidebar │                  │                        │
│ │            │      │      │       │  │      │  │ Content │                  │                        │
│ │            └────┬─┴──────┴───────┘  └──┬───┘  └────┬────┘                  │                        │
│ │                 │                      │           │                        │                       │
│ │  LEVEL 4-5 ┌────┴──────┐          ┌────┴─────┐ ┌───┴────┐                  │                        │
│ │ (Component)│ LoginForm │          │ NodePanel│ │ NavMenu│                  │                        │
│ │            │ SocialAuth│          │ Toolbar  │ │ Profile│                  │                        │
│ │            └────┬──────┘          └────┬─────┘ └───┬────┘                  │                        │
│ │                 │                      │           │                        │                       │
│ │  LEVEL 6-7 ┌────┴──────┐          ┌────┴─────┐ ┌───┴────┐                  │                        │
│ │  (Element) │ Input     │          │ Button   │ │ Avatar │                  │                        │
│ │            │ Button    │          │ Icon     │ │ Badge  │                  │                        │
│ │            │ Checkbox  │          │ Tooltip  │ │ Link   │                  │                        │
│ │            └───────────┘          └──────────┘ └────────┘                  │                        │
│ │                                                                             │                       │
│ └─────────────────────────────────────────────────────────────────────────────┘                       │
│                                                                                                       │
│ 5.2 UI Entity Types (Enhanced)                                                                        │
│                                                                                                       │
│ File: /frontend/packages/types/src/ui-entities.ts (new)                                               │
│                                                                                                       │
│ // UI Entity type taxonomy                                                                            │
│ export type UIEntityType =                                                                            │
│   // Application level                                                                                │
│   | 'application' | 'site' | 'app_shell'                                                              │
│                                                                                                       │
│   // Route/Page level                                                                                 │
│   | 'page' | 'screen' | 'view' | 'route'                                                              │
│                                                                                                       │
│   // Layout level                                                                                     │
│   | 'layout' | 'template' | 'frame'                                                                   │
│                                                                                                       │
│   // Section level (semantic page regions)                                                            │
│   | 'section' | 'header' | 'footer' | 'sidebar' | 'main'                                              │
│   | 'hero' | 'nav' | 'content_area' | 'card_grid'                                                     │
│                                                                                                       │
│   // Modal/Overlay level                                                                              │
│   | 'modal' | 'dialog' | 'drawer' | 'popup' | 'toast' | 'tooltip' | 'dropdown'                        │
│                                                                                                       │
│   // Component level (reusable)                                                                       │
│   | 'component' | 'widget' | 'block' | 'pattern'                                                      │
│                                                                                                       │
│   // Subcomponent level                                                                               │
│   | 'subcomponent' | 'compound_part'                                                                  │
│                                                                                                       │
│   // Element level (atomic)                                                                           │
│   | 'element' | 'atom' | 'primitive';                                                                 │
│                                                                                                       │
│ // Page template taxonomy                                                                             │
│ export type PageTemplate =                                                                            │
│   | 'landing' | 'dashboard' | 'form' | 'list' | 'detail'                                              │
│   | 'auth' | 'settings' | 'search' | 'wizard' | 'empty_state';                                        │
│                                                                                                       │
│ // Section taxonomy (common page regions)                                                             │
│ export type SectionType =                                                                             │
│   | 'hero' | 'navigation' | 'breadcrumb' | 'search_bar'                                               │
│   | 'sidebar' | 'content' | 'card_grid' | 'table'                                                     │
│   | 'form' | 'footer' | 'call_to_action' | 'testimonials';                                            │
│                                                                                                       │
│ // UI Item extension                                                                                  │
│ export interface UIItem extends Item {                                                                │
│   uiRef: {                                                                                            │
│     entityType: UIEntityType;                                                                         │
│                                                                                                       │
│     // Hierarchy                                                                                      │
│     depth: number;               // 0-7                                                               │
│     path: string[];              // ["app", "dashboard", "main-layout", "sidebar"]                    │
│                                                                                                       │
│     // Page context                                                                                   │
│     pageTemplate?: PageTemplate;                                                                      │
│     sectionType?: SectionType;                                                                        │
│                                                                                                       │
│     // Route info                                                                                     │
│     routePath?: string;          // "/projects/:id/views/:viewType"                                   │
│     routeParams?: string[];      // ["id", "viewType"]                                                │
│                                                                                                       │
│     // Component library reference                                                                    │
│     libraryRef?: {                                                                                    │
│       libraryId: string;                                                                              │
│       componentName: string;     // "Button", "Modal", "DataTable"                                    │
│       variantName?: string;      // "primary", "destructive"                                          │
│       storyId?: string;          // Storybook story ID                                                │
│     };                                                                                                │
│                                                                                                       │
│     // Design reference                                                                               │
│     designRef?: {                                                                                     │
│       figmaNodeId?: string;                                                                           │
│       figmaFileKey?: string;                                                                          │
│       figmaPageName?: string;                                                                         │
│     };                                                                                                │
│                                                                                                       │
│     // Interaction                                                                                    │
│     interactions?: {                                                                                  │
│       navigatesTo?: string[];    // Page IDs                                                          │
│       opensModal?: string[];     // Modal IDs                                                         │
│       triggersEvent?: string[];  // Event names                                                       │
│     };                                                                                                │
│                                                                                                       │
│     // Responsiveness                                                                                 │
│     deviceVariants?: ('desktop' | 'tablet' | 'mobile')[];                                             │
│     breakpoints?: Record<string, Partial<UIItem>>;                                                    │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ 5.3 Component Library Dimension                                                                       │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────┐                       │
│ │                       COMPONENT LIBRARY STRUCTURE                            │                      │
│ ├─────────────────────────────────────────────────────────────────────────────┤                       │
│ │                                                                             │                       │
│ │  ┌─────────────────────────────────────────────────────────────────────┐   │                        │
│ │  │ DESIGN SYSTEM ROOT                                                   │   │                       │
│ │  │ "@tracertm/ui" or project design system                             │   │                        │
│ │  └───────────────────────────┬─────────────────────────────────────────┘   │                        │
│ │                              │                                              │                       │
│ │  ┌───────────────────────────┼───────────────────────────────────────┐     │                        │
│ │  │                           │                                        │     │                       │
│ │  ▼                           ▼                                        ▼     │                       │
│ │  ┌──────────────┐   ┌──────────────┐                      ┌──────────────┐ │                        │
│ │  │ FOUNDATIONS  │   │ COMPONENTS   │                      │ PATTERNS     │ │                        │
│ │  │ (Tokens)     │   │ (UI Lib)     │                      │ (Templates)  │ │                        │
│ │  └──────┬───────┘   └──────┬───────┘                      └──────┬───────┘ │                        │
│ │         │                  │                                      │         │                       │
│ │  ┌──────┴─────────┐  ┌─────┴────────────────────────┐    ┌───────┴──────┐  │                        │
│ │  │ Colors        │  │ Primitives    │ Compounds     │    │ Page         │  │                        │
│ │  │ Typography    │  │ ───────────   │ ─────────     │    │ Templates    │  │                        │
│ │  │ Spacing       │  │ Button        │ Card          │    │              │  │                        │
│ │  │ Shadows       │  │ Input         │ Modal         │    │ Dashboard    │  │                        │
│ │  │ Borders       │  │ Badge         │ DataTable     │    │ Form         │  │                        │
│ │  │ Icons         │  │ Avatar        │ Sidebar       │    │ List         │  │                        │
│ │  │ Motion        │  │ Icon          │ Header        │    │ Detail       │  │                        │
│ │  └───────────────┘  │ Link          │ CommandPalette│    └──────────────┘  │                        │
│ │                     └───────────────┴───────────────┘                      │                        │
│ │                                                                             │                       │
│ │  COMPONENT METADATA:                                                        │                       │
│ │  ─────────────────                                                          │                       │
│ │  • Storybook: storybook.tracertm.dev/docs/components-button--docs          │                        │
│ │  • Figma: figma.com/file/xxx/Design-System?node-id=123:456                 │                        │
│ │  • Source: /frontend/packages/ui/src/components/button.tsx                 │                        │
│ │  • Props: variant, size, disabled, loading, leftIcon, rightIcon            │                        │
│ │  • Variants: default, primary, secondary, destructive, ghost, link         │                        │
│ │  • Usage Count: 847 instances across 23 pages                              │                        │
│ │                                                                             │                       │
│ └─────────────────────────────────────────────────────────────────────────────┘                       │
│                                                                                                       │
│ 5.4 Component Library Entity                                                                          │
│                                                                                                       │
│ // File: /frontend/packages/types/src/component-library.ts (new)                                      │
│                                                                                                       │
│ export interface ComponentLibrary {                                                                   │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   name: string;                     // "@tracertm/ui"                                                 │
│   description?: string;                                                                               │
│                                                                                                       │
│   // Source references                                                                                │
│   packagePath?: string;             // "frontend/packages/ui"                                         │
│   storybookUrl?: string;            // "https://storybook.tracertm.dev"                               │
│   figmaFileKey?: string;            // Figma file containing the design system                        │
│                                                                                                       │
│   // Version tracking                                                                                 │
│   version: string;                                                                                    │
│   publishedAt?: string;                                                                               │
│                                                                                                       │
│   metadata?: Record<string, unknown>;                                                                 │
│ }                                                                                                     │
│                                                                                                       │
│ export interface LibraryComponent {                                                                   │
│   id: string;                                                                                         │
│   libraryId: string;                                                                                  │
│                                                                                                       │
│   // Identity                                                                                         │
│   name: string;                     // "Button"                                                       │
│   displayName: string;              // "Button"                                                       │
│   category: ComponentCategory;                                                                        │
│                                                                                                       │
│   // Location                                                                                         │
│   sourcePath: string;               // "src/components/button.tsx"                                    │
│   exportName: string;               // "Button" or "default"                                          │
│                                                                                                       │
│   // Documentation                                                                                    │
│   description?: string;                                                                               │
│   storyId?: string;                 // "components-button--docs"                                      │
│   figmaNodeId?: string;                                                                               │
│   docUrl?: string;                                                                                    │
│                                                                                                       │
│   // Schema                                                                                           │
│   propsSchema?: PropSchema[];                                                                         │
│   variants?: ComponentVariant[];                                                                      │
│   slots?: ComponentSlot[];                                                                            │
│                                                                                                       │
│   // Usage metrics                                                                                    │
│   usageCount: number;                                                                                 │
│   usedInPages: string[];            // Page IDs using this component                                  │
│   dependsOn: string[];              // Other component IDs                                            │
│   dependedOnBy: string[];                                                                             │
│                                                                                                       │
│   // Status                                                                                           │
│   status: 'stable' | 'beta' | 'deprecated' | 'experimental';                                          │
│   deprecationMessage?: string;                                                                        │
│   replacedBy?: string;              // Component ID of replacement                                    │
│                                                                                                       │
│   createdAt: string;                                                                                  │
│   updatedAt: string;                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ export type ComponentCategory =                                                                       │
│   | 'primitives'      // Button, Input, Badge                                                         │
│   | 'forms'           // Form, Field, Select                                                          │
│   | 'layout'          // Container, Grid, Stack                                                       │
│   | 'navigation'      // Nav, Breadcrumb, Tabs                                                        │
│   | 'feedback'        // Alert, Toast, Progress                                                       │
│   | 'overlays'        // Modal, Drawer, Popover                                                       │
│   | 'data-display'    // Table, List, Card                                                            │
│   | 'utilities';      // Portal, VisuallyHidden                                                       │
│                                                                                                       │
│ export interface ComponentVariant {                                                                   │
│   name: string;                     // "primary", "destructive"                                       │
│   propsOverride: Record<string, unknown>;                                                             │
│   preview?: {                                                                                         │
│     screenshotUrl?: string;                                                                           │
│     storyId?: string;                                                                                 │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ export interface PropSchema {                                                                         │
│   name: string;                                                                                       │
│   type: string;                     // "string", "boolean", "ReactNode"                               │
│   required: boolean;                                                                                  │
│   defaultValue?: unknown;                                                                             │
│   description?: string;                                                                               │
│   enumValues?: string[];            // For union types                                                │
│ }                                                                                                     │
│                                                                                                       │
│ 5.5 UI-to-Code Traceability Links                                                                     │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────┐                       │
│ │                     UI-TO-CODE TRACEABILITY                                  │                      │
│ ├─────────────────────────────────────────────────────────────────────────────┤                       │
│ │                                                                             │                       │
│ │  UI DIMENSION                         CODE DIMENSION                        │                       │
│ │  ────────────                         ──────────────                        │                       │
│ │                                                                             │                       │
│ │  ┌───────────────┐                    ┌───────────────────────────────────┐│                        │
│ │  │ LoginPage     │───implements───────▶│ src/pages/auth/login.tsx         ││                        │
│ │  │ (page)        │                    │ LoginPage component               ││                        │
│ │  └───────┬───────┘                    └───────────────────────────────────┘│                        │
│ │          │                                                                  │                       │
│ │          │ contains                                                         │                       │
│ │          ▼                                                                  │                       │
│ │  ┌───────────────┐                    ┌───────────────────────────────────┐│                        │
│ │  │ LoginForm     │───implements───────▶│ src/components/auth/LoginForm.tsx││                        │
│ │  │ (component)   │                    │ LoginForm component               ││                        │
│ │  └───────┬───────┘                    └───────────────────────────────────┘│                        │
│ │          │                                       │                          │                       │
│ │          │ uses                                  │ imports                  │                       │
│ │          ▼                                       ▼                          │                       │
│ │  ┌───────────────┐                    ┌───────────────────────────────────┐│                        │
│ │  │ Button        │◀───implements──────│ @tracertm/ui/button.tsx           ││                        │
│ │  │ (lib component)                    │ Button component                  ││                        │
│ │  └───────────────┘                    └───────────────────────────────────┘│                        │
│ │          │                                       │                          │                       │
│ │          │                                       │ calls                    │                       │
│ │          │                                       ▼                          │                       │
│ │          │                            ┌───────────────────────────────────┐│                        │
│ │          │                            │ src/api/auth.ts                   ││                        │
│ │          └────────────uses_api────────▶│ login() function                 ││                        │
│ │                                       └───────────────────────────────────┘│                        │
│ │                                                  │                          │                       │
│ │                                                  │ calls                    │                       │
│ │                                                  ▼                          │                       │
│ │  ┌───────────────┐                    ┌───────────────────────────────────┐│                        │
│ │  │ User Story    │◀───implements──────│ POST /api/v1/auth/login           ││                        │
│ │  │ "Login Flow"  │                    │ Backend handler                   ││                        │
│ │  │ (product view)│                    └───────────────────────────────────┘│                        │
│ │  └───────────────┘                                                          │                       │
│ │                                                                             │                       │
│ └─────────────────────────────────────────────────────────────────────────────┘                       │
│                                                                                                       │
│ 5.6 UI Link Types                                                                                     │
│                                                                                                       │
│ // Additional link types for UI dimension                                                             │
│ export type UILinkType =                                                                              │
│   | 'renders'           // Component A renders Component B                                            │
│   | 'uses_component'    // Page uses a library component                                              │
│   | 'layout_contains'   // Layout contains section/component                                          │
│   | 'navigates_to'      // UI element navigates to page                                               │
│   | 'opens_modal'       // UI element opens modal                                                     │
│   | 'triggers_event'    // UI interaction triggers event                                              │
│   | 'styled_by'         // Component uses design token                                                │
│   | 'variant_of'        // Component variant of base                                                  │
│   | 'deprecated_by'     // Old component deprecated by new                                            │
│   | 'designed_in'       // UI references Figma design                                                 │
│   | 'documented_in';    // UI documented in Storybook story                                           │
│                                                                                                       │
│ 5.7 Design System Integration                                                                         │
│                                                                                                       │
│ // Design token reference                                                                             │
│ export interface DesignTokenRef {                                                                     │
│   tokenType: 'color' | 'typography' | 'spacing' | 'shadow' | 'border' | 'motion';                     │
│   tokenPath: string;              // "colors.primary.500"                                             │
│   resolvedValue?: string;         // "#3b82f6"                                                        │
│   figmaStyleId?: string;                                                                              │
│ }                                                                                                     │
│                                                                                                       │
│ // Figma integration                                                                                  │
│ export interface FigmaIntegration {                                                                   │
│   fileKey: string;                                                                                    │
│   pageName?: string;                                                                                  │
│   nodeId?: string;                                                                                    │
│   lastSyncedAt?: string;                                                                              │
│   syncStatus: 'synced' | 'outdated' | 'unlinked';                                                     │
│ }                                                                                                     │
│                                                                                                       │
│ // Storybook integration                                                                              │
│ export interface StorybookIntegration {                                                               │
│   storyId: string;                // "components-button--primary"                                     │
│   storyUrl?: string;                                                                                  │
│   lastBuildAt?: string;                                                                               │
│   hasVisualTests: boolean;                                                                            │
│   visualTestStatus?: 'passed' | 'failed' | 'pending';                                                 │
│ }                                                                                                     │
│                                                                                                       │
│ 5.8 UI Dimension Database Schema                                                                      │
│                                                                                                       │
│ -- Component libraries                                                                                │
│ CREATE TABLE component_libraries (                                                                    │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│                                                                                                       │
│   name VARCHAR(255) NOT NULL,                                                                         │
│   description TEXT,                                                                                   │
│   package_path VARCHAR(500),                                                                          │
│   storybook_url VARCHAR(500),                                                                         │
│   figma_file_key VARCHAR(100),                                                                        │
│                                                                                                       │
│   version VARCHAR(50),                                                                                │
│   published_at TIMESTAMPTZ,                                                                           │
│                                                                                                       │
│   metadata JSONB DEFAULT '{}',                                                                        │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Library components                                                                                 │
│ CREATE TABLE library_components (                                                                     │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   library_id UUID NOT NULL REFERENCES component_libraries(id) ON DELETE CASCADE,                      │
│   item_id UUID REFERENCES items(id),          -- Links to UI dimension item                           │
│                                                                                                       │
│   name VARCHAR(255) NOT NULL,                                                                         │
│   display_name VARCHAR(255),                                                                          │
│   category VARCHAR(50) NOT NULL,                                                                      │
│                                                                                                       │
│   source_path VARCHAR(500),                                                                           │
│   export_name VARCHAR(255),                                                                           │
│                                                                                                       │
│   description TEXT,                                                                                   │
│   story_id VARCHAR(255),                                                                              │
│   figma_node_id VARCHAR(100),                                                                         │
│   doc_url VARCHAR(500),                                                                               │
│                                                                                                       │
│   props_schema JSONB,                                                                                 │
│   variants JSONB,                                                                                     │
│   slots JSONB,                                                                                        │
│                                                                                                       │
│   usage_count INTEGER DEFAULT 0,                                                                      │
│   status VARCHAR(20) DEFAULT 'stable',                                                                │
│   deprecation_message TEXT,                                                                           │
│   replaced_by UUID REFERENCES library_components(id),                                                 │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Component usage tracking                                                                           │
│ CREATE TABLE component_usage (                                                                        │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   component_id UUID NOT NULL REFERENCES library_components(id) ON DELETE CASCADE,                     │
│                                                                                                       │
│   page_item_id UUID REFERENCES items(id),     -- Which page uses it                                   │
│   file_path VARCHAR(500),                      -- Source file using it                                │
│   line_number INTEGER,                                                                                │
│   usage_context VARCHAR(100),                  -- e.g., "form-field", "navigation"                    │
│                                                                                                       │
│   props_used JSONB,                            -- Which props are passed                              │
│   variant_used VARCHAR(100),                                                                          │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Design token references                                                                            │
│ CREATE TABLE design_token_refs (                                                                      │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   component_id UUID REFERENCES library_components(id) ON DELETE CASCADE,                              │
│   item_id UUID REFERENCES items(id),                                                                  │
│                                                                                                       │
│   token_type VARCHAR(50) NOT NULL,                                                                    │
│   token_path VARCHAR(255) NOT NULL,                                                                   │
│   resolved_value VARCHAR(255),                                                                        │
│   figma_style_id VARCHAR(100),                                                                        │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Figma sync state                                                                                   │
│ CREATE TABLE figma_sync_state (                                                                       │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   item_id UUID REFERENCES items(id),                                                                  │
│   component_id UUID REFERENCES library_components(id),                                                │
│                                                                                                       │
│   file_key VARCHAR(100) NOT NULL,                                                                     │
│   page_name VARCHAR(255),                                                                             │
│   node_id VARCHAR(100),                                                                               │
│                                                                                                       │
│   last_synced_at TIMESTAMPTZ,                                                                         │
│   sync_status VARCHAR(20) DEFAULT 'unlinked',                                                         │
│   figma_modified_at TIMESTAMPTZ,                                                                      │
│                                                                                                       │
│   UNIQUE(item_id, file_key, node_id)                                                                  │
│ );                                                                                                    │
│                                                                                                       │
│ 5.9 UI Dimension Views                                                                                │
│                                                                                                       │
│ Existing Components to Enhance:                                                                       │
│ - UIComponentTree.tsx → Becomes the primary UI dimension navigator                                    │
│ - PageInteractionFlow.tsx → User journey visualization within UI                                      │
│ - ThumbnailPreview.tsx → Screenshot previews with version tracking                                    │
│                                                                                                       │
│ New Components:                                                                                       │
│ ┌──────────────────────────┬───────────────────────────────────────┐                                  │
│ │        Component         │                Purpose                │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ ComponentLibraryExplorer │ Browse and search component library   │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ PageDecompositionView    │ Hierarchical page → element breakdown │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ DesignTokenBrowser       │ View and link design tokens           │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ FigmaSyncPanel           │ Manage Figma integration status       │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ ComponentUsageMatrix     │ Where is each component used          │                                  │
│ ├──────────────────────────┼───────────────────────────────────────┤                                  │
│ │ UICodeTracePanel         │ Show UI → code → requirement chain    │                                  │
│ └──────────────────────────┴───────────────────────────────────────┘                                  │
│ ---                                                                                                   │
│ Part 6: Unified Graph Architecture                                                                    │
│                                                                                                       │
│ 6.1 Unified Graph View                                                                                │
│                                                                                                       │
│ File: /frontend/apps/web/src/components/graph/UnifiedGraphView.tsx                                    │
│                                                                                                       │
│ interface UnifiedGraphViewProps {                                                                     │
│   projectId: string;                                                                                  │
│                                                                                                       │
│   // View controls                                                                                    │
│   activePerspectives: string[];      // Multiple perspectives visible                                 │
│   activeDimensions: DimensionFilter[];                                                                │
│                                                                                                       │
│   // Equivalence display                                                                              │
│   showEquivalences: boolean;                                                                          │
│   equivalenceMode: 'hide' | 'highlight' | 'merge';                                                    │
│                                                                                                       │
│   // Canonical concepts                                                                               │
│   showCanonicalLayer: boolean;                                                                        │
│                                                                                                       │
│   // Journey overlay                                                                                  │
│   activeJourney?: DerivedJourney;                                                                     │
│ }                                                                                                     │
│                                                                                                       │
│ 5.2 Multi-Perspective Display Modes                                                                   │
│ ┌─────────┬─────────────────────────────────────────────────────────────┐                             │
│ │  Mode   │                         Description                         │                             │
│ ├─────────┼─────────────────────────────────────────────────────────────┤                             │
│ │ Single  │ One perspective, cross-links hidden                         │                             │
│ ├─────────┼─────────────────────────────────────────────────────────────┤                             │
│ │ Split   │ Side-by-side perspectives, equivalences as bridges          │                             │
│ ├─────────┼─────────────────────────────────────────────────────────────┤                             │
│ │ Layered │ Perspectives as semi-transparent layers                     │                             │
│ ├─────────┼─────────────────────────────────────────────────────────────┤                             │
│ │ Unified │ All perspectives merged, dimension-colored                  │                             │
│ ├─────────┼─────────────────────────────────────────────────────────────┤                             │
│ │ Pivot   │ Focus on one node, show its projections in all perspectives │                             │
│ └─────────┴─────────────────────────────────────────────────────────────┘                             │
│ 5.3 Dimension Filters                                                                                 │
│                                                                                                       │
│ File: /frontend/apps/web/src/components/graph/DimensionFilters.tsx                                    │
│                                                                                                       │
│ interface DimensionFilter {                                                                           │
│   dimension: string;           // 'maturity', 'complexity', 'coverage'                                │
│   operator: 'eq' | 'neq' | 'gt' | 'lt' | 'in';                                                        │
│   value: string | number | string[];                                                                  │
│   displayMode: 'filter' | 'highlight' | 'color';                                                      │
│ }                                                                                                     │
│                                                                                                       │
│ // Example usage:                                                                                     │
│ const filters: DimensionFilter[] = [                                                                  │
│   { dimension: 'maturity', operator: 'eq', value: 'approved', displayMode: 'filter' },                │
│   { dimension: 'coverage', operator: 'lt', value: 50, displayMode: 'highlight' },                     │
│   { dimension: 'complexity', operator: 'in', value: ['high', 'critical'], displayMode: 'color' }      │
│ ];                                                                                                    │
│                                                                                                       │
│ 5.4 Pivot Navigation                                                                                  │
│                                                                                                       │
│ interface PivotNavigationProps {                                                                      │
│   currentNode: Item;                                                                                  │
│   equivalentNodes: {                                                                                  │
│     perspectiveId: string;                                                                            │
│     item: Item;                                                                                       │
│     confidence: number;                                                                               │
│     source: string;                                                                                   │
│   }[];                                                                                                │
│   onPivot: (perspectiveId: string, itemId: string) => void;                                           │
│ }                                                                                                     │
│                                                                                                       │
│ // UI: When viewing "Login Feature" in Product perspective,                                           │
│ // show sidebar with:                                                                                 │
│ // - Technical: "AuthService.login()" [0.95 confidence]                                               │
│ // - Security: "SEC-AUTH-001" [0.90 confidence]                                                       │
│ // - Code: "src/auth/login.ts:42" [1.0 confidence]                                                    │
│ // Click to pivot to that perspective focused on that node                                            │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 7: Temporal Navigation Dimension - Versioning, Branching & Futures                               │
│                                                                                                       │
│ The temporal dimension enables navigation across time (past/present/future) and variation             │
│ (alternative approaches, forks, experiments). This is not just audit history - it's a first-class     │
│ navigable dimension supporting complex branching like git.                                            │
│                                                                                                       │
│ 7.1 Temporal Model: Four Temporal States                                                              │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────┐                       │
│ │                         TEMPORAL STATE MODEL                                 │                      │
│ ├─────────────────────────────────────────────────────────────────────────────┤                       │
│ │                                                                             │                       │
│ │    PAST (History)          PRESENT (Active)         FUTURE (Planned)        │                       │
│ │    ──────────────          ────────────────         ────────────────        │                       │
│ │                                                                             │                       │
│ │    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐         │                        │
│ │    │ Snapshots   │ ──────▶ │ HEAD        │ ──────▶ │ Branches    │         │                        │
│ │    │ v1, v2, v3  │         │ (current)   │         │ Proposals   │         │                        │
│ │    └─────────────┘         └─────────────┘         │ Experiments │         │                        │
│ │                                                    └─────────────┘         │                        │
│ │    Archive/Retired          Active/Live            Draft/Planned           │                        │
│ │    Superseded               Master                 Feature branches        │                        │
│ │    Historical               Production             RFC/ADR proposals       │                        │
│ │                                                                             │                       │
│ │ ════════════════════════════════════════════════════════════════════════   │                        │
│ │                                                                             │                       │
│ │    VARIATIONS (Orthogonal to Time)                                         │                        │
│ │    ───────────────────────────────                                         │                        │
│ │                                                                             │                       │
│ │    ┌─────────────────────────────────────────────────────────────────┐     │                        │
│ │    │                         Option A                                │     │                        │
│ │    │                         (Stripe payment)                        │     │                        │
│ │    │                              │                                  │     │                        │
│ │    │      BASE ──────────────────┼──────────────────▶ CHOSEN        │     │                         │
│ │    │   (payment needed)          │                    (Stripe)       │     │                        │
│ │    │                              │                                  │     │                        │
│ │    │                         Option B                                │     │                        │
│ │    │                         (PayPal payment)                        │     │                        │
│ │    └─────────────────────────────────────────────────────────────────┘     │                        │
│ │                                                                             │                       │
│ │    Use Cases:                                                               │                       │
│ │    • "What if" exploration (2 UI designs)                                  │                        │
│ │    • A/B testing variations                                                 │                       │
│ │    • Competing architectural approaches                                     │                       │
│ │    • Migration paths (gradual vs big-bang)                                 │                        │
│ │                                                                             │                       │
│ └─────────────────────────────────────────────────────────────────────────────┘                       │
│                                                                                                       │
│ 7.2 Version Branch Tree (Git-like Model)                                                              │
│                                                                                                       │
│ // File: /frontend/packages/types/src/temporal.ts (new)                                               │
│                                                                                                       │
│ export interface VersionBranch {                                                                      │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   name: string;                      // "main", "feature/new-payment", "experiment/ai-routing"        │
│                                                                                                       │
│   // Branch type                                                                                      │
│   branchType: BranchType;                                                                             │
│                                                                                                       │
│   // Tree structure                                                                                   │
│   parentBranchId?: string;           // What branch this was created from                             │
│   baseVersionId?: string;            // Which version it forked from                                  │
│                                                                                                       │
│   // State                                                                                            │
│   status: BranchStatus;                                                                               │
│   isDefault: boolean;                // Is this the "main" branch                                     │
│   isProtected: boolean;              // Prevent direct edits                                          │
│                                                                                                       │
│   // Metadata                                                                                         │
│   description?: string;                                                                               │
│   createdBy: string;                                                                                  │
│   createdAt: string;                                                                                  │
│   updatedAt: string;                                                                                  │
│   mergedAt?: string;                 // If merged back                                                │
│   mergedInto?: string;               // Which branch it merged into                                   │
│ }                                                                                                     │
│                                                                                                       │
│ export type BranchType =                                                                              │
│   | 'main'           // Primary production branch                                                     │
│   | 'release'        // Release candidate                                                             │
│   | 'feature'        // Feature development                                                           │
│   | 'experiment'     // A/B testing, "what if"                                                        │
│   | 'hotfix'         // Emergency fixes                                                               │
│   | 'archive';       // Historical reference                                                          │
│                                                                                                       │
│ export type BranchStatus =                                                                            │
│   | 'active'         // Being worked on                                                               │
│   | 'review'         // Under review for merge                                                        │
│   | 'merged'         // Successfully merged                                                           │
│   | 'abandoned'      // Discarded                                                                     │
│   | 'archived';      // Kept for reference                                                            │
│                                                                                                       │
│ export interface Version {                                                                            │
│   id: string;                                                                                         │
│   branchId: string;                                                                                   │
│   versionNumber: number;             // Sequential within branch                                      │
│                                                                                                       │
│   // Tree                                                                                             │
│   parentVersionId?: string;          // Previous version (linear history)                             │
│   childVersionIds: string[];         // Branches from this point                                      │
│                                                                                                       │
│   // Snapshot                                                                                         │
│   snapshotId: string;                // Reference to full state snapshot                              │
│   changesetId?: string;              // Delta from parent                                             │
│                                                                                                       │
│   // Metadata                                                                                         │
│   tag?: string;                      // "v1.0.0", "MVP", "Q1-Release"                                 │
│   message: string;                   // Commit-style message                                          │
│   createdBy: string;                                                                                  │
│   createdAt: string;                                                                                  │
│                                                                                                       │
│   // Quality gates                                                                                    │
│   status: VersionStatus;                                                                              │
│   approvedBy?: string;                                                                                │
│   approvedAt?: string;                                                                                │
│ }                                                                                                     │
│                                                                                                       │
│ export type VersionStatus =                                                                           │
│   | 'draft'          // Work in progress                                                              │
│   | 'pending_review' // Awaiting approval                                                             │
│   | 'approved'       // Ready for use                                                                 │
│   | 'rejected'       // Failed review                                                                 │
│   | 'superseded';    // Replaced by newer version                                                     │
│                                                                                                       │
│ 7.3 Temporal Item State                                                                               │
│                                                                                                       │
│ // Enhanced Item with temporal awareness                                                              │
│ export interface TemporalItem extends Item {                                                          │
│   temporal: {                                                                                         │
│     // Version tracking                                                                               │
│     versionId: string;               // Which version this item exists in                             │
│     branchId: string;                // Which branch                                                  │
│     introducedInVersion: string;     // First appeared                                                │
│     lastModifiedVersion: string;     // Last change                                                   │
│                                                                                                       │
│     // Lifecycle                                                                                      │
│     lifecycle: ItemLifecycle;                                                                         │
│                                                                                                       │
│     // Variations                                                                                     │
│     alternatives?: {                                                                                  │
│       itemId: string;                // Alternative item ID                                           │
│       relationship: 'alternative_to' | 'supersedes' | 'experiment_of';                                │
│       chosenAt?: string;             // When this was selected as the winner                          │
│       chosenBy?: string;                                                                              │
│     }[];                                                                                              │
│                                                                                                       │
│     // Future planning                                                                                │
│     plannedFor?: {                                                                                    │
│       targetVersion?: string;        // Which version it's planned for                                │
│       targetDate?: string;                                                                            │
│       probability?: number;          // 0-1 likelihood                                                │
│       dependencies?: string[];       // Must complete first                                           │
│     };                                                                                                │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ export type ItemLifecycle =                                                                           │
│   | 'idea'           // Just an idea, no commitment                                                   │
│   | 'proposed'       // Formally proposed                                                             │
│   | 'planned'        // Scheduled for implementation                                                  │
│   | 'in_progress'    // Being worked on                                                               │
│   | 'implemented'    // Code complete                                                                 │
│   | 'verified'       // Tested/validated                                                              │
│   | 'released'       // In production                                                                 │
│   | 'deprecated'     // Being phased out                                                              │
│   | 'retired';       // No longer active                                                              │
│                                                                                                       │
│ 7.4 Project Progress Dimension                                                                        │
│                                                                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────────┐                       │
│ │                    PROJECT PROGRESS DIMENSION                                │                      │
│ ├─────────────────────────────────────────────────────────────────────────────┤                       │
│ │                                                                             │                       │
│ │  This dimension focuses on EXECUTION STATE rather than product DEFINITION   │                       │
│ │  (closer to Jira/Linear experience vs the traceability model)               │                       │
│ │                                                                             │                       │
│ │  ┌───────────────────────────────────────────────────────────────────────┐ │                        │
│ │  │ INITIATIVE / EPIC                                                      │ │                       │
│ │  │ "Payment System Overhaul"                                              │ │                       │
│ │  │ Progress: ████████░░ 80%                                               │ │                       │
│ │  └─────────────────────────────────────────────────────────────────┬─────┘ │                        │
│ │                                                                    │       │                        │
│ │    ┌───────────────────────┬───────────────────────┬──────────────┘       │                         │
│ │    ▼                       ▼                       ▼                       │                        │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │                          │
│ │  │ MILESTONE       │  │ MILESTONE       │  │ MILESTONE       │           │                          │
│ │  │ "API Complete"  │  │ "UI Complete"   │  │ "Launch"        │           │                          │
│ │  │ ██████████ 100% │  │ ████████░░ 75%  │  │ ░░░░░░░░░░ 0%   │           │                          │
│ │  │ Due: Jan 15     │  │ Due: Feb 1      │  │ Due: Feb 15     │           │                          │
│ │  │ Status: DONE    │  │ Status: AT_RISK │  │ Status: BLOCKED │           │                          │
│ │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘           │                          │
│ │           │                    │                    │                     │                         │
│ │    ┌──────┴──────┐      ┌──────┴──────┐      ┌──────┴──────┐             │                          │
│ │    │ TASKS       │      │ TASKS       │      │ TASKS       │             │                          │
│ │    │ 12/12 done  │      │ 8/15 done   │      │ 0/10 done   │             │                          │
│ │    │ 0 blocked   │      │ 2 blocked   │      │ 3 blocked   │             │                          │
│ │    └─────────────┘      └─────────────┘      └─────────────┘             │                          │
│ │                                                                           │                         │
│ │  PROGRESS METRICS:                                                        │                         │
│ │  ─────────────────                                                        │                         │
│ │  • Velocity: 8 items/week                                                 │                         │
│ │  • Burndown: On track / Behind / Ahead                                    │                         │
│ │  • Risk Score: Based on blocked items + dependencies                      │                         │
│ │  • Health: Green/Yellow/Red based on progress vs plan                     │                         │
│ │                                                                           │                         │
│ └─────────────────────────────────────────────────────────────────────────────┘                       │
│                                                                                                       │
│ 7.5 Progress Tracking Types                                                                           │
│                                                                                                       │
│ // File: /frontend/packages/types/src/progress.ts (new)                                               │
│                                                                                                       │
│ export interface Milestone {                                                                          │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   parentId?: string;                 // Parent milestone/initiative                                   │
│                                                                                                       │
│   name: string;                                                                                       │
│   description?: string;                                                                               │
│                                                                                                       │
│   // Timing                                                                                           │
│   startDate?: string;                                                                                 │
│   targetDate: string;                                                                                 │
│   actualDate?: string;               // When actually completed                                       │
│                                                                                                       │
│   // Status                                                                                           │
│   status: MilestoneStatus;                                                                            │
│   health: HealthStatus;                                                                               │
│                                                                                                       │
│   // Progress                                                                                         │
│   progress: {                                                                                         │
│     totalItems: number;                                                                               │
│     completedItems: number;                                                                           │
│     blockedItems: number;                                                                             │
│     percentage: number;                                                                               │
│   };                                                                                                  │
│                                                                                                       │
│   // Risk                                                                                             │
│   riskScore: number;                 // Computed from dependencies, blocks, timeline                  │
│   riskFactors?: string[];                                                                             │
│                                                                                                       │
│   // Items                                                                                            │
│   itemIds: string[];                 // Items in this milestone                                       │
│   dependsOnMilestones?: string[];    // Must complete first                                           │
│ }                                                                                                     │
│                                                                                                       │
│ export type MilestoneStatus =                                                                         │
│   | 'not_started'                                                                                     │
│   | 'in_progress'                                                                                     │
│   | 'at_risk'                                                                                         │
│   | 'blocked'                                                                                         │
│   | 'completed'                                                                                       │
│   | 'cancelled';                                                                                      │
│                                                                                                       │
│ export type HealthStatus = 'green' | 'yellow' | 'red' | 'unknown';                                    │
│                                                                                                       │
│ export interface Sprint {                                                                             │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   name: string;                      // "Sprint 23" or "Q1 Week 3"                                    │
│                                                                                                       │
│   startDate: string;                                                                                  │
│   endDate: string;                                                                                    │
│                                                                                                       │
│   goal?: string;                                                                                      │
│   status: SprintStatus;                                                                               │
│                                                                                                       │
│   // Capacity                                                                                         │
│   plannedPoints?: number;                                                                             │
│   completedPoints?: number;                                                                           │
│   velocity?: number;                                                                                  │
│                                                                                                       │
│   // Items                                                                                            │
│   itemIds: string[];                                                                                  │
│   carryoverItemIds?: string[];       // Not completed, carried forward                                │
│ }                                                                                                     │
│                                                                                                       │
│ export type SprintStatus =                                                                            │
│   | 'planning'                                                                                        │
│   | 'active'                                                                                          │
│   | 'completed'                                                                                       │
│   | 'cancelled';                                                                                      │
│                                                                                                       │
│ export interface ProgressSnapshot {                                                                   │
│   id: string;                                                                                         │
│   projectId: string;                                                                                  │
│   timestamp: string;                                                                                  │
│                                                                                                       │
│   // Aggregate metrics                                                                                │
│   metrics: {                                                                                          │
│     totalItems: number;                                                                               │
│     byStatus: Record<ItemStatus, number>;                                                             │
│     byLifecycle: Record<ItemLifecycle, number>;                                                       │
│     byPriority: Record<string, number>;                                                               │
│                                                                                                       │
│     // Velocity                                                                                       │
│     completedThisWeek: number;                                                                        │
│     completedLastWeek: number;                                                                        │
│     velocity: number;                // Average over N weeks                                          │
│                                                                                                       │
│     // Health                                                                                         │
│     blockedCount: number;                                                                             │
│     atRiskCount: number;                                                                              │
│     overdueCount: number;                                                                             │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ 7.6 Temporal Navigation UI                                                                            │
│                                                                                                       │
│ // File: /frontend/apps/web/src/components/temporal/TemporalNavigator.tsx (new)                       │
│                                                                                                       │
│ interface TemporalNavigatorProps {                                                                    │
│   projectId: string;                                                                                  │
│                                                                                                       │
│   // View mode                                                                                        │
│   mode: 'timeline' | 'branches' | 'comparison' | 'progress';                                          │
│                                                                                                       │
│   // Current position                                                                                 │
│   currentBranchId: string;                                                                            │
│   currentVersionId: string;                                                                           │
│                                                                                                       │
│   // Navigation                                                                                       │
│   onBranchChange: (branchId: string) => void;                                                         │
│   onVersionChange: (versionId: string) => void;                                                       │
│   onCompare: (versionA: string, versionB: string) => void;                                            │
│ }                                                                                                     │
│                                                                                                       │
│ // Timeline view: Horizontal timeline with version markers                                            │
│ // Branches view: Tree visualization of branches                                                      │
│ // Comparison view: Side-by-side diff of two versions                                                 │
│ // Progress view: Milestone/sprint tracking dashboard                                                 │
│                                                                                                       │
│ 7.7 Version Comparison & Diff                                                                         │
│                                                                                                       │
│ export interface VersionDiff {                                                                        │
│   versionA: string;                                                                                   │
│   versionB: string;                                                                                   │
│                                                                                                       │
│   // Changes                                                                                          │
│   added: DiffItem[];                 // New in B                                                      │
│   removed: DiffItem[];               // Gone in B                                                     │
│   modified: DiffItem[];              // Changed between A and B                                       │
│   unchanged: number;                 // Count of unchanged                                            │
│                                                                                                       │
│   // Statistics                                                                                       │
│   stats: {                                                                                            │
│     totalChanges: number;                                                                             │
│     addedCount: number;                                                                               │
│     removedCount: number;                                                                             │
│     modifiedCount: number;                                                                            │
│   };                                                                                                  │
│ }                                                                                                     │
│                                                                                                       │
│ export interface DiffItem {                                                                           │
│   itemId: string;                                                                                     │
│   type: string;                                                                                       │
│   title: string;                                                                                      │
│                                                                                                       │
│   changeType: 'added' | 'removed' | 'modified';                                                       │
│                                                                                                       │
│   // For modified items                                                                               │
│   fieldChanges?: {                                                                                    │
│     field: string;                                                                                    │
│     oldValue: unknown;                                                                                │
│     newValue: unknown;                                                                                │
│   }[];                                                                                                │
│ }                                                                                                     │
│                                                                                                       │
│ 7.8 Temporal Database Schema                                                                          │
│                                                                                                       │
│ -- Version branches (like git branches)                                                               │
│ CREATE TABLE version_branches (                                                                       │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│                                                                                                       │
│   name VARCHAR(255) NOT NULL,                                                                         │
│   branch_type VARCHAR(50) NOT NULL,                                                                   │
│                                                                                                       │
│   parent_branch_id UUID REFERENCES version_branches(id),                                              │
│   base_version_id UUID,                                                                               │
│                                                                                                       │
│   status VARCHAR(50) DEFAULT 'active',                                                                │
│   is_default BOOLEAN DEFAULT FALSE,                                                                   │
│   is_protected BOOLEAN DEFAULT FALSE,                                                                 │
│                                                                                                       │
│   description TEXT,                                                                                   │
│   created_by VARCHAR(255),                                                                            │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   merged_at TIMESTAMPTZ,                                                                              │
│   merged_into UUID REFERENCES version_branches(id),                                                   │
│                                                                                                       │
│   UNIQUE(project_id, name)                                                                            │
│ );                                                                                                    │
│                                                                                                       │
│ -- Versions (like git commits)                                                                        │
│ CREATE TABLE versions (                                                                               │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   branch_id UUID NOT NULL REFERENCES version_branches(id) ON DELETE CASCADE,                          │
│                                                                                                       │
│   version_number INTEGER NOT NULL,                                                                    │
│   parent_version_id UUID REFERENCES versions(id),                                                     │
│                                                                                                       │
│   snapshot_id UUID NOT NULL,         -- Full state snapshot                                           │
│   changeset_id UUID,                 -- Delta changes                                                 │
│                                                                                                       │
│   tag VARCHAR(100),                                                                                   │
│   message TEXT NOT NULL,                                                                              │
│                                                                                                       │
│   status VARCHAR(50) DEFAULT 'draft',                                                                 │
│   created_by VARCHAR(255),                                                                            │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   approved_by VARCHAR(255),                                                                           │
│   approved_at TIMESTAMPTZ,                                                                            │
│                                                                                                       │
│   UNIQUE(branch_id, version_number)                                                                   │
│ );                                                                                                    │
│                                                                                                       │
│ -- Item version mapping (which items exist in which version)                                          │
│ CREATE TABLE item_versions (                                                                          │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,                                       │
│   version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,                                 │
│                                                                                                       │
│   state JSONB NOT NULL,              -- Item state at this version                                    │
│   lifecycle VARCHAR(50),                                                                              │
│   introduced_in UUID REFERENCES versions(id),                                                         │
│   last_modified_in UUID REFERENCES versions(id),                                                      │
│                                                                                                       │
│   UNIQUE(item_id, version_id)                                                                         │
│ );                                                                                                    │
│                                                                                                       │
│ -- Alternative items (variations/experiments)                                                         │
│ CREATE TABLE item_alternatives (                                                                      │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   base_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,                                  │
│   alternative_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,                           │
│                                                                                                       │
│   relationship VARCHAR(50) NOT NULL, -- 'alternative_to', 'supersedes', 'experiment_of'               │
│   description TEXT,                                                                                   │
│                                                                                                       │
│   -- Selection tracking                                                                               │
│   is_chosen BOOLEAN DEFAULT FALSE,                                                                    │
│   chosen_at TIMESTAMPTZ,                                                                              │
│   chosen_by VARCHAR(255),                                                                             │
│   chosen_reason TEXT,                                                                                 │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│                                                                                                       │
│   UNIQUE(base_item_id, alternative_item_id)                                                           │
│ );                                                                                                    │
│                                                                                                       │
│ -- Milestones                                                                                         │
│ CREATE TABLE milestones (                                                                             │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│   parent_id UUID REFERENCES milestones(id),                                                           │
│                                                                                                       │
│   name VARCHAR(255) NOT NULL,                                                                         │
│   description TEXT,                                                                                   │
│                                                                                                       │
│   start_date DATE,                                                                                    │
│   target_date DATE NOT NULL,                                                                          │
│   actual_date DATE,                                                                                   │
│                                                                                                       │
│   status VARCHAR(50) DEFAULT 'not_started',                                                           │
│   health VARCHAR(20) DEFAULT 'unknown',                                                               │
│                                                                                                       │
│   risk_score DECIMAL(3,2) DEFAULT 0,                                                                  │
│   risk_factors JSONB,                                                                                 │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│   updated_at TIMESTAMPTZ DEFAULT NOW()                                                                │
│ );                                                                                                    │
│                                                                                                       │
│ -- Milestone-item associations                                                                        │
│ CREATE TABLE milestone_items (                                                                        │
│   milestone_id UUID NOT NULL REFERENCES milestones(id) ON DELETE CASCADE,                             │
│   item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,                                       │
│   added_at TIMESTAMPTZ DEFAULT NOW(),                                                                 │
│   PRIMARY KEY (milestone_id, item_id)                                                                 │
│ );                                                                                                    │
│                                                                                                       │
│ -- Progress snapshots (for burndown/velocity charts)                                                  │
│ CREATE TABLE progress_snapshots (                                                                     │
│   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                                      │
│   project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,                                 │
│                                                                                                       │
│   snapshot_date DATE NOT NULL,                                                                        │
│   metrics JSONB NOT NULL,            -- All progress metrics                                          │
│                                                                                                       │
│   created_at TIMESTAMPTZ DEFAULT NOW(),                                                               │
│                                                                                                       │
│   UNIQUE(project_id, snapshot_date)                                                                   │
│ );                                                                                                    │
│                                                                                                       │
│ ---                                                                                                   │
│ Part 8: Implementation Phases                                                                         │
│                                                                                                       │
│ Phase 1: Foundation (Week 1-3)                                                                        │
│                                                                                                       │
│ - Add canonical concept types and database tables                                                     │
│ - Extend Item model with canonicalId, dimensions, codeRef, docRef                                     │
│ - Add new link types (same_as, represents, manifests_as, documents)                                   │
│ - Make perspective configs project-customizable                                                       │
│ - Create database migrations                                                                          │
│                                                                                                       │
│ Phase 2: Equivalence Engine (Week 3-5)                                                                │
│                                                                                                       │
│ - IN PROGRESS: Go backend being created                                                               │
│   - Naming pattern matcher implementation started                                                     │
│   - Semantic similarity with embeddings being designed                                                │
│   - API contract matcher in development                                                               │
│   - Annotation parser (@trace-implements) framework created                                           │
│   - Confidence aggregation logic being implemented                                                    │
│                                                                                                       │
│ Phase 3: Code Indexing (Week 4-6)                                                                     │
│                                                                                                       │
│ - IN PROGRESS: Go backend being created                                                               │
│   - Tree-sitter parser architecture designed for TS, Go, Python                                       │
│   - GitHub webhook integration framework in development                                               │
│   - Cross-language reference resolution strategy being developed                                      │
│   - Code entity → canonical concept linking logic being designed                                      │
│   - LSP integration for call hierarchies being researched                                             │
│                                                                                                       │
│ Phase 4: Documentation Indexing (Week 5-7)                                                            │
│                                                                                                       │
│ - IN PROGRESS: Go backend being created                                                               │
│   - Markdown parser with section extraction in development                                            │
│   - Semantic chunk detection strategy being designed                                                  │
│   - Code reference extraction from docs being implemented                                             │
│   - Business concept extraction framework being created                                               │
│   - Doc → code → requirement linking architecture designed                                            │
│                                                                                                       │
│ Phase 5: Multi-Perspective UI (Week 6-8)                                                              │
│                                                                                                       │
│ - DONE: Frontend UI components created                                                                │
│   - UnifiedGraphView with perspective layers - Complete                                               │
│   - DimensionFilters control component - Complete                                                     │
│   - PivotNavigation component - Complete                                                              │
│   - EquivalencePanel visualization - Complete                                                         │
│   - Cross-perspective link highlighting - Complete                                                    │
│                                                                                                       │
│ Phase 6: Hierarchy & Grouping (Week 7-9)                                                              │
│                                                                                                       │
│ - IN PROGRESS: Frontend utilities being created                                                       │
│   - Enhanced grouping algorithms (link targets, dependencies, paths, semantic) in development         │
│   - Hierarchy navigation with breadcrumbs being designed                                              │
│   - Project → repo → module → file → function drill-down logic being created                          │
│   - Canonical concept grouping utilities being implemented                                            │
│                                                                                                       │
│ Phase 7: Journey Derivation (Week 8-10)                                                               │
│                                                                                                       │
│ - IN PROGRESS: Backend and UI being created                                                           │
│   - User navigation flow detection logic in development                                               │
│   - Data flow path tracing algorithms being designed                                                  │
│   - Call chain analysis framework being created                                                       │
│   - Journey scoring and ranking system being implemented                                              │
│   - Journey explorer UI components being built                                                        │
│                                                                                                       │
│ Phase 8: UI Dimension (Week 9-11)                                                                     │
│                                                                                                       │
│ - PARTIAL DONE: Core components created                                                               │
│   - PageDecompositionView component - Complete                                                        │
│   - ComponentLibraryExplorer component - Complete                                                     │
│   - IN PROGRESS: Remaining UI components                                                              │
│       - UI entity types and component library schema - Complete                                       │
│     - Page decomposition hierarchy (page → element) - Complete                                        │
│     - Component library indexing from Storybook - In development                                      │
│     - Figma integration (Code Connect / plugin sync) - In development                                 │
│     - UI → code traceability auto-detection - In development                                          │
│     - Component usage tracking and metrics - In development                                           │
│     - Design token linking - In development                                                           │
│                                                                                                       │
│ Phase 9: Temporal Dimension (Week 11-13)                                                              │
│                                                                                                       │
│ - Version branch and version tables (git-like model)                                                  │
│ - Item version mapping and snapshot system                                                            │
│ - Alternative items tracking (variations/experiments)                                                 │
│ - Branch management UI (create, merge, compare)                                                       │
│ - Timeline navigation component                                                                       │
│ - Version comparison and diff visualization                                                           │
│ - Milestone and sprint tracking                                                                       │
│ - Progress dashboard with burndown/velocity charts                                                    │
│                                                                                                       │
│ Phase 10: Performance & Polish (Week 13-16)                                                           │
│                                                                                                       │
│ - IN PROGRESS: Performance optimizations being created                                                │
│   - Virtual rendering for large graphs - In development                                               │
│   - Web Workers for heavy computation - In development                                                │
│   - Caching strategies - Being designed                                                               │
│   - Cross-perspective search - In development                                                         │
│   - Export/import of equivalence mappings - Being researched                                          │
│   - Storybook visual testing integration - In development                                             │
│                                                                                                       │
│ ---                                                                                                   │
│ Implementation Notes                                                                                  │
│                                                                                                       │
│ Files Created                                                                                         │
│                                                                                                       │
│ Frontend - UI Dimension Components:                                                                   │
│ - /frontend/apps/web/src/components/graph/PageDecompositionView.tsx - Hierarchical page → element     │
│ breakdown with interactive drill-down                                                                 │
│ - /frontend/apps/web/src/components/graph/ComponentLibraryExplorer.tsx - Browse and search component  │
│ library with usage metrics                                                                            │
│ - /frontend/apps/web/src/components/graph/DimensionFilters.tsx - Multi-dimensional filtering with     │
│ filter/highlight/color modes                                                                          │
│ - /frontend/apps/web/src/components/graph/EquivalencePanel.tsx - Visualization of cross-perspective   │
│ equivalence relationships                                                                             │
│ - /frontend/apps/web/src/components/graph/PivotNavigation.tsx - Navigate between equivalent nodes     │
│ across perspectives                                                                                   │
│                                                                                                       │
│ Frontend - UI Dimension Views:                                                                        │
│ - Enhanced /frontend/apps/web/src/components/graph/UnifiedGraphView.tsx - Multi-perspective display   │
│ with dimension overlay                                                                                │
│ - Enhanced /frontend/apps/web/src/components/graph/UIComponentTree.tsx - Primary UI dimension         │
│ navigator                                                                                             │
│                                                                                                       │
│ Types & Models:                                                                                       │
│ - /frontend/packages/types/src/canonical.ts (partial) - CanonicalConcept entity definition            │
│ - /frontend/packages/types/src/ui-entities.ts (partial) - UIItem and UIEntityType definitions         │
│ - /frontend/packages/types/src/component-library.ts (partial) - ComponentLibrary and LibraryComponent │
│  definitions                                                                                          │
│                                                                                                       │
│ Agent Work In Progress                                                                                │
│                                                                                                       │
│ Backend Development (Go):                                                                             │
│ - Equivalence Engine: Implementing multi-strategy confidence scoring with naming patterns, semantic   │
│ similarity, and API contract matching                                                                 │
│ - Code Indexing: Designing Tree-sitter integrations for TypeScript, Go, and Python with GitHub        │
│ webhook support                                                                                       │
│ - Documentation Indexing: Creating markdown parser with section extraction and code reference linking │
│                                                                                                       │
│ Frontend Development (React/TypeScript):                                                              │
│ - Journey Derivation: Building user flow detection and journey explorer UI                            │
│ - Hierarchy & Grouping: Creating advanced grouping algorithms for code relationships and canonical    │
│ concepts                                                                                              │
│ - Performance Optimization: Implementing virtual rendering and caching strategies                     │
│ - Cross-Perspective Search: Building unified search across all perspectives with dimension filtering  │
│                                                                                                       │
│ Architecture Decisions Made                                                                           │
│                                                                                                       │
│ 1. Three-Layer Equivalence Model: Canonical concepts as abstract view-independent entities, with      │
│ projections in each perspective                                                                       │
│ 2. Orthogonal Dimensions: Maturity, complexity, coverage, priority - independent from perspective     │
│ filtering                                                                                             │
│ 3. Confidence-Based Detection: Multi-strategy equivalence engine with aggregation (annotation >       │
│ manual > API contract > semantic > naming > structural)                                               │
│ 4. UI as First-Class Dimension: Complete perspective with own hierarchy, component library, and       │
│ design system integration                                                                             │
│ 5. Hierarchical Documentation: Three-level doc indexing (document → section → chunk) with AI-parsed   │
│ semantic units                                                                                        │
│                                                                                                       │
│ Key Design Patterns Identified                                                                        │
│                                                                                                       │
│ - Perspective Projection Pattern: Items exist independently in each perspective, linked via canonical │
│  concepts                                                                                             │
│ - Confidence Scoring: All equivalence detection includes confidence metrics for user guidance         │
│ - Extensible Dimensions: New dimensions can be added without schema migration (JSONB storage)         │
│ - Code-First Traceability: From code entities up to canonical concepts to requirements                │
│ - Design System Integration: Bidirectional Figma-Storybook-Code sync for UI dimension                 │
│                                                                                                       │
│ Dependencies & Blockers                                                                               │
│                                                                                                       │
│ 1. Vector Database Setup: Embedding-based semantic search requires pgvector extension and model       │
│ loading                                                                                               │
│ 2. Code Repository Access: Full code indexing requires GitHub/GitLab API integration with proper auth │
│ 3. Design System Sync: Figma Code Connect feature requires Figma Enterprise plan                      │
│ 4. Performance at Scale: Virtual rendering and Web Workers needed for 1000+ node graphs               │
│ 5. Semantic Chunking: AI-based document chunking requires LLM integration for optimal results         │
│                                                                                                       │
│ Testing Coverage                                                                                      │
│                                                                                                       │
│ - Unit Tests: Dimension filtering logic, canonical concept CRUD, equivalence detection strategies     │
│ - Integration Tests: Multi-perspective linking, code parsing, doc indexing with real files            │
│ - E2E Tests: Perspective pivoting, equivalence discovery, journey derivation, page decomposition      │
│ workflows                                                                                             │
│ - Performance Tests: 100 items/5 perspectives (<100ms), 1000 code entities (<500ms), doc parsing      │
│ (<200ms)                                                                                              │
│                                                                                                       │
│ Next Priority Actions                                                                                 │
│                                                                                                       │
│ 1. Complete Equivalence Engine: Finish Go backend with all confidence strategies                      │
│ 2. Code Indexing MVP: Implement basic Tree-sitter parser for TypeScript code                          │
│ 3. Journey Derivation UI: Build journey explorer and flow visualization                               │
│ 4. Performance Testing: Benchmark graph rendering at scale, identify optimization targets             │
│ 5. Figma Integration: Implement Code Connect plugin for design-code bidirectional sync                │
│                                                                                                       │
│ ---                                                                                                   │
│ Critical Files Summary                                                                                │
│ Category: Types (Core)                                                                                │
│ Files: frontend/packages/types/src/canonical.ts (new), frontend/packages/types/src/item.ts,           │
│   frontend/packages/types/src/link.ts                                                                 │
│ ────────────────────────────────────────                                                              │
│ Category: Types (UI)                                                                                  │
│ Files: frontend/packages/types/src/ui-entities.ts (new),                                              │
│   frontend/packages/types/src/component-library.ts (new)                                              │
│ ────────────────────────────────────────                                                              │
│ Category: Backend Equivalence                                                                         │
│ Files: backend/internal/equivalence/engine.go (new), backend/internal/equivalence/strategies/         │
│ ────────────────────────────────────────                                                              │
│ Category: Backend Code Index                                                                          │
│ Files: backend/internal/codeindex/parsers/, backend/internal/codeindex/sync/                          │
│ ────────────────────────────────────────                                                              │
│ Category: Backend Doc Index                                                                           │
│ Files: backend/internal/docindex/parser.go (new), backend/internal/docindex/linker.go                 │
│ ────────────────────────────────────────                                                              │
│ Category: Frontend Graph                                                                              │
│ Files: frontend/apps/web/src/components/graph/UnifiedGraphView.tsx,                                   │
│   frontend/apps/web/src/components/graph/PerspectiveSelector.tsx                                      │
│ ────────────────────────────────────────                                                              │
│ Category: Frontend Dimensions                                                                         │
│ Files: frontend/apps/web/src/components/graph/DimensionFilters.tsx (new)                              │
│ ────────────────────────────────────────                                                              │
│ Category: Frontend Equivalence                                                                        │
│ Files: frontend/apps/web/src/components/graph/EquivalencePanel.tsx (new),                             │
│   frontend/apps/web/src/components/graph/PivotNavigation.tsx (new)                                    │
│ ────────────────────────────────────────                                                              │
│ Category: Frontend UI Dimension                                                                       │
│ Files: frontend/apps/web/src/components/graph/UIComponentTree.tsx (enhance),                          │
│   frontend/apps/web/src/components/graph/PageDecompositionView.tsx (new),                             │
│   frontend/apps/web/src/components/graph/ComponentLibraryExplorer.tsx (new)                           │
│ ────────────────────────────────────────                                                              │
│ Category: Frontend Temporal                                                                           │
│ Files: frontend/apps/web/src/components/temporal/TemporalNavigator.tsx (new),                         │
│   frontend/apps/web/src/components/temporal/BranchExplorer.tsx (new),                                 │
│   frontend/apps/web/src/components/temporal/VersionDiff.tsx (new),                                    │
│   frontend/apps/web/src/components/temporal/ProgressDashboard.tsx (new)                               │
│ ────────────────────────────────────────                                                              │
│ Category: Types (Temporal)                                                                            │
│ Files: frontend/packages/types/src/temporal.ts (new), frontend/packages/types/src/progress.ts (new)   │
│ ────────────────────────────────────────                                                              │
│ Category: Database                                                                                    │
│ Files: alembic/versions/XXX_canonical_concepts.py, alembic/versions/XXX_doc_entities.py,              │
│   alembic/versions/XXX_perspective_configs.py, alembic/versions/XXX_component_libraries.py (new),     │
│   alembic/versions/XXX_version_branches.py (new), alembic/versions/XXX_milestones.py (new)            │
│ ---                                                                                                   │
│ Verification Plan                                                                                     │
│                                                                                                       │
│ Unit Tests                                                                                            │
│                                                                                                       │
│ - Equivalence detection strategies (each with test cases)                                             │
│ - Documentation parser with sample markdown                                                           │
│ - Canonical concept CRUD operations                                                                   │
│ - Dimension filtering logic                                                                           │
│                                                                                                       │
│ Integration Tests                                                                                     │
│                                                                                                       │
│ - Code indexing: Parse real TS/Go files, verify entities and references                               │
│ - Doc indexing: Parse README, verify code links                                                       │
│ - Equivalence: Create items in multiple perspectives, verify inference                                │
│ - Cross-perspective links: Verify visibility rules                                                    │
│                                                                                                       │
│ E2E Tests                                                                                             │
│                                                                                                       │
│ - Create canonical concept, link items from 3 perspectives                                            │
│ - Pivot navigation between perspectives                                                               │
│ - Dimension filtering with multiple criteria                                                          │
│ - Journey derivation and overlay                                                                      │
│ - Page decomposition: Create page with sections and components, verify hierarchy                      │
│ - Component library: Import from Storybook, verify component catalog                                  │
│ - UI-to-code tracing: Link UI component to implementation code                                        │
│                                                                                                       │
│ Performance Benchmarks                                                                                │
│                                                                                                       │
│ - 100 items across 5 perspectives: <100ms render                                                      │
│ - 1000 code entities: <500ms equivalence inference                                                    │
│ - 50 documents: <200ms doc parsing                                                                    │
│ - Cross-perspective search: <300ms                                                                    │
│                                                                                                       │
│ ---                                                                                                   │
│ Research Sources                                                                                      │
│                                                                                                       │
│ Traceability & Requirements:                                                                          │
│ - https://link.springer.com/article/10.1007/s10796-007-9038-3 - Model conformance traceability        │
│ - https://ieeexplore.ieee.org/document/7323119/ - ReqIF standardized interchange                      │
│ - https://mid.de/en/competences/model-based-systems-engineering/ - UML/SysML to requirements to code  │
│ - https://www.sciencedirect.com/topics/engineering/requirement-traceability - Four orthogonal         │
│ traceability dimensions in SPL                                                                        │
│                                                                                                       │
│ Design System & UI Integration:                                                                       │
│ - https://help.figma.com/hc/en-us/articles/360045003494-Storybook-and-Figma - Official                │
│ Figma-Storybook linking                                                                               │
│ - https://www.figma.com/blog/what-we-launched-at-framework-2024/ - Production code snippets in Figma  │
│ Dev Mode                                                                                              │
│ - https://story.to.design/blog/from-storybook-to-figma - Sync Storybook components to Figma           │
│ - https://www.animaapp.com/blog/design-systems/how-to-sync-your-storybook-design-system-into-figma/ - │
│  Storybook → Figma sync                                                                               │
│ - https://medium.com/comsystoreply/design-code-%EF%B8%8F-how-to-bridge-the-gap-with-figma-and-storybo │
│ ok-41719ff44ade - Bridging design and development                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                                                                                         
⏺ I'll implement this comprehensive multi-dimensional traceability model. Let me start by exploring the  
  current codebase structure to understand what exists and what needs to be created.                     
                                                                                                         
⏺ Explore(Explore codebase structure)                                                                    
  ⎿  Done (24 tool uses · 108.1k tokens · 1m 32s)                                                        
                                                                                                         
⏺ Excellent! The codebase already has significant infrastructure in place. Now let me examine what       
  specific files need to be created or enhanced based on the implementation plan. Let me check the       
  current state of key files.                                                                            
                                                                                                         
⏺ Searched for 2 patterns, read 1 file (ctrl+o to expand)                                                
                                                                                                         
⏺ The temporal components don't exist yet. Let me check the existing type files to understand what's     
  already implemented:                                                                                   
                                                                                                         
⏺ Read 3 files (ctrl+o to expand)                                                                        
                                                                                                         
⏺ The types are already well-established. Now let me check what graph components exist and what temporal 
  components need to be created:                                                                         
                                                                                                         
⏺ Searched for 2 patterns (ctrl+o to expand)                                                             
                                                                                                         
⏺ Many graph components already exist. Let me check the latest migration number and examine existing     
  temporal-related code, then create the missing pieces:                                                 
                                                                                                         
⏺ Read 2 files (ctrl+o to expand)                                                                        
                                                                                                         
⏺ Now I have a clear picture. Based on the plan, I need to implement Phase 9: Temporal Dimension. Let me 
  create the task list and start implementing:                                                           
                                                                                                         
⏺ Now let me create the temporal.ts types file:                                                          
                                                                                                         
⏺ Write(frontend/packages/types/src/temporal.ts)                                                         
  ⎿  Wrote 555 lines to frontend/packages/types/src/temporal.ts                                          
       1 // Temporal Dimension Types                                                                     
       2 // Supports versioning, branching, and futures for multi-dimensional traceability               
       3 // Enables navigation across time (past/present/future) and variation (alternatives, fork       
         s, experiments)                                                                                 
       4                                                                                                 
       5 // =============================================================================                
       6 // VERSION BRANCH TYPES                                                                         
       7 // =============================================================================                
       8                                                                                                 
       9 /**                                                                                             
      10  * Branch type classification - similar to git branch naming conventions                        
     … +545 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the progress.ts types file:                                                          
                                                                                                         
⏺ Write(frontend/packages/types/src/progress.ts)                                                         
  ⎿  Wrote 581 lines to frontend/packages/types/src/progress.ts                                          
       1 // Progress Dimension Types                                                                     
       2 // Focuses on EXECUTION STATE (Jira/Linear-like experience)                                     
       3 // Supports milestones, sprints, burndown charts, and velocity tracking                         
       4                                                                                                 
       5 // =============================================================================                
       6 // MILESTONE TYPES                                                                              
       7 // =============================================================================                
       8                                                                                                 
       9 /**                                                                                             
      10  * Milestone status - lifecycle of a milestone                                                  
     … +571 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the database migration for version branches:                                         
                                                                                                         
⏺ Write(alembic/versions/043_add_version_branches.py)                                                    
  ⎿  Wrote 580 lines to alembic/versions/043_add_version_branches.py                                     
      1 """Add version_branches and related tables for temporal dimension.                               
      2                                                                                                  
      3 Implements git-like versioning and branching for traceability items.                             
      4 Enables time travel, branching, merging, and alternative tracking.                               
      5                                                                                                  
      6 Revision ID: 043_add_version_branches                                                            
      7 Revises: 042_add_derived_journeys                                                                
      8 Create Date: 2026-01-30                                                                          
      9 """                                                                                              
     … +570 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the milestones migration:                                                            
                                                                                                         
⏺ Write(alembic/versions/044_add_milestones.py)                                                          
  ⎿  Wrote 525 lines to alembic/versions/044_add_milestones.py                                           
      1 """Add milestones, sprints, and progress tracking tables.                                        
      2                                                                                                  
      3 Implements project progress dimension with milestones, sprints,                                  
      4 burndown/velocity tracking, and progress snapshots.                                              
      5                                                                                                  
      6 Revision ID: 044_add_milestones                                                                  
      7 Revises: 043_add_version_branches                                                                
      8 Create Date: 2026-01-30                                                                          
      9 """                                                                                              
     … +515 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the temporal directory and the TemporalNavigator component. First, let me check if   
  the temporal directory exists:                                                                         
                                                                                                         
⏺ Bash(mkdir -p                                                                                          
      /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/temporal)        
  ⎿  (No content)                                                                                        
                                                                                                         
⏺ Write(frontend/apps/web/src/components/temporal/TemporalNavigator.tsx)                                 
  ⎿  Wrote 642 lines to frontend/apps/web/src/components/temporal/TemporalNavigator.tsx                  
      1 /**                                                                                              
      2  * TemporalNavigator - Main temporal navigation component                                        
      3  *                                                                                               
      4  * Provides navigation across the temporal dimension:                                            
      5  * - Timeline view: Horizontal timeline with version markers                                     
      6  * - Branches view: Tree visualization of branches                                               
      7  * - Comparison view: Side-by-side diff of two versions                                          
      8  * - Progress view: Milestone/sprint tracking dashboard                                          
      9  */                                                                                              
     … +632 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the BranchExplorer component:                                                        
                                                                                                         
⏺ Write(frontend/apps/web/src/components/temporal/BranchExplorer.tsx)                                    
  ⎿  Wrote 654 lines to frontend/apps/web/src/components/temporal/BranchExplorer.tsx                     
       1 /**                                                                                             
       2  * BranchExplorer - Tree visualization of version branches                                      
       3  *                                                                                              
       4  * Features:                                                                                    
       5  * - Visual branch tree with parent-child relationships                                         
       6  * - Branch creation from any point                                                             
       7  * - Merge request initiation                                                                   
       8  * - Branch comparison                                                                          
       9  * - Status and health indicators                                                               
      10  */                                                                                             
     … +644 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ Now let me create the VersionDiff component:                                                           
                                                                                                         
⏺ Write(frontend/apps/web/src/components/temporal/VersionDiff.tsx)                                       
  ⎿  Wrote 510 lines to frontend/apps/web/src/components/temporal/VersionDiff.tsx                        
       1 /**                                                                                             
       2  * VersionDiff - Side-by-side diff visualization of two versions                                
       3  *                                                                                              
       4  * Features:                                                                                    
       5  * - Visual comparison of added/removed/modified items                                          
       6  * - Field-level change highlighting                                                            
       7  * - Statistics summary                                                                         
       8  * - Filter by change type                                                                      
       9  * - Expandable diff details                                                                    
      10  */                                                                                             
     … +500 lines (ctrl+o to expand)                                                                     
                                                                                                         
⏺ The temporal.ts file was automatically updated by a linter with better type definitions. Let me        
  continue with the ProgressDashboard:                                                                   
                                                                                                         
⏺ Write(frontend/apps/web/src/components/temporal/ProgressDashboard.tsx)                                 
  ⎿  Error writing file                                                                                  
                                                                                                         
⏺ The file was auto-linted. Let me create the ProgressDashboard file:                                    
                                                                                                         
⏺ Write(frontend/apps/web/src/components/temporal/ProgressDashboard.tsx)                                 
  ⎿  Error writing file                                                                                  
                                                                                                         
✶ Compacting conversation… (13m 33s · ↑ 48.6k tokens)                                                    
  ⎿  ◼ Create ProgressDashboard component                                                                
     ◻ Export temporal types from index.ts                                                               
     ◻ Create temporal components index                                                                  
     ✔ Create temporal.ts types file                                                                     
     ✔ Create progress.ts types file                                                                     
     ✔ Create database migration for version branches                                                    
     ✔ Create database migration for milestones                                                          
     ✔ Create TemporalNavigator component                                                                
     ✔ Create BranchExplorer component                                                                   
     ✔ Create VersionDiff component                                                                      
                                                                                                         
─────────────────────────────────────────────────────────────────────────────────────────────────────────
❯                                                                                                        
─────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ bypass permissions on (shift+Tab to cycle) · esc to interrupt  Context left until :auto-compact: 0%  


