package server

import (
	"context"
	"log/slog"
	"os"
	"strings"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/equivalence"
	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/journey"
	"github.com/kooshapari/tracertm-backend/internal/metrics"
	custommw "github.com/kooshapari/tracertm-backend/internal/middleware"
	"github.com/kooshapari/tracertm-backend/internal/progress"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

func (s *Server) setupRoutes() {
	s.registerHealthRoutes()
	s.registerMetricsRoute()
	s.registerCSRFRoute()
	s.startWebSocketHub()
	s.setupNATSToWebSocketBridge()
	s.setupEventConsumer()

	api := s.echo.Group("/api/v1")
	api.GET("/health", handlers.HealthCheck)

	authProvider, realtimeBroadcaster := s.resolveAdapters()
	slog.Info("✓ Injecting services into handlers")

	s.registerOAuthRoutes(authProvider)

	protected := s.registerAuthRoutes(api, authProvider)
	s.registerAuthKitRoutes(api, authProvider)
	s.registerWebSocketRoutes(api, authProvider)
	s.registerNotificationRoutes(protected, authProvider)
	s.registerProjectRoutes(api, authProvider, realtimeBroadcaster)
	s.registerItemRoutes(api, authProvider, realtimeBroadcaster)
	s.registerLinkRoutes(api)
	s.registerAgentRoutes(api, authProvider, realtimeBroadcaster)
	s.registerDistributedCoordinationRoutes(api, authProvider, realtimeBroadcaster)
	s.registerGraphRoutes(api)
	s.registerGraphViewportRoutes(api)
	s.registerGraphStreamRoutes(api)
	s.registerSearchRoutes(api, authProvider, realtimeBroadcaster)
	s.registerEquivalenceRoutes(api)
	s.registerJourneyRoutes(api)
	s.registerDocRoutes(api, authProvider, realtimeBroadcaster)
	s.registerTemporalRoutes(api)
	s.registerCodeIndexRoutes(api)
	s.registerProgressRoutes(api)
	s.registerTraceabilityRoutes(api, authProvider, realtimeBroadcaster)
	s.registerStorageRoutes(api)
	s.registerDelegationRoutes(api)
	s.registerDashboardRoutes(api)
}

func (s *Server) registerHealthRoutes() {
	s.echo.GET("/health", handlers.HealthCheck)
}

func (s *Server) registerMetricsRoute() {
	s.echo.GET("/metrics", metrics.Handler())
}

func (s *Server) registerCSRFRoute() {
	s.echo.GET("/api/v1/csrf-token", handlers.GetCSRFToken)
}

func (s *Server) startWebSocketHub() {
	go s.wsHub.Run(context.Background())
}

func (s *Server) resolveAdapters() (interface{}, interface{}) {
	if s.adapterFactory == nil {
		return nil, nil
	}

	return s.adapterFactory.GetAuthProvider(), s.adapterFactory.GetRealtimeBroadcaster()
}

func (s *Server) registerWebSocketRoutes(api *echo.Group, authProvider interface{}) {
	if ap, ok := authProvider.(auth.Provider); ok && ap != nil {
		api.GET("/ws", websocket.Handler(s.wsHub, ap))
		api.GET("/ws/stats", websocket.StatsHandler(s.wsHub))
		return
	}

	slog.Info("⚠️  WebSocket handler not registered: auth provider not configured")
}

func (s *Server) registerAuthRoutes(api *echo.Group, authProvider interface{}) *echo.Group {
	var authHandler *handlers.AuthHandler
	if ap, ok := authProvider.(auth.Provider); ok && ap != nil {
		authHandler = handlers.NewAuthHandler(
			ap,
			s.redisClient,
			s.cfg.JWTSecret,
			sessionTTL,
			s.cfg.Env == "production",
		)

		// Login and Register removed -- use AuthKit hosted UI flow instead
		// (/api/v1/auth/authkit/authorize + /api/v1/auth/authkit/callback).
		api.POST("/auth/refresh", authHandler.Refresh)
		api.POST("/auth/logout", authHandler.Logout)
		api.GET("/auth/verify", authHandler.VerifyToken)
	}

	var protected *echo.Group
	if ap, ok := authProvider.(auth.Provider); ok && ap != nil {
		protected = api.Group("")
		protected.Use(custommw.AuthAdapterMiddleware(custommw.AuthAdapterConfig{
			AuthProvider: ap,
			Skipper:      custommw.HealthCheckSkipper,
		}))
		protected.GET("/auth/me", handlers.AuthMe)
		if authHandler != nil {
			protected.GET("/auth/user", authHandler.GetUser)
		}
	}

	return protected
}

func (s *Server) registerAuthKitRoutes(api *echo.Group, authProvider interface{}) {
	ap, ok := authProvider.(auth.Provider)
	if !ok || ap == nil {
		slog.Info("AuthKit routes not registered: auth provider not configured")
		return
	}

	clientID, redirectURI, apiKey, err := handlers.LoadAuthKitEnv()
	if err != nil {
		slog.Error("AuthKit routes not registered", "error", err)
		return
	}

	kitAdapter := s.adapterFactory.GetKitAdapter()
	if kitAdapter == nil {
		slog.Error("AuthKit routes not registered: auth provider is not a KitAdapter")
		return
	}

	authHandler := handlers.NewAuthHandler(
		ap,
		s.redisClient,
		s.cfg.JWTSecret,
		sessionTTL,
		s.cfg.Env == "production",
	)

	authKitHandler := handlers.NewAuthKitHandler(
		apiKey,
		kitAdapter,
		s.redisClient,
		authHandler,
		clientID,
		redirectURI,
	)

	api.GET("/auth/authkit/authorize", authKitHandler.Authorize)
	api.POST("/auth/authkit/callback", authKitHandler.Callback)
	api.POST("/auth/authkit/refresh", authKitHandler.Refresh)
}

func (s *Server) registerOAuthRoutes(authProvider interface{}) {
	var ap auth.Provider
	if p, ok := authProvider.(auth.Provider); ok {
		ap = p
	}

	oauthHandler := handlers.NewOAuthHandler(s.redisClient, ap)
	oauth := s.echo.Group("/oauth")

	oauth.Use(noCacheFrameDenyMiddleware())

	// Strict CORS allowlist for browser calls to OAuth helper endpoints.
	oauth.Use(custommw.SecureCORS(parseAllowedOriginsEnv("CORS_ALLOWED_ORIGINS")))

	// Dedicated OAuth rate limiting (stricter than default /api/v1/*).
	oauthLimiter := custommw.NewEnhancedRateLimiter(custommw.EnhancedRateLimitConfig{
		RedisClient:              s.redisClient,
		DefaultRequestsPerMinute: 30,
		DefaultBurstSize:         10,
		Skipper:                  nil,
		AddHeaders:               true,
		RateLimitTTL:             1 * time.Hour,
		ErrorMessage:             "",
		EndpointLimits: []custommw.EndpointLimit{
			{
				Pattern:           "/oauth/login",
				RequestsPerMinute: 10,
				BurstSize:         5,
				KeyExtractor: func(c *echo.Context) string {
					return "ip:" + (*c).RealIP() + ":oauth_login"
				},
			},
			{
				Pattern:           "/oauth/callback",
				RequestsPerMinute: 20,
				BurstSize:         10,
				KeyExtractor: func(c *echo.Context) string {
					return "ip:" + (*c).RealIP() + ":oauth_callback"
				},
			},
			{
				Pattern:           "/oauth/status",
				RequestsPerMinute: 60,
				BurstSize:         20,
				KeyExtractor: func(c *echo.Context) string {
					return "ip:" + (*c).RealIP() + ":oauth_status"
				},
			},
			{
				Pattern:           "/oauth/logout",
				RequestsPerMinute: 30,
				BurstSize:         10,
				KeyExtractor: func(c *echo.Context) string {
					return "ip:" + (*c).RealIP() + ":oauth_logout"
				},
			},
		},
	})
	oauth.Use(oauthLimiter.Middleware())

	// Validate request content-type and body size for POSTs.
	oauth.Use(custommw.ContentTypeValidator("application/json"))
	const oauthMaxBodyKB = 16
	oauth.Use(custommw.RequestSizeLimiter(oauthMaxBodyKB * 1024))

	oauth.POST("/login", oauthHandler.Login)
	oauth.GET("/callback", oauthHandler.Callback)

	// Logout should be authenticated. If no auth provider is configured, the handler fails loudly.
	if ap != nil {
		protected := oauth.Group("")
		protected.Use(custommw.AuthAdapterMiddleware(custommw.AuthAdapterConfig{
			AuthProvider: ap,
			Skipper:      nil,
		}))
		protected.POST("/logout", oauthHandler.Logout)
		protected.GET("/status", oauthHandler.Status)
	} else {
		oauth.POST("/logout", oauthHandler.Logout)
		oauth.GET("/status", oauthHandler.Status)
	}
}

func noCacheFrameDenyMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			h := c.Response().Header()
			h.Set("Cache-Control", "no-store")
			h.Set("Pragma", "no-cache")
			h.Set("X-Frame-Options", "DENY")
			return next(c)
		}
	}
}

