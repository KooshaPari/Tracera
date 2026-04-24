package equivalence

import (
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// DetectEquivalences handles POST /equivalences/detect
func (handler *Handler) DetectEquivalences(echoCtx echo.Context) error {
	var req DetectionRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	suggestions, err := handler.service.DetectEquivalences(echoCtx.Request().Context(), &req)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, suggestions)
}

// GetSuggestions handles GET /equivalences/suggestions
func (handler *Handler) GetSuggestions(ctx echo.Context) error {
	projectID, err := uuid.Parse(ctx.QueryParam("project_id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	limit, offset := parsePagination(ctx)

	suggestions, err := handler.service.GetSuggestions(ctx.Request().Context(), projectID, limit, offset)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.JSON(http.StatusOK, suggestions)
}

// ConfirmSuggestion handles POST /equivalences/suggestions/:id/confirm
func (handler *Handler) ConfirmSuggestion(ctx echo.Context) error {
	suggestionID, err := uuid.Parse(ctx.Param("id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid suggestion id"})
	}

	userID := getUserIDFromEchoContext(ctx)

	link, err := handler.service.ConfirmSuggestion(ctx.Request().Context(), suggestionID, userID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.JSON(http.StatusOK, link)
}

// RejectSuggestion handles POST /equivalences/suggestions/:id/reject
func (handler *Handler) RejectSuggestion(echoCtx echo.Context) error {
	suggestionID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid suggestion id"})
	}

	userID := getUserIDFromEchoContext(echoCtx)

	if err := handler.service.RejectSuggestion(echoCtx.Request().Context(), suggestionID, userID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// BulkConfirm handles POST /equivalences/suggestions/bulk-confirm
func (handler *Handler) BulkConfirm(echoCtx echo.Context) error {
	var req BulkConfirmRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	userID := getUserIDFromEchoContext(echoCtx)

	links, err := handler.service.BulkConfirm(echoCtx.Request().Context(), req.EquivalenceIDs, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, links)
}

// BulkReject handles POST /equivalences/suggestions/bulk-reject
func (handler *Handler) BulkReject(ctx echo.Context) error {
	var req BulkConfirmRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	userID := getUserIDFromEchoContext(ctx)

	if err := handler.service.BulkReject(ctx.Request().Context(), req.EquivalenceIDs, userID); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.NoContent(http.StatusNoContent)
}

// Helpers

func applyDetectionDefaults(req *DetectionRequest) {
	if req.MaxResults <= 0 {
		req.MaxResults = 100
	}
	if req.MinConfidence <= 0 {
		req.MinConfidence = defaultMinConfidence
	}
}

func buildDetectionStats(suggestions []Suggestion, req *DetectionRequest, startTime time.Time) DetectionStats {
	strategyBreakdown := make(map[StrategyType]int)
	avgConf := 0.0
	for _, suggestion := range suggestions {
		for _, strategy := range suggestion.Strategies {
			strategyBreakdown[strategy]++
		}
		avgConf += suggestion.Confidence
	}
	if len(suggestions) > 0 {
		avgConf /= float64(len(suggestions))
	}

	return DetectionStats{
		TotalItemsScanned: len(req.CandidatePool),
		EquivalencesFound: len(suggestions),
		AverageConfidence: avgConf,
		StrategyBreakdown: strategyBreakdown,
		DurationMs:        time.Since(startTime).Milliseconds(),
	}
}
