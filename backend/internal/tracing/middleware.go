package tracing

import (
	"github.com/labstack/echo/v4"
	"go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho"
)

// Middleware returns an Echo middleware that instruments HTTP requests with OpenTelemetry
func Middleware() echo.MiddlewareFunc {
	return otelecho.Middleware("tracertm-backend")
}
