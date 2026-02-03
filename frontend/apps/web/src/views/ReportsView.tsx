import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import {
	ClipboardList,
	Download,
	FileSearch,
	FileText,
	History as HistoryIcon,
	Layers,
	ShieldCheck,
	TrendingUp,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { api } from "../api/endpoints";

type ReportFormat = "json" | "csv" | "pdf" | "xlsx";

interface ReportTemplate {
	id: string;
	name: string;
	description: string;
	format: ReportFormat[];
	icon: React.ComponentType<{ className?: string }>;
	color: string;
}

const reportTemplates: ReportTemplate[] = [
	{
		color: "text-blue-500",
		description: "End-to-end mapping from reqs to implementation.",
		format: ["pdf", "xlsx", "csv"],
		icon: Layers,
		id: "coverage",
		name: "Traceability Matrix",
	},
	{
		color: "text-green-500",
		description: "High-level project health and risk assessment.",
		format: ["pdf", "xlsx"],
		icon: TrendingUp,
		id: "status",
		name: "Executive Summary",
	},
	{
		color: "text-purple-500",
		description: "Full export of all nodes and metadata.",
		format: ["json", "csv", "xlsx"],
		icon: ClipboardList,
		id: "items",
		name: "Entity Registry",
	},
	{
		color: "text-orange-500",
		description: "Complete history of changes and transitions.",
		format: ["pdf", "json"],
		icon: ShieldCheck,
		id: "audit",
		name: "Compliance Audit",
	},
];

export function ReportsView() {
	const [selectedFormat, setSelectedFormat] = useState<
		Record<string, ReportFormat>
	>({});
	const [selectedProject, setSelectedProject] = useState<string>("");

	const projectsQuery = useQuery({
		queryFn: () => api.projects.list(),
		queryKey: ["projects"],
	});

	const generateReportMutation = useMutation({
		mutationFn: async ({
			templateId,
			format,
			projectId,
		}: {
			templateId: string;
			format: ReportFormat;
			projectId?: string;
		}) => {
			if (format === "json" || format === "csv") {
				if (!projectId) {
					throw new Error("Select project context");
				}
				const out = await api.exportImport.export(projectId, format);
				if (!(out instanceof Blob)) {
					toast.error("Export did not return a downloadable file");
					return { success: false };
				}
				const url = globalThis.URL.createObjectURL(out);
				const a = document.createElement("a");
				a.href = url;
				a.download = `${templateId}-export.${format}`;
				document.body.append(a);
				a.click();
				globalThis.URL.revokeObjectURL(url);
				document.body.removeChild(a);
				return { success: true };
			}
			// Simulate long generation for PDF/XLSX
			await new Promise((r) => setTimeout(r, 1500));
			toast.info(
				`${templateId.toUpperCase()} generation initialized in background`,
			);
			return { success: false };
		},
		onError: (error) => {
			toast.error(error.message || "Engine failure during generation");
		},
		onSuccess: (data) => {
			if (data.success) {
				toast.success("Export successful");
			}
		},
	});

	const handleGenerate = (templateId: string) => {
		const format =
			selectedFormat[templateId] ||
			reportTemplates.find((t) => t.id === templateId)?.format[0] ||
			"pdf";
		if ((format === "json" || format === "csv") && !selectedProject) {
			toast.error("Global scope export disabled. Select project.");
			return;
		}
		generateReportMutation.mutate({
			format,
			projectId: selectedProject,
			templateId,
		});
	};

	return (
		<div className="p-6 space-y-8 max-w-6xl mx-auto animate-in-fade-up pb-20">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase text-primary">
						Intelligence Hub
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Generate deterministic reports and structural exports.
					</p>
				</div>
			</div>

			{/* Project Context Selector */}
			<Card className="p-6 border-none bg-muted/30 rounded-[2rem] shadow-inner">
				<div className="flex flex-col md:flex-row items-center gap-6">
					<div className="h-12 w-12 rounded-2xl bg-background shadow-sm flex items-center justify-center shrink-0">
						<FileSearch className="h-6 w-6 text-primary" />
					</div>
					<div className="flex-1 space-y-1">
						<h3 className="text-xs font-black uppercase tracking-widest">
							Global Context
						</h3>
						<p className="text-[10px] font-bold text-muted-foreground uppercase">
							Filter intelligence by project boundary
						</p>
					</div>
					<div className="w-full md:w-72">
						<Select
							value={selectedProject || "all"}
							onValueChange={(v) => setSelectedProject(v === "all" ? "" : v)}
						>
							<SelectTrigger className="h-11 bg-background border-none shadow-md rounded-xl">
								<SelectValue placeholder="All Active Projects" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">System-Wide Registry</SelectItem>
								{projectsQuery.data?.map((project) => (
									<SelectItem key={project.id} value={project.id}>
										{project.name}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>
				</div>
			</Card>

			{/* Templates Grid */}
			<div className="grid grid-cols-1 md:grid-cols-2 gap-6 stagger-children">
				{reportTemplates.map((template) => (
					<Card
						key={template.id}
						className="p-8 border-none bg-card/50 shadow-sm hover:shadow-xl active:scale-[0.99] transition-all duration-200 ease-out group overflow-hidden relative"
					>
						{/* Subtle Icon Background */}
						<div className="absolute -right-4 -bottom-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
							<template.icon className="h-40 w-40" />
						</div>

						<div className="flex items-start gap-6 relative z-10">
							<div
								className={cn(
									"h-14 w-14 rounded-2xl bg-muted/50 flex items-center justify-center shrink-0",
									template.color,
								)}
							>
								<template.icon className="h-7 w-7" />
							</div>
							<div className="flex-1 space-y-4">
								<div>
									<h3 className="text-lg font-black tracking-tight">
										{template.name}
									</h3>
									<p className="text-xs text-muted-foreground font-medium leading-relaxed mt-1">
										{template.description}
									</p>
								</div>

								<div className="space-y-3">
									<p className="text-[9px] font-black uppercase tracking-[0.2em] text-muted-foreground">
										Select Format
									</p>
									<div className="flex flex-wrap gap-2">
										{template.format.map((format) => (
											<button
												key={format}
												onClick={() =>
													setSelectedFormat({
														...selectedFormat,
														[template.id]: format,
													})
												}
												className={cn(
													"px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tighter border transition-all",
													selectedFormat[template.id] === format ||
														(!selectedFormat[template.id] &&
															template.format[0] === format)
														? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20"
														: "bg-background border-border hover:border-primary/50 text-muted-foreground",
												)}
											>
												{format}
											</button>
										))}
									</div>
								</div>

								<Button
									onClick={() => handleGenerate(template.id)}
									className="w-full h-11 rounded-xl font-black uppercase tracking-[0.1em] gap-2 shadow-lg shadow-primary/10"
									disabled={generateReportMutation.isPending}
								>
									{generateReportMutation.isPending ? (
										<TrendingUp className="h-4 w-4 animate-bounce" />
									) : (
										<Download className="h-4 w-4" />
									)}
									Compile Engine
								</Button>
							</div>
						</div>
					</Card>
				))}
			</div>

			{/* Recent Activity */}
			<Card className="p-8 border-none bg-muted/20 rounded-[2rem]">
				<div className="flex items-center gap-3 mb-8">
					<HistoryIcon className="h-5 w-5 text-primary" />
					<h2 className="text-sm font-black uppercase tracking-widest">
						Archive History
					</h2>
				</div>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					{[
						{ date: "2h ago", name: "Full Integrity Matrix", type: "PDF" },
						{ date: "Yesterday", name: "Node Registry v1.4", type: "JSON" },
					].map((r, i) => (
						<div
							key={i}
							className="flex items-center justify-between p-4 rounded-2xl bg-background/50 border border-border/50 group hover:border-primary/30 transition-colors"
						>
							<div className="flex items-center gap-4">
								<div className="h-10 w-10 rounded-xl bg-primary/5 flex items-center justify-center">
									<FileText className="h-5 w-5 text-primary" />
								</div>
								<div>
									<div className="font-bold text-sm">{r.name}</div>
									<div className="text-[10px] text-muted-foreground font-black uppercase tracking-tighter">
										{r.date} • {r.type}
									</div>
								</div>
							</div>
							<Button
								variant="ghost"
								size="icon"
								className="rounded-full group-hover:bg-primary group-hover:text-white transition-all"
							>
								<Download className="h-4 w-4" />
							</Button>
						</div>
					))}
				</div>
			</Card>
		</div>
	);
}
