import { createFileRoute } from "@tanstack/react-router";
import { SearchView } from "@/views/SearchView";

export const Route = createFileRoute("/search/")({
	component: SearchComponent,
	loader: async () => {
		// SearchView fetches its own data
		return {};
	},
});

function SearchComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Search Results</h1>
					<p className="text-muted-foreground">
						Enterprise search across all project items, code, and documentation
					</p>
				</div>
			</div>

			<SearchView />
		</div>
	);
}
