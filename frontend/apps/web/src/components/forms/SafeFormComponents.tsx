/**
 * Safe Form Components - Form components wrapped with error boundaries
 *
 * This file provides error-boundary-wrapped versions of critical form components
 * to prevent form errors from crashing the entire application.
 */

import { lazy, Suspense } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@tracertm/ui/components/Button";

// Lazy load form components for better code splitting
const CreateItemForm = lazy(() =>
	import("./CreateItemForm").then((m) => ({ default: m.CreateItemForm })),
);
const CreateProblemForm = lazy(() =>
	import("./CreateProblemForm").then((m) => ({ default: m.CreateProblemForm })),
);
const CreateProcessForm = lazy(() =>
	import("./CreateProcessForm").then((m) => ({ default: m.CreateProcessForm })),
);
const CreateTestCaseForm = lazy(() =>
	import("./CreateTestCaseForm").then((m) => ({ default: m.CreateTestCaseForm })),
);
const CreateProjectForm = lazy(() =>
	import("./CreateProjectForm").then((m) => ({ default: m.CreateProjectForm })),
);
const CreateLinkForm = lazy(() =>
	import("./CreateLinkForm").then((m) => ({ default: m.CreateLinkForm })),
);

// Loading fallback for form components
function FormLoadingFallback() {
	return (
		<div className="space-y-4 p-4">
			<Skeleton className="h-10 w-full" />
			<Skeleton className="h-32 w-full" />
			<Skeleton className="h-10 w-full" />
			<div className="flex gap-2 justify-end">
				<Skeleton className="h-10 w-24" />
				<Skeleton className="h-10 w-24" />
			</div>
		</div>
	);
}

// Error fallback for form components
function FormErrorFallback(error: Error, reset: () => void) {
	return (
		<div className="flex items-center justify-center min-h-[300px] border border-destructive/50 rounded-lg bg-destructive/5 p-6">
			<div className="max-w-md text-center space-y-4">
				<div className="flex justify-center">
					<AlertCircle className="h-12 w-12 text-destructive" />
				</div>
				<h3 className="text-lg font-semibold text-destructive">
					Form Error
				</h3>
				<p className="text-sm text-muted-foreground">
					{error.message || "Unable to load form"}
				</p>
				<div className="flex gap-2 justify-center">
					<Button variant="outline" onClick={reset}>
						Try Again
					</Button>
					<Button variant="ghost" onClick={() => window.location.reload()}>
						Reload Page
					</Button>
				</div>
			</div>
		</div>
	);
}

/**
 * Safe wrapper for CreateItemForm with error boundary and lazy loading
 */
export function SafeCreateItemForm(props: React.ComponentProps<typeof CreateItemForm>) {
	return (
		<ErrorBoundary name="CreateItemForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateItemForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for CreateProblemForm with error boundary and lazy loading
 */
export function SafeCreateProblemForm(props: React.ComponentProps<typeof CreateProblemForm>) {
	return (
		<ErrorBoundary name="CreateProblemForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateProblemForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for CreateProcessForm with error boundary and lazy loading
 */
export function SafeCreateProcessForm(props: React.ComponentProps<typeof CreateProcessForm>) {
	return (
		<ErrorBoundary name="CreateProcessForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateProcessForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for CreateTestCaseForm with error boundary and lazy loading
 */
export function SafeCreateTestCaseForm(props: React.ComponentProps<typeof CreateTestCaseForm>) {
	return (
		<ErrorBoundary name="CreateTestCaseForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateTestCaseForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for CreateProjectForm with error boundary and lazy loading
 */
export function SafeCreateProjectForm(props: React.ComponentProps<typeof CreateProjectForm>) {
	return (
		<ErrorBoundary name="CreateProjectForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateProjectForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for CreateLinkForm with error boundary and lazy loading
 */
export function SafeCreateLinkForm(props: React.ComponentProps<typeof CreateLinkForm>) {
	return (
		<ErrorBoundary name="CreateLinkForm" fallback={FormErrorFallback}>
			<Suspense fallback={<FormLoadingFallback />}>
				<CreateLinkForm {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}
