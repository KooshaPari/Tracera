/**
 * Create GitHub repository modal component.
 */

import { Input } from "@tracertm/ui";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@tracertm/ui/components/Dialog";
import { Label } from "@tracertm/ui/components/Label";
import { Textarea } from "@tracertm/ui/components/Textarea";
import { Github, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import type { GitHubAppInstallation } from "@/api/github";
import { Button } from "@/components/ui/enterprise-button";
import { useCreateGitHubRepo } from "@/hooks/useGitHub";
import type { ApiErrorResponse } from "@/types";

export interface CreateRepoModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	installation: GitHubAppInstallation;
	accountId: string;
	onSuccess?: (repo: { id: string; full_name: string; name: string }) => void;
}

export function CreateRepoModal({
	open,
	onOpenChange,
	installation,
	accountId,
	onSuccess,
}: CreateRepoModalProps) {
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [isPrivate, setIsPrivate] = useState(false);

	const createRepo = useCreateGitHubRepo();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!name.trim()) {
			toast.error("Repository name is required");
			return;
		}

		try {
			const trimmedDescription = description.trim();
			const orgValue =
				installation.target_type === "Organization"
					? installation.account_login
					: undefined;
			const repo = await createRepo.mutateAsync({
				installation_id: installation.id,
				account_id: accountId,
				name: name.trim(),
				...(trimmedDescription ? { description: trimmedDescription } : {}),
				private: isPrivate,
				...(orgValue ? { org: orgValue } : {}),
			});

			toast.success(`Repository "${repo.full_name}" created successfully`);
			onSuccess?.(repo);
			onOpenChange(false);

			// Reset form
			setName("");
			setDescription("");
			setIsPrivate(false);
		} catch (error) {
			const message =
				error instanceof Error
					? error.message
					: (error &&
							typeof error === "object" &&
							"message" in error &&
							typeof (error as ApiErrorResponse).message === "string"
						? (error as ApiErrorResponse).message
						: "Failed to create repository");
			toast.error(message);
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-[500px]">
				<DialogHeader>
					<DialogTitle className="flex items-center gap-2">
						<Github className="h-5 w-5" />
						Create New Repository
					</DialogTitle>
					<DialogDescription>
						Create a new repository in {installation.account_login}
					</DialogDescription>
				</DialogHeader>

				<form onSubmit={handleSubmit}>
					<div className="space-y-4 py-4">
						<div className="space-y-2">
							<Label htmlFor="repo-name">Repository Name *</Label>
							<Input
								id="repo-name"
								placeholder="my-awesome-repo"
								value={name}
								onChange={(e) => setName(e.target.value)}
								disabled={createRepo.isPending}
								pattern="[a-zA-Z0-9._-]+"
								title="Repository name can only contain letters, numbers, dots, hyphens, and underscores"
							/>
							<p className="text-xs text-muted-foreground">
								Repository name can only contain letters, numbers, dots,
								hyphens, and underscores
							</p>
						</div>

						<div className="space-y-2">
							<Label htmlFor="repo-description">Description</Label>
							<Textarea
								id="repo-description"
								placeholder="A short description of your repository"
								value={description}
								onChange={(e) => setDescription(e.target.value)}
								disabled={createRepo.isPending}
								rows={3}
							/>
						</div>

						<div className="flex items-center space-x-2">
							<input
								type="checkbox"
								id="repo-private"
								checked={isPrivate}
								onChange={(e) => setIsPrivate(e.target.checked)}
								disabled={createRepo.isPending}
								className="h-4 w-4 rounded border-gray-300"
							/>
							<Label htmlFor="repo-private" className="cursor-pointer">
								Make this repository private
							</Label>
						</div>
					</div>

					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
							disabled={createRepo.isPending}
						>
							Cancel
						</Button>
						<Button
							type="submit"
							disabled={createRepo.isPending || !name.trim()}
						>
							{createRepo.isPending && (
								<Loader2 className="mr-2 h-4 w-4 animate-spin" />
							)}
							Create Repository
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
