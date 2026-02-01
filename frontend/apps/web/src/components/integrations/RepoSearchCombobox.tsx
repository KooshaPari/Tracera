/**
 * Repository search and select combobox component.
 */

import { Input } from "@tracertm/ui";
import { Github, Loader2, Plus, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { GitHubRepo } from "@/api/github";
import { Button } from "@/components/ui/enterprise-button";
import { useGitHubRepos } from "@/hooks/useGitHub";
import { cn } from "@/lib/utils";

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

export function RepoSearchCombobox({
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

	// Debounce search query
	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearch(searchQuery);
		}, 300);
		return () => clearTimeout(timer);
	}, [searchQuery]);

	const { data, isLoading } = useGitHubRepos({
		...(accountId ? { accountId } : {}),
		...(installationId ? { installationId } : {}),
		...(credentialId ? { credentialId } : {}),
		...(debouncedSearch ? { search: debouncedSearch } : {}),
		perPage: 20,
	});

	const repos = useMemo(() => data?.repos || [], [data]);

	const handleSelect = (repo: GitHubRepo) => {
		onSelect?.(repo);
		setIsOpen(false);
		setSearchQuery("");
	};

	const handleClear = () => {
		onSelect?.(null);
		setSearchQuery("");
	};

	return (
		<div className={cn("relative w-full", className)}>
			<div className="relative">
				<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
				<Input
					type="text"
					placeholder={placeholder}
					value={searchQuery || value?.full_name || ""}
					onChange={(e) => {
						setSearchQuery(e.target.value);
						setIsOpen(true);
					}}
					onFocus={() => setIsOpen(true)}
					disabled={disabled}
					className="pl-9 pr-20"
				/>
				{value && (
					<button
						onClick={handleClear}
						className="absolute right-10 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded p-1 transition-colors cursor-pointer"
						type="button"
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
					{isLoading ? (
						<div className="flex items-center justify-center p-4">
							<Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
						</div>
					) : repos.length === 0 ? (
						<div className="p-4 text-sm text-muted-foreground text-center">
							{searchQuery
								? "No repositories found"
								: "No repositories available"}
						</div>
					) : (
						<div className="p-1">
							{repos.map((repo) => (
								<button
									key={repo.id}
									onClick={() => handleSelect(repo)}
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
					)}
				</div>
			)}

			{/* Click outside to close */}
			{isOpen && (
				<div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
			)}
		</div>
	);
}
