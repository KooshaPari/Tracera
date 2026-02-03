import { useEffect, useState } from "react";
import { useNavigate, useParams } from "@tanstack/react-router";
import type { ADR } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	AlertTriangle,
	ArrowLeft,
	CheckCircle,
	Edit2,
	FileText,
	GitBranch,
	Link2,
	Save,
	Trash2,
	TrendingUp,
	X,
} from "lucide-react";
import { toast } from "sonner";
import { ComplianceGauge } from "@/components/specifications/adr/ComplianceGauge";
import { DecisionMatrix } from "@/components/specifications/adr/DecisionMatrix";
import { useADR, useADRActivities } from "@/hooks/useSpecifications";

// Mock data - replace with actual API call
const mockADR: ADR = {
	adrNumber: "ADR-0001",
	complianceScore: 85,
	consequences:
		"PostgreSQL introduces operational overhead for maintenance and backups. Schema migrations must be carefully managed. Performance tuning may be required for large datasets.",
	consideredOptions: [
		{
			description: "NoSQL flexibility for unstructured data",
			id: "opt-1",
			isChosen: false,
			title: "MongoDB",
		},
		{
			description: "Similar to PostgreSQL but fewer features",
			id: "opt-2",
			isChosen: false,
			title: "MySQL",
		},
		{
			description: "Best overall fit for requirements",
			id: "opt-3",
			isChosen: true,
			title: "PostgreSQL",
		},
	],
	context:
		"The team needs a reliable, scalable database solution that supports complex queries and transactions. Current in-memory storage is insufficient for production workloads.",
	createdAt: "2025-01-15T10:00:00Z",
	date: "2025-01-15",
	decision:
		"We will use PostgreSQL as our primary database. It provides ACID compliance, excellent query performance, and rich extension ecosystem.",
	decisionDrivers: ["scalability", "reliability", "cost"],
	id: "adr-1",
	projectId: "proj-1",
	relatedRequirements: ["REQ-001", "REQ-042"],
	status: "accepted",
	tags: ["database", "infrastructure", "persistence"],
	title: "Use PostgreSQL for Data Persistence",
	updatedAt: "2025-01-15T10:00:00Z",
	version: 1,
};

interface ADRDetailViewProps {
	adrId?: string;
}

// Save delay in milliseconds
const API_SAVE_DELAY_MS = 500;

