import type {
	IntegrationCredential,
	IntegrationMapping,
	IntegrationProvider,
	SyncConflict,
} from "@tracertm/types";
import { useState } from "react";
import {
	useConflicts,
	useCreateMapping,
	useCredentials,
	useDeleteCredential,
	useGitHubProjects,
	useGitHubRepos,
	useIntegrationStats,
	useLinearProjects,
	useMappings,
	useResolveConflict,
	useStartOAuth,
	useSyncStatus,
	useTriggerSync,
	useValidateCredential,
} from "../../../hooks/useIntegrations";

interface IntegrationsViewProps {
	projectId: string;
	mode?: "project" | "account";
	initialTab?: "overview" | "credentials" | "mappings" | "sync" | "conflicts";
	allowedTabs?: Array<
		"overview" | "credentials" | "mappings" | "sync" | "conflicts"
	>;
}

export default function IntegrationsView({
	projectId,
	mode = "project",
	initialTab = "overview",
	allowedTabs,
}: IntegrationsViewProps) {
	const [activeTab, setActiveTab] = useState<
		"overview" | "credentials" | "mappings" | "sync" | "conflicts"
	>(initialTab);

	const { data: statsData, isLoading: statsLoading } =
		useIntegrationStats(projectId);
	const { data: credentialsData, isLoading: credentialsLoading } =
		useCredentials(projectId);
	const { data: mappingsData, isLoading: mappingsLoading } =
		useMappings(projectId);
	const { data: syncStatus, isLoading: syncLoading } = useSyncStatus(projectId);
	const { data: conflictsData, isLoading: conflictsLoading } = useConflicts(
		projectId,
		"pending",
	);

	const defaultTabs =
		mode === "account"
			? [
					{ id: "overview", label: "Overview" },
					{ id: "credentials", label: "Credentials" },
				]
			: [
					{ id: "overview", label: "Overview" },
					{ id: "mappings", label: "Mappings" },
					{ id: "sync", label: "Sync Status" },
					{ id: "conflicts", label: "Conflicts" },
				];
	const tabs = (
		allowedTabs
			? defaultTabs.filter((tab) =>
					allowedTabs.includes(
						tab.id as
							| "overview"
							| "credentials"
							| "mappings"
							| "sync"
							| "conflicts",
					),
				)
			: defaultTabs
	) as Array<{
		id: "overview" | "credentials" | "mappings" | "sync" | "conflicts";
		label: string;
	}>;

	return (
		<div className="p-6">
			<div className="mb-6">
				<h1 className="text-2xl font-bold text-gray-900 dark:text-white">
					External Integrations
				</h1>
				<p className="text-gray-600 dark:text-gray-400">
					Connect GitHub, GitHub Projects, and Linear to sync items
					bidirectionally.
				</p>
			</div>

			{/* Tabs */}
			<div className="border-b border-gray-200 dark:border-gray-700 mb-6">
				<nav className="flex space-x-8">
					{tabs.map((tab) => (
						<button
							type="button"
							key={tab.id}
							onClick={() => setActiveTab(tab.id)}
							className={`py-2 px-1 border-b-2 font-medium text-sm ${
								activeTab === tab.id
									? "border-blue-500 text-blue-600 dark:text-blue-400"
									: "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
							}`}
						>
							{tab.label}
							{tab.id === "conflicts" &&
								conflictsData &&
								conflictsData.total > 0 && (
									<span className="ml-2 bg-red-100 text-red-800 text-xs font-medium px-2 py-0.5 rounded dark:bg-red-900 dark:text-red-300">
										{conflictsData.total}
									</span>
								)}
						</button>
					))}
				</nav>
			</div>

			{/* Tab Content */}
			{activeTab === "overview" && (
				<OverviewTab
					stats={statsData}
					isLoading={statsLoading}
					projectId={projectId}
					mode={mode}
				/>
			)}
			{activeTab === "credentials" && mode !== "project" && (
				<CredentialsTab
					credentials={credentialsData?.credentials || []}
					isLoading={credentialsLoading}
					projectId={projectId}
				/>
			)}
			{activeTab === "mappings" && mode !== "account" && (
				<MappingsTab
					mappings={mappingsData?.mappings || []}
					isLoading={mappingsLoading}
					projectId={projectId}
				/>
			)}
			{activeTab === "sync" && mode !== "account" && (
				<SyncTab
					syncStatus={syncStatus}
					isLoading={syncLoading}
					projectId={projectId}
				/>
			)}
			{activeTab === "conflicts" && mode !== "account" && (
				<ConflictsTab
					conflicts={conflictsData?.conflicts || []}
					isLoading={conflictsLoading}
				/>
			)}
		</div>
	);
}

