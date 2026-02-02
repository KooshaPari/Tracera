import { Badge, Input } from "@tracertm/ui";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Activity,
	Box,
	CheckCircle2,
	Download,
	FileText,
	Layers,
	Search,
} from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

interface TraceabilityMatrixViewProps {
	projectId: string;
}

export function TraceabilityMatrixView({
	projectId,
}: TraceabilityMatrixViewProps) {
	const { data: itemsData, isLoading } = useItems({
		projectId,
	});
	const { data: linksData } = useLinks({
		projectId,
	});

	const [searchQuery, setSearchQuery] = useState("");

	const items = itemsData?.items ?? [];
	const links = linksData?.links ?? [];

	const matrix = useMemo(() => {
		if (items.length === 0) {return { coverage: {}, features: [], requirements: [] };}

		const requirements = items.filter(
			(i: any) =>
				i.type === "requirement" &&
				i.title.toLowerCase().includes(searchQuery.toLowerCase()),
		);
		const features = items.filter((i: any) => i.type === "feature");

		const coverage: Record<string, Set<string>> = {};
		links.forEach((link: any) => {
			if (!coverage[link.sourceId]) {coverage[link.sourceId] = new Set();}
			coverage[link.sourceId]?.add(link.targetId);
		});

		return { coverage, features, requirements };
	}, [items, links, searchQuery]);

	const coveragePercent = useMemo(() => {
		if (matrix.requirements.length === 0) {return 0;}
		const covered = matrix.requirements.filter(
			(r) => (matrix.coverage[r.id]?.size ?? 0) > 0,
		).length;
		return Math.round((covered / matrix.requirements.length) * 100);
	}, [matrix]);

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="flex gap-4">
					{[1, 2, 3].map((i) => (
						<Skeleton key={i} className="h-24 flex-1 rounded-2xl" />
					))}
				</div>
				<Skeleton className="h-[500px] w-full rounded-2xl" />
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1800px] mx-auto animate-in fade-in duration-500">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Traceability Matrix
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Validation grid mapping high-level requirements to functional
						features.
					</p>
				</div>
				<Button
					variant="outline"
					size="sm"
					className="gap-2 rounded-xl"
					onClick={() => toast.success("Matrix exported to CSV")}
				>
					<Download className="h-4 w-4" /> Export
				</Button>
			</div>

			{/* Stats Bar */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				{[
					{
						color: "text-blue-500",
						icon: FileText,
						label: "High-Level REQS",
						value: matrix.requirements.length,
					},
					{
						color: "text-purple-500",
						icon: Box,
						label: "Mapped Features",
						value: matrix.features.length,
					},
					{
						color: "text-green-500",
						icon: Activity,
						label: "Integrity Ratio",
						progress: true,
						value: `${coveragePercent}%`,
					},
				].map((s, i) => (
					<Card
						key={i}
						className="p-5 border-none bg-card/50 shadow-sm flex flex-col justify-between h-28"
					>
						<div className="flex justify-between items-start">
							<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								{s.label}
							</p>
							<s.icon className={cn("h-4 w-4 opacity-30", s.color)} />
						</div>
						<div className="flex items-end justify-between">
							<h3 className="text-2xl font-black leading-none">{s.value}</h3>
							{s.progress && (
								<div className="h-1.5 w-24 bg-muted rounded-full overflow-hidden shrink-0 mb-1">
									<div
										className="h-full bg-green-500"
										style={{ width: `${coveragePercent}%` }}
									/>
								</div>
							)}
						</div>
					</Card>
				))}
			</div>

			{/* Filters Control */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex items-center gap-2">
				<div className="relative flex-1">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search requirements..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2" />
				<Badge
					variant="outline"
					className="h-8 px-3 rounded-lg font-bold uppercase tracking-tighter"
				>
					{matrix.requirements.length} REQS x {matrix.features.length} FEATS
				</Badge>
			</Card>

			{/* Matrix Grid */}
			<Card className="border-none bg-card/50 shadow-xl rounded-[2rem] overflow-hidden">
				<div className="overflow-x-auto custom-scrollbar">
					<table className="w-full border-collapse">
						<thead>
							<tr>
								<th className="sticky left-0 z-20 p-6 text-left bg-card border-b border-r min-w-[300px]">
									<div className="flex items-center gap-2">
										<FileText className="h-4 w-4 text-primary" />
										<span className="text-[10px] font-black uppercase tracking-widest">
											Requirement Detail
										</span>
									</div>
								</th>
								{matrix.features.map((feature) => (
									<th
										key={feature.id}
										className="p-4 bg-muted/30 border-b border-r min-w-[120px] align-bottom"
									>
										<div className="[writing-mode:vertical-lr] rotate-180 text-left mx-auto">
											<span className="text-[10px] font-bold uppercase tracking-tighter text-muted-foreground truncate max-h-[150px]">
												{feature.title}
											</span>
										</div>
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{matrix.requirements.map((req) => (
								<tr
									key={req.id}
									className="group hover:bg-muted/20 transition-colors"
								>
									<td className="sticky left-0 z-10 p-4 bg-card border-b border-r group-hover:bg-muted/10 transition-colors">
										<div className="flex flex-col gap-1">
											<span className="text-sm font-bold group-hover:text-primary transition-colors">
												{req.title}
											</span>
											<span className="text-[9px] font-mono text-muted-foreground uppercase">
												{req.id.slice(0, 8)}
											</span>
										</div>
									</td>
									{matrix.features.map((feature) => {
										const isLinked = matrix.coverage[req.id]?.has(feature.id);
										return (
											<td
												key={feature.id}
												className={cn(
													"p-4 text-center border-b border-r transition-all",
													isLinked ? "bg-green-500/[0.03]" : "opacity-20",
												)}
											>
												<div className="flex justify-center">
													{isLinked ? (
														<div className="h-6 w-6 rounded-full bg-green-500/10 flex items-center justify-center text-green-600 shadow-sm">
															<CheckCircle2 className="h-4 w-4" />
														</div>
													) : (
														<div className="h-1 w-1 rounded-full bg-muted-foreground" />
													)}
												</div>
											</td>
										);
									})}
								</tr>
							))}
						</tbody>
					</table>

					{matrix.requirements.length === 0 && (
						<div className="flex flex-col items-center justify-center py-32 text-muted-foreground/30">
							<Layers className="h-16 w-16 mb-4 opacity-10" />
							<p className="text-xs font-black uppercase tracking-[0.2em]">
								No mapping data available
							</p>
						</div>
					)}
				</div>
			</Card>

			{/* Legend */}
			<div className="flex justify-center gap-8 py-4">
				<div className="flex items-center gap-2">
					<div className="h-3 w-3 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center">
						<CheckCircle2 className="h-2 w-2 text-green-600" />
					</div>
					<span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
						Validated Link
					</span>
				</div>
				<div className="flex items-center gap-2">
					<div className="h-1 w-1 rounded-full bg-muted-foreground opacity-30" />
					<span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
						No Connection
					</span>
				</div>
			</div>
		</div>
	);
}