export const ADRDetailView = ({ adrId }: ADRDetailViewProps) => {
	const params = useParams({ strict: false });
	const navigate = useNavigate();
	const effectiveAdrId = adrId || params?.adrId || "";
	const { data: adrData, isLoading: adrLoading } = useADR(effectiveAdrId);
	const { data: activityData } = useADRActivities(effectiveAdrId);
	const activities = activityData ?? [];

	const [adr, setAdr] = useState<ADR>(adrData || mockADR);
	const [isEditing, setIsEditing] = useState(false);
	const [editedADR, setEditedADR] = useState<ADR>(adrData || mockADR);
	const [isLoading, setIsLoading] = useState(false);

	useEffect(() => {
		if (adrData) {
			setAdr(adrData);
			setEditedADR(adrData);
		}
	}, [adrData]);

	const handleSave = async () => {
		setIsLoading(true);
		try {
			// API call would go here
			await new Promise((resolve) => setTimeout(resolve, API_SAVE_DELAY_MS));
			setAdr(editedADR);
			setIsEditing(false);
			toast.success("ADR updated successfully");
		} catch {
			toast.error("Failed to update ADR");
		} finally {
			setIsLoading(false);
		}
	};

	const handleDelete = async () => {
		if (!confirm("Are you sure you want to delete this ADR?")) {
			return;
		}
		try {
			// API call would go here
			await new Promise((resolve) => setTimeout(resolve, API_SAVE_DELAY_MS));
			toast.success("ADR deleted");
			navigate("/adrs");
		} catch {
			toast.error("Failed to delete ADR");
		}
	};

	const handleEditClick = () => {
		setEditedADR(adr);
		setIsEditing(true);
	};

	const handleCancelEdit = () => {
		setIsEditing(false);
		setEditedADR(adr);
	};

	const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setEditedADR({ ...editedADR, title: e.target.value });
	};

	const handleContextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setEditedADR({
			...editedADR,
			context: e.target.value,
		});
	};

	const handleDecisionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setEditedADR({
			...editedADR,
			decision: e.target.value,
		});
	};

	const handleConsequencesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setEditedADR({
			...editedADR,
			consequences: e.target.value,
		});
	};

	const handleBackClick = () => {
		navigate("/adrs");
	};

	const statusColors = {
		accepted: "bg-green-500/10 text-green-600",
		deprecated: "bg-gray-500/10 text-gray-600",
		proposed: "bg-yellow-500/10 text-yellow-600",
		rejected: "bg-red-500/10 text-red-600",
		superseded: "bg-orange-500/10 text-orange-600",
	};

	if (adrLoading && !adrData) {
		return (
			<div className="p-6 space-y-6">
				<div className="h-8 w-40 bg-muted/40 rounded" />
				<div className="h-32 bg-muted/30 rounded-xl" />
				<div className="h-64 bg-muted/20 rounded-xl" />
			</div>
		);
	}

	return (
		<div className="p-6 space-y-6 max-w-[1400px] mx-auto pb-20">
			{/* Header */}
			<div className="flex items-center justify-between gap-4">
				<button
					onClick={handleBackClick}
					className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
				>
					<ArrowLeft className="h-4 w-4" />
					Back to ADRs
				</button>

				{!isEditing && (
					<div className="flex gap-2">
						<Button
							variant="outline"
							size="sm"
							onClick={handleEditClick}
						>
							<Edit2 className="h-4 w-4 mr-2" />
							Edit
						</Button>
						<Button
							variant="ghost"
							size="sm"
							className="text-destructive hover:bg-destructive/10"
							onClick={handleDelete}
						>
							<Trash2 className="h-4 w-4 mr-2" />
							Delete
						</Button>
					</div>
				)}

				{isEditing && (
					<div className="flex gap-2">
						<Button
							variant="outline"
							size="sm"
							onClick={handleCancelEdit}
						>
							<X className="h-4 w-4 mr-2" />
							Cancel
						</Button>
						<Button size="sm" onClick={handleSave} disabled={isLoading}>
							<Save className="h-4 w-4 mr-2" />
							{isLoading ? "Saving..." : "Save Changes"}
						</Button>
					</div>
				)}
			</div>

			{/* Title and Status */}
			<div className="space-y-4">
				{isEditing ? (
					<input
						type="text"
						value={editedADR.title}
						onChange={handleTitleChange}
						className="text-3xl font-black w-full bg-transparent border-b-2 border-primary outline-none"
					/>
				) : (
					<h1 className="text-3xl font-black tracking-tight">{adr.title}</h1>
				)}

				<div className="flex flex-wrap items-center gap-3">
					<Badge variant="outline" className="font-mono text-sm">
						{adr.adrNumber}
					</Badge>
					<Badge
						className={statusColors[adr.status as keyof typeof statusColors]}
					>
						{adr.status}
					</Badge>
					{adr.date && (
						<span className="text-sm text-muted-foreground">
							{format(new Date(adr.date), "MMM d, yyyy")}
						</span>
					)}
				</div>
			</div>

			{/* Main Content Grid */}
			<div className="grid gap-6 lg:grid-cols-3">
				{/* Left Column - Main Content */}
				<div className="lg:col-span-2 space-y-6">
					<Tabs defaultValue="madr" className="w-full">
						<TabsList className="w-full justify-start">
							<TabsTrigger value="madr">MADR Format</TabsTrigger>
							<TabsTrigger value="matrix">Decision Matrix</TabsTrigger>
							<TabsTrigger value="history">Version History</TabsTrigger>
						</TabsList>

						{/* MADR Format */}
						<TabsContent value="madr" className="space-y-6">
							{/* Context */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<FileText className="h-4 w-4" />
										Context
									</CardTitle>
								</CardHeader>
								<CardContent>
									{isEditing ? (
										<textarea
											value={editedADR.context || ""}
											onChange={handleContextChange}
											className="w-full h-32 px-3 py-2 rounded-lg border border-input bg-background"
										/>
									) : (
										<p className="text-sm leading-relaxed text-muted-foreground">
											{adr.context}
										</p>
									)}
								</CardContent>
							</Card>

							{/* Decision */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<CheckCircle className="h-4 w-4 text-green-600" />
										Decision
									</CardTitle>
								</CardHeader>
								<CardContent>
									{isEditing ? (
										<textarea
											value={editedADR.decision || ""}
											onChange={handleDecisionChange}
											className="w-full h-32 px-3 py-2 rounded-lg border border-input bg-background"
										/>
									) : (
										<p className="text-sm leading-relaxed font-medium">
											{adr.decision}
										</p>
									)}
								</CardContent>
							</Card>

							{/* Consequences */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<AlertTriangle className="h-4 w-4 text-orange-600" />
										Consequences
									</CardTitle>
								</CardHeader>
								<CardContent>
									{isEditing ? (
										<textarea
											value={editedADR.consequences || ""}
											onChange={handleConsequencesChange}
											className="w-full h-32 px-3 py-2 rounded-lg border border-input bg-background"
										/>
									) : (
										<p className="text-sm leading-relaxed text-muted-foreground">
											{adr.consequences}
										</p>
									)}
								</CardContent>
							</Card>

							{/* Considered Options */}
							{adr.consideredOptions && adr.consideredOptions.length > 0 && (
								<Card className="border-none bg-card/50">
									<CardHeader>
										<CardTitle className="text-base">
											Considered Options
										</CardTitle>
									</CardHeader>
									<CardContent className="space-y-3">
										{adr.consideredOptions.map((option) => (
											<div
												key={option.id}
												className="flex items-start gap-3 p-3 rounded-lg border border-border/50"
											>
												<div className="flex-1">
													<div className="flex items-center gap-2 mb-1">
														<h4 className="font-medium text-sm">
															{option.title}
														</h4>
														{!option.isChosen && (
															<Badge variant="secondary" className="text-xs">
																Not Chosen
															</Badge>
														)}
													</div>
													<p className="text-xs text-muted-foreground">
														{option.description}
													</p>
												</div>
											</div>
										))}
									</CardContent>
								</Card>
							)}
						</TabsContent>

						{/* Decision Matrix */}
						<TabsContent value="matrix">
							{adr.consideredOptions && adr.consideredOptions.length > 0 && (
								<Card className="border-none bg-card/50">
									<CardContent className="pt-6">
										<DecisionMatrix options={adr.consideredOptions} />
									</CardContent>
								</Card>
							)}
						</TabsContent>

						{/* Version History */}
						<TabsContent value="history">
							<Card className="border-none bg-card/50">
								<CardContent className="pt-6">
									{activities.length === 0 ? (
										<div className="text-sm text-muted-foreground">
											No activity yet. Changes and verifications will appear
											here.
										</div>
									) : (
										<div className="space-y-4">
											{activities.map((activity) => (
												<div
													key={activity.id}
													className="flex gap-4 pb-4 border-b border-border/50 last:border-0"
												>
													<div className="flex-shrink-0">
														<Badge variant="secondary" className="font-mono">
															{activity.activityType}
														</Badge>
													</div>
													<div className="flex-1">
														<p className="font-medium text-sm">
															{activity.description || "Updated"}
														</p>
														{activity.fromValue || activity.toValue ? (
															<p className="text-xs text-muted-foreground mt-1">
																{activity.fromValue || "—"} →{" "}
																{activity.toValue || "—"}
															</p>
														) : null}
														<p className="text-xs text-muted-foreground mt-1">
															{activity.performedBy || "System"} ·{" "}
															{activity.createdAt
																? format(
																		new Date(activity.createdAt),
																		"MMM d, yyyy HH:mm",
																	)
																: "—"}
														</p>
													</div>
												</div>
											))}
										</div>
									)}
								</CardContent>
							</Card>
						</TabsContent>
					</Tabs>
				</div>

				{/* Right Column - Sidebar */}
				<div className="space-y-6">
					{/* Compliance Score */}
					{adr.complianceScore !== undefined && (
						<Card className="border-none bg-gradient-to-br from-card to-muted/20">
							<CardHeader>
								<CardTitle className="text-sm">Compliance Score</CardTitle>
							</CardHeader>
							<CardContent className="flex justify-center py-4">
								<ComplianceGauge
									score={adr.complianceScore}
									size={120}
									showLabel
								/>
							</CardContent>
						</Card>
					)}

					{/* Decision Drivers */}
					{adr.decisionDrivers && adr.decisionDrivers.length > 0 && (
						<Card className="border-none bg-card/50">
							<CardHeader>
								<CardTitle className="text-sm flex items-center gap-2">
									<TrendingUp className="h-4 w-4" />
									Decision Drivers
								</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="flex flex-wrap gap-2">
									{adr.decisionDrivers.map((driver) => (
										<Badge key={driver} variant="outline">
											{driver}
										</Badge>
									))}
								</div>
							</CardContent>
						</Card>
					)}

					{/* Related Requirements */}
					{adr.relatedRequirements && adr.relatedRequirements.length > 0 && (
						<Card className="border-none bg-card/50">
							<CardHeader>
								<CardTitle className="text-sm flex items-center gap-2">
									<Link2 className="h-4 w-4" />
									Related Requirements
								</CardTitle>
							</CardHeader>
							<CardContent className="space-y-2">
								{adr.relatedRequirements.map((req) => (
									<button
										key={req}
										className="w-full text-left p-2 rounded-lg hover:bg-muted/50 transition-colors text-sm"
									>
										<div className="font-medium text-primary">{req}</div>
									</button>
								))}
							</CardContent>
						</Card>
					)}

					{/* Tags */}
					{adr.tags && adr.tags.length > 0 && (
						<Card className="border-none bg-card/50">
							<CardHeader>
								<CardTitle className="text-sm">Tags</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="flex flex-wrap gap-2">
									{adr.tags.map((tag) => (
										<Badge key={tag} variant="secondary" className="text-xs">
											{tag}
										</Badge>
									))}
								</div>
							</CardContent>
						</Card>
					)}

					{/* Supersedes */}
					{adr.supersedes && (
						<Card className="border-none bg-card/50 border-l-4 border-l-orange-500">
							<CardHeader>
								<CardTitle className="text-sm flex items-center gap-2">
									<GitBranch className="h-4 w-4" />
									Supersedes
								</CardTitle>
							</CardHeader>
							<CardContent>
								<button className="text-sm text-primary hover:underline">
									{adr.supersedes}
								</button>
							</CardContent>
						</Card>
					)}
				</div>
			</div>
		</div>
	);
};
