package middleware

import (
	"net/http"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/labstack/echo/v4"
)

const (
	sentryFlushTimeout   = 2 * time.Second
	slowRequestThreshold = 1 * time.Second
)

// SentryMiddleware captures errors and performance data for requests using Echo framework
func SentryMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Create a new Sentry hub for this request (isolated scope)
			hub := sentry.CurrentHub().Clone()
			c.Set("sentry_hub", hub)

			transaction := startSentryTransaction(c)
			defer transaction.Finish()

			// Store transaction in context for child spans
			c.SetRequest(c.Request().WithContext(transaction.Context()))

			annotateRequestScope(c, hub)

			// Capture start time
			start := time.Now()

			// Process request
			err := next(c)

			finalizeSentryTransaction(c, hub, transaction, start, err)

			return err
		}
	}
}

func startSentryTransaction(c echo.Context) *sentry.Span {
	options := []sentry.SpanOption{
		sentry.WithOpName("http.server"),
		sentry.ContinueFromRequest(c.Request()),
	}
	return sentry.StartTransaction(
		c.Request().Context(),
		c.Request().Method+" "+c.Path(),
		options...,
	)
}

func annotateRequestScope(c echo.Context, hub *sentry.Hub) {
	hub.Scope().SetRequest(c.Request())
	hub.Scope().SetContext("request", map[string]interface{}{
		"method":      c.Request().Method,
		"url":         c.Request().URL.String(),
		"remote_addr": c.RealIP(),
		"user_agent":  c.Request().UserAgent(),
	})

	hub.Scope().SetTag("route", c.Path())
	hub.Scope().SetTag("method", c.Request().Method)
}

func finalizeSentryTransaction(c echo.Context, hub *sentry.Hub, transaction *sentry.Span, start time.Time, err error) {
	duration := time.Since(start)
	transaction.SetData("duration_ms", duration.Milliseconds())

	status := c.Response().Status
	transaction.Status = sentry.HTTPtoSpanStatus(status)
	hub.Scope().SetTag("status_code", http.StatusText(status))

	if err != nil {
		hub.CaptureException(err)
	}

	if duration > slowRequestThreshold {
		hub.AddBreadcrumb(&sentry.Breadcrumb{
			Type:     "http",
			Category: "slow_request",
			Message:  "Slow request: " + c.Request().Method + " " + c.Path(),
			Level:    sentry.LevelWarning,
			Data: map[string]interface{}{
				"duration_ms": duration.Milliseconds(),
				"status_code": status,
			},
		}, nil)
	}

	hub.Flush(sentryFlushTimeout)
}

// handleSentryRecover recovers from a panic, reports to Sentry, and responds with 500.
func handleSentryRecover(c echo.Context, panicVal interface{}) {
	hub := c.Get("sentry_hub")
	if sentryHub, ok := hub.(*sentry.Hub); ok {
		sentryHub.RecoverWithContext(c.Request().Context(), panicVal)
	} else {
		sentry.CurrentHub().RecoverWithContext(c.Request().Context(), panicVal)
	}

	sentry.Flush(sentryFlushTimeout)

	if jsonErr := c.JSON(http.StatusInternalServerError, map[string]string{
		"error": "Internal server error",
	}); jsonErr != nil {
		c.Logger().Error(jsonErr)
	}
}

// SentryRecoverMiddleware captures panics and sends them to Sentry
func SentryRecoverMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			defer func() {
				if err := recover(); err != nil {
					handleSentryRecover(c, err)
				}
			}()
			return next(c)
		}
	}
}
