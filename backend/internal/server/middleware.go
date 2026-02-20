package server

import (
	"log/slog"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	custommw "github.com/kooshapari/tracertm-backend/internal/middleware"
	"github.com/kooshapari/tracertm-backend/internal/tracing"
)

func (s *Server) setupMiddleware() {
	// Recovery middleware (must be first)
	s.echo.Use(custommw.RecoveryMiddleware())

	// OpenTelemetry tracing middleware (after recovery, before logging)
	if s.infra.TracerProvider != nil {
		s.echo.Use(tracing.Middleware())
		slog.Info("✅ OpenTelemetry tracing middleware enabled")
	}

	// Sentry error tracking and performance monitoring
	if s.cfg.SentryDSN != "" {
		s.echo.Use(custommw.SentryRecoverMiddleware())
		s.echo.Use(custommw.SentryMiddleware())
		slog.Error("✅ Sentry error tracking middleware enabled")
	}

	// Request logger
	s.echo.Use(custommw.RequestLoggerMiddleware())

	// Gzip compression - compress responses > 1KB
	s.echo.Use(middleware.GzipWithConfig(middleware.GzipConfig{
		Level:     gzipLevel,     // 1-9, 5 is balanced between speed and compression
		MinLength: gzipMinLength, // Only compress responses > 1KB
		Skipper: func(c echo.Context) bool {
			// Don't compress WebSocket, streaming, or download endpoints
			path := c.Request().URL.Path
			return path == "/health" ||
				path == "/api/v1/health" ||
				path == "/api/v1/ws" ||
				path == "/metrics" ||
				c.Response().Header().Get("Content-Type") == "application/octet-stream"
		},
	}))

	// CORS
	s.echo.Use(middleware.CORSWithConfig(custommw.CORSConfig()))

	// CSRF protection
	csrfConfig := custommw.NewCSRFConfig()
	s.echo.Use(custommw.CSRFMiddleware(csrfConfig))

	// Cache control headers and ETag support
	s.echo.Use(custommw.CacheControlMiddleware(custommw.CacheControlConfig{
		Skipper: custommw.HealthCheckSkipper,
	}))
	s.echo.Use(custommw.ETagMiddleware(custommw.ETagConfig{
		Skipper: custommw.HealthCheckSkipper,
	}))
	s.echo.Use(custommw.VariationsMiddleware())
	s.echo.Use(custommw.CORSCacheMiddleware())

	// Error handler
	s.echo.Use(custommw.ErrorHandlerMiddleware())

	// Enhanced rate limiting with per-endpoint controls
	rateLimiter := custommw.CreateStandardRateLimiter(s.redisClient)
	s.echo.Use(rateLimiter.Middleware())

	// Store rate limiter for cleanup on shutdown
	s.echo.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			c.Set("rate_limiter", rateLimiter)
			return next(c)
		}
	})
}