func parseAllowedOriginsEnv(envKey string) []string {
	raw := strings.TrimSpace(os.Getenv(envKey))
	if raw == "" {
		return []string{
			"http://localhost:4000", "http://127.0.0.1:4000",
			"http://localhost:5173", "http://127.0.0.1:5173",
			"http://localhost:3000", "http://127.0.0.1:3000",
		}
	}

	parts := strings.Split(raw, ",")
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		val := strings.TrimSpace(p)
		if val == "" {
			continue
		}
		if val == "*" || strings.Contains(val, "*") {
			continue
		}
		out = append(out, val)
	}
	if len(out) == 0 {
		return []string{
			"http://localhost:4000", "http://127.0.0.1:4000",
			"http://localhost:5173", "http://127.0.0.1:5173",
			"http://localhost:3000", "http://127.0.0.1:3000",
		}
	}
	return out
}

func (s *Server) registerProjectRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	projectHandler := handlers.NewProjectHandler(
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
		&handlers.EchoBinder{},
		s.serviceContainer.ProjectService(),
	)
	api.POST("/projects", projectHandler.CreateProject)
	api.GET("/projects", projectHandler.ListProjects)
	api.GET("/projects/:id", projectHandler.GetProject)
	api.PUT("/projects/:id", projectHandler.UpdateProject)
	api.DELETE("/projects/:id", projectHandler.DeleteProject)
}

