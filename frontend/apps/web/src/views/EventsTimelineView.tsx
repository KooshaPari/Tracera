import {
	Button,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import {
	ArrowRight,
	Calendar,
	Clock,
	Edit,
	Folder,
	History,
	Link2,
	Plus,
	Search,
	User,
	Zap,
} from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

interface Event {
	id: string;
	type: "item_created" | "item_updated" | "link_created" | "project_created";
	title: string;
	description: string;
	timestamp: Date;
	user: string;
	projectId?: string;
}

const eventConfigs = {
	item_created: { color: "bg-green-500", icon: Plus, text: "Created node" },
	item_updated: { color: "bg-blue-500", icon: Edit, text: "Modified node" },
	link_created: { color: "bg-purple-500", icon: Link2, text: "Mapped link" },
	project_created: {
		color: "bg-orange-500",
		icon: Folder,
		text: "Initialized project",
	},
};

export function EventsTimelineView() {
	const [searchQuery, setSearchQuery] = useState("");
	const [typeFilter, setTypeFilter] = useState("all");

	// Mock events - replace with actual API call (stable reference for hook deps)
	const events = useMemo<Event[]>(
		() => [
			{
				description: "New security requirement initialized in Project Alpha.",
				id: "1",
				projectId: "alpha-1",
				timestamp: new Date(),
				title: "User Authentication",
				type: "item_created",
				user: "Admin",
			},
			{
				description: "Connected 'Auth Logic' to 'Security Spec v1'.",
				id: "2",
				projectId: "alpha-1",
				timestamp: new Date(Date.now() - 3_600_000),
				title: "Traceability Link",
				type: "link_created",
				user: "Jane Doe",
			},
			{
				description: "Field 'user_id' updated to UUID for higher integrity.",
				id: "3",
				projectId: "beta-2",
				timestamp: new Date(Date.now() - 86_400_000),
				title: "Database Schema",
				type: "item_updated",
				user: "System",
			},
		],
		[],
	);

	const filteredEvents = useMemo(() => events.filter((e) => {
			const matchesQuery =
				e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				e.description.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesType = typeFilter === "all" || e.type === typeFilter;
			return matchesQuery && matchesType;
		}), [events, searchQuery, typeFilter]);

	return (
		<div className="p-6 space-y-8 max-w-4xl mx-auto animate-in fade-in duration-500">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4 text-center md:text-left">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Audit Timeline
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Immutable record of system activity and entity transitions.
					</p>
				</div>
				<Button
					variant="outline"
					size="sm"
					className="rounded-xl gap-2 font-bold uppercase tracking-widest text-[10px]"
				>
					<History className="h-3 w-3" /> Export Logs
				</Button>
			</div>

			{/* Filters Bar */}
			<Card className="p-2 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-2">
				<div className="relative flex-1 min-w-[200px]">
					<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						placeholder="Search audit trail..."
						className="pl-10 h-10 border-none bg-transparent focus-visible:ring-0"
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
					/>
				</div>
				<div className="h-6 w-px bg-border/50 mx-2 hidden md:block" />
				<Select value={typeFilter} onValueChange={setTypeFilter}>
					<SelectTrigger className="w-[160px] h-10 border-none bg-transparent hover:bg-background/50 transition-colors">
						<SelectValue placeholder="Event Type" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All Events</SelectItem>
						{Object.keys(eventConfigs).map((t) => (
							<SelectItem key={t} value={t} className="capitalize">
								{t.replace("_", " ")}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</Card>

			{/* Timeline Content */}
			<div className="relative space-y-8 before:absolute before:left-[19px] before:top-2 before:bottom-2 before:w-px before:bg-border/50">
				{filteredEvents.length > 0 ? (
					filteredEvents.map((event) => {
						const config = eventConfigs[event.type];
						return (
							<div key={event.id} className="relative pl-12 group">
								{/* Timeline Node */}
								<div
									className={cn(
										"absolute left-0 top-1.5 h-10 w-10 rounded-2xl flex items-center justify-center shadow-lg transition-transform group-hover:scale-110",
										config.color,
										"shadow-current/20",
									)}
								>
									<config.icon className="h-5 w-5 text-white" />
								</div>

								<Card className="p-6 border-none bg-card/50 shadow-sm group-hover:shadow-md transition-all group-hover:bg-card">
									<div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
										<div className="space-y-2 flex-1">
											<div className="flex flex-wrap items-center gap-2">
												<h3 className="font-black text-sm tracking-tight">
													{event.title}
												</h3>
												<Badge
													variant="secondary"
													className="text-[8px] font-black uppercase tracking-tighter h-4"
												>
													{config.text}
												</Badge>
												{event.projectId && (
													<span className="text-[9px] font-bold text-primary uppercase bg-primary/5 px-1.5 py-0.5 rounded">
														{event.projectId}
													</span>
												)}
											</div>
											<p className="text-sm text-muted-foreground leading-relaxed font-medium">
												{event.description}
											</p>
										</div>
										<div className="text-right shrink-0">
											<div className="flex items-center justify-end gap-1.5 text-[10px] font-black uppercase text-muted-foreground mb-1">
												<Clock className="h-3 w-3" />
												{new Date(event.timestamp).toLocaleTimeString([], {
													hour: "2-digit",
													minute: "2-digit",
												})}
											</div>
											<div className="flex items-center justify-end gap-1.5 text-[10px] font-bold text-muted-foreground/60">
												<User className="h-2.5 w-2.5" />
												{event.user}
											</div>
										</div>
									</div>

									<div className="mt-4 flex items-center justify-between pt-4 border-t border-dashed">
										<div className="flex items-center gap-4">
											<div className="flex items-center gap-1">
												<Calendar className="h-3 w-3 text-muted-foreground" />
												<span className="text-[9px] font-bold text-muted-foreground uppercase">
													{new Date(event.timestamp).toLocaleDateString()}
												</span>
											</div>
										</div>
										<Button
											variant="ghost"
											size="xs"
											className="text-[9px] font-black uppercase gap-1 group/btn"
										>
											View Context{" "}
											<ArrowRight className="h-2.5 w-2.5 group-hover/btn:translate-x-1 transition-transform" />
										</Button>
									</div>
								</Card>
							</div>
						);
					})
				) : (
					<div className="flex flex-col items-center justify-center py-32 text-muted-foreground/30">
						<Zap className="h-16 w-16 mb-4 opacity-10" />
						<p className="text-xs font-black uppercase tracking-[0.2em]">
							End of Audit Trail
						</p>
					</div>
				)}
			</div>
		</div>
	);
}
