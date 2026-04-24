package graph

// Path represents a shortest path between two items
type Path struct {
	Source    string   `json:"source"`
	Target    string   `json:"target"`
	Nodes     []string `json:"nodes"`
	Length    int      `json:"length"`
	LinkTypes []string `json:"link_types"`
}

// Cycle represents a detected cycle in the graph
type Cycle struct {
	Nodes    []string `json:"nodes"`
	Length   int      `json:"length"`
	Severity string   `json:"severity"` // "warning", "error"
}

// CentralityMetrics contains centrality calculations for a project
type CentralityMetrics struct {
	ProjectID   string             `json:"project_id"`
	Betweenness map[string]float64 `json:"betweenness"`
	Closeness   map[string]float64 `json:"closeness"`
	PageRank    map[string]float64 `json:"page_rank"`
	MostCentral []CentralNode      `json:"most_central"`
}

// CentralNode represents a node with high centrality
type CentralNode struct {
	ItemID           string  `json:"item_id"`
	BetweennessScore float64 `json:"betweenness_score"`
	ClosenessScore   float64 `json:"closeness_score"`
	PageRankScore    float64 `json:"page_rank_score"`
}

// DependencyTree represents a dependency hierarchy
type DependencyTree struct {
	Root     string                  `json:"root"`
	Depth    int                     `json:"depth"`
	Children map[string][]Dependency `json:"children"`
}

// Dependency represents a single dependency relationship
type Dependency struct {
	ItemID   string `json:"item_id"`
	LinkType string `json:"link_type"`
	Depth    int    `json:"depth"`
}

// ImpactReport represents an impact analysis result
type ImpactReport struct {
	SourceItems    []string       `json:"source_items"`
	DirectImpact   []string       `json:"direct_impact"`
	IndirectImpact []string       `json:"indirect_impact"`
	TotalAffected  int            `json:"total_affected"`
	ImpactLevels   map[string]int `json:"impact_levels"`
}

// CoverageReport represents graph coverage analysis
type CoverageReport struct {
	ProjectID       string   `json:"project_id"`
	TotalItems      int      `json:"total_items"`
	ConnectedItems  int      `json:"connected_items"`
	IsolatedItems   []string `json:"isolated_items"`
	CoveragePercent float64  `json:"coverage_percent"`
}

// Metrics represents overall graph statistics
type Metrics struct {
	ProjectID           string  `json:"project_id"`
	TotalNodes          int     `json:"total_nodes"`
	TotalEdges          int     `json:"total_edges"`
	Density             float64 `json:"density"`
	AvgDegree           float64 `json:"avg_degree"`
	MaxDepth            int     `json:"max_depth"`
	ConnectedComponents int     `json:"connected_components"`
}