func (s *Server) registerItemRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	itemHandler := handlers.NewItemHandler(
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
		&handlers.EchoBinder{},
	)
	itemHandler.SetItemService(s.serviceContainer.ItemService())
	api.POST("/items", itemHandler.CreateItem)
	api.GET("/items", itemHandler.ListItems)
	api.GET("/items/:id", itemHandler.GetItem)
	api.PUT("/items/:id", itemHandler.UpdateItem)
	api.DELETE("/items/:id", itemHandler.DeleteItem)
	api.POST("/items/:id/pivot", itemHandler.PivotNavigation)
	api.GET("/items/:id/pivot-targets", itemHandler.GetPivotTargets)
}

func (s *Server) registerLinkRoutes(api *echo.Group) {
	linkHandler := handlers.NewLinkHandler(
		s.serviceContainer.LinkService(),
		s.serviceContainer.ItemService(),
		&handlers.EchoBinder{},
	)
	api.POST("/links", linkHandler.CreateLink)
	api.GET("/links", linkHandler.ListLinks)
	api.GET("/links/:id", linkHandler.GetLink)
	api.PUT("/links/:id", linkHandler.UpdateLink)
	api.DELETE("/links/:id", linkHandler.DeleteLink)
}

func (s *Server) registerAgentRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	agentCoordinator := agents.NewCoordinator(s.infra.GormDB, agentCoordinatorInterval)
	agentHandler := handlers.NewAgentHandler(
		s.serviceContainer.AgentService(),
		agentCoordinator,
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
		&handlers.EchoBinder{},
	)
	api.POST("/agents", agentHandler.CreateAgent)
	api.GET("/agents", agentHandler.ListAgents)
	api.GET("/agents/:id", agentHandler.GetAgent)
	api.PUT("/agents/:id", agentHandler.UpdateAgent)
	api.DELETE("/agents/:id", agentHandler.DeleteAgent)
	api.POST("/agents/register", agentHandler.RegisterAgent)
	api.DELETE("/agents/:id/unregister", agentHandler.UnregisterAgent)
	api.POST("/agents/heartbeat", agentHandler.AgentHeartbeat)
	api.GET("/agents/:id/status", agentHandler.GetAgentStatus)
	api.GET("/agents/:id/metrics", agentHandler.GetAgentMetrics)
	api.GET("/agents/:id/task", agentHandler.GetNextTask)
	api.POST("/agents/task/assign", agentHandler.AssignTask)
	api.POST("/agents/task/result", agentHandler.SubmitTaskResult)
	api.POST("/agents/task/error", agentHandler.SubmitTaskError)
	api.GET("/agents/tasks/:task_id", agentHandler.GetTaskDetails)
	api.DELETE("/agents/tasks/:task_id/cancel", agentHandler.CancelTask)
	api.GET("/agents/registered", agentHandler.ListRegisteredAgents)
	api.GET("/agents/coordinator/status", agentHandler.GetCoordinatorStatus)
	api.GET("/agents/coordinator/health", agentHandler.CoordinatorHealthCheck)
	api.GET("/agents/queue/stats", agentHandler.GetQueueStats)
	api.GET("/agents/queue/tasks", agentHandler.ListQueuedTasks)
	api.POST("/agents/queue/rebalance", agentHandler.RebalanceTasks)
	api.GET("/agents/:id/history", agentHandler.GetAgentHistory)
}

func (s *Server) registerDistributedCoordinationRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	lockManager := agents.NewLockManager(s.infra.GormDB, lockManagerTTL)
	conflictDetector := agents.NewConflictDetector(s.infra.GormDB, lockManager)
	teamManager := agents.NewTeamManager(s.infra.GormDB)
	distributedCoordinator := agents.NewDistributedCoordinator(s.infra.GormDB, lockManager, conflictDetector, teamManager)
	distCoordHandler := handlers.NewDistributedCoordinationHandler(
		s.pool,
		distributedCoordinator,
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
		&handlers.EchoBinder{},
	)
	api.POST("/operations/distributed", distCoordHandler.CreateDistributedOperation)
	api.GET("/operations/distributed/:id", distCoordHandler.GetOperationStatus)
	api.GET("/operations/distributed", distCoordHandler.ListOperations)
	api.POST("/operations/distributed/:id/assign", distCoordHandler.AssignOperationToAgents)
	api.PUT("/operations/distributed/:id/status", distCoordHandler.UpdateOperationStatus)
	api.POST("/operations/distributed/:id/complete", distCoordHandler.CompleteOperation)
	api.GET("/operations/distributed/:operation_id/participants/:agent_id", distCoordHandler.GetParticipantStatus)
	api.POST("/operations/distributed/:operation_id/participants/:agent_id/result", distCoordHandler.SubmitParticipantResult)
	api.GET("/operations/distributed/:id/results", distCoordHandler.GetOperationResults)
}

