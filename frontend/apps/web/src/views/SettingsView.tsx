import { useMutation } from "@tanstack/react-query";
import { Button } from "@tracertm/ui/components/Button";
import { Input } from "@tracertm/ui/components/Input";
import { Label } from "@tracertm/ui/components/Label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import {
	Bell,
	Globe,
	Key,
	Link2,
	Monitor,
	RefreshCcw,
	Save,
	Settings as SettingsIcon,
	Shield,
	User,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Checkbox } from "@/components/ui/checkbox";
import { useProjects } from "@/hooks/useProjects";
import { getProjectDisplayName } from "@/lib/project-name-utils";
import { cn } from "@/lib/utils";
import IntegrationsView from "@/pages/projects/views/IntegrationsView";
import { saveSettings } from "../api/settings";

export function SettingsView() {
	const [theme, setTheme] = useState<"light" | "dark" | "system">("system");
	const [displayName, setDisplayName] = useState("System Administrator");
	const [email, setEmail] = useState("admin@tracertm.io");
	const [emailNotifications, setEmailNotifications] = useState(true);
	const [desktopNotifications, setDesktopNotifications] = useState(false);
	const [weeklySummary, setWeeklySummary] = useState(true);
	const { data: projects } = useProjects();
	const [integrationProjectId, setIntegrationProjectId] = useState<string>("");

	useEffect(() => {
		if (
			!integrationProjectId &&
			Array.isArray(projects) &&
			projects.length > 0 &&
			projects[0]
		) {
			setIntegrationProjectId(projects[0].id);
		}
	}, [integrationProjectId, projects]);

	const saveSettingsMutation = useMutation({
		mutationFn: async (settings: any) => saveSettings(settings),
		onError: (error: any) => {
			toast.error(`Sync failure: ${error.message}`);
		},
		onSuccess: () => {
			toast.success("Identity parameters synchronized");
		},
	});

	const handleSave = () => {
		saveSettingsMutation.mutate({
			desktopNotifications,
			displayName,
			email,
			emailNotifications,
			theme,
			weeklySummary,
		});
	};

	return (
		<div className="p-6 space-y-8 max-w-5xl mx-auto animate-in-fade-up pb-24">
			{/* Header */}
			<div className="flex items-center gap-4 mb-12">
				<div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center">
					<SettingsIcon className="h-7 w-7 text-primary" />
				</div>
				<div>
					<h1 className="text-3xl font-black tracking-tight uppercase">
						System Preferences
					</h1>
					<p className="text-muted-foreground font-medium uppercase text-[10px] tracking-widest">
						Global Configuration Panel
					</p>
				</div>
			</div>

			<Tabs
				defaultValue="profile"
				className="grid grid-cols-1 lg:grid-cols-4 gap-12 items-start"
			>
				{/* Sidebar Tabs */}
				<div className="lg:col-span-1 space-y-4">
					<TabsList className="flex flex-col bg-transparent h-auto space-y-1 items-stretch">
						{[
							{ icon: User, id: "profile", label: "Identity" },
							{ icon: Monitor, id: "appearance", label: "Visuals" },
							{ icon: Key, id: "api", label: "Engine Access" },
							{ icon: Bell, id: "notifications", label: "Comms" },
							{ icon: Shield, id: "security", label: "Safety" },
							{ icon: Link2, id: "integrations", label: "Integrations" },
						].map((tab) => (
							<TabsTrigger
								key={tab.id}
								value={tab.id}
								className="justify-start gap-3 px-4 py-3 rounded-xl data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all border border-transparent hover:border-border"
							>
								<tab.icon className="h-4 w-4" />
								<span className="font-bold text-sm tracking-tight">
									{tab.label}
								</span>
							</TabsTrigger>
						))}
					</TabsList>
				</div>

				{/* Content Panels */}
				<div className="lg:col-span-3">
					<TabsContent
						value="profile"
						className="mt-0 space-y-8 animate-in slide-in-from-right-2 duration-300"
					>
						<div className="space-y-1">
							<h2 className="text-xl font-black uppercase tracking-tight">
								Public Identity
							</h2>
							<p className="text-sm text-muted-foreground font-medium">
								How you appear across the project network.
							</p>
						</div>
						<Separator className="bg-border/50" />
						<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
							<div className="space-y-2">
								<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
									Registry Name
								</Label>
								<Input
									value={displayName}
									onChange={(e) => setDisplayName(e.target.value)}
									className="h-12 bg-muted/30 border-none rounded-xl font-bold"
								/>
							</div>
							<div className="space-y-2">
								<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
									Direct Comms (Email)
								</Label>
								<Input
									type="email"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
									className="h-12 bg-muted/30 border-none rounded-xl font-bold"
								/>
							</div>
						</div>
						<div className="space-y-2 pt-4">
							<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
								Timezone / Location Context
							</Label>
							<Select value="UTC">
								<SelectTrigger className="h-12 bg-muted/30 border-none rounded-xl font-bold">
									<div className="flex items-center gap-2">
										<Globe className="h-4 w-4 text-primary" />
										<SelectValue />
									</div>
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="UTC" className="font-bold">
										Coordinated Universal Time (UTC)
									</SelectItem>
									<SelectItem value="PST" className="font-bold">
										Pacific Standard Time
									</SelectItem>
								</SelectContent>
							</Select>
						</div>
					</TabsContent>

					<TabsContent
						value="appearance"
						className="mt-0 space-y-8 animate-in slide-in-from-right-2 duration-300"
					>
						<div className="space-y-1">
							<h2 className="text-xl font-black uppercase tracking-tight">
								Interface Directives
							</h2>
							<p className="text-sm text-muted-foreground font-medium">
								Configure visual rendering and layouts.
							</p>
						</div>
						<Separator className="bg-border/50" />
						<div className="space-y-6">
							<div className="flex items-center justify-between p-4 rounded-2xl bg-muted/30">
								<div className="space-y-1">
									<p className="text-sm font-bold uppercase tracking-tight">
										Color Schema
									</p>
									<p className="text-[10px] font-medium text-muted-foreground uppercase">
										Adaptive, dark or light mode
									</p>
								</div>
								<div className="flex gap-1">
									{["light", "dark", "system"].map((t) => (
										<button
											key={t}
											onClick={() => setTheme(t as any)}
											className={cn(
												"px-4 py-2 rounded-xl text-[10px] font-black uppercase border transition-all",
												theme === t
													? "bg-primary text-primary-foreground border-primary"
													: "bg-background border-border hover:border-primary/50",
											)}
										>
											{t}
										</button>
									))}
								</div>
							</div>

							<div className="flex items-center justify-between p-4 rounded-2xl bg-muted/30">
								<div className="space-y-1">
									<p className="text-sm font-bold uppercase tracking-tight">
										Information Density
									</p>
									<p className="text-[10px] font-medium text-muted-foreground uppercase">
										Scaling for data presentation
									</p>
								</div>
								<div className="flex gap-1">
									{["low", "medium", "high"].map((d) => (
										<button
											key={d}
											className={cn(
												"px-4 py-2 rounded-xl text-[10px] font-black uppercase border transition-all",
												d === "medium"
													? "bg-primary text-primary-foreground border-primary"
													: "bg-background border-border",
											)}
										>
											{d}
										</button>
									))}
								</div>
							</div>
						</div>
					</TabsContent>

					<TabsContent
						value="api"
						className="mt-0 space-y-8 animate-in slide-in-from-right-2 duration-300"
					>
						<div className="space-y-1">
							<h2 className="text-xl font-black uppercase tracking-tight">
								Engine Interface Access
							</h2>
							<p className="text-sm text-muted-foreground font-medium">
								Manage cryptographic keys for external integrations.
							</p>
						</div>
						<Separator className="bg-border/50" />
						<div className="space-y-6">
							<div className="p-6 rounded-2xl border-2 border-dashed bg-muted/10 space-y-4">
								<div className="space-y-2">
									<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Master API Link
									</Label>
									<div className="flex gap-2">
										<Input
											type="password"
											value="************************"
											disabled
											className="h-12 bg-background border-none rounded-xl font-mono shadow-sm"
										/>
										<Button
											variant="outline"
											className="h-12 rounded-xl px-6 font-black uppercase tracking-widest text-[10px]"
										>
											REGEN
										</Button>
									</div>
								</div>
								<p className="text-[10px] text-muted-foreground font-medium leading-relaxed italic">
									Caution: API keys grant deep access to the graph repository.
									Never expose these in client-side codebases.
								</p>
							</div>
						</div>
					</TabsContent>

					<TabsContent
						value="notifications"
						className="mt-0 space-y-8 animate-in slide-in-from-right-2 duration-300"
					>
						<div className="space-y-1">
							<h2 className="text-xl font-black uppercase tracking-tight">
								Telemetry & Comms
							</h2>
							<p className="text-sm text-muted-foreground font-medium">
								Control notification frequency and channels.
							</p>
						</div>
						<Separator className="bg-border/50" />
						<div className="space-y-4">
							{[
								{
									id: "e",
									label: "Email Dispatches",
									set: setEmailNotifications,
									state: emailNotifications,
									sub: "System status and daily digests",
								},
								{
									id: "d",
									label: "Desktop Stream",
									set: setDesktopNotifications,
									state: desktopNotifications,
									sub: "Real-time push alerts for link changes",
								},
								{
									id: "w",
									label: "Executive Weekly",
									set: setWeeklySummary,
									state: weeklySummary,
									sub: "Intelligence summary of project health",
								},
							].map((n) => (
								<div
									key={n.id}
									className="flex items-center justify-between p-5 rounded-2xl bg-muted/30 hover:bg-muted/50 transition-colors"
								>
									<div className="space-y-1">
										<p className="text-sm font-bold uppercase tracking-tight">
											{n.label}
										</p>
										<p className="text-[10px] font-medium text-muted-foreground uppercase">
											{n.sub}
										</p>
									</div>
									<Checkbox
										checked={n.state}
										onCheckedChange={(checked) => n.set(checked as boolean)}
										className="h-6 w-6 rounded-lg border-2"
									/>
								</div>
							))}
						</div>
					</TabsContent>

					<TabsContent
						value="integrations"
						className="mt-0 space-y-8 animate-in slide-in-from-right-2 duration-300"
					>
						<div className="space-y-1">
							<h2 className="text-xl font-black uppercase tracking-tight">
								Account Integrations
							</h2>
							<p className="text-sm text-muted-foreground font-medium">
								Link external accounts once, then map them per project.
							</p>
						</div>
						<Separator className="bg-border/50" />
						<div className="space-y-4">
							<div className="space-y-2">
								<Label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">
									Project Context
								</Label>
								<Select
									value={integrationProjectId || "none"}
									onValueChange={(value) =>
										setIntegrationProjectId(value === "none" ? "" : value)
									}
								>
									<SelectTrigger className="h-12 bg-muted/30 border-none rounded-xl font-bold">
										<SelectValue placeholder="Select a project to link accounts" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="none" className="font-bold">
											No project selected
										</SelectItem>
										{Array.isArray(projects) &&
											projects.map((project) => (
												<SelectItem
													key={project.id}
													value={project.id}
													className="font-bold"
												>
													{getProjectDisplayName(project)}
												</SelectItem>
											))}
									</SelectContent>
								</Select>
							</div>

							{integrationProjectId ? (
								<IntegrationsView
									projectId={integrationProjectId}
									mode="account"
									initialTab="overview"
								/>
							) : (
								<div className="text-sm text-muted-foreground">
									Select a project to link external accounts.
								</div>
							)}
						</div>
					</TabsContent>

					{/* Sticky Action Footer for Mobile/Desktop */}
					<div className="fixed bottom-0 left-0 lg:left-72 right-0 p-6 bg-background/80 backdrop-blur-md border-t z-50">
						<div className="max-w-5xl mx-auto flex justify-end gap-4">
							<Button
								variant="ghost"
								className="rounded-xl px-8 font-black uppercase tracking-[0.2em] text-[10px]"
							>
								Reset Panel
							</Button>
							<Button
								onClick={handleSave}
								disabled={saveSettingsMutation.isPending}
								className="rounded-xl px-12 font-black uppercase tracking-[0.2em] text-[10px] shadow-xl shadow-primary/20 gap-3 h-12"
							>
								{saveSettingsMutation.isPending ? (
									<RefreshCcw className="h-4 w-4 animate-spin" />
								) : (
									<Save className="h-4 w-4" />
								)}
								Synchronize Parameters
							</Button>
						</div>
					</div>
				</div>
			</Tabs>
		</div>
	);
}
