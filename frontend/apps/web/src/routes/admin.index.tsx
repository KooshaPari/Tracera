import { requireAdmin } from "@/lib/route-guards";
import { createFileRoute } from "@tanstack/react-router";
import { Shield } from "lucide-react";

function AdminPage() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center gap-3">
				<Shield className="h-8 w-8 text-primary" aria-hidden />
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Admin Panel</h1>
					<p className="text-muted-foreground">
						System administration and platform settings
					</p>
				</div>
			</div>

			<div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
				<h2 className="text-lg font-semibold mb-2">System admin access</h2>
				<p className="text-sm text-muted-foreground">
					You are signed in as a system administrator. Admin-only features and
					full access to projects and resources are available.
				</p>
			</div>

			<div className="rounded-lg border bg-muted/50 p-6 text-muted-foreground text-sm">
				<p>
					Additional admin tools (e.g. user management, audit logs, feature
					flags) can be added here as needed.
				</p>
			</div>
		</div>
	);
}

export const Route = createFileRoute("/admin/")({
	beforeLoad: () => requireAdmin(),
	component: AdminPage,
});
