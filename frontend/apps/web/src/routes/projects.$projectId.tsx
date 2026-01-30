import {
	createFileRoute,
	useParams,
	Outlet,
	useLocation,
} from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { ErrorBoundary } from "@/components/layout/ErrorBoundary";

const ProjectDetailView = lazy(() =>
	import("@/views/ProjectDetailView").then((m) => ({
		default: m.ProjectDetailView,
	})),
);

export const Route = createFileRoute("/projects/$projectId")({
	component: ProjectDetailComponent,
	loader: async ({ params }: { params: { projectId: string } }) => {
		// ProjectDetailView fetches its own data
		// Don't throw errors here - let ProjectDetailView handle them
		return { projectId: params.projectId };
	},
	errorComponent: ErrorComponent,
});

function ProjectDetailComponent() {
	const params = Route.useParams();
	const location = useLocation();

	// Check if we are deeper than the project root (i.e. showing a child route)
	const currentPath = location.pathname.replace(/\/$/, "");
	const rootPath = `/projects/${params.projectId}`;
	const isChildRoute = currentPath !== rootPath;

	return (
		<ErrorBoundary>
			{isChildRoute ? (
				<Outlet />
			) : (
				<Suspense
					fallback={
						<div className="flex items-center justify-center h-64">
							Loading project...
						</div>
					}
				>
					<ProjectDetailView />
				</Suspense>
			)}
		</ErrorBoundary>
	);
}

function ErrorComponent({ error }: { error?: Error }) {
	const { projectId } = useParams({ strict: false });
	return (
		<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
			<h1 className="text-2xl font-bold text-destructive mb-4">
				Project Not Found
			</h1>
			<p className="text-muted-foreground mb-6">
				The project you're looking for doesn't exist or you don't have access.
			</p>
			{error && (
				<p className="text-sm text-muted-foreground mb-4">
					Error: {error.message}
				</p>
			)}
			{projectId && (
				<p className="text-xs text-muted-foreground mb-4">
					Project ID: {projectId}
				</p>
			)}
			<button
				onClick={() => window.history.back()}
				className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
			>
				Go Back
			</button>
		</div>
	);
}
