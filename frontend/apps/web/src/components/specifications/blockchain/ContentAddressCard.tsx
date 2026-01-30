/**
 * Content Address Card Component
 * Displays IPFS-style content addressing information
 */

import { cn } from "@/lib/utils";
import { useState } from "react";

interface ContentAddressCardProps {
	contentHash: string;
	contentCid: string;
	versionChainHead?: string | null;
	previousVersionHash?: string | null;
	versionNumber: number;
	digitalSignature?: string | null;
	signatureValid?: boolean | null;
	createdAt: string;
	lastModifiedAt: string;
	className?: string;
}

export function ContentAddressCard({
	contentHash,
	contentCid,
	versionChainHead,
	previousVersionHash,
	versionNumber,
	digitalSignature,
	signatureValid,
	createdAt,
	lastModifiedAt,
	className,
}: ContentAddressCardProps) {
	const [copiedField, setCopiedField] = useState<string | null>(null);

	const copyToClipboard = async (text: string, field: string) => {
		try {
			await navigator.clipboard.writeText(text);
			setCopiedField(field);
			setTimeout(() => setCopiedField(null), 2000);
		} catch {
			// Clipboard API not available
		}
	};

	const formatDate = (dateStr: string) => {
		const date = new Date(dateStr);
		return date.toLocaleString();
	};

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-lg font-semibold flex items-center gap-2">
						<span>📍</span>
						Content Address
					</h3>
					<p className="text-sm text-muted-foreground">
						Version {versionNumber} • Immutable content identifier
					</p>
				</div>
				{digitalSignature && (
					<div>
						{signatureValid === true ? (
							<span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-md font-medium flex items-center gap-1">
								<span>🔏</span>
								Signed & Valid
							</span>
						) : signatureValid === false ? (
							<span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md font-medium flex items-center gap-1">
								<span>⚠</span>
								Invalid Signature
							</span>
						) : (
							<span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-md font-medium flex items-center gap-1">
								<span>🔏</span>
								Signed
							</span>
						)}
					</div>
				)}
			</div>

			{/* Primary Identifiers */}
			<div className="space-y-3">
				{/* Content CID */}
				<HashField
					label="Content CID (IPFS-style)"
					value={contentCid}
					icon="📦"
					onCopy={() => copyToClipboard(contentCid, "cid")}
					copied={copiedField === "cid"}
					highlight
				/>

				{/* Content Hash */}
				<HashField
					label="Content Hash (SHA-256)"
					value={contentHash}
					icon="🔒"
					onCopy={() => copyToClipboard(contentHash, "hash")}
					copied={copiedField === "hash"}
				/>
			</div>

			{/* Version Chain */}
			{(versionChainHead || previousVersionHash) && (
				<div className="border-t pt-4 space-y-3">
					<h4 className="text-sm font-medium">Version Chain</h4>

					{versionChainHead && (
						<HashField
							label="Chain Head"
							value={versionChainHead}
							icon="⛓"
							onCopy={() => copyToClipboard(versionChainHead, "chain")}
							copied={copiedField === "chain"}
						/>
					)}

					{previousVersionHash && (
						<HashField
							label="Previous Version"
							value={previousVersionHash}
							icon="⬅"
							onCopy={() => copyToClipboard(previousVersionHash, "prev")}
							copied={copiedField === "prev"}
						/>
					)}
				</div>
			)}

			{/* Digital Signature */}
			{digitalSignature && (
				<div className="border-t pt-4">
					<HashField
						label="Digital Signature"
						value={digitalSignature}
						icon="🔏"
						onCopy={() => copyToClipboard(digitalSignature, "sig")}
						copied={copiedField === "sig"}
					/>
				</div>
			)}

			{/* Timestamps */}
			<div className="border-t pt-4 grid grid-cols-2 gap-4 text-sm">
				<div>
					<div className="text-muted-foreground mb-1">Created</div>
					<div>{formatDate(createdAt)}</div>
				</div>
				<div>
					<div className="text-muted-foreground mb-1">Last Modified</div>
					<div>{formatDate(lastModifiedAt)}</div>
				</div>
			</div>
		</div>
	);
}

interface HashFieldProps {
	label: string;
	value: string;
	icon?: string;
	onCopy?: () => void;
	copied?: boolean;
	highlight?: boolean;
}

function HashField({
	label,
	value,
	icon,
	onCopy,
	copied,
	highlight,
}: HashFieldProps) {
	return (
		<div
			className={cn(
				"p-3 rounded-lg",
				highlight ? "bg-primary/5 border border-primary/20" : "bg-muted",
			)}
		>
			<div className="flex items-center justify-between mb-1">
				<div className="flex items-center gap-1.5 text-xs text-muted-foreground">
					{icon && <span>{icon}</span>}
					<span>{label}</span>
				</div>
				{onCopy && (
					<button
						onClick={onCopy}
						className="text-xs px-2 py-0.5 rounded hover:bg-muted-foreground/10 transition-colors"
					>
						{copied ? "Copied!" : "Copy"}
					</button>
				)}
			</div>
			<code className="text-xs font-mono break-all">{value}</code>
		</div>
	);
}

interface ContentAddressBadgeProps {
	contentCid: string;
	versionNumber: number;
	signed?: boolean;
	className?: string;
}

export function ContentAddressBadge({
	contentCid,
	versionNumber,
	signed,
	className,
}: ContentAddressBadgeProps) {
	return (
		<div
			className={cn(
				"inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-muted text-sm",
				className,
			)}
		>
			<span>📍</span>
			<code className="font-mono text-xs">{contentCid.slice(0, 12)}...</code>
			<span className="text-muted-foreground">v{versionNumber}</span>
			{signed && <span title="Digitally signed">🔏</span>}
		</div>
	);
}

interface ContentHashComparisonProps {
	currentHash: string;
	baselineHash: string;
	className?: string;
}

export function ContentHashComparison({
	currentHash,
	baselineHash,
	className,
}: ContentHashComparisonProps) {
	const matches = currentHash === baselineHash;

	return (
		<div className={cn("rounded-lg border p-4 space-y-3", className)}>
			<div className="flex items-center justify-between">
				<h4 className="text-sm font-medium">Content Hash Comparison</h4>
				{matches ? (
					<span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-md font-medium">
						✓ Matches
					</span>
				) : (
					<span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md font-medium">
						✕ Modified
					</span>
				)}
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
				<div className="p-2 bg-muted rounded">
					<div className="text-xs text-muted-foreground mb-1">Current</div>
					<code className="text-xs font-mono break-all">{currentHash}</code>
				</div>
				<div className="p-2 bg-muted rounded">
					<div className="text-xs text-muted-foreground mb-1">Baseline</div>
					<code className="text-xs font-mono break-all">{baselineHash}</code>
				</div>
			</div>

			{!matches && (
				<p className="text-sm text-amber-600">
					⚠ Content has been modified since baseline was established
				</p>
			)}
		</div>
	);
}