func (s *Server) registerGraphRoutes(api *echo.Group) {
	graphHandler := handlers.NewGraphHandler(s.pool)
	api.GET("/graph/ancestors/:id", graphHandler.GetAncestors)
	api.GET("/graph/descendants/:id", graphHandler.GetDescendants)
	api.GET("/graph/path", graphHandler.FindPath)
	api.GET("/graph/paths", graphHandler.FindAllPaths)
	api.GET("/graph/full", graphHandler.GetFullGraph)
	api.GET("/graph/cycles", graphHandler.DetectCycles)
	api.GET("/graph/topo-sort", graphHandler.TopologicalSort)
	api.GET("/graph/impact/:id", graphHandler.GetImpactAnalysis)
	api.GET("/graph/dependencies/:id", graphHandler.GetDependencyAnalysis)
	api.GET("/graph/orphans", graphHandler.GetOrphanItems)
	api.GET("/graph/traverse/:id", graphHandler.Traverse)
	api.GET("/graph/transitive-closure", graphHandler.ComputeTransitiveClosure)
	api.GET("/graph/impact-paths/:id", graphHandler.AnalyzeImpactPaths)
	api.GET("/graph/metrics", graphHandler.GetMetrics)
	api.POST("/graph/cache/invalidate", graphHandler.InvalidateCache)
}

func (s *Server) registerGraphViewportRoutes(api *echo.Group) {
	graphViewportHandler := handlers.NewGraphViewportHandler(s.infra.GormDB, s.pool)
	api.POST("/graph/viewport/:project_id", graphViewportHandler.GetViewportGraph)
	api.GET("/graph/viewport/:project_id/bounds", graphViewportHandler.GetViewportBounds)
}

func (s *Server) registerGraphStreamRoutes(api *echo.Group) {
	graphStreamHandler := handlers.NewGraphStreamHandler(s.infra.GormDB, s.pool)
	api.POST("/projects/:project_id/graph/stream", graphStreamHandler.StreamGraphIncremental)
	api.POST("/projects/:project_id/graph/stream/prefetch", graphStreamHandler.StreamGraphPrefetch)
	api.GET("/projects/:project_id/graph/stream/stats", graphStreamHandler.GetStreamStats)
}

func (s *Server) registerSearchRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	searchService := services.NewSearchService(
		s.searchEngine,
		s.searchIndexer,
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
	)
	searchHandler := handlers.NewSearchHandler(searchService)
	api.POST("/search", searchHandler.Search)
	api.GET("/search", searchHandler.SearchGet)
	api.GET("/search/suggest", searchHandler.Suggest)
	api.POST("/search/index/:id", searchHandler.IndexItem)
	api.POST("/search/batch-index", searchHandler.BatchIndex)
	api.POST("/search/reindex", searchHandler.ReindexAll)
	api.GET("/search/stats", searchHandler.IndexStats)
	api.GET("/search/health", searchHandler.SearchHealth)
	api.DELETE("/search/index/:id", searchHandler.DeleteIndex)
}

func (s *Server) registerNotificationRoutes(protected *echo.Group, authProvider interface{}) {
	if protected == nil {
		return
	}

	ap, ok := authProvider.(auth.Provider)
	if !ok || ap == nil {
		slog.Info("⚠️  Notification handler not registered: auth provider not configured")
		return
	}

	notificationService := s.serviceContainer.NotificationService()
	notificationHandler := handlers.NewNotificationHandler(notificationService, ap)
	protected.GET("/notifications", notificationHandler.ListNotifications)
	protected.POST("/notifications/:id/read", notificationHandler.MarkAsRead)
	protected.POST("/notifications/read-all", notificationHandler.MarkAllAsRead)
	protected.DELETE("/notifications/:id", notificationHandler.DeleteNotification)
	protected.GET("/notifications/stream", notificationHandler.StreamNotifications)
	protected.POST("/notifications", notificationHandler.CreateNotification)
}

func (s *Server) registerEquivalenceRoutes(api *echo.Group) {
	equivalenceRepo := equivalence.NewPgxRepository(s.pool)
	equivalenceService := equivalence.NewService(equivalenceRepo, nil)
	equivalenceHandler := equivalence.NewHandler(equivalenceService)
	equivalenceHandler.RegisterRoutes(api)
}

