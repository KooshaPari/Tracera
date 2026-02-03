/**
 * DiffViewer - Field-by-field diff visualization for modified items
 *
 * Features:
 * - Side-by-side field comparison
 * - Visual highlighting of old/new values
 * - Expandable field details
 * - Copy value functionality
 * - JSON value formatting
 */

import type { DiffItem, DiffViewerState, FieldDiffChange } from "@repo/types";
import { CheckCircle, ChevronDown, ChevronUp, Copy } from "lucide-react";
import { useState } from "react";

interface DiffViewerProps {
	item: DiffItem;
	fieldChanges: FieldDiffChange[];
	viewerState: DiffViewerState;
	compact?: boolean;
}

export function DiffViewer({ fieldChanges, compact = false }: DiffViewerProps) {
	const [copiedField, setCopiedField] = useState<string | null>(null);

	const handleCopyValue = (value: unknown, field: string) => {
		const text = formatValueForCopy(value);
		undefined;
	};

	return (
		<div className="space-y-4">
			<div className="text-sm font-medium text-gray-700">
				{fieldChanges.length} field{fieldChanges.length !== 1 ? "s" : ""}{" "}
				changed
			</div>

			<div className="space-y-3">
				{fieldChanges.map((change) => (
					<FieldChangeRow
						key={change.field}
						change={change}
						onCopy={handleCopyValue}
						isCopied={copiedField === change.field}
						compact={compact}
					/>
				))}
			</div>
		</div>
	);
}

interface FieldChangeRowProps {
	change: FieldDiffChange;
	onCopy: (value: unknown, field: string) => void;
	isCopied: boolean;
	compact?: boolean;
}

function getChangeTypeColor(changeType: string) {
	switch (changeType) {
		case "added": {
			return "bg-green-50 border-l-green-500 text-green-900";
		}
		case "removed": {
			return "bg-red-50 border-l-red-500 text-red-900";
		}
		case "modified": {
			return "bg-blue-50 border-l-blue-500 text-blue-900";
		}
		default: {
			return "bg-gray-50 border-l-gray-500";
		}
	}
}

function FieldChangeRow({
	change,
	onCopy,
	isCopied,
	compact = false,
}: FieldChangeRowProps) {
	const [expanded, setExpanded] = useState(!compact);

	return (
		<div
			className={`border-l-4 ${getChangeTypeColor(change.changeType)} rounded-r-lg`}
		>
			<div className="p-4">
				{/* Field Header */}
				<div
					className="flex items-center justify-between cursor-pointer"
					onClick={() => setExpanded(!expanded)}
				>
					<div className="flex items-center gap-2">
						{expanded ? (
							<ChevronUp className="w-4 h-4 text-gray-500" />
						) : (
							<ChevronDown className="w-4 h-4 text-gray-500" />
						)}
						<span className="font-semibold text-sm">{change.field}</span>
						<ChangeTypeBadge type={change.changeType} />
					</div>
				</div>

				{/* Expanded Content */}
				{expanded && (
					<div className="mt-3 space-y-2">
						{change.changeType !== "added" && (
							<ValueDisplay
								label="Old Value"
								value={change.oldValue}
								type="old"
								onCopy={() => onCopy(change.oldValue, change.field)}
								isCopied={isCopied}
							/>
						)}

						{change.changeType !== "removed" && (
							<ValueDisplay
								label="New Value"
								value={change.newValue}
								type="new"
								onCopy={() => onCopy(change.newValue, change.field)}
								isCopied={isCopied}
							/>
						)}
					</div>
				)}
			</div>
		</div>
	);
}

interface ChangeTypeBadgeProps {
	type: string;
}

function ChangeTypeBadge({ type }: ChangeTypeBadgeProps) {
	const badges: Record<string, { bg: string; text: string; label: string }> = {
		added: {
			bg: "bg-green-100",
			label: "Added",
			text: "text-green-800",
		},
		modified: {
			bg: "bg-blue-100",
			label: "Modified",
			text: "text-blue-800",
		},
		removed: {
			bg: "bg-red-100",
			label: "Removed",
			text: "text-red-800",
		},
	};

	const badge = badges[type] || badges.modified;

	return (
		<span
			className={`inline-block px-2 py-1 text-xs font-medium rounded ${badge.bg} ${badge.text}`}
		>
			{badge.label}
		</span>
	);
}

interface ValueDisplayProps {
	label: string;
	value: unknown;
	type: "old" | "new";
	onCopy: () => void;
	isCopied: boolean;
}

function ValueDisplay({
	label,
	value,
	type,
	onCopy,
	isCopied,
}: ValueDisplayProps) {
	const isComplex = typeof value === "object" && value !== null;

	return (
		<div className="bg-white rounded border border-gray-200">
			<div className="px-3 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
				<span className="text-xs font-medium text-gray-600">{label}</span>
				<button
					onClick={onCopy}
					className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
					title="Copy to clipboard"
				>
					{isCopied ? (
						<CheckCircle className="w-4 h-4 text-green-600" />
					) : (
						<Copy className="w-4 h-4" />
					)}
				</button>
			</div>
			<div
				className={`px-3 py-3 font-mono text-sm break-words max-h-48 overflow-y-auto ${
					type === "old"
						? "bg-red-50 text-red-900"
						: "bg-green-50 text-green-900"
				}`}
			>
				{isComplex ? (
					<pre className="whitespace-pre-wrap">
						{JSON.stringify(value, null, 2)}
					</pre>
				) : value === null || value === undefined ? (
					<span className="italic opacity-60">null</span>
				) : typeof value === "boolean" ? (
					<span>{value ? "true" : "false"}</span>
				) : typeof value === "object" ? (
					<span>{JSON.stringify(value)}</span>
				) : (
					<span>{String(value)}</span>
				)}
			</div>
		</div>
	);
}

// Helper functions
function formatValueForCopy(value: unknown): string {
	if (value === null || value === undefined) {
		return "null";
	}
	if (typeof value === "object") {
		return JSON.stringify(value, null, 2);
	}
	return String(value);
}

export default DiffViewer;
export type { DiffViewerProps };
