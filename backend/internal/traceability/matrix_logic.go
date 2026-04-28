package traceability

import "fmt"

func (s *MatrixService) determineCoverageStatus(upstream, downstream []Link) string {
	totalLinks := len(upstream) + len(downstream)

	if totalLinks == 0 {
		return "none"
	} else if totalLinks >= coverageFullyTraced {
		return "full"
	}
	return "partial"
}

func (s *MatrixService) generateCoverageRecommendations(report *CoverageReport, untracedItems []string) []string {
	recommendations := []string{}

	if report.Overall.CoveragePercent < coverageCriticallyLow {
		recommendations = append(recommendations, fmt.Sprintf(
			"Coverage is critically low (<%d%%). Prioritize creating traceability links.",
			coverageCriticallyLow))
	} else if report.Overall.CoveragePercent < coverageBelowTarget {
		recommendations = append(recommendations, fmt.Sprintf(
			"Coverage is below target (%d%%). Continue adding traceability links.",
			coverageBelowTarget))
	}

	if len(untracedItems) > 0 {
		recommendations = append(recommendations, fmt.Sprintf(
			"%d items have no traceability links. Start with the oldest items.",
			len(untracedItems)))
	}

	for itemType, metrics := range report.ByType {
		if metrics.CoveragePercent < coverageCriticallyLow {
			recommendations = append(recommendations, fmt.Sprintf(
				"%s coverage is critically low (%.1f%%). Focus on this area.",
				itemType, metrics.CoveragePercent))
		}
	}

	if len(recommendations) == 0 {
		recommendations = append(recommendations, "Traceability coverage is good. Maintain current practices.")
	}

	return recommendations
}

func (s *MatrixService) generateGapRecommendations(analysis *GapAnalysis) []string {
	recommendations := []string{}

	if len(analysis.MissingForward) > 0 {
		recommendations = append(recommendations, fmt.Sprintf(
			"%d requirements lack test coverage. Create test cases for validation.",
			len(analysis.MissingForward)))
	}

	if len(analysis.MissingBackward) > 0 {
		recommendations = append(recommendations, fmt.Sprintf(
			"%d tests are not linked to requirements. Ensure all tests validate specific requirements.",
			len(analysis.MissingBackward)))
	}

	if len(analysis.Orphaned) > 0 {
		recommendations = append(recommendations, fmt.Sprintf(
			"%d items are completely orphaned. Link them to the traceability matrix.",
			len(analysis.Orphaned)))
	}

	if len(recommendations) == 0 {
		recommendations = append(recommendations, "No traceability gaps detected. All items are properly linked.")
	}

	return recommendations
}