func (s *Server) registerJourneyRoutes(api *echo.Group) {
	itemRepo := repository.NewItemRepository(s.infra.GormDB)
	linkRepo := repository.NewLinkRepository(s.infra.GormDB)
	journeyRepo := journey.NewJourneyRepository(s.infra.GormDB)
	journeyHandler := journey.NewHandler(
		s.pool,
		itemRepo,
		linkRepo,
		journeyRepo,
		&journey.DetectionConfig{
			MinPathLength:       journeyMinPathLength,
			MaxPathLength:       journeyMaxPathLength,
			MinFrequency:        journeyMinFrequency,
			MinScore:            journeyMinScore,
			AllowCycles:         false,
			GroupSimilar:        true,
			SimilarityThreshold: journeySimilarityThreshold,
		},
	)
	journeyHandler.RegisterRoutes(api)
}

func (s *Server) registerDocRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	docHandler := handlers.NewDocIndexHandler(
		s.pool,
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
		&handlers.EchoBinder{},
	)
	api.POST("/docs", docHandler.IndexDocumentation)
	api.GET("/docs", docHandler.ListDocumentation)
	api.GET("/docs/:id", docHandler.GetDocumentation)
	api.PUT("/docs/:id", docHandler.UpdateDocumentation)
	api.DELETE("/docs/:id", docHandler.DeleteDocumentation)
	api.GET("/docs/search", docHandler.SearchDocumentation)
}

func (s *Server) registerTemporalRoutes(api *echo.Group) {
	servicesBranchRepo := services.NewBranchRepository(s.pool)
	servicesVersionRepo := services.NewVersionRepository(s.pool)
	servicesItemVersionRepo := services.NewItemVersionRepository(s.pool)
	servicesAltRepo := services.NewAlternativeRepository(s.pool)
	servicesMergeRepo := services.NewMergeRepository(s.pool)

	branchRepo := &branchRepoAdapter{repo: servicesBranchRepo}
	versionRepo := &versionRepoAdapter{repo: servicesVersionRepo}
	itemVersionRepo := &itemVersionRepoAdapter{repo: servicesItemVersionRepo}
	altRepo := &altRepoAdapter{repo: servicesAltRepo}
	mergeRepo := &mergeRepoAdapter{repo: servicesMergeRepo}

	temporalService := services.NewTemporalService(
		branchRepo,
		versionRepo,
		itemVersionRepo,
		altRepo,
		mergeRepo,
		nil,
		s.redisClient,
	)
	if temporalService == nil {
		return
	}

	s.infra.TemporalService = temporalService
	temporalHandler := handlers.NewTemporalHandler(temporalService)
	api.GET("/projects/:projectId/branches", temporalHandler.ListBranches)
	api.POST("/projects/:projectId/branches", temporalHandler.CreateBranch)
	api.GET("/branches/:branchId", temporalHandler.GetBranch)
	api.PUT("/branches/:branchId", temporalHandler.UpdateBranch)
	api.DELETE("/branches/:branchId", temporalHandler.DeleteBranch)
	api.GET("/branches/:branchId/versions", temporalHandler.ListVersions)
	api.POST("/branches/:branchId/versions", temporalHandler.CreateVersion)
	api.GET("/versions/:versionId", temporalHandler.GetVersion)
	api.POST("/versions/:versionId/approve", temporalHandler.ApproveVersion)
	api.POST("/versions/:versionId/reject", temporalHandler.RejectVersion)
	api.GET("/items/:itemId/versions/:versionId", temporalHandler.GetItemVersion)
	api.GET("/items/:itemId/version-history", temporalHandler.GetItemVersionHistory)
	api.POST("/items/:itemId/restore", temporalHandler.RestoreItemVersion)
	api.GET("/items/:itemId/alternatives", temporalHandler.ListAlternatives)
	api.POST("/items/:itemId/alternatives", temporalHandler.CreateAlternative)
	api.POST("/alternatives/:altId/select", temporalHandler.SelectAlternative)
	api.GET("/projects/:projectId/merge-requests", temporalHandler.ListMergeRequests)
	api.POST("/projects/:projectId/merge-requests", temporalHandler.CreateMergeRequest)
	api.GET("/merge-requests/:mrId", temporalHandler.GetMergeRequest)
	api.GET("/merge-requests/:mrId/diff", temporalHandler.GetMergeDiff)
	api.POST("/merge-requests/:mrId/merge", temporalHandler.MergeBranches)
	api.GET("/versions/:versionAId/compare/:versionBId", temporalHandler.CompareVersions)
}

