import { createFileRoute } from "@tanstack/react-router";
import { SettingsView } from "@/views/SettingsView";

export const Route = createFileRoute("/settings/")({
	component: SettingsComponent,
	loader: async () => {
		// SettingsView fetches its own data
		return {};
	},
});

function SettingsComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Settings</h1>
					<p className="text-muted-foreground">
						Configure your TraceRTM platform preferences and integrations
					</p>
				</div>
			</div>

			<SettingsView />
		</div>
	);
}
