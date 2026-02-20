package services

// Compile-time interface verification for all mock services
// This file ensures that all mock implementations satisfy their respective interfaces
// If any mock is incomplete, this file will fail to compile

// Note: Verification for core service interfaces defined in services.go
// Additional services (CodeIndexService, SearchService, etc.) are verified
// when they are used in actual implementation files.
var (
	_ ItemService    = (*MockItemService)(nil)
	_ LinkService    = (*MockLinkService)(nil)
	_ ProjectService = (*MockProjectService)(nil)
	_ AgentService   = (*MockAgentService)(nil)
)