func (s *Server) registerCodeIndexRoutes(api *echo.Group) {
	codeEntityRepo := repository.NewCodeEntityRepository(s.infra.GormDB)
	codeRelationshipRepo := repository.NewCodeEntityRelationshipRepository(s.infra.GormDB)
	codeIndexService := services.NewCodeIndexServiceImpl(
		codeEntityRepo,
		codeRelationshipRepo,
		s.redisCache,
	)
	codeIndexHandler := handlers.NewCodeIndexHandler(
		codeIndexService,
		&handlers.EchoBinder{},
	)
	api.POST("/code/index", codeIndexHandler.IndexCode)
	api.GET("/code/entities", codeIndexHandler.ListEntities)
	api.GET("/code/entities/:id", codeIndexHandler.GetEntity)
	api.PUT("/code/entities/:id", codeIndexHandler.UpdateEntity)
	api.DELETE("/code/entities/:id", codeIndexHandler.DeleteEntity)
	api.POST("/code/search", codeIndexHandler.SearchEntities)
	api.GET("/code/search", codeIndexHandler.SearchEntities)
	api.POST("/code/reindex", codeIndexHandler.Reindex)
	api.POST("/code/batch-index", codeIndexHandler.BatchIndexCode)
	api.GET("/code/stats", codeIndexHandler.GetStats)
}

func (s *Server) registerProgressRoutes(api *echo.Group) {
	progressRepo := repository.NewProgressRepository(s.pool)
	milestoneService := progress.NewMilestoneService(progressRepo, nil)
	sprintService := progress.NewSprintService(progressRepo, nil)
	metricsService := progress.NewMetricsService(nil)
	snapshotService := progress.NewSnapshotService(progressRepo, metricsService, nil)
	progressHandler := progress.NewHandler(
		milestoneService,
		sprintService,
		metricsService,
		snapshotService,
	)
	api.GET("/milestones", s.wrapMuxHandler(progressHandler.ListMilestones))
	api.POST("/milestones", s.wrapMuxHandler(progressHandler.CreateMilestone))
	api.GET("/milestones/:id", s.wrapMuxHandler(progressHandler.GetMilestone))
	api.PUT("/milestones/:id", s.wrapMuxHandler(progressHandler.UpdateMilestone))
	api.DELETE("/milestones/:id", s.wrapMuxHandler(progressHandler.DeleteMilestone))
	api.GET("/milestones/:id/progress", s.wrapMuxHandler(progressHandler.GetMilestoneProgress))
	api.POST("/milestones/:id/health", s.wrapMuxHandler(progressHandler.UpdateMilestoneHealth))
	api.POST("/milestones/:id/items/:itemId", s.wrapMuxHandler(progressHandler.AddItemToMilestone))
	api.DELETE("/milestones/:id/items/:itemId", s.wrapMuxHandler(progressHandler.RemoveItemFromMilestone))
	api.GET("/sprints", s.wrapMuxHandler(progressHandler.ListSprints))
	api.POST("/sprints", s.wrapMuxHandler(progressHandler.CreateSprint))
	api.GET("/sprints/:id", s.wrapMuxHandler(progressHandler.GetSprint))
	api.PUT("/sprints/:id", s.wrapMuxHandler(progressHandler.UpdateSprint))
	api.DELETE("/sprints/:id", s.wrapMuxHandler(progressHandler.DeleteSprint))
	api.POST("/sprints/:id/close", s.wrapMuxHandler(progressHandler.CloseSprint))
	api.POST("/sprints/:id/burndown", s.wrapMuxHandler(progressHandler.RecordBurndown))
	api.POST("/sprints/:id/health", s.wrapMuxHandler(progressHandler.UpdateSprintHealth))
	api.POST("/sprints/:id/items/:itemId", s.wrapMuxHandler(progressHandler.AddItemToSprint))
	api.DELETE("/sprints/:id/items/:itemId", s.wrapMuxHandler(progressHandler.RemoveItemFromSprint))
	api.GET("/metrics", s.wrapMuxHandler(progressHandler.GetProjectMetrics))
	api.GET("/metrics/velocity", s.wrapMuxHandler(progressHandler.GetVelocity))
	api.GET("/metrics/velocity/history", s.wrapMuxHandler(progressHandler.GetVelocityHistory))
	api.GET("/metrics/cycle-time", s.wrapMuxHandler(progressHandler.GetCycleTime))
	api.GET("/snapshots", s.wrapMuxHandler(progressHandler.ListSnapshots))
	api.POST("/snapshots", s.wrapMuxHandler(progressHandler.CreateSnapshot))
	api.GET("/snapshots/:id", s.wrapMuxHandler(progressHandler.GetSnapshot))
}

