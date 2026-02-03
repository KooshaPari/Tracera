import { Link } from "@tanstack/react-router";
import {
	Input,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Activity,
	ArrowRight,
	ExternalLink,
	Layers,
	Link2,
	Network,
	Plus,
	Search,
	Trash2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { CardErrorFallback } from "@/lib/lazy-loading";
import { cn } from "@/lib/utils";
import { useItems } from "../hooks/useItems";
import { useDeleteLink, useLinks } from "../hooks/useLinks";

function buildItemLink(
	itemId: string,
	item?: {
		projectId?: string;
		project_id?: string;
		view?: string;
		view_type?: string;
	},
) {
	const projectId = item?.projectId || item?.project_id;
	const viewType = item?.view || item?.view_type || "feature";
	return projectId
		? `/projects/${projectId}/views/${String(viewType).toLowerCase()}/${itemId}`
		: "/projects";
}

export function LinksView() {
	const { data: linksData, isLoading: linksLoading, error } = useLinks();
	const { data: itemsData } = useItems();
	const deleteLink = useDeleteLink();

	const [searchQuery, setSearchQuery] = useState("");
	const [typeFilter, setTypeFilter] = useState("all");

	const links = linksData?.links ?? [];
	const items = itemsData?.items ?? [];

	const filteredLinks = useMemo(
		() =>
			links.filter((link) => {
				const matchesQuery =
					link.sourceId.toLowerCase().includes(searchQuery.toLowerCase()) ||
					link.targetId.toLowerCase().includes(searchQuery.toLowerCase()) ||
					link.type.toLowerCase().includes(searchQuery.toLowerCase());
				const matchesType = typeFilter === "all" || link.type === typeFilter;
				return matchesQuery && matchesType;
			}),
		[links, searchQuery, typeFilter],
	);

	const handleDelete = async (id: string) => {
		try {
			await deleteLink.mutateAsync(id);
			toast.success("Relationship link dissolved");
		} catch {
			toast.error("Failed to delete link");
		}
	};

	// Surface load failures to the user via toast
	useEffect(() => {
		if (error) {
			toast.error("Failed to load links", {
				action: {
					label: "Retry",
					onClick: () => globalThis.location.reload(),
				},
				description: error.message,
			});
		}
	}, [error]);

	if (linksLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<Skeleton className="h-12 w-full rounded-2xl" />
				<div className="space-y-4">
					{[1, 2, 3, 4, 5].map((i) => (
						<Skeleton key={i} className="h-20 w-full rounded-xl" />
					))}
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="p-6 max-w-md mx-auto">
				<CardErrorFallback
					title="Traceability interrupted"
					message="Failed to synchronize relationship graph."
					error={error}
					retry={() => globalThis.location.reload()}
					className="flex flex-col items-center justify-center text-center p-8 rounded-lg border border-destructive/20 bg-destructive/5"
				/>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1400px] mx-auto animate-in-fade-up">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Traceability Links
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Manage the semantic connections between project entities.
					</p>
				</div>
				<Button
					size="sm"
					className="gap-2 rounded-xl shadow-lg shadow-primary/20"
					onClick={() =>
						toast.info("Create a link by selecting source and target items")
					}
				>
					<Plus className="h-4 w-4" /> Create Connection
				</Button>
			</div>

			{/* Executive Summary */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-children">
				{[
					{
						color: "text-blue-500",
						icon: Network,
						label: "Total Connections",
						value: links.length,
					},
					{
						color: "text-green-500",
						icon: Activity,
						label: "Connection Density",
						value: `${items.length > 0 ? (links.length / items.length).toFixed(2) : 0}`,
					},
					{
						color: "text-orange-500",
						icon: Layers,
						label: "Orphan Nodes",
						value: items.filter(
							(i) =>
								!links.some((l) => l.sourceId === i.id || l.targetId === i.id),
						).length,
					},
				].map((s, i) => (
					<Card
						key={i}
						className="p-5 border-none bg-card/50 shadow-sm flex items-center justify-between group hover:bg-card hover:shadow-md active:scale-[0.99] transition-all duration-200 ease-out"
					>
						<div>
							<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								{s.label}
							</p>
							<p className="text-2xl font-black mt-1">{s.value}</p>
						</div>
						<div
							className={cn(
								"h-10 w-10 rounded-xl bg-muted flex items-center justify-center group-hover:scale-110 transition-transform",
								s.color,
							)}
						>
							<s.icon className="h-5 w-5" />
						</div>
					</Card>
				))}
			</div>

			{/* Filters */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[300px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search by ID or connection type..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<Select value={typeFilter} onValueChange={setTypeFilter}>
					<SelectTrigger className="w-[180px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors">
						<SelectValue placeholder="Link Type" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Types</SelectItem>
						{[...new Set(links.map((l) => l.type))].map((t) => (
							<SelectItem key={t} value={t}>
								{t}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</Card>

			{/* Links List */}
			<div className="space-y-3 stagger-children">
				{filteredLinks.length > 0 ? (
					filteredLinks.map((link) => {
						const sourceItem = items.find((i) => i.id === link.sourceId);
						const targetItem = items.find((i) => i.id === link.targetId);

						return (
							<Card
								key={link.id}
								className="p-4 border-none bg-card/50 hover:bg-card hover:shadow-md active:scale-[0.99] transition-all duration-200 ease-out group overflow-hidden relative"
							>
								<div className="flex flex-col md:flex-row md:items-center gap-6 relative z-10">
									{/* Source */}
									<Link
										to={buildItemLink(link.sourceId, sourceItem)}
										className="flex-1 min-w-0"
									>
										<div className="p-3 rounded-xl border bg-background/50 hover:border-primary/50 transition-colors group/node">
											<div className="flex items-center justify-between mb-1">
												<span className="text-[9px] font-black uppercase text-muted-foreground">
													Source
												</span>
												<ExternalLink className="h-3 w-3 opacity-0 group-hover/node:opacity-100 transition-opacity" />
											</div>
											<p className="text-sm font-bold truncate">
												{sourceItem?.title || link.sourceId}
											</p>
											<p className="text-[10px] font-mono text-primary truncate">
												{link.sourceId.slice(0, 8)}
											</p>
										</div>
									</Link>

									{/* Relationship Type */}
									<div className="flex flex-col items-center justify-center shrink-0">
										<Badge
											variant="secondary"
											className="px-3 py-1 font-black uppercase text-[10px] tracking-widest bg-primary/10 text-primary border-none"
										>
											{link.type}
										</Badge>
										<div className="flex items-center gap-1 mt-2 text-muted-foreground/30">
											<div className="h-px w-8 bg-current" />
											<ArrowRight className="h-4 w-4" />
											<div className="h-px w-8 bg-current" />
										</div>
									</div>

									{/* Target */}
									<Link
										to={buildItemLink(link.targetId, targetItem)}
										className="flex-1 min-w-0"
									>
										<div className="p-3 rounded-xl border bg-background/50 hover:border-primary/50 transition-colors group/node">
											<div className="flex items-center justify-between mb-1">
												<span className="text-[9px] font-black uppercase text-muted-foreground">
													Target
												</span>
												<ExternalLink className="h-3 w-3 opacity-0 group-hover/node:opacity-100 transition-opacity" />
											</div>
											<p className="text-sm font-bold truncate">
												{targetItem?.title || link.targetId}
											</p>
											<p className="text-[10px] font-mono text-primary truncate">
												{link.targetId.slice(0, 8)}
											</p>
										</div>
									</Link>

									{/* Actions */}
									<div className="flex justify-end pr-2">
										<Button
											variant="ghost"
											size="icon"
											onClick={() => handleDelete(link.id)}
											className="h-9 w-9 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10"
										>
											<Trash2 className="h-4 w-4" />
										</Button>
									</div>
								</div>

								{/* Background decoration */}
								<div className="absolute top-0 right-0 p-1 bg-primary/5 rounded-bl-xl text-[8px] font-black uppercase text-primary/40 opacity-0 group-hover:opacity-100 transition-opacity">
									ID: {link.id.slice(0, 6)}
								</div>
							</Card>
						);
					})
				) : (
					<div className="flex flex-col items-center justify-center py-20 text-muted-foreground/40">
						<Link2 className="h-16 w-16 mb-4 opacity-10" />
						<p className="text-xs font-black uppercase tracking-[0.2em]">
							No connections found
						</p>
					</div>
				)}
			</div>
		</div>
	);
}
