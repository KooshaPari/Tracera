/**
 * Repository search and select combobox component.
 */

import type { GitHubRepo } from "@/api/github";
import {
	Github,
	Loader2,
	Plus,
	Search,
} from "lucide-react";
import { Button } from "@/components/ui/enterprise-button";
import { useGitHubRepos } from "@/hooks/useGitHub";
import { cn } from "@/lib/utils";
import { Input } from "@tracertm/ui";
import { useCallback, useEffect, useMemo, useState } from "react";

const DEBOUNCE_MS = 300;

export interface RepoSearchComboboxProps {
	accountId?: string;
	installationId?: string;
	credentialId?: string;
	value?: GitHubRepo | null;
	onSelect?: (repo: GitHubRepo | null) => void;
	onCreateRepo?: () => void;
	className?: string;
	placeholder?: string;
	disabled?: boolean;
}

export const RepoSearchCombobox = function RepoSearchCombobox({
	accountId,
	installationId,
	credentialId,
	value,
	onSelect,
	onCreateRepo,
	className,
	placeholder = "Search repositories...",
	disabled = false,
}: RepoSearchComboboxProps) {
	const [searchQuery, setSearchQuery] = useState("");
	const [isOpen, setIsOpen] = useState(false);
	const [debouncedSearch, setDebouncedSearch] = useState("");

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearch(searchQuery);
		}, DEBOUNCE_MS);
		return () => clearTimeout(timer);
	}, [searchQuery]);

	const { data, isLoading } = useGitHubRepos({
		...(accountId ? { accountId } : {}),
		...(installationId ? { installationId } : {}),
		...(credentialId ? { credentialId } : {}),
		...(debouncedSearch ? { search: debouncedSearch } : {}),
		perPage: 20,
	});

	const repos = useMemo(() => data?.repos ?? [], [data]);

	const handleSelect = useCallback(
		(repo: GitHubRepo) => {
			onSelect?.(repo);
			setIsOpen(false);
			setSearchQuery("");
		},
		[onSelect],
	);

	const handleClear = useCallback(() => {
		onSelect?.(null);
		setSearchQuery("");
	}, [onSelect]);

	const handleSearchChange = useCallback(
		(e: React.ChangeEvent<HTMLInputElement>) => {
			setSearchQuery(e.target.value);
			setIsOpen(true);
		},
		[],
	);
	const handleFocus = useCallback(() => setIsOpen(true), []);
	const handleClose = useCallback(() => setIsOpen(false), []);

	const handleClearKeyDown = useCallback(
		(e: React.KeyboardEvent) => {
			if (e.key === "Enter" || e.key === " ") {
				e.preventDefault();
				handleClear();
			}
		},
		[handleClear],
	);

	const handleRepoClick = useCallback(
		(e: React.MouseEvent<HTMLButtonElement>) => {
			const id = Number(
				(e.currentTarget as HTMLButtonElement).dataset["repoId"],
			);
			const repo = repos.find((r: GitHubRepo) => r.id === id);
			if (repo) handleSelect(repo);
		},
		[repos, handleSelect],
	);

	function renderListContent() {
		if (isLoading) {
			return (
				<div className="flex items-center justify-center p-4">
					<Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
				</div>
			);
		}
		if (repos.length === 0) {
			return (
				<div className="p-4 text-sm text-muted-foreground text-center">
					{searchQuery
						? "No repositories found"
						: "No repositories available"}
				</div>
			);
		}
		return (
			<div className="p-1">
				{repos.map((repo: GitHubRepo) => (
					<button
						key={repo.id}
						data-repo-id={repo.id}
						onClick={handleRepoClick}
						className={cn(
							"w-full text-left px-3 py-2 rounded-sm hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer",
							value?.id === repo.id && "bg-accent",
						)}
						type="button"
					>
						<div className="flex items-center gap-2">
							<Github className="h-4 w-4 text-muted-foreground shrink-0" />
							<div className="flex-1 min-w-0">
								<div className="font-medium text-sm truncate">
									{repo.full_name}
								</div>
								{repo.description && (
									<div className="text-xs text-muted-foreground truncate">
										{repo.description}
									</div>
								)}
							</div>
							{repo.private && (
								<span className="text-xs text-muted-foreground shrink-0">
									Private
								</span>
							)}
						</div>
					</button>
				))}
			</div>
		);
	}

	return (
		<div className={cn("relative w-full", className)}>
			<div className="relative">
				<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
				<Input
					type="text"
					placeholder={placeholder}
					value={searchQuery || value?.full_name || ""}
					onChange={handleSearchChange}
					onFocus={handleFocus}
					disabled={disabled}
					className="pl-9 pr-20"
				/>
				{value && (
					<button
						type="button"
						onClick={handleClear}
						onKeyDown={handleClearKeyDown}
						className="absolute right-10 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded p-1 transition-colors cursor-pointer"
						aria-label="Clear selection"
					>
						×
					</button>
				)}
				{onCreateRepo && (
					<Button
						size="sm"
						variant="ghost"
						onClick={onCreateRepo}
						className="absolute right-1 top-1/2 -translate-y-1/2 h-7 px-2"
						type="button"
					>
						<Plus className="h-4 w-4" />
					</Button>
				)}
			</div>

			{isOpen && (searchQuery || repos.length > 0) && (
				<div className="absolute z-50 w-full mt-1 bg-popover border border-border rounded-md shadow-lg max-h-60 overflow-auto">
					{renderListContent()}
				</div>
			)}

			{isOpen && (
				<div
					className="fixed inset-0 z-40"
					onClick={handleClose}
					aria-hidden
				/>
			)}
		</div>
	);
};
