/**
 * React Hook for Real-time NATS Event Updates via WebSocket
 *
 * Automatically subscribes to project-specific events and invalidates
 * React Query cache for real-time UI updates.
 */

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { realtimeClient } from "../lib/websocket";
import { logger } from '@/lib/logger';

export interface RealtimeConfig {
	projectId?: string;
	onEvent?: (event: any) => void;
	enableToasts?: boolean;
}

export function useRealtime(config: RealtimeConfig = {}) {
	const { projectId, onEvent } = config;
	// const queryClient = useQueryClient();
	const [isConnected, setIsConnected] = useState(false);

	useEffect(() => {
		// Get auth token from storage or context
		// TODO: Replace with your actual auth token retrieval
		const token = localStorage.getItem("auth_token") || "";

		if (!token) {
			logger.warn("No auth token found, skipping WebSocket connection");
			return;
		}

		// Connect to WebSocket with token and optional project ID
		realtimeClient.connect(token, projectId);

		// Monitor connection status
		const checkConnection = setInterval(() => {
			setIsConnected(realtimeClient.isConnected());
		}, 1000);

		// Cleanup
		return () => {
			clearInterval(checkConnection);
			realtimeClient.disconnect();
		};
	}, [projectId]);

	// Listen for all events and call custom handler
	useEffect(() => {
		if (!onEvent) return;

		const unsubscribe = realtimeClient.on("*", onEvent);
		return unsubscribe;
	}, [onEvent]);

	return { isConnected };
}

export function useRealtimeUpdates(projectId?: string) {
	const queryClient = useQueryClient();

	useEffect(() => {
		if (!projectId) return;

		// Get auth token
		const token = localStorage.getItem("auth_token") || "";
		if (!token) return;

		// Connect to WebSocket
		realtimeClient.connect(token, projectId);

		// Subscribe to item events
		const unsubItem = realtimeClient.on("item.created", (event) => {
			logger.info("Item created:", event);
			void queryClient.invalidateQueries({ queryKey: ["items", projectId] });

			toast.success(`New item created: ${event.data['title'] || event.entity_id}`);
		});

		const unsubItemUpdate = realtimeClient.on("item.updated", (event) => {
			logger.info("Item updated:", event);
			void queryClient.invalidateQueries({ queryKey: ["items", projectId] });
			void queryClient.invalidateQueries({ queryKey: ["item", event.entity_id] });

			toast.info(`Item updated: ${event.data['title'] || event.entity_id}`);
		});

		const unsubItemDelete = realtimeClient.on("item.deleted", (event) => {
			logger.info("Item deleted:", event);
			void queryClient.invalidateQueries({ queryKey: ["items", projectId] });

			toast.info(`Item deleted: ${event.entity_id}`);
		});

		// Subscribe to link events
		const unsubLink = realtimeClient.on("link.created", (event) => {
			logger.info("Link created:", event);
			void queryClient.invalidateQueries({ queryKey: ["links", projectId] });

			toast.success("New link created");
		});

		const unsubLinkDelete = realtimeClient.on("link.deleted", (event) => {
			logger.info("Link deleted:", event);
			void queryClient.invalidateQueries({ queryKey: ["links", projectId] });

			toast.info("Link deleted");
		});

		// Subscribe to spec events (from Python backend)
		const unsubSpec = realtimeClient.on("spec.created", (event) => {
			logger.info("Spec created:", event);
			void queryClient.invalidateQueries({
				queryKey: ["specifications", projectId],
			});

			toast.success(`New specification created`);
		});

		const unsubSpecUpdate = realtimeClient.on("spec.updated", (event) => {
			logger.info("Spec updated:", event);
			void queryClient.invalidateQueries({
				queryKey: ["specifications", projectId],
			});
			void queryClient.invalidateQueries({
				queryKey: ["specification", event.entity_id],
			});

			toast.info(`Specification updated`);
		});

		// Subscribe to AI analysis events
		const unsubAI = realtimeClient.on("ai.analysis.complete", (event) => {
			logger.info("AI analysis complete:", event);
			void queryClient.invalidateQueries({
				queryKey: ["specification", event.data['spec_id']],
			});

			toast.success(
				`AI analysis complete for specification ${event.data['spec_id']}`,
			);
		});

		// Subscribe to execution events
		const unsubExecution = realtimeClient.on("execution.completed", (event) => {
			logger.info("Execution completed:", event);
			void queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
			void queryClient.invalidateQueries({
				queryKey: ["execution", event.entity_id],
			});

			toast.success(`Execution ${event.entity_id} completed`);
		});

		const unsubExecutionFailed = realtimeClient.on(
			"execution.failed",
			(event) => {
				logger.info("Execution failed:", event);
				void queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
				void queryClient.invalidateQueries({
					queryKey: ["execution", event.entity_id],
				});

				toast.error(`Execution ${event.entity_id} failed`);
			},
		);

		// Subscribe to workflow events
		const unsubWorkflow = realtimeClient.on("workflow.completed", (event) => {
			logger.info("Workflow completed:", event);
			void queryClient.invalidateQueries({ queryKey: ["workflows", projectId] });

			toast.success(`Workflow completed`);
		});

		// Subscribe to project events
		const unsubProject = realtimeClient.on("project.updated", (event) => {
			logger.info("Project updated:", event);
			void queryClient.invalidateQueries({ queryKey: ["project", projectId] });
			void queryClient.invalidateQueries({ queryKey: ["projects"] });

			toast.info("Project updated");
		});

		// Cleanup all subscriptions
		return () => {
			unsubItem();
			unsubItemUpdate();
			unsubItemDelete();
			unsubLink();
			unsubLinkDelete();
			unsubSpec();
			unsubSpecUpdate();
			unsubAI();
			unsubExecution();
			unsubExecutionFailed();
			unsubWorkflow();
			unsubProject();
			realtimeClient.disconnect();
		};
	}, [projectId, queryClient]);
}

export function useRealtimeEvent(
	eventType: string,
	callback: (event: any) => void,
) {
	useEffect(() => {
		const unsubscribe = realtimeClient.on(eventType, callback);
		return unsubscribe;
	}, [eventType, callback]);
}
