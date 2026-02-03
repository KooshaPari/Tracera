/**
 * CreateItemDialog Usage Example
 *
 * This file demonstrates how to use the CreateItemDialog component
 * in your views/pages.
 */

import { CreateItemDialog } from "./CreateItemDialog";
import type { ViewType } from "@tracertm/types";
import { useCallback, useState } from "react";

const CreateItemDialogInstructions = () => (
	<div className="mt-8 space-y-4">
		<h2 className="text-xl font-semibold">How it works:</h2>
		<ol className="list-decimal list-inside space-y-2">
			<li>Click &quot;Create New Item&quot; to open the dialog</li>
			<li>Select an item type from the available options (based on current view)</li>
			<li>Fill in the type-specific form</li>
			<li>Submit to create the item (currently mocked with console.log)</li>
			<li>Or click &quot;Back&quot; to return to type selection</li>
		</ol>
		<h2 className="text-xl font-semibold mt-6">Props:</h2>
		<ul className="list-disc list-inside space-y-2">
			<li><code className="bg-muted px-1 py-0.5 rounded">open</code>: boolean - Controls dialog visibility</li>
			<li><code className="bg-muted px-1 py-0.5 rounded">onOpenChange</code>: (open: boolean) =&gt; void</li>
			<li><code className="bg-muted px-1 py-0.5 rounded">projectId</code>: string</li>
			<li><code className="bg-muted px-1 py-0.5 rounded">defaultView</code>: ViewType</li>
		</ul>
		<h2 className="text-xl font-semibold mt-6">Available Item Types:</h2>
		<ul className="list-disc list-inside space-y-2">
			<li>Test, Requirement, Epic, User Story, Task, Defect/Bug</li>
		</ul>
	</div>
);

export const CreateItemDialogExample = () => {
	const [isOpen, setIsOpen] = useState(false);
	const projectId = "example-project-123";
	const currentView: ViewType = "TEST";
	const onOpenClick = useCallback(() => setIsOpen(true), []);

	return (
		<div className="p-4">
			<h1 className="text-2xl font-bold mb-4">CreateItemDialog Example</h1>
			<button
				type="button"
				onClick={onOpenClick}
				className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
			>
				Create New Item
			</button>
			<CreateItemDialog
				open={isOpen}
				onOpenChange={setIsOpen}
				projectId={projectId}
				defaultView={currentView}
			/>
			<CreateItemDialogInstructions />
		</div>
	);
};
