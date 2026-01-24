import { useMutation } from "@tanstack/react-query";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
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
import { useState } from "react";
import { toast } from "sonner";
import { Checkbox } from "@/components/ui/checkbox";
import { saveSettings } from "../api/settings";

export function SettingsView() {
	const [theme, setTheme] = useState<"light" | "dark" | "system">("system");
	const [apiKey, setApiKey] = useState("");
	const [displayName, setDisplayName] = useState("");
	const [email, setEmail] = useState("");
	const [fontSize, setFontSize] = useState("medium");
	const [emailNotifications, setEmailNotifications] = useState(true);
	const [desktopNotifications, setDesktopNotifications] = useState(false);
	const [weeklySummary, setWeeklySummary] = useState(true);

	const saveSettingsMutation = useMutation({
		mutationFn: async (settings: {
			displayName?: string;
			email?: string;
			theme?: string;
			fontSize?: string;
			emailNotifications?: boolean;
			desktopNotifications?: boolean;
			weeklySummary?: boolean;
		}) => {
			return saveSettings(settings);
		},
		onSuccess: () => {
			toast.success("Settings saved successfully!");
		},
		onError: (error) => {
			toast.error(`Failed to save settings: ${error.message}`);
		},
	});

	return (
		<div className="space-y-6 p-6">
			<div>
				<h1 className="text-3xl font-bold tracking-tight">Settings</h1>
				<p className="mt-2 text-muted-foreground">
					Manage your preferences and configuration
				</p>
			</div>

			<Card className="p-6">
				<Tabs defaultValue="general">
					<TabsList>
						<TabsTrigger value="general">General</TabsTrigger>
						<TabsTrigger value="appearance">Appearance</TabsTrigger>
						<TabsTrigger value="api">API Keys</TabsTrigger>
						<TabsTrigger value="notifications">Notifications</TabsTrigger>
					</TabsList>

					<TabsContent value="general">
						<div className="space-y-6 mt-6">
							<div className="space-y-2">
								<Label htmlFor="display-name">Display Name</Label>
								<Input
									id="display-name"
									placeholder="Your name"
									value={displayName}
									onChange={(e) => setDisplayName(e.target.value)}
								/>
							</div>
							<div className="space-y-2">
								<Label htmlFor="email">Email</Label>
								<Input
									id="email"
									type="email"
									placeholder="your@email.com"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
								/>
							</div>
							<div className="space-y-2">
								<Label htmlFor="timezone">Timezone</Label>
								<Select value="UTC" onValueChange={() => {}}>
									<SelectTrigger id="timezone">
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="UTC">UTC</SelectItem>
										<SelectItem value="America/New_York">
											Eastern Time
										</SelectItem>
										<SelectItem value="America/Chicago">
											Central Time
										</SelectItem>
										<SelectItem value="America/Denver">
											Mountain Time
										</SelectItem>
										<SelectItem value="America/Los_Angeles">
											Pacific Time
										</SelectItem>
									</SelectContent>
								</Select>
							</div>
							<Separator />
							<Button
								onClick={() =>
									saveSettingsMutation.mutate({
										displayName,
										email,
										theme,
										fontSize,
									})
								}
								disabled={saveSettingsMutation.isPending}
							>
								{saveSettingsMutation.isPending ? "Saving..." : "Save Changes"}
							</Button>
						</div>
					</TabsContent>

					<TabsContent value="appearance">
						<div className="space-y-6 mt-6">
							<div className="space-y-2">
								<Label htmlFor="theme-select">Theme</Label>
								<Select
									value={theme}
									onValueChange={(v) => setTheme(v as typeof theme)}
								>
									<SelectTrigger id="theme-select">
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="light">Light</SelectItem>
										<SelectItem value="dark">Dark</SelectItem>
										<SelectItem value="system">System</SelectItem>
									</SelectContent>
								</Select>
							</div>
							<div className="space-y-2">
								<Label htmlFor="font-size-select">Font Size</Label>
								<Select value={fontSize} onValueChange={setFontSize}>
									<SelectTrigger id="font-size-select">
										<SelectValue />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="small">Small</SelectItem>
										<SelectItem value="medium">Medium</SelectItem>
										<SelectItem value="large">Large</SelectItem>
									</SelectContent>
								</Select>
							</div>
							<div className="flex items-center space-x-2">
								<Checkbox id="compact-mode" />
								<Label
									htmlFor="compact-mode"
									className="text-sm font-normal cursor-pointer"
								>
									Use compact layout
								</Label>
							</div>
							<Separator />
							<Button
								onClick={() =>
									saveSettingsMutation.mutate({
										theme,
										fontSize,
									})
								}
								disabled={saveSettingsMutation.isPending}
							>
								{saveSettingsMutation.isPending ? "Saving..." : "Save Changes"}
							</Button>
						</div>
					</TabsContent>

					<TabsContent value="api">
						<div className="space-y-6 mt-6">
							<div className="space-y-2">
								<Label htmlFor="api-key">API Key</Label>
								<Input
									id="api-key"
									type="password"
									value={apiKey}
									onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
										setApiKey((e.currentTarget as HTMLInputElement).value)
									}
									placeholder="Enter API key"
								/>
								<p className="text-sm text-muted-foreground">
									Used for external integrations and webhooks
								</p>
							</div>
							<Separator />
							<div className="flex gap-2">
								<Button>Generate New Key</Button>
								<Button variant="outline">Revoke Key</Button>
							</div>
						</div>
					</TabsContent>

					<TabsContent value="notifications">
						<div className="space-y-6 mt-6">
							<div className="flex items-center justify-between">
								<div className="space-y-0.5">
									<Label
										htmlFor="email-notifications"
										className="cursor-pointer"
									>
										Email Notifications
									</Label>
									<p className="text-sm text-muted-foreground">
										Receive email updates
									</p>
								</div>
								<Checkbox
									id="email-notifications"
									checked={emailNotifications}
									onCheckedChange={(checked) =>
										setEmailNotifications(checked as boolean)
									}
								/>
							</div>
							<Separator />
							<div className="flex items-center justify-between">
								<div className="space-y-0.5">
									<Label
										htmlFor="desktop-notifications"
										className="cursor-pointer"
									>
										Desktop Notifications
									</Label>
									<p className="text-sm text-muted-foreground">
										Browser push notifications
									</p>
								</div>
								<Checkbox
									id="desktop-notifications"
									checked={desktopNotifications}
									onCheckedChange={(checked) =>
										setDesktopNotifications(checked as boolean)
									}
								/>
							</div>
							<Separator />
							<div className="flex items-center justify-between">
								<div className="space-y-0.5">
									<Label htmlFor="weekly-summary" className="cursor-pointer">
										Weekly Summary
									</Label>
									<p className="text-sm text-muted-foreground">
										Get a weekly digest
									</p>
								</div>
								<Checkbox
									id="weekly-summary"
									checked={weeklySummary}
									onCheckedChange={(checked) =>
										setWeeklySummary(checked as boolean)
									}
								/>
							</div>
							<Separator />
							<div className="flex items-center justify-between">
								<div className="space-y-0.5">
									<Label htmlFor="item-updates" className="cursor-pointer">
										Item Updates
									</Label>
									<p className="text-sm text-muted-foreground">
										Notify when items change
									</p>
								</div>
								<Checkbox id="item-updates" />
							</div>
							<Separator />
							<Button
								onClick={() =>
									saveSettingsMutation.mutate({
										emailNotifications,
										desktopNotifications,
										weeklySummary,
									})
								}
								disabled={saveSettingsMutation.isPending}
							>
								{saveSettingsMutation.isPending
									? "Saving..."
									: "Save Preferences"}
							</Button>
						</div>
					</TabsContent>
				</Tabs>
			</Card>
		</div>
	);
}
