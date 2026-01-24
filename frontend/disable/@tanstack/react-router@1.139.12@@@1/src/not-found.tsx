import type { NotFoundError } from "@tanstack/router-core";
import { isNotFound } from "@tanstack/router-core";
import type * as React from "react";
import type { ErrorInfo } from "react";
import { CatchBoundary } from "./CatchBoundary";
import { useRouterState } from "./useRouterState";

export function CatchNotFound(props: {
	fallback?: (error: NotFoundError) => React.ReactElement;
	onCatch?: (error: Error, errorInfo: ErrorInfo) => void;
	children: React.ReactNode;
}) {
	// TODO: Some way for the user to programmatically reset the not-found boundary?
	const resetKey = useRouterState({
		select: (s) => `not-found-${s.location.pathname}-${s.status}`,
	});

	return (
		<CatchBoundary
			getResetKey={() => resetKey}
			onCatch={(error, errorInfo) => {
				if (isNotFound(error)) {
					props.onCatch?.(error, errorInfo);
				} else {
					throw error;
				}
			}}
			errorComponent={({ error }) => {
				if (isNotFound(error)) {
					return props.fallback?.(error);
				} else {
					throw error;
				}
			}}
		>
			{props.children}
		</CatchBoundary>
	);
}

export function DefaultGlobalNotFound() {
	return <p>Not Found</p>;
}
