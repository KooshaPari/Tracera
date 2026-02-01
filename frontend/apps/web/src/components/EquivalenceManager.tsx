import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import { Download, Link2, Upload } from "lucide-react";
import { useState } from "react";
import {
	EquivalenceExport,
	EquivalenceImport,
	EquivalencePanel,
} from "./graph";

interface EquivalenceManagerProps {
	projectId: string;
}

/**
 * Equivalence Management UI
 * Provides export, import, and equivalence mapping management
 */
export function EquivalenceManager({ projectId }: EquivalenceManagerProps) {
	const [activeTab, setActiveTab] = useState<"panel" | "export" | "import">(
		"panel",
	);

	// Mock data for equivalence components (would be loaded from API)
	const mockEquivalenceLinks = [];
	const mockCanonicalConcepts = [];
	const mockCanonicalProjections = [];

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
						<Link2 className="w-6 h-6" />
						Equivalence Management
					</h2>
					<p className="text-muted-foreground">
						Manage concept equivalence mappings and canonical relationships
					</p>
				</div>
			</div>

			<Tabs
				value={activeTab}
				onValueChange={(tab) => setActiveTab(tab as typeof activeTab)}
				className="w-full"
			>
				<TabsList>
					<TabsTrigger value="panel" className="flex items-center gap-2">
						<Link2 className="w-4 h-4" />
						Equivalence Map
					</TabsTrigger>
					<TabsTrigger value="export" className="flex items-center gap-2">
						<Download className="w-4 h-4" />
						Export
					</TabsTrigger>
					<TabsTrigger value="import" className="flex items-center gap-2">
						<Upload className="w-4 h-4" />
						Import
					</TabsTrigger>
				</TabsList>

				<TabsContent value="panel" className="space-y-4">
					<div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
						<p className="text-sm text-blue-900 dark:text-blue-100">
							View and manage equivalence relationships between items across
							different perspectives. Mark items as representing the same
							concept with confidence levels.
						</p>
					</div>
					<EquivalencePanel projectId={projectId} />
				</TabsContent>

				<TabsContent value="export" className="space-y-4">
					<div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
						<p className="text-sm text-green-900 dark:text-green-100">
							Export equivalence mappings and canonical concepts to JSON or CSV
							format. Useful for sharing with other projects or archiving.
						</p>
					</div>
					<EquivalenceExport
						projectId={projectId}
						equivalenceLinks={mockEquivalenceLinks}
						canonicalConcepts={mockCanonicalConcepts}
						canonicalProjections={mockCanonicalProjections}
					/>
				</TabsContent>

				<TabsContent value="import" className="space-y-4">
					<div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
						<p className="text-sm text-amber-900 dark:text-amber-100">
							Import equivalence mappings from JSON or CSV files. Merge with
							existing mappings or overwrite based on your preferences.
						</p>
					</div>
					<EquivalenceImport projectId={projectId} />
				</TabsContent>
			</Tabs>
		</div>
	);
}
