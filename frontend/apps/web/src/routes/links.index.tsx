import { createFileRoute } from "@tanstack/react-router";
import { LinksView } from "@/views/LinksView";

export const Route = createFileRoute("/links/")({
	component: LinksComponent,
	loader: async () => {
		// LinksView fetches its own data
		return {};
	},
});

function LinksComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Relationship Links
					</h1>
					<p className="text-muted-foreground">
						Manage 60+ link types and relationships between project items
					</p>
				</div>
			</div>

			<LinksView />
		</div>
	);
}
