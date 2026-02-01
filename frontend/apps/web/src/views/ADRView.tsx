import { useParams } from "@tanstack/react-router";
import { Button, Tabs, TabsList, TabsTrigger } from "@tracertm/ui";
import { History, LayoutList, Plus } from "lucide-react";
import { useState } from "react";
import { ADRCard } from "@/components/specifications/adr/ADRCard";
import { ADREditor } from "@/components/specifications/adr/ADREditor";
import { ADRTimeline } from "@/components/specifications/adr/ADRTimeline";
import { useADRs, useCreateADR } from "@/hooks/useSpecifications";

export function ADRView() {
	const { projectId } = useParams({ strict: false });
	const { data: adrsData } = useADRs({ projectId: projectId || "" });
	const adrs = adrsData?.adrs ?? [];
	const createADR = useCreateADR();
	const [viewMode, setViewMode] = useState<"list" | "timeline">("list");
	const [isEditing, setIsEditing] = useState(false);

	if (isEditing) {
		return (
			<div className="p-6">
				<ADREditor
					onSave={async (data) => {
						await createADR.mutateAsync({
							projectId: projectId || "",
							title: data.title || "",
							context: data.context || "",
							decision: data.decision || "",
							consequences: data.consequences || "",
						});
						setIsEditing(false);
					}}
					onCancel={() => setIsEditing(false)}
				/>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h1 className="text-2xl font-bold">Architecture Decisions</h1>
					<p className="text-muted-foreground">
						Log and track architectural choices (MADR 4.0).
					</p>
				</div>
				<div className="flex gap-2">
					<Tabs value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
						<TabsList>
							<TabsTrigger value="list">
								<LayoutList className="w-4 h-4" />
							</TabsTrigger>
							<TabsTrigger value="timeline">
								<History className="w-4 h-4" />
							</TabsTrigger>
						</TabsList>
					</Tabs>
					<Button onClick={() => setIsEditing(true)}>
						<Plus className="w-4 h-4 mr-2" />
						New ADR
					</Button>
				</div>
			</div>

			{viewMode === "list" ? (
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{adrs.map((adr) => (
						<ADRCard key={adr.id} adr={adr} />
					))}
				</div>
			) : (
				<ADRTimeline adrs={adrs} />
			)}
		</div>
	);
}
