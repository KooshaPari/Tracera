package export

import "github.com/kooshapari/tracertm-backend/internal/equivalence"

func convertLinks(
	links []equivalence.Link,
	includeMetadata bool,
) []EquivalenceLink {
	result := make([]EquivalenceLink, 0, len(links))

	for _, link := range links {
		export := EquivalenceLink{
			ID:           link.ID,
			ProjectID:    link.ProjectID,
			SourceItemID: link.SourceItemID,
			TargetItemID: link.TargetItemID,
			CanonicalID:  link.CanonicalID,
			LinkType:     link.LinkType,
			Confidence:   link.Confidence,
			Provenance:   string(link.Provenance),
			Status:       string(link.Status),
			ConfirmedBy:  link.ConfirmedBy,
			ConfirmedAt:  link.ConfirmedAt,
			CreatedAt:    link.CreatedAt,
			UpdatedAt:    link.UpdatedAt,
		}

		export.Evidence = make([]Evidence, 0, len(link.Evidence))
		for _, ev := range link.Evidence {
			exportEv := Evidence{
				Strategy:    string(ev.Strategy),
				Confidence:  ev.Confidence,
				Description: ev.Description,
				DetectedAt:  ev.DetectedAt,
			}
			if includeMetadata && len(ev.Details) > 0 {
				exportEv.Details = ev.Details
			}
			export.Evidence = append(export.Evidence, exportEv)
		}

		result = append(result, export)
	}

	return result
}