// ==================== Overview Tab ====================

function OverviewTab({
	stats,
	isLoading,
	projectId,
	mode,
}: {
	stats: any;
	isLoading: boolean;
	projectId: string;
	mode: "project" | "account";
}) {
	const startOAuth = useStartOAuth();

	const handleConnect = async (provider: IntegrationProvider) => {
		const redirectUri = `${window.location.origin}/integrations/callback`;
		try {
			const result = await startOAuth.mutateAsync({
				projectId,
				provider,
				redirectUri,
				credentialScope: mode === "account" ? "user" : "project",
			});
			// Redirect to OAuth provider
			window.location.href = result.auth_url;
		} catch (error) {
			console.error("Failed to start OAuth:", error);
		}
	};

	if (isLoading) {
		return <div className="animate-pulse">Loading stats...</div>;
	}

	return (
		<div className="space-y-6">
			{/* Stats Cards */}
			<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
				<StatCard
					title="Connected Providers"
					value={stats?.providers?.length || 0}
					subtitle="integrations active"
				/>
				<StatCard
					title="Active Mappings"
					value={stats?.mappings?.active || 0}
					subtitle={`of ${stats?.mappings?.total || 0} total`}
				/>
				<StatCard
					title="Sync Success Rate"
					value={`${stats?.sync?.successRate || 0}%`}
					subtitle={`${stats?.sync?.recentSyncs || 0} recent syncs`}
				/>
				<StatCard
					title="Pending Conflicts"
					value={stats?.conflicts?.pending || 0}
					subtitle="need resolution"
					warning={stats?.conflicts?.pending > 0}
				/>
			</div>

			{/* Connect Providers */}
			{mode === "account" ? (
				<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
					<h2 className="text-lg font-semibold mb-4">Connect New Provider</h2>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
						<ProviderCard
							name="GitHub"
							description="Sync issues, PRs, and repositories"
							icon="github"
							connected={stats?.providers?.some(
								(p: any) => p.provider === "github",
							)}
							onConnect={() => handleConnect("github")}
						/>
						<ProviderCard
							name="GitHub Projects"
							description="Sync project boards and cards"
							icon="github"
							connected={stats?.providers?.some(
								(p: any) => p.provider === "github_projects",
							)}
							onConnect={() => handleConnect("github_projects")}
						/>
						<ProviderCard
							name="Linear"
							description="Sync issues, projects, and teams"
							icon="linear"
							connected={stats?.providers?.some(
								(p: any) => p.provider === "linear",
							)}
							onConnect={() => handleConnect("linear")}
						/>
					</div>
				</div>
			) : (
				<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
					<h2 className="text-lg font-semibold mb-2">
						Account connections moved
					</h2>
					<p className="text-sm text-gray-500">
						Link external accounts in Settings. Project mappings and sync
						controls live here.
					</p>
				</div>
			)}

			{/* Provider Status */}
			{stats?.providers && stats.providers.length > 0 && (
				<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
					<h2 className="text-lg font-semibold mb-4">Connected Providers</h2>
					<div className="space-y-3">
						{stats.providers.map((provider: any, index: number) => (
							<div
								key={`${provider.provider}-${index}`}
								className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
							>
								<div className="flex items-center space-x-3">
									<ProviderIcon provider={provider.provider} />
									<div>
										<div className="font-medium capitalize">
											{provider.provider.replace("_", " ")}
										</div>
										<div className="text-sm text-gray-500">
											{provider.credentialType}
										</div>
									</div>
								</div>
								<StatusBadge status={provider.status} />
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	);
}

// ==================== Credentials Tab ====================

function CredentialsTab({
	credentials,
	isLoading,
	projectId: _projectId,
}: {
	credentials: IntegrationCredential[];
	isLoading: boolean;
	projectId: string;
}) {
	const deleteCredential = useDeleteCredential();
	const validateCredential = useValidateCredential();

	if (isLoading) {
		return <div className="animate-pulse">Loading credentials...</div>;
	}

	if (credentials.length === 0) {
		return (
			<div className="text-center py-12 text-gray-500">
				No credentials configured. Connect a provider from the Overview tab.
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{credentials.map((cred) => (
				<div
					key={cred.id}
					className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
				>
					<div className="flex items-center justify-between">
						<div className="flex items-center space-x-4">
							<ProviderIcon provider={cred.provider} />
							<div>
								<div className="font-medium capitalize">
									{cred.provider.replace("_", " ")}
								</div>
								<div className="text-sm text-gray-500">
									Type: {cred.credentialType} | Scopes:{" "}
									{cred.scopes?.join(", ") || "none"}
								</div>
								{cred.lastValidatedAt && (
									<div className="text-xs text-gray-400">
										Last validated:{" "}
										{new Date(cred.lastValidatedAt).toLocaleString()}
									</div>
								)}
							</div>
						</div>
						<div className="flex items-center space-x-2">
							<StatusBadge status={cred.status} />
							<button
								type="button"
								onClick={() => validateCredential.mutate(cred.id)}
								disabled={validateCredential.isPending}
								className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
							>
								Validate
							</button>
							<button
								type="button"
								onClick={() => {
									if (confirm("Delete this credential?")) {
										deleteCredential.mutate(cred.id);
									}
								}}
								className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
							>
								Delete
							</button>
						</div>
					</div>
				</div>
			))}
		</div>
	);
}

// ==================== Mappings Tab ====================

function MappingsTab({
	mappings,
	isLoading,
	projectId,
}: {
	mappings: IntegrationMapping[];
	isLoading: boolean;
	projectId: string;
}) {
	const triggerSync = useTriggerSync();
	const createMapping = useCreateMapping();
	const { data: credentialData } = useCredentials(projectId);
	const credentials = credentialData?.credentials || [];
	const [provider, setProvider] = useState<IntegrationProvider>("github");
	const [credentialId, setCredentialId] = useState("");
	const [repoSearch, setRepoSearch] = useState("");
	const [projectOwner, setProjectOwner] = useState("");
	const [projectOwnerIsOrg, setProjectOwnerIsOrg] = useState(false);

	const providerCredentials = credentials.filter(
		(cred) => cred.provider === provider,
	);

	const activeCredentialId = credentialId || providerCredentials[0]?.id || "";

	const { data: githubRepos } = useGitHubRepos(
		provider === "github" ? activeCredentialId : "",
		repoSearch || undefined,
		1,
	);
	const { data: githubProjects } = useGitHubProjects(
		provider === "github_projects" ? activeCredentialId : "",
		projectOwner,
		projectOwnerIsOrg,
	);
	const { data: linearProjects } = useLinearProjects(
		provider === "linear" ? activeCredentialId : "",
	);

	const handleCreateMapping = async ({
		externalId,
		externalType,
		externalUrl,
		externalKey,
		mappingMetadata,
	}: {
		externalId: string;
		externalType: string;
		externalUrl?: string;
		externalKey?: string;
		mappingMetadata?: Record<string, unknown>;
	}) => {
		if (!activeCredentialId) {
			alert("Select a credential before creating a mapping.");
			return;
		}
		await createMapping.mutateAsync({
			credentialId: activeCredentialId,
			projectId,
			localItemId: projectId,
			localItemType: "project",
			externalId,
			externalType,
			...(externalUrl ? { externalUrl } : {}),
			...(externalKey ? { externalKey } : {}),
			...(mappingMetadata ? { mappingMetadata } : {}),
			direction: "bidirectional",
			syncEnabled: true,
		});
	};

	if (isLoading) {
		return <div className="animate-pulse">Loading mappings...</div>;
	}

	return (
		<div className="space-y-6">
			<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
				<div>
					<h2 className="text-lg font-semibold">Link external repo/project</h2>
					<p className="text-sm text-gray-500">
						Attach this project to an external repository or planning system to
						enable sync.
					</p>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div className="space-y-2">
						<label className="text-xs font-semibold text-gray-500">
							Provider
						</label>
						<select
							className="w-full border rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-900"
							value={provider}
							onChange={(e) =>
								setProvider(e.target.value as IntegrationProvider)
							}
						>
							<option value="github">GitHub</option>
							<option value="github_projects">GitHub Projects</option>
							<option value="linear">Linear</option>
						</select>
					</div>
					<div className="space-y-2 md:col-span-2">
						<label className="text-xs font-semibold text-gray-500">
							Credential
						</label>
						<select
							className="w-full border rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-900"
							value={activeCredentialId}
							onChange={(e) => setCredentialId(e.target.value)}
						>
							{providerCredentials.length === 0 && (
								<option value="">
									No credentials for {provider}. Connect in Settings.
								</option>
							)}
							{providerCredentials.map((cred) => (
								<option key={cred.id} value={cred.id}>
									{cred.providerUserId || cred.id.slice(0, 8)}
								</option>
							))}
						</select>
					</div>
				</div>

				{provider === "github" && (
					<div className="space-y-3">
						<input
							className="w-full border rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-900"
							placeholder="Search repositories..."
							value={repoSearch}
							onChange={(e) => setRepoSearch(e.target.value)}
						/>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
							{(githubRepos?.repos || []).map((repo) => (
								<div
									key={repo.id}
									className="p-3 border rounded-lg flex items-center justify-between gap-3"
								>
									<div>
										<div className="font-medium text-sm">{repo.fullName}</div>
										<div className="text-xs text-gray-500">
											{repo.description || "No description"}
										</div>
									</div>
									<button
										type="button"
										onClick={() =>
											handleCreateMapping({
												externalId: repo.fullName,
												externalType: "github_repo",
												externalUrl: repo.htmlUrl,
												externalKey: repo.fullName,
												mappingMetadata: {
													repo_full_name: repo.fullName,
													external_kind: "repo",
												},
											})
										}
										className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
									>
										Link
									</button>
								</div>
							))}
						</div>
					</div>
				)}

				{provider === "github_projects" && (
					<div className="space-y-3">
						<div className="grid grid-cols-1 md:grid-cols-3 gap-3">
							<input
								className="w-full border rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-900 md:col-span-2"
								placeholder="Owner or org (e.g. vercel)"
								value={projectOwner}
								onChange={(e) => setProjectOwner(e.target.value)}
							/>
							<label className="flex items-center gap-2 text-xs text-gray-600">
								<input
									type="checkbox"
									checked={projectOwnerIsOrg}
									onChange={(e) => setProjectOwnerIsOrg(e.target.checked)}
								/>
								Org owner
							</label>
						</div>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
							{(githubProjects?.projects || []).map((project) => (
								<div
									key={project.id}
									className="p-3 border rounded-lg flex items-center justify-between gap-3"
								>
									<div>
										<div className="font-medium text-sm">{project.title}</div>
										<div className="text-xs text-gray-500">
											{project.description || "No description"}
										</div>
									</div>
									<button
										type="button"
										onClick={() =>
											handleCreateMapping({
												externalId: project.id,
												externalType: "github_project",
												externalUrl: project.url,
												externalKey: project.title,
												mappingMetadata: {
													project_id: project.id,
													project_owner: projectOwner,
													project_owner_is_org: projectOwnerIsOrg,
													external_kind: "project",
												},
											})
										}
										className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
									>
										Link
									</button>
								</div>
							))}
						</div>
					</div>
				)}

				{provider === "linear" && (
					<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
						{(linearProjects?.projects || []).map((project) => (
							<div
								key={project.id}
								className="p-3 border rounded-lg flex items-center justify-between gap-3"
							>
								<div>
									<div className="font-medium text-sm">{project.name}</div>
									<div className="text-xs text-gray-500">
										{project.description || "No description"}
									</div>
								</div>
								<button
									type="button"
									onClick={() =>
										handleCreateMapping({
											externalId: project.id,
											externalType: "linear_project",
											externalUrl: project.url,
											externalKey: project.name,
											mappingMetadata: {
												project_id: project.id,
												external_kind: "project",
											},
										})
									}
									className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
								>
									Link
								</button>
							</div>
						))}
					</div>
				)}
			</div>

			{mappings.length === 0 ? (
				<div className="text-center py-12 text-gray-500">
					No mappings configured. Link a repo or project to enable sync.
				</div>
			) : (
				<div className="space-y-4">
					{mappings.map((mapping) => (
						<div
							key={mapping.id}
							className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
						>
							<div className="flex items-center justify-between">
								<div>
									<div className="flex items-center space-x-2">
										<span className="font-medium">{mapping.localItemType}</span>
										<span className="text-gray-400">
											{mapping.direction === "bidirectional" ? "<->" : "->"}
										</span>
										<span className="font-medium capitalize">
											{mapping.provider} {mapping.externalType}
										</span>
									</div>
									<div className="text-sm text-gray-500 mt-1">
										Local: {mapping.localItemId.substring(0, 8)}... | External:{" "}
										{mapping.externalKey || mapping.externalId}
									</div>
									{mapping.externalUrl && (
										<a
											href={mapping.externalUrl}
											target="_blank"
											rel="noopener noreferrer"
											className="text-sm text-blue-500 hover:underline"
										>
											View external
										</a>
									)}
								</div>
								<div className="flex items-center space-x-2">
									<StatusBadge status={mapping.status} />
									<button
										type="button"
										onClick={() =>
											triggerSync.mutate({
												mappingId: mapping.id,
												direction: "pull",
											})
										}
										disabled={triggerSync.isPending}
										className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
									>
										Sync
									</button>
								</div>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}

// ==================== Sync Tab ====================

function SyncTab({
	syncStatus,
	isLoading,
	projectId: _projectId,
}: {
	syncStatus: any;
	isLoading: boolean;
	projectId: string;
}) {
	if (isLoading) {
		return <div className="animate-pulse">Loading sync status...</div>;
	}

	return (
		<div className="space-y-6">
			{/* Queue Status */}
			<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
				<h2 className="text-lg font-semibold mb-4">Sync Queue</h2>
				<div className="grid grid-cols-4 gap-4">
					<div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded">
						<div className="text-2xl font-bold text-yellow-600">
							{syncStatus?.queue?.pending || 0}
						</div>
						<div className="text-sm text-gray-500">Pending</div>
					</div>
					<div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded">
						<div className="text-2xl font-bold text-blue-600">
							{syncStatus?.queue?.processing || 0}
						</div>
						<div className="text-sm text-gray-500">Processing</div>
					</div>
					<div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded">
						<div className="text-2xl font-bold text-green-600">
							{syncStatus?.queue?.completed || 0}
						</div>
						<div className="text-sm text-gray-500">Completed</div>
					</div>
					<div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded">
						<div className="text-2xl font-bold text-red-600">
							{syncStatus?.queue?.failed || 0}
						</div>
						<div className="text-sm text-gray-500">Failed</div>
					</div>
				</div>
			</div>

			{/* Recent Syncs */}
			<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
				<h2 className="text-lg font-semibold mb-4">Recent Syncs</h2>
				{syncStatus?.recentSyncs?.length > 0 ? (
					<div className="space-y-2">
						{syncStatus.recentSyncs.map((sync: any) => (
							<div
								key={sync.id}
								className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded"
							>
								<div>
									<div className="font-medium">
										{sync.provider} - {sync.eventType}
									</div>
									<div className="text-sm text-gray-500">
										{sync.itemsProcessed} items processed
										{sync.itemsFailed > 0 && `, ${sync.itemsFailed} failed`}
									</div>
								</div>
								<div className="text-right">
									<StatusBadge status={sync.status} />
									<div className="text-xs text-gray-400 mt-1">
										{sync.startedAt &&
											new Date(sync.startedAt).toLocaleString()}
									</div>
								</div>
							</div>
						))}
					</div>
				) : (
					<div className="text-gray-500 text-center py-4">No recent syncs</div>
				)}
			</div>
		</div>
	);
}

// ==================== Conflicts Tab ====================

function ConflictsTab({
	conflicts,
	isLoading,
}: {
	conflicts: SyncConflict[];
	isLoading: boolean;
}) {
	const resolveConflict = useResolveConflict();

	if (isLoading) {
		return <div className="animate-pulse">Loading conflicts...</div>;
	}

	if (conflicts.length === 0) {
		return (
			<div className="text-center py-12 text-gray-500">
				No pending conflicts. All syncs are in harmony.
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{conflicts.map((conflict) => (
				<div
					key={conflict.id}
					className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
				>
					<div className="flex items-center justify-between mb-4">
						<div>
							<div className="font-medium">
								{conflict.conflictType} conflict
								{conflict.fieldName && ` - ${conflict.fieldName}`}
							</div>
							<div className="text-sm text-gray-500">
								Provider: {conflict.provider}
							</div>
						</div>
						<StatusBadge status={conflict.status} />
					</div>

					<div className="grid grid-cols-2 gap-4 mb-4">
						<div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
							<div className="text-sm font-medium text-blue-700 dark:text-blue-300">
								Local Value
							</div>
							<div className="text-sm mt-1 font-mono">
								{JSON.stringify(conflict.localValue, null, 2)}
							</div>
							{conflict.localModifiedAt && (
								<div className="text-xs text-gray-500 mt-2">
									Modified:{" "}
									{new Date(conflict.localModifiedAt).toLocaleString()}
								</div>
							)}
						</div>
						<div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded">
							<div className="text-sm font-medium text-purple-700 dark:text-purple-300">
								External Value
							</div>
							<div className="text-sm mt-1 font-mono">
								{JSON.stringify(conflict.externalValue, null, 2)}
							</div>
							{conflict.externalModifiedAt && (
								<div className="text-xs text-gray-500 mt-2">
									Modified:{" "}
									{new Date(conflict.externalModifiedAt).toLocaleString()}
								</div>
							)}
						</div>
					</div>

					<div className="flex space-x-2">
						<button
							type="button"
							onClick={() =>
								resolveConflict.mutate({
									conflictId: conflict.id,
									resolution: "local",
								})
							}
							disabled={resolveConflict.isPending}
							className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
						>
							Use Local
						</button>
						<button
							type="button"
							onClick={() =>
								resolveConflict.mutate({
									conflictId: conflict.id,
									resolution: "external",
								})
							}
							disabled={resolveConflict.isPending}
							className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
						>
							Use External
						</button>
						<button
							type="button"
							onClick={() =>
								resolveConflict.mutate({
									conflictId: conflict.id,
									resolution: "skip",
								})
							}
							disabled={resolveConflict.isPending}
							className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
						>
							Skip
						</button>
					</div>
				</div>
			))}
		</div>
	);
}

// ==================== Helper Components ====================

function StatCard({
	title,
	value,
	subtitle,
	warning,
}: {
	title: string;
	value: string | number;
	subtitle: string;
	warning?: boolean;
}) {
	return (
		<div
			className={`bg-white dark:bg-gray-800 rounded-lg border p-4 ${
				warning
					? "border-red-300 dark:border-red-700"
					: "border-gray-200 dark:border-gray-700"
			}`}
		>
			<div className="text-sm text-gray-500">{title}</div>
			<div
				className={`text-2xl font-bold ${warning ? "text-red-600" : "text-gray-900 dark:text-white"}`}
			>
				{value}
			</div>
			<div className="text-xs text-gray-400">{subtitle}</div>
		</div>
	);
}

function ProviderCard({
	name,
	description,
	icon,
	connected,
	onConnect,
}: {
	name: string;
	description: string;
	icon: string;
	connected: boolean;
	onConnect: () => void;
}) {
	return (
		<div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
			<div className="flex items-center space-x-3 mb-2">
				<ProviderIcon provider={icon as IntegrationProvider} />
				<div className="font-medium">{name}</div>
			</div>
			<p className="text-sm text-gray-500 mb-4">{description}</p>
			{connected ? (
				<span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-700">
					Connected
				</span>
			) : (
				<button
					type="button"
					onClick={onConnect}
					className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
				>
					Connect
				</button>
			)}
		</div>
	);
}

function ProviderIcon({
	provider,
}: {
	provider: IntegrationProvider | string;
}) {
	const className = "w-8 h-8";

	if (provider === "github" || provider === "github_projects") {
		return (
			<svg className={className} viewBox="0 0 24 24" fill="currentColor">
				<title>GitHub</title>
				<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
			</svg>
		);
	}

	if (provider === "linear") {
		return (
			<svg className={className} viewBox="0 0 100 100" fill="currentColor">
				<title>Linear</title>
				<path d="M1.22 61.4a48.97 48.97 0 0 0 37.38 37.38l-37.38-37.38zm-1.1-8.96a49.48 49.48 0 0 0 48.44 47.44L.12 52.44zm-.12-9.34a49.36 49.36 0 0 0 57.78 57.78L0 43.1zm.67-9.08l65.21 65.21a50.25 50.25 0 0 0 6.73-6.73L7.4 27.29a50.25 50.25 0 0 0-6.73 6.73zm12.5-12.5l65.21 65.21a49.68 49.68 0 0 0 5.51-8.6L13.77 13.27a49.68 49.68 0 0 0-5.6 8.6L12.17 21.87zm10.02-8.71l64.1 64.1a49.93 49.93 0 0 0 3.98-10.37L25.09 9.72a49.93 49.93 0 0 0-10.37 3.98l7.47 7.46zm15.38-3.16l62 62a49.06 49.06 0 0 0 1.43-14.3L40.87 8.57a49.06 49.06 0 0 0-14.3 1.43l11.0 11.0zM50 0a49.33 49.33 0 0 0-8.96.82L99.18 58.96A49.33 49.33 0 0 0 100 50c0-27.61-22.39-50-50-50z" />
			</svg>
		);
	}

	return (
		<div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
			?
		</div>
	);
}

function StatusBadge({ status }: { status: string }) {
	const colors: Record<string, string> = {
		active:
			"bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
		completed:
			"bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
		pending:
			"bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
		processing:
			"bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
		failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
		error: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
		expired:
			"bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
		paused: "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400",
	};

	return (
		<span
			className={`px-2 py-1 rounded text-xs font-medium ${colors[status] || "bg-gray-100 text-gray-700"}`}
		>
			{status}
		</span>
	);
}
