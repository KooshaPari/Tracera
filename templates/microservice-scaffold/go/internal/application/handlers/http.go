package handlers

import (
	"encoding/json"
	"net/http"
)

type HTTPHandler struct {
	commands *CommandHandler
	queries  *QueryHandler
}

func NewHTTPHandler(cmd *CommandHandler, qry *QueryHandler) *HTTPHandler {
	return &HTTPHandler{
		commands: cmd,
		queries:  qry,
	}
}

func (h *HTTPHandler) Health(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

func (h *HTTPHandler) Ready(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{"status": "ready"})
}
