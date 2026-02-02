import { Input, Separator } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	ArrowRight,
	ChevronRight,
	FileText,
	Info,
	Search,
	ShieldAlert,
	Target,
	Zap,
} from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

interface ImpactAnalysisViewProps {
	projectId: string;
}

export function ImpactAnalysisView({ projectId }: ImpactAnalysisViewProps) {
	const { data: itemsData, isLoading: itemsLoading } = useItems({
		projectId,
	});
	const { data: linksData } = useLinks({
		projectId,
	});
	const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
	const [searchQuery, setSearchQuery] = useState("");

	const items = itemsData?.items ?? [];
	const links = linksData?.links ?? [];

	const filteredItems = useMemo(() => items.filter((i) =>
			i.title.toLowerCase().includes(searchQuery.toLowerCase()),
		), [items, searchQuery]);

	const analyzeImpact = (itemId: string) => {
		if (links.length === 0) {return { direct: [], indirect: [] };}

		const direct = new Set<string>();
		const indirect = new Set<string>();

		links.forEach((link: any) => {
			if (link.sourceId === itemId) {direct.add(link.targetId);}
		});

		direct.forEach((directId) => {
			links.forEach((link: any) => {
				if (
					link.sourceId === directId &&
					!direct.has(link.targetId) &&
					link.targetId !== itemId
				) {
					indirect.add(link.targetId);
				}
			});
		});

		return {
			direct: [...direct],
			indirect: [...indirect],
		};
	};

	const impact = selectedItemId ? analyzeImpact(selectedItemId) : null;
	const selectedItem = items.find((i: any) => i.id === selectedItemId);

	if (itemsLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="grid grid-cols-1 md:grid-cols-2 gap-8">
					<Skeleton className="h-[600px] rounded-2xl" />
					<Skeleton className="h-[600px] rounded-2xl" />
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in fade-in duration-500">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Impact Intelligence
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Predict the ripple effect of changes across the traceability
						network.
					</p>
				</div>
				<div className="flex gap-2">
					<Button
						variant="outline"
						size="sm"
						className="rounded-xl gap-2 font-bold uppercase tracking-widest text-[10px]"
					>
						<ShieldAlert className="h-3 w-3" /> Risk Map
					</Button>
				</div>
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
				{/* Selection Column */}
				<div className="lg:col-span-2 space-y-4">
					<div className="flex items-center gap-2 mb-2">
						<Search className="h-4 w-4 text-primary" />
						<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
							Source Node
						</h3>
					</div>
					<Card className="p-4 border-none bg-muted/30 rounded-2xl space-y-4">
						<div className="relative">
							<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
							<Input
								placeholder="Search project items..."
								className="pl-10 bg-background border-none shadow-sm rounded-xl"
								value={searchQuery}
								onChange={(e) => setSearchQuery(e.target.value)}
							/>
						</div>
						<div className="space-y-1 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
							{filteredItems.map((item) => (
								<div
									key={item.id}
									onClick={() => setSelectedItemId(item.id)}
									className={cn(
										"p-3 rounded-xl cursor-pointer transition-all border-2 border-transparent group",
										selectedItemId === item.id
											? "bg-primary text-primary-foreground shadow-lg shadow-primary/20 border-primary"
											: "bg-background/50 hover:bg-background hover:border-primary/20",
									)}
								>
									<div className="flex items-center justify-between gap-3">
										<div className="flex items-center gap-3 min-w-0">
											<div
												className={cn(
													"h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors",
													selectedItemId === item.id
														? "bg-primary-foreground/20"
														: "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary",
												)}
											>
												<FileText className="h-4 w-4" />
											</div>
											<div className="min-w-0">
												<p className="text-sm font-bold truncate">
													{item.title}
												</p>
												<p
													className={cn(
														"text-[9px] font-black uppercase tracking-widest leading-none mt-1",
														selectedItemId === item.id
															? "text-primary-foreground/60"
															: "text-muted-foreground",
													)}
												>
													{item.type}
												</p>
											</div>
										</div>
										<ChevronRight
											className={cn(
												"h-4 w-4 opacity-40 shrink-0",
												selectedItemId === item.id
													? "text-primary-foreground"
													: "",
											)}
										/>
									</div>
								</div>
							))}
						</div>
					</Card>
				</div>

				{/* Result Column */}
				<div className="lg:col-span-3 space-y-6">
					{selectedItem && impact ? (
						<div className="space-y-6 animate-in slide-in-from-right-4 duration-500">
							{/* Assessment Summary */}
							<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
								<Card className="p-5 border-none bg-primary text-primary-foreground rounded-2xl shadow-xl shadow-primary/20">
									<p className="text-[10px] font-black uppercase tracking-widest opacity-70">
										Blast Radius
									</p>
									<div className="flex items-end gap-2 mt-2">
										<span className="text-4xl font-black">
											{impact.direct.length + impact.indirect.length}
										</span>
										<span className="text-xs font-bold mb-1 opacity-70">
											NODES
										</span>
									</div>
								</Card>
								<Card className="p-5 border-none bg-muted/30 rounded-2xl">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Direct Links
									</p>
									<div className="flex items-end gap-2 mt-2">
										<span className="text-4xl font-black">
											{impact.direct.length}
										</span>
										<div className="h-2 w-2 rounded-full bg-orange-500 animate-pulse mb-2" />
									</div>
								</Card>
								<Card className="p-5 border-none bg-muted/30 rounded-2xl">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Indirect (Lv2)
									</p>
									<div className="flex items-end gap-2 mt-2">
										<span className="text-4xl font-black">
											{impact.indirect.length}
										</span>
										<div className="h-2 w-2 rounded-full bg-yellow-500 mb-2" />
									</div>
								</Card>
							</div>

							{/* Detail Card */}
							<Card className="p-8 border-none bg-card/50 rounded-[2rem] shadow-sm space-y-8">
								<div className="flex items-center gap-4">
									<div className="h-12 w-12 rounded-2xl bg-muted flex items-center justify-center">
										<Target className="h-6 w-6 text-primary" />
									</div>
									<div>
										<h2 className="text-xl font-black tracking-tight uppercase">
											Analysis Report
										</h2>
										<p className="text-xs text-muted-foreground font-bold uppercase tracking-widest">
											Selected Item: {selectedItem.id.slice(0, 8)}
										</p>
									</div>
								</div>

								<div className="space-y-6">
									{/* Direct Section */}
									<div className="space-y-4">
										<div className="flex items-center gap-2">
											<div className="h-1.5 w-1.5 rounded-full bg-orange-500" />
											<h3 className="text-xs font-black uppercase tracking-widest">
												Primary Impact Surface
											</h3>
										</div>
										<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
											{impact.direct.length > 0 ? (
												impact.direct.map((id) => {
													const item = items.find((i) => i.id === id);
													return (
														<div
															key={id}
															className="p-3 rounded-xl border border-orange-500/20 bg-orange-500/5 group hover:bg-orange-500/10 transition-colors"
														>
															<p className="text-xs font-bold truncate">
																{item?.title || id}
															</p>
															<div className="flex justify-between items-center mt-1">
																<Badge
																	variant="outline"
																	className="text-[8px] h-3.5 px-1 border-orange-500/30 text-orange-600 uppercase font-black"
																>
																	{item?.type || "node"}
																</Badge>
																<ArrowRight className="h-3 w-3 text-orange-500 opacity-0 group-hover:opacity-100 transition-opacity" />
															</div>
														</div>
													);
												})
											) : (
												<div className="col-span-full p-8 border-2 border-dashed rounded-2xl text-center text-muted-foreground italic">
													<p className="text-xs">
														No direct dependencies identified
													</p>
												</div>
											)}
										</div>
									</div>

									<Separator className="bg-border/50" />

									{/* Indirect Section */}
									<div className="space-y-4">
										<div className="flex items-center gap-2">
											<div className="h-1.5 w-1.5 rounded-full bg-yellow-500" />
											<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
												Secondary Ripple Effect
											</h3>
										</div>
										<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
											{impact.indirect.length > 0 ? (
												impact.indirect.map((id) => {
													const item = items.find((i) => i.id === id);
													return (
														<div
															key={id}
															className="p-3 rounded-xl border border-border bg-muted/20 group hover:bg-muted/40 transition-colors"
														>
															<p className="text-xs font-bold truncate text-muted-foreground group-hover:text-foreground transition-colors">
																{item?.title || id}
															</p>
															<div className="flex justify-between items-center mt-1">
																<Badge
																	variant="outline"
																	className="text-[8px] h-3.5 px-1 uppercase font-black"
																>
																	{item?.type || "node"}
																</Badge>
																<ArrowRight className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
															</div>
														</div>
													);
												})
											) : (
												<div className="col-span-full p-8 border-2 border-dashed rounded-2xl text-center text-muted-foreground italic">
													<p className="text-xs">
														No secondary impacts predicted
													</p>
												</div>
											)}
										</div>
									</div>
								</div>

								{/* AI Footer Alert */}
								<div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex gap-4 items-start">
									<Info className="h-5 w-5 text-blue-500 shrink-0" />
									<div className="space-y-1">
										<p className="text-xs font-bold text-blue-700 dark:text-blue-400">
											Heuristic Analysis Tip
										</p>
										<p className="text-[10px] leading-relaxed text-blue-600 dark:text-blue-300 font-medium">
											Items in the ripple effect have a higher probability of
											requiring regression testing. Consider prioritizing these
											in your next sprint.
										</p>
									</div>
								</div>
							</Card>
						</div>
					) : (
						<div className="h-full min-h-[400px] flex flex-col items-center justify-center text-center p-12 border-2 border-dashed rounded-[2rem] text-muted-foreground/40">
							<div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
								<Zap className="h-10 w-10 opacity-20" />
							</div>
							<h3 className="text-sm font-black uppercase tracking-[0.2em]">
								System Standby
							</h3>
							<p className="text-xs font-medium mt-2">
								Select a node from the registry to initialize impact
								computation.
							</p>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
