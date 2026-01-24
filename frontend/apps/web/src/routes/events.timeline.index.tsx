import { createFileRoute } from "@tanstack/react-router";
import { EventsTimelineView } from "@/views/EventsTimelineView";

export const Route = createFileRoute("/events/timeline/")({
	component: EventsTimelineComponent,
	loader: async () => {
		// EventsTimelineView fetches its own data
		return {};
	},
});

function EventsTimelineComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Events Timeline</h1>
					<p className="text-muted-foreground">
						Complete audit trail and project history with time-travel
						capabilities
					</p>
				</div>
			</div>

			<EventsTimelineView />
		</div>
	);
}
