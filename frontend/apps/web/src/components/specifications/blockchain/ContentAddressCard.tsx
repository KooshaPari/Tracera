/**
 * Content Address Card Component
 * Displays IPFS-style content addressing information
 */

import { useCallback, useState } from "react";

import { cn } from "@/lib/utils";

const COPY_RESET_MS = 2000;

const formatDate = (dateStr: string): string => {
	const date = new Date(dateStr);
	return date.toLocaleString();
};

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

const ContentAddressCardHeader = ({
	versionNumber,
	digitalSignature,
	signatureValid,
}: Pick<
	ContentAddressCardProps,
	"versionNumber" | "digitalSignature" | "signatureValid"
>) => (
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
				) : (signatureValid === false ? (
					<span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md font-medium flex items-center gap-1">
						<span>⚠</span>
						Invalid Signature
					</span>
				) : (
					<span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-md font-medium flex items-center gap-1">
						<span>🔏</span>
						Signed
					</span>
				))}
			</div>
		)}
	</div>
);

export const ContentAddressCard = ({
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
}: ContentAddressCardProps) => {
	const [copiedField, setCopiedField] = useState<string | null>(null);

	const copyToClipboard = useCallback(async (text: string, field: string) => {
		try {
			await navigator.clipboard.writeText(text);
			setCopiedField(field);
			setTimeout(() => setCopiedField(null), COPY_RESET_MS);
		} catch {
			// Clipboard API not available
		}
	}, []);

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			<ContentAddressCardHeader
				digitalSignature={digitalSignature}
				signatureValid={signatureValid}
				versionNumber={versionNumber}
			/>
			<div className="space-y-3">
				<HashField
					copied={copiedField === "cid"}
					fieldId="cid"
					highlight
					icon="📦"
					label="Content CID (IPFS-style)"
					onCopy={copyToClipboard}
					value={contentCid}
				/>
				<HashField
					copied={copiedField === "hash"}
					fieldId="hash"
					icon="🔒"
					label="Content Hash (SHA-256)"
					onCopy={copyToClipboard}
					value={contentHash}
				/>
			</div>
			{(versionChainHead || previousVersionHash) && (
				<div className="border-t pt-4 space-y-3">
					<h4 className="text-sm font-medium">Version Chain</h4>
					{versionChainHead && (
						<HashField
							copied={copiedField === "chain"}
							fieldId="chain"
							icon="⛓"
							label="Chain Head"
							onCopy={copyToClipboard}
							value={versionChainHead}
						/>
					)}
					{previousVersionHash && (
						<HashField
							copied={copiedField === "prev"}
							fieldId="prev"
							icon="⬅"
							label="Previous Version"
							onCopy={copyToClipboard}
							value={previousVersionHash}
						/>
					)}
				</div>
			)}
			{digitalSignature && (
				<div className="border-t pt-4">
					<HashField
						copied={copiedField === "sig"}
						fieldId="sig"
						icon="🔏"
						label="Digital Signature"
						onCopy={copyToClipboard}
						value={digitalSignature}
					/>
				</div>
			)}
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
};

interface HashFieldProps {
	label: string;
	value: string;
	icon?: string;
	fieldId: string;
	onCopy?: (text: string, field: string) => void;
	copied?: boolean;
	highlight?: boolean;
}

const HashField = ({
	label,
	value,
	icon,
	fieldId,
	onCopy,
	copied,
	highlight,
}: HashFieldProps) => {
	const handleClick = useCallback(() => {
		onCopy?.(value, fieldId);
	}, [value, fieldId, onCopy]);
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
						type="button"
						onClick={handleClick}
						className="text-xs px-2 py-0.5 rounded hover:bg-muted-foreground/10 transition-colors"
					>
						{copied ? "Copied!" : "Copy"}
					</button>
				)}
			</div>
			<code className="text-xs font-mono break-all">{value}</code>
		</div>
	);
};

const CID_PREVIEW_LENGTH = 12;

interface ContentAddressBadgeProps {
	contentCid: string;
	versionNumber: number;
	signed?: boolean;
	className?: string;
}

export const ContentAddressBadge = ({
	contentCid,
	versionNumber,
	signed,
	className,
}: ContentAddressBadgeProps) => (
	<div
		className={cn(
			"inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-muted text-sm",
			className,
		)}
	>
		<span>📍</span>
		<code className="font-mono text-xs">
			{contentCid.slice(0, CID_PREVIEW_LENGTH)}...
		</code>
		<span className="text-muted-foreground">v{versionNumber}</span>
		{signed && <span title="Digitally signed">🔏</span>}
	</div>
);

interface ContentHashComparisonProps {
	currentHash: string;
	baselineHash: string;
	className?: string;
}

export const ContentHashComparison = ({
	currentHash,
	baselineHash,
	className,
}: ContentHashComparisonProps) => {
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
};
