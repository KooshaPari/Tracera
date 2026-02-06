package cache

// ProjectKey generates cache key for a project.
func ProjectKey(projectID string) string {
	return "project:" + projectID
}

// ItemKey generates cache key for an item.
func ItemKey(itemID string) string {
	return "item:" + itemID
}

// LinkKey generates cache key for a link.
func LinkKey(linkID string) string {
	return "link:" + linkID
}

// AgentKey generates cache key for an agent.
func AgentKey(agentID string) string {
	return "agent:" + agentID
}

// SearchKey generates cache key for a search query scoped to a project.
func SearchKey(query, projectID string) string {
	return "search:" + projectID + ":" + query
}

func SessionKey(sessionID string) string {
	return "session:" + sessionID
}

func RateLimitKey(identifier, window string) string {
	return "ratelimit:" + identifier + ":" + window
}
