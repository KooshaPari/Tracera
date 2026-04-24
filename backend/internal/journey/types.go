package journey

import (
	"time"
)

// Type represents the classification of a discovered journey
type Type string

const (
	// UserFlow represents navigation through UI pages
	UserFlow Type = "user_flow"
	// DataPath represents data flowing through the system
	DataPath Type = "data_path"
	// CallChain represents function call sequences
	CallChain Type = "call_chain"
	// TestTrace represents test execution flows
	TestTrace Type = "test_trace"
)

// DerivedJourney represents a discovered journey through the system
type DerivedJourney struct {
	ID        string    `json:"id"`
	ProjectID string    `json:"project_id"`
	Name      string    `json:"name"`
	Type      Type      `json:"type"`
	NodeIDs   []string  `json:"node_ids"`
	Links     []Link    `json:"links"`
	Color     *string   `json:"color,omitempty"`
	Metadata  Metadata  `json:"metadata"`
	Score     float64   `json:"score"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Link represents a connection between nodes in a journey
type Link struct {
	SourceID string `json:"source_id"`
	TargetID string `json:"target_id"`
	Type     string `json:"type"`
	Weight   int    `json:"weight"`
}

// Metadata stores additional journey information
type Metadata struct {
	Frequency    int                    `json:"frequency"`
	Importance   float64                `json:"importance"`
	Completeness float64                `json:"completeness"`
	UserCount    int                    `json:"user_count"`
	AverageTime  int                    `json:"average_time"` // in milliseconds
	Description  string                 `json:"description"`
	Tags         []string               `json:"tags"`
	Variations   int                    `json:"variations"`
	LastDetected time.Time              `json:"last_detected"`
	CustomData   map[string]interface{} `json:"custom_data,omitempty"`
}

// Path represents a traversed sequence of nodes and links for detectors.
type Path struct {
	Nodes     []string
	Links     []string
	Score     float64
	Type      Type
	Frequency int
}

// PathNode represents a node in the system (Item, Page, Function, etc.)
type PathNode struct {
	ID       string
	Title    string
	Type     string
	Category string
	Metadata map[string]interface{}
}

// PathEdge represents a connection between path nodes
type PathEdge struct {
	SourceID string
	TargetID string
	LinkType string
	Weight   int
	Count    int
}

// DetectionConfig configures journey detection behavior
type DetectionConfig struct {
	// Minimum path length to consider as a journey
	MinPathLength int
	// Maximum path length to explore
	MaxPathLength int
	// Minimum frequency for a path to be considered valid
	MinFrequency int
	// Minimum score threshold
	MinScore float64
	// Whether to detect cycles
	AllowCycles bool
	// Whether to group similar paths
	GroupSimilar bool
	// Similarity threshold for grouping (0-1)
	SimilarityThreshold float64
}

// DetectionResult holds the results of journey detection
type DetectionResult struct {
	Journeys        []*DerivedJourney
	TotalPaths      int
	ValidPaths      int
	DetectionTimeMs int64 `json:"detection_time_ms"`
	Errors          []string
}

// ScoringMetrics holds individual scoring components
type ScoringMetrics struct {
	FrequencyScore    float64
	ImportanceScore   float64
	CompletenessScore float64
	UniquenessScore   float64
	RecencyScore      float64
	TotalScore        float64
}

// Stats provides aggregate statistics about detected journeys
type Stats struct {
	TotalJourneys       int
	ByType              map[Type]int
	AveragePathLength   float64
	AverageScore        float64
	MostCommonStart     string
	MostCommonEnd       string
	CommonIntermediates []string
	TimeRange           struct {
		Start time.Time
		End   time.Time
	}
}

// VisualizationData formats journey data for frontend visualization
type VisualizationData struct {
	Journey *DerivedJourney
	Nodes   map[string]*VisualizationNode
	Edges   []*VisualizationEdge
}

// VisualizationNode represents a node for visualization
type VisualizationNode struct {
	ID    string
	Label string
	Type  string
	Size  int
	Color string
}

// VisualizationEdge represents an edge for visualization
type VisualizationEdge struct {
	Source string
	Target string
	Type   string
	Weight int
}

// DetectionFilter allows filtering journeys during detection
type DetectionFilter struct {
	StartNodeID   *string
	EndNodeID     *string
	MinPathLength int
	MaxPathLength int
	JourneyTypes  []Type
	MinScore      float64
}

// FrequencyData tracks how often paths occur
type FrequencyData struct {
	PathHash    string
	Count       int
	LastSeen    time.Time
	FirstSeen   time.Time
	Occurrences []time.Time
}

// DependencyInfo represents dependency information for scoring
type DependencyInfo struct {
	InDegree   int
	OutDegree  int
	Centrality float64
	IsRoot     bool
	IsLeaf     bool
}
