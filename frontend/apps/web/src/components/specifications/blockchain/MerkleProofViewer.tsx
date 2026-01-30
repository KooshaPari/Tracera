/**
 * Merkle Proof Viewer Component
 * Displays Merkle tree proof for baseline verification
 */

import { cn } from "@/lib/utils";

interface MerkleProofViewerProps {
	root: string;
	proof: string[];
	leafIndex: number;
	leafHash: string;
	verified: boolean;
	verificationPath?: Array<{ direction: string; hash: string }>;
	treeSize?: number;
	algorithm?: string;
	className?: string;
}

export function MerkleProofViewer({
	root,
	proof,
	leafIndex,
	leafHash,
	verified,
	verificationPath,
	treeSize,
	algorithm = "SHA-256",
	className,
}: MerkleProofViewerProps) {
	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-lg font-semibold flex items-center gap-2">
						<span>🌳</span>
						Merkle Proof
					</h3>
					<p className="text-sm text-muted-foreground">
						{algorithm} • {treeSize ?? proof.length + 1} items in tree
					</p>
				</div>
				<div>
					{verified ? (
						<span className="px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-md font-medium flex items-center gap-1.5">
							<span className="text-green-600">✓</span>
							Verified
						</span>
					) : (
						<span className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-md font-medium flex items-center gap-1.5">
							<span className="text-red-600">✕</span>
							Verification Failed
						</span>
					)}
				</div>
			</div>

			{/* Root Hash */}
			<div className="p-3 bg-primary/5 border border-primary/20 rounded-lg">
				<div className="text-xs text-muted-foreground mb-1">Merkle Root</div>
				<code className="text-sm font-mono break-all">{root}</code>
			</div>

			{/* Leaf Info */}
			<div className="grid grid-cols-2 gap-3">
				<div className="p-3 bg-muted rounded-lg">
					<div className="text-xs text-muted-foreground mb-1">Leaf Index</div>
					<div className="font-mono text-lg">{leafIndex}</div>
				</div>
				<div className="p-3 bg-muted rounded-lg">
					<div className="text-xs text-muted-foreground mb-1">Leaf Hash</div>
					<code className="text-xs font-mono break-all">{leafHash}</code>
				</div>
			</div>

			{/* Proof Visualization */}
			{verificationPath && verificationPath.length > 0 && (
				<div className="space-y-2">
					<h4 className="text-sm font-medium">Verification Path</h4>
					<div className="relative pl-8">
						{/* Vertical line */}
						<div className="absolute left-3 top-2 bottom-2 w-0.5 bg-border" />

						{/* Leaf */}
						<div className="relative mb-3">
							<div className="absolute left-[-20px] top-2 w-2 h-2 rounded-full bg-green-500" />
							<div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
								<div className="text-xs text-green-600 font-medium mb-1">
									Leaf (Index {leafIndex})
								</div>
								<code className="text-xs font-mono break-all">
									{leafHash.slice(0, 32)}...
								</code>
							</div>
						</div>

						{/* Path nodes */}
						{verificationPath.map((node, idx) => (
							<div key={idx} className="relative mb-3">
								<div className="absolute left-[-20px] top-2 w-2 h-2 rounded-full bg-blue-500" />
								<div className="p-2 bg-blue-50 border border-blue-200 rounded text-sm">
									<div className="flex items-center gap-2 mb-1">
										<span className="text-xs text-blue-600 font-medium">
											Level {idx + 1}
										</span>
										<span
											className={cn(
												"px-1.5 py-0.5 text-xs rounded",
												node.direction === "left"
													? "bg-orange-100 text-orange-700"
													: "bg-purple-100 text-purple-700",
											)}
										>
											{node.direction === "left"
												? "← Left sibling"
												: "→ Right sibling"}
										</span>
									</div>
									<code className="text-xs font-mono break-all">
										{node.hash.slice(0, 32)}...
									</code>
								</div>
							</div>
						))}

						{/* Root */}
						<div className="relative">
							<div className="absolute left-[-20px] top-2 w-2 h-2 rounded-full bg-primary" />
							<div className="p-2 bg-primary/10 border border-primary/30 rounded text-sm">
								<div className="text-xs text-primary font-medium mb-1">
									Root
								</div>
								<code className="text-xs font-mono break-all">
									{root.slice(0, 32)}...
								</code>
							</div>
						</div>
					</div>
				</div>
			)}

			{/* Proof Hashes */}
			<div className="space-y-2">
				<h4 className="text-sm font-medium">Proof ({proof.length} hashes)</h4>
				<div className="max-h-48 overflow-y-auto space-y-1 p-2 bg-muted rounded-lg">
					{proof.map((hash, idx) => (
						<div key={idx} className="flex items-center gap-2 text-xs">
							<span className="text-muted-foreground w-4">{idx}</span>
							<code className="font-mono flex-1 break-all">{hash}</code>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

interface MerkleVerificationBadgeProps {
	verified: boolean;
	proofLength?: number;
	className?: string;
}

export function MerkleVerificationBadge({
	verified,
	proofLength,
	className,
}: MerkleVerificationBadgeProps) {
	return (
		<div
			className={cn(
				"inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm font-medium",
				verified ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700",
				className,
			)}
		>
			<span>🌳</span>
			{verified ? (
				<>
					<span>Merkle Verified</span>
					<span className="text-green-600">✓</span>
				</>
			) : (
				<>
					<span>Verification Failed</span>
					<span className="text-red-600">✕</span>
				</>
			)}
			{proofLength !== undefined && (
				<span className="opacity-70">({proofLength} hashes)</span>
			)}
		</div>
	);
}