func (s *Server) registerTraceabilityRoutes(api *echo.Group, authProvider, realtimeBroadcaster interface{}) {
	traceabilityHandler := handlers.NewTraceabilityHandler(
		s.pool,
		s.redisCache,
		s.eventPublisher,
		realtimeBroadcaster,
		authProvider,
	)
	api.GET("/traceability/matrix/:project_id", traceabilityHandler.GenerateMatrix)
	api.GET("/traceability/coverage/:project_id", traceabilityHandler.GetCoverage)
	api.GET("/traceability/gaps/:project_id", traceabilityHandler.GetGapAnalysis)
	api.GET("/traceability/items/:item_id", traceabilityHandler.GetItemTraceability)
	api.GET("/traceability/validate/:project_id", traceabilityHandler.ValidateCompleteness)
	api.GET("/traceability/impact/:item_id", traceabilityHandler.GetChangeImpact)
}

func (s *Server) registerStorageRoutes(api *echo.Group) {
	if s.s3Storage == nil {
		return
	}

	storageHandler := handlers.NewStorageHandler(s.s3Storage)
	api.POST("/storage/upload", storageHandler.Upload)
	api.POST("/storage/upload-with-thumbnail", storageHandler.UploadWithThumbnail)
	api.GET("/storage/download", storageHandler.Download)
	api.DELETE("/storage/:key", storageHandler.Delete)
	api.GET("/storage/presigned/:key", storageHandler.GetPresignedURL)
	api.POST("/storage/presigned-upload", storageHandler.GenerateUploadPresignedURL)
	api.GET("/storage/info", storageHandler.GetFileInfo)
}

func (s *Server) registerDashboardRoutes(api *echo.Group) {
	dashboardHandler := handlers.NewDashboardHandler(s.infra.GormDB)
	api.GET("/dashboard/summary", dashboardHandler.GetDashboardSummary)
}

func (s *Server) registerDelegationRoutes(api *echo.Group) {
	if ai := s.serviceContainer.AIClient(); ai != nil {
		handlers.RegisterAIRoutes(api, ai)
	}
	if spec := s.serviceContainer.SpecAnalyticsClient(); spec != nil {
		handlers.RegisterSpecAnalyticsRoutes(api, spec)
	}
	if exec := s.serviceContainer.ExecutionClient(); exec != nil {
		handlers.RegisterExecutionRoutes(api, exec, s.eventPublisher)
	}
	if wf := s.serviceContainer.WorkflowClient(); wf != nil {
		handlers.RegisterWorkflowRoutes(api, wf, s.eventPublisher)
	}
	if chaos := s.serviceContainer.ChaosClient(); chaos != nil {
		handlers.RegisterChaosRoutes(api, chaos)
	}
}
