/**
 * Digital Signature Badge Component
 * Displays signature verification status
 */

import { cn } from "@/lib/utils";

interface DigitalSignatureBadgeProps {
	signature?: string | null;
	valid?: boolean | null;
	signedBy?: string | null;
	signedAt?: string | null;
	algorithm?: string;
	size?: "sm" | "md" | "lg";
	showDetails?: boolean;
	className?: string;
}

export function DigitalSignatureBadge({
	signature,
	valid,
	signedBy,
	signedAt,
	algorithm = "ECDSA",
	size = "md",
	showDetails = false,
	className,
}: DigitalSignatureBadgeProps) {
	if (!signature) {
		return (
			<div
				className={cn(
					"inline-flex items-center gap-1.5 rounded-md border font-medium",
					"bg-gray-100 text-gray-600 border-gray-300",
					sizeClasses[size],
					className,
				)}
			>
				<span>📝</span>
				<span>Unsigned</span>
			</div>
		);
	}

	const statusConfig =
		valid === true
			? {
					bg: "bg-green-100",
					border: "border-green-300",
					icon: "✓",
					label: "Verified",
					text: "text-green-700",
				}
			: (valid === false
				? {
						bg: "bg-red-100",
						text: "text-red-700",
						border: "border-red-300",
						icon: "✕",
						label: "Invalid",
					}
				: {
						bg: "bg-yellow-100",
						text: "text-yellow-700",
						border: "border-yellow-300",
						icon: "?",
						label: "Unverified",
					});

	if (!showDetails) {
		return (
			<div
				className={cn(
					"inline-flex items-center gap-1.5 rounded-md border font-medium",
					statusConfig.bg,
					statusConfig.text,
					statusConfig.border,
					sizeClasses[size],
					className,
				)}
				title={
					signature ? `Signature: ${signature.slice(0, 20)}...` : undefined
				}
			>
				<span>🔏</span>
				<span>{statusConfig.label}</span>
				<span>{statusConfig.icon}</span>
			</div>
		);
	}

	return (
		<div className={cn("rounded-lg border p-3 space-y-2", className)}>
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<span className="text-lg">🔏</span>
					<span className="font-medium">Digital Signature</span>
				</div>
				<div
					className={cn(
						"px-2 py-0.5 rounded text-xs font-medium",
						statusConfig.bg,
						statusConfig.text,
					)}
				>
					{statusConfig.label} {statusConfig.icon}
				</div>
			</div>

			<div className="space-y-1.5 text-sm">
				<div className="flex justify-between">
					<span className="text-muted-foreground">Algorithm</span>
					<span className="font-mono text-xs">{algorithm}</span>
				</div>

				{signedBy && (
					<div className="flex justify-between">
						<span className="text-muted-foreground">Signed By</span>
						<span>{signedBy}</span>
					</div>
				)}

				{signedAt && (
					<div className="flex justify-between">
						<span className="text-muted-foreground">Signed At</span>
						<span>{new Date(signedAt).toLocaleString()}</span>
					</div>
				)}

				<div className="pt-2 border-t">
					<div className="text-xs text-muted-foreground mb-1">Signature</div>
					<code className="text-xs font-mono break-all block p-2 bg-muted rounded">
						{signature}
					</code>
				</div>
			</div>
		</div>
	);
}

const sizeClasses = {
	lg: "text-base px-3 py-1.5",
	md: "text-sm px-2.5 py-1",
	sm: "text-xs px-2 py-0.5",
};

interface SignatureVerificationStatusProps {
	hasSignature: boolean;
	isValid?: boolean | null;
	className?: string;
}

export function SignatureVerificationStatus({
	hasSignature,
	isValid,
	className,
}: SignatureVerificationStatusProps) {
	if (!hasSignature) {
		return (
			<div
				className={cn(
					"flex items-center gap-1.5 text-sm text-muted-foreground",
					className,
				)}
			>
				<span className="w-2 h-2 rounded-full bg-gray-400" />
				<span>Not signed</span>
			</div>
		);
	}

	if (isValid === true) {
		return (
			<div
				className={cn(
					"flex items-center gap-1.5 text-sm text-green-600",
					className,
				)}
			>
				<span className="w-2 h-2 rounded-full bg-green-500" />
				<span>Signature verified</span>
			</div>
		);
	}

	if (isValid === false) {
		return (
			<div
				className={cn(
					"flex items-center gap-1.5 text-sm text-red-600",
					className,
				)}
			>
				<span className="w-2 h-2 rounded-full bg-red-500" />
				<span>Invalid signature</span>
			</div>
		);
	}

	return (
		<div
			className={cn(
				"flex items-center gap-1.5 text-sm text-yellow-600",
				className,
			)}
		>
			<span className="w-2 h-2 rounded-full bg-yellow-500" />
			<span>Signature pending verification</span>
		</div>
	);
}

interface SignatureHistoryProps {
	signatures: {
		signature: string;
		signedBy: string;
		signedAt: string;
		valid: boolean;
		algorithm?: string;
	}[];
	className?: string;
}

export function SignatureHistory({
	signatures,
	className,
}: SignatureHistoryProps) {
	if (signatures.length === 0) {
		return (
			<div
				className={cn(
					"text-sm text-muted-foreground p-4 text-center",
					className,
				)}
			>
				No signature history available
			</div>
		);
	}

	return (
		<div className={cn("space-y-2", className)}>
			{signatures.map((sig, idx) => (
				<div
					key={idx}
					className={cn(
						"p-3 rounded-lg border",
						sig.valid
							? "bg-green-50 border-green-200"
							: "bg-red-50 border-red-200",
					)}
				>
					<div className="flex items-center justify-between mb-2">
						<div className="flex items-center gap-2">
							<span>{sig.valid ? "✓" : "✕"}</span>
							<span className="font-medium">{sig.signedBy}</span>
						</div>
						<span className="text-xs text-muted-foreground">
							{new Date(sig.signedAt).toLocaleString()}
						</span>
					</div>
					<code className="text-xs font-mono break-all opacity-70">
						{sig.signature.slice(0, 40)}...
					</code>
				</div>
			))}
		</div>
	);
}
