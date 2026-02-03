import { type FC, useCallback } from "react";
import type { ContractStatus } from "../../..";
import {
	Button,
	Input,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "lucide-react";
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
			<div
				className="fixed inset-0 bg-black/50 backdrop-blur-sm"
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
							<Select>
								<SelectTrigger id="contract-type" className="h-10">
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="api">API</SelectItem>
									<SelectItem value="function">Function</SelectItem>
									<SelectItem value="invariant">Invariant</SelectItem>
									<SelectItem value="data">Data</SelectItem>
									<SelectItem value="integration">Integration</SelectItem>
								</SelectContent>
							</Select>
						</div>

						<div>
							<label
								htmlFor="contract-status"
								className="block text-sm font-medium mb-1"
							>
								Status
							</label>
							<Select>
								<SelectTrigger id="contract-status" className="h-10">
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="draft">Draft</SelectItem>
									<SelectItem value="active">Active</SelectItem>
									<SelectItem value="verified">Verified</SelectItem>
									<SelectItem value="violated">Violated</SelectItem>
									<SelectItem value="deprecated">Deprecated</SelectItem>
								</SelectContent>
							</Select>
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
