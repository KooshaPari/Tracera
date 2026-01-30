/**
 * GitHub App installation component.
 */

import { useState } from "react";
import { Github, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/enterprise-button";
import { Card } from "@tracertm/ui";
import { Badge } from "@tracertm/ui";
import {
	useGitHubAppInstallUrl,
	useGitHubAppInstallations,
	useDeleteGitHubAppInstallation,
} from "@/hooks/useGitHub";
import { toast } from "sonner";
import { CreateRepoModal } from "./CreateRepoModal";
import { RepoSearchCombobox } from "./RepoSearchCombobox";
import type { GitHubRepo } from "@/api/github";

export interface GitHubAppInstallProps {
	accountId: string;
	onRepoSelect?: (repo: GitHubRepo | null) => void;
	selectedRepo?: GitHubRepo | null;
}

export function GitHubAppInstall({
	accountId,
	onRepoSelect,
	selectedRepo,
}: GitHubAppInstallProps) {
	const [createRepoOpen, setCreateRepoOpen] = useState(false);
	const [_selectedInstallation, setSelectedInstallation] = useState<
		string | null
	>(null);

	const { data: installUrlData, isLoading: installUrlLoading } =
		useGitHubAppInstallUrl(accountId);
	const { data: installationsData, isLoading: _installationsLoading } =
		useGitHubAppInstallations(accountId);
	const deleteInstallation = useDeleteGitHubAppInstallation();

	const installations = installationsData?.installations || [];

	const handleInstall = () => {
		if (installUrlData?.install_url) {
			window.location.href = installUrlData.install_url;
		}
	};

	const handleUninstall = async (installationId: string) => {
		if (
			!confirm(
				"Are you sure you want to uninstall this GitHub App installation?",
			)
		) {
			return;
		}

		try {
			await deleteInstallation.mutateAsync(installationId);
			toast.success("GitHub App installation removed");
		} catch (error: any) {
			toast.error(error.message || "Failed to remove installation");
		}
	};

	const activeInstallation = installations.find((inst) => !inst.suspended_at);
	const installationForCreate = activeInstallation || installations[0];

	return (
		<div className="space-y-4">
			{/* Installation Status */}
			{installations.length === 0 ? (
				<Card className="p-6">
					<div className="flex items-center justify-between">
						<div>
							<h3 className="text-lg font-semibold mb-2">
								GitHub App Installation
							</h3>
							<p className="text-sm text-muted-foreground mb-4">
								Install the GitHub App to access repositories and create new
								ones.
							</p>
						</div>
						<Button
							onClick={handleInstall}
							disabled={installUrlLoading}
							className="gap-2"
						>
							<Github className="h-4 w-4" />
							{installUrlLoading ? "Loading..." : "Install GitHub App"}
						</Button>
					</div>
				</Card>
			) : (
				<div className="space-y-4">
					{/* Installed Installations */}
					{installations.map((installation) => (
						<Card key={installation.id} className="p-4">
							<div className="flex items-start justify-between">
								<div className="flex-1">
									<div className="flex items-center gap-2 mb-2">
										<Github className="h-5 w-5" />
										<h3 className="font-semibold">
											{installation.account_login}
										</h3>
										<Badge
											variant={
												installation.suspended_at ? "destructive" : "default"
											}
										>
											{installation.suspended_at ? "Suspended" : "Active"}
										</Badge>
										<Badge variant="outline">{installation.target_type}</Badge>
									</div>
									<p className="text-sm text-muted-foreground">
										Repository selection: {installation.repository_selection}
									</p>
								</div>
								<div className="flex items-center gap-2">
									<Button
										variant="ghost"
										size="sm"
										onClick={() => handleUninstall(installation.id)}
										disabled={deleteInstallation.isPending}
									>
										<Trash2 className="h-4 w-4" />
									</Button>
								</div>
							</div>
						</Card>
					))}

					{/* Repository Search/Select */}
					{activeInstallation && (
						<Card className="p-4">
							<h3 className="font-semibold mb-4">Select Repository</h3>
							<RepoSearchCombobox
								accountId={accountId}
								installationId={activeInstallation.id}
								value={selectedRepo || null}
								{...(onRepoSelect ? { onSelect: onRepoSelect } : {})}
								onCreateRepo={() => {
									setSelectedInstallation(activeInstallation.id);
									setCreateRepoOpen(true);
								}}
								placeholder="Search or select a repository..."
							/>
						</Card>
					)}

					{/* Create Repo Modal */}
					{installationForCreate && (
						<CreateRepoModal
							open={createRepoOpen}
							onOpenChange={setCreateRepoOpen}
							installation={installationForCreate}
							accountId={accountId}
							onSuccess={(repo) => {
								onRepoSelect?.(repo);
							}}
						/>
					)}
				</div>
			)}
		</div>
	);
}
