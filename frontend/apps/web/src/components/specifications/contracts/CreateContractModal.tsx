import { type FC, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

interface CreateContractModalProps {
	readonly isOpen: boolean;
	readonly onClose: () => void;
}

export const CreateContractModal: FC<CreateContractModalProps> = ({
	isOpen,
	onClose,
}) => {
	const handleCreate = useCallback(async () => {
		toast.error("Not implemented - API integration required");
	}, []);

	if (!isOpen) return null;

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center">
			<button
				type="button"
				className="fixed inset-0 bg-black/50 backdrop-blur-sm"
				aria-label="Close dialog"
				onClick={onClose}
			/>
			<div
				className="relative w-full max-w-2xl rounded-xl border bg-background p-6 shadow-2xl"
				role="dialog"
				aria-modal="true"
				aria-labelledby="create-contract-title"
			>
				<div className="flex items-center justify-between mb-6">
					<h2 id="create-contract-title" className="text-lg font-semibold">
						Create New Contract
					</h2>
					<button
						type="button"
						onClick={onClose}
						aria-label="Close dialog"
						className="rounded-lg p-1 hover:bg-accent"
					>
						✕
					</button>
				</div>

				<div className="space-y-4">
					<div>
						<label
							htmlFor="contract-title"
							className="block text-sm font-medium mb-1"
						>
							Title
						</label>
						<Input
							id="contract-title"
							placeholder="e.g., User API Contract"
							className="h-10"
						/>
					</div>

					<div className="grid gap-4 sm:grid-cols-2">
						<div>
							<label
								htmlFor="contract-type"
								className="block text-sm font-medium mb-1"
							>
								Type
							</label>
							<select
								id="contract-type"
								className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
							>
								<option value="api">API</option>
								<option value="function">Function</option>
								<option value="invariant">Invariant</option>
								<option value="data">Data</option>
								<option value="integration">Integration</option>
							</select>
						</div>

						<div>
							<label
								htmlFor="contract-status"
								className="block text-sm font-medium mb-1"
							>
								Status
							</label>
							<select
								id="contract-status"
								className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
							>
								<option value="draft">Draft</option>
								<option value="active">Active</option>
								<option value="verified">Verified</option>
								<option value="violated">Violated</option>
								<option value="deprecated">Deprecated</option>
							</select>
						</div>
					</div>

					<div>
						<label
							htmlFor="contract-description"
							className="block text-sm font-medium mb-1"
						>
							Description
						</label>
						<textarea
							id="contract-description"
							placeholder="Describe the contract..."
							className="w-full h-24 px-3 py-2 rounded-lg border border-input bg-background"
						/>
					</div>

					<div className="flex justify-end gap-2 pt-4">
						<Button variant="ghost" onClick={onClose}>
							Cancel
						</Button>
						<Button onClick={handleCreate}>Create Contract</Button>
					</div>
				</div>
			</div>
		</div>
	);
};
