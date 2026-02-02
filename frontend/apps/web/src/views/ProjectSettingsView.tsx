import { useNavigate, useSearch } from "@tanstack/react-router";
import { Button } from "@tracertm/ui/components/Button";
import { Input } from "@tracertm/ui/components/Input";
import { Label } from "@tracertm/ui/components/Label";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import { Textarea } from "@tracertm/ui/components/Textarea";
import { Save } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { useProject, useUpdateProject } from "@/hooks/useProjects";
import { getProjectDisplayName } from "@/lib/project-name-utils";
import IntegrationsView from "@/pages/projects/views/IntegrationsView";

export function ProjectSettingsView({ projectId }: { projectId: string }) {
	const { data: project } = useProject(projectId);
	const navigate = useNavigate();
	const search = useSearch({ strict: false }) as { tab?: string };
	const updateProject = useUpdateProject();
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");

	useEffect(() => {
		if (project) {
			setName(project.name || "");
			setDescription(project.description || "");
		}
	}, [project]);

	const activeTab = useMemo(() => {
		if (search?.tab === "integrations") {return "integrations";}
		return "general";
	}, [search]);

	const handleSave = async () => {
		if (!project) {return;}
		try {
			await updateProject.mutateAsync({
				data: { description: description.trim(), name: name.trim() },
				id: project.id,
			});
			toast.success("Project settings updated");
		} catch {
			toast.error("Failed to update project settings");
		}
	};

	if (!project) {
		return (
			<div className="p-6 text-sm text-muted-foreground">
				Loading project settings...
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-5xl mx-auto animate-in fade-in duration-500 pb-24">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-black tracking-tight uppercase">
						Project Settings
					</h1>
					<p className="text-muted-foreground font-medium uppercase text-[10px] tracking-widest">
						{getProjectDisplayName(project)}
					</p>
				</div>
				<Button
					variant="ghost"
					className="text-[10px] font-black uppercase tracking-widest"
					onClick={() => navigate({ to: `/projects/${project.id}` })}
				>
					Back to Overview
				</Button>
			</div>

			<Tabs defaultValue={activeTab} className="space-y-6">
				<TabsList className="w-full justify-start bg-transparent gap-2">
					<TabsTrigger value="general">General</TabsTrigger>
					<TabsTrigger value="integrations">Integrations</TabsTrigger>
				</TabsList>

				<TabsContent value="general" className="space-y-6">
					<div className="space-y-1">
						<h2 className="text-xl font-black uppercase tracking-tight">
							Project Identity
						</h2>
						<p className="text-sm text-muted-foreground font-medium">
							Edit project metadata and registry details.
						</p>
					</div>
					<Separator className="bg-border/50" />
					<div className="space-y-4">
						<div className="space-y-2">
							<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
								Project Name
							</Label>
							<Input
								value={name}
								onChange={(e) => setName(e.target.value)}
								className="h-12 bg-muted/30 border-none rounded-xl font-bold"
							/>
						</div>
						<div className="space-y-2">
							<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
								Description
							</Label>
							<Textarea
								value={description}
								onChange={(e) => setDescription(e.target.value)}
								className="bg-muted/30 border-none rounded-xl font-medium p-4 min-h-[120px]"
							/>
						</div>
						<div className="flex justify-end">
							<Button
								onClick={handleSave}
								disabled={updateProject.isPending}
								className="rounded-xl px-8 font-black uppercase tracking-widest text-[10px] gap-2 h-12"
							>
								<Save className="h-4 w-4" />
								Save
							</Button>
						</div>
					</div>
				</TabsContent>

				<TabsContent value="integrations" className="space-y-4">
					<div className="space-y-1">
						<h2 className="text-xl font-black uppercase tracking-tight">
							Project Integrations
						</h2>
						<p className="text-sm text-muted-foreground font-medium">
							Link repositories or planning systems and manage sync operations.
						</p>
					</div>
					<Separator className="bg-border/50" />
					<IntegrationsView
						projectId={project.id}
						mode="project"
						initialTab="mappings"
					/>
				</TabsContent>
			</Tabs>
		</div>
	);
}
