import { Link } from "@tanstack/react-router";
import type { Item } from "@tracertm/types";
import { Button, Separator } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	ArrowRight,
	Box,
	Command,
	Layers,
	Search as SearchIcon,
} from "lucide-react";
import { useState } from "react";
import { useSearch } from "../hooks/useSearch";

export function SearchView() {
	const [query, setQuery] = useState("");
	const [filters, setFilters] = useState({
		project: "",
		status: "",
		type: "",
	});

	const { results, isLoading } = useSearch({ q: query, ...filters });

	return (
		<div className="p-6 space-y-8 max-w-5xl mx-auto animate-in-fade-up">
			{/* Header */}
			<div className="flex flex-col items-center text-center space-y-4 mb-12">
				<div className="h-16 w-16 rounded-[2rem] bg-primary/10 flex items-center justify-center shadow-inner">
					<Command className="h-8 w-8 text-primary animate-pulse" />
				</div>
				<div>
					<h1 className="text-3xl font-black tracking-tight uppercase">
						Omni-Search
					</h1>
					<p className="text-muted-foreground font-medium max-w-lg mx-auto">
						Search the entire graph repository for nodes, projects, and metadata
						links.
					</p>
				</div>
			</div>

			{/* Search Control Bar */}
			<div className="relative group max-w-3xl mx-auto">
				<div className="absolute inset-0 bg-primary/20 blur-2xl group-focus-within:blur-3xl transition-all opacity-0 group-focus-within:opacity-100" />
				<Card className="relative p-2 border-none bg-card shadow-2xl rounded-[2.5rem] flex flex-col md:flex-row items-center gap-2 overflow-hidden ring-1 ring-border">
					<div className="relative flex-1 w-full">
						<SearchIcon className="absolute left-6 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
						<Input
							type="search"
							placeholder="Type anything to search..."
							value={query}
							onChange={(e) => setQuery(e.target.value)}
							className="pl-14 h-14 border-none bg-transparent focus-visible:ring-0 text-lg font-medium"
						/>
					</div>
					<div className="flex items-center gap-2 px-2 w-full md:w-auto">
						<Separator orientation="vertical" className="h-8 hidden md:block" />
						<Select
							value={filters.type || "all"}
							onValueChange={(v) =>
								setFilters({ ...filters, type: v === "all" ? "" : v })
							}
						>
							<SelectTrigger className="h-10 border-none bg-muted/50 rounded-2xl md:w-32">
								<SelectValue placeholder="All Types" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">Any Type</SelectItem>
								<SelectItem value="requirement">Requirement</SelectItem>
								<SelectItem value="feature">Feature</SelectItem>
								<SelectItem value="test">Test Case</SelectItem>
							</SelectContent>
						</Select>
						<Button className="h-10 px-6 rounded-2xl font-black uppercase tracking-widest text-[10px] shadow-lg shadow-primary/20">
							Query
						</Button>
					</div>
				</Card>
			</div>

			{/* Results Surface */}
			<div className="space-y-6">
				{isLoading ? (
					<div className="space-y-4">
						{[1, 2, 3].map((i) => (
							<Skeleton key={i} className="h-32 w-full rounded-[2rem]" />
						))}
					</div>
				) : results?.items && results.items.length > 0 ? (
					<div className="space-y-4 animate-in slide-in-from-bottom-4 duration-500">
						<div className="flex items-center justify-between px-2">
							<h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2">
								<Layers className="h-3 w-3" /> Search Results
							</h2>
							<Badge variant="secondary" className="font-bold rounded-full">
								{results.items.length} nodes matched
							</Badge>
						</div>

						<div className="grid grid-cols-1 gap-4 stagger-children">
							{results.items.map((item) => {
								const raw = item as Item & {
									item_view?: string;
									project_id?: string;
									view_type?: string;
								};
								const projectId = item.projectId ?? raw.project_id;
								const viewTypeCandidate1 = item.view ?? raw.view_type;
								const viewTypeCandidate2 = viewTypeCandidate1 ?? raw.item_view;
								const viewType = viewTypeCandidate2 ?? "feature";

								const targetPath = projectId
									? `/projects/${projectId}/views/${String(viewType).toLowerCase()}/${item.id}`
									: "/projects";

								return (
									<Link key={item.id} to={targetPath}>
										<Card className="p-6 border-none bg-card/50 hover:bg-card shadow-sm hover:shadow-xl active:scale-[0.99] transition-all duration-200 ease-out group rounded-[2rem]">
											<div className="flex flex-col md:flex-row md:items-center gap-6">
												<div className="h-12 w-12 rounded-2xl bg-muted flex items-center justify-center shrink-0 group-hover:bg-primary/10 transition-colors">
													<Box className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
												</div>
												<div className="flex-1 space-y-1">
													<div className="flex items-center gap-2 flex-wrap">
														<h3 className="font-bold text-lg leading-none group-hover:text-primary transition-colors">
															{item.title}
														</h3>
														<Badge
															variant="outline"
															className="text-[8px] font-black uppercase tracking-tighter h-4 border-primary/20 text-primary"
														>
															{item.type}
														</Badge>
													</div>
													<p className="text-sm text-muted-foreground line-clamp-1 font-medium">
														{item.description ||
															"No registry description provided for this node."}
													</p>
												</div>
												<div className="flex items-center gap-6 shrink-0">
													<div className="text-right hidden sm:block">
														<p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
															Status
														</p>
														<div className="flex items-center justify-end gap-1 mt-0.5">
															<div className="h-1.5 w-1.5 rounded-full bg-green-500" />
															<span className="text-[10px] font-bold uppercase">
																{item.status}
															</span>
														</div>
													</div>
													<div className="h-10 w-10 rounded-full border border-border flex items-center justify-center opacity-0 group-hover:opacity-100 group-hover:translate-x-0 -translate-x-4 transition-all">
														<ArrowRight className="h-4 w-4 text-primary" />
													</div>
												</div>
											</div>
										</Card>
									</Link>
								);
							})}
						</div>
					</div>
				) : query ? (
					<div className="flex flex-col items-center justify-center py-32 text-center">
						<div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
							<SearchIcon className="h-10 w-10 opacity-10" />
						</div>
						<h3 className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground">
							Zero matches in registry
						</h3>
						<p className="text-xs font-medium text-muted-foreground/60 mt-2">
							Adjust your query or check filters for specific projects.
						</p>
					</div>
				) : (
					<div className="flex flex-col items-center justify-center py-32 text-muted-foreground/20">
						<Command className="h-24 w-24 mb-4 opacity-5" />
						<p className="text-[10px] font-black uppercase tracking-[0.3em]">
							Awaiting Input Sequence
						</p>
					</div>
				)}
			</div>
		</div>
	);
}
