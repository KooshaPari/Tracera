// Thumbnail Preview Component
// Displays thumbnails on hover, lazy loads full screenshots
// Supports version selector and fallback to component code

import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Code, ExternalLink, Image as ImageIcon } from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { logger } from "@/lib/logger";
import { generateThumbnail } from "../../utils/screenshot";
import type { ScreenshotMetadata } from "../../utils/screenshot";

export type VersionType = "design" | "draft" | "review" | "release";

const VERSION_COLORS: Record<VersionType, string> = {
	design: "#8b5cf6", // Violet
	draft: "#f59e0b", // Amber
	review: "#3b82f6", // Blue
	release: "#22c55e", // Green
};

const VERSION_LABELS: Record<VersionType, string> = {
	design: "Design",
	draft: "Draft",
	release: "Release",
	review: "Review",
};

interface ThumbnailPreviewProps {
	/** URL of the screenshot thumbnail */
	thumbnailUrl?: string;
	/** URL of the full screenshot */
	screenshotUrl?: string;
	/** Component code to display as fallback */
	componentCode?: string;
	/** Version of the screenshot */
	version?: string;
	/** Type of version */
	versionType?: VersionType;
	/** Available versions to select from */
	versions?: ScreenshotMetadata[];
	/** Called when version is selected */
	onVersionChange?: (metadata: ScreenshotMetadata) => void;
	/** Title/label */
	label?: string;
	/** Show as card or inline */
	variant?: "card" | "inline";
	/** Custom CSS class */
	className?: string;
}

function ThumbnailPreviewComponent({
	thumbnailUrl,
	screenshotUrl,
	componentCode,
	version,
	versionType = "draft",
	versions = [],
	onVersionChange,
	label,
	variant = "card",
	className,
}: ThumbnailPreviewProps) {
	const [isLoading, setIsLoading] = useState(false);
	const [selectedVersion, setSelectedVersion] = useState(versionType);
	const [displayScreenshot, setDisplayScreenshot] = useState<string | null>(
		null,
	);
	const [showFullScreenshot, setShowFullScreenshot] = useState(false);

	// Generate thumbnail from screenshot URL if needed
	useEffect(() => {
		let cancelled = false;

		async function generateAndSetThumbnail() {
			if (!thumbnailUrl && screenshotUrl) {
				setIsLoading(true);
				try {
					const generated = await generateThumbnail(screenshotUrl, "medium");
					if (!cancelled) {
						setDisplayScreenshot(generated);
					}
				} catch (error) {
					logger.error("Failed to generate thumbnail:", error);
				} finally {
					if (!cancelled) {
						setIsLoading(false);
					}
				}
			} else if (thumbnailUrl && !cancelled) {
				setDisplayScreenshot(thumbnailUrl);
			}
		}

		undefined;

		return () => {
			cancelled = true;
		};
	}, [thumbnailUrl, screenshotUrl]);

	const handleVersionSelect = useCallback(
		(versionId: string) => {
			const selected = versions.find((v) => v.id === versionId);
			if (selected) {
				setSelectedVersion(selected.versionType);
				setDisplayScreenshot(selected.thumbnailUrl || selected.url);
				onVersionChange?.(selected);
			}
		},
		[versions, onVersionChange],
	);

	const versionColor = VERSION_COLORS[selectedVersion];
	const versionLabel = VERSION_LABELS[selectedVersion];

	// Content rendering based on available data
	const hasScreenshot = displayScreenshot || screenshotUrl;
	const hasCode = componentCode;

	const content = useMemo(() => {
		if (showFullScreenshot && screenshotUrl) {
			return (
				<div className="relative w-full bg-muted/50 rounded-lg overflow-hidden">
					<img
						src={screenshotUrl}
						alt="Full screenshot"
						className="w-full h-auto"
						onLoad={() => setIsLoading(false)}
						onError={() => setIsLoading(false)}
					/>
					<Button
						variant="secondary"
						size="sm"
						className="absolute top-2 right-2"
						onClick={() => setShowFullScreenshot(false)}
					>
						Close
					</Button>
				</div>
			);
		}

		if (isLoading) {
			return <Skeleton className="w-full h-48 rounded-lg" />;
		}

		if (hasScreenshot && displayScreenshot) {
			return (
				<TooltipProvider>
					<Tooltip>
						<TooltipTrigger asChild>
							<div
								className="relative w-full bg-muted/50 rounded-lg overflow-hidden cursor-pointer group"
								onClick={() => setShowFullScreenshot(true)}
							>
								<img
									src={displayScreenshot}
									alt={label || "Screenshot"}
									className="w-full h-auto group-hover:opacity-75 transition-opacity"
								/>
								<div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
									<ImageIcon className="w-6 h-6 text-white" />
								</div>
							</div>
						</TooltipTrigger>
						<TooltipContent>Click to view full screenshot</TooltipContent>
					</Tooltip>
				</TooltipProvider>
			);
		}

		if (hasCode) {
			return (
				<div className="relative w-full bg-muted p-3 rounded-lg font-mono text-xs overflow-x-auto max-h-48">
					<Code className="w-4 h-4 text-muted-foreground mb-2" />
					<pre className="text-muted-foreground">
						<code>{componentCode}</code>
					</pre>
				</div>
			);
		}

		return (
			<div className="w-full h-48 rounded-lg border-2 border-dashed border-muted-foreground/20 flex items-center justify-center">
				<div className="text-center">
					<ImageIcon className="w-8 h-8 text-muted-foreground/40 mx-auto mb-2" />
					<p className="text-sm text-muted-foreground">No preview available</p>
				</div>
			</div>
		);
	}, [
		showFullScreenshot,
		screenshotUrl,
		displayScreenshot,
		isLoading,
		hasScreenshot,
		hasCode,
		componentCode,
		label,
	]);

	if (variant === "inline") {
		return (
			<div className={cn("inline-block", className)}>
				<TooltipProvider>
					<Tooltip delayDuration={300}>
						<TooltipTrigger asChild>
							<div className="h-24 w-24 rounded-lg overflow-hidden border bg-muted/50 cursor-pointer">
								{displayScreenshot ? (
									<img
										src={displayScreenshot}
										alt={label}
										className="w-full h-full object-cover"
									/>
								) : (
									<div className="w-full h-full flex items-center justify-center">
										<ImageIcon className="w-4 h-4 text-muted-foreground/50" />
									</div>
								)}
							</div>
						</TooltipTrigger>
						<TooltipContent side="right" className="w-72">
							<div className="space-y-2">
								{label && <p className="font-semibold">{label}</p>}
								{displayScreenshot && (
									<img
										src={displayScreenshot}
										alt={label}
										className="w-full rounded-md border"
									/>
								)}
								{version && (
									<Badge variant="secondary" className="text-xs">
										{version}
									</Badge>
								)}
							</div>
						</TooltipContent>
					</Tooltip>
				</TooltipProvider>
			</div>
		);
	}

	return (
		<Card className={cn("overflow-hidden", className)}>
			{/* Header */}
			{label && (
				<div className="p-3 border-b bg-muted/30">
					<div className="flex items-center justify-between gap-2">
						<h4 className="font-semibold text-sm">{label}</h4>
						{versions.length > 1 && (
							<Select
								value={selectedVersion}
								onValueChange={handleVersionSelect}
							>
								<SelectTrigger className="w-24 h-7 text-xs">
									<SelectValue placeholder="Version" />
								</SelectTrigger>
								<SelectContent>
									{versions.map((v) => (
										<SelectItem key={v.id} value={v.id}>
											<Badge
												variant="outline"
												style={{
													backgroundColor: `${VERSION_COLORS[v.versionType]}20`,
													borderColor: VERSION_COLORS[v.versionType],
													color: VERSION_COLORS[v.versionType],
												}}
											>
												{VERSION_LABELS[v.versionType]}
											</Badge>
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						)}
					</div>
				</div>
			)}

			{/* Content */}
			<div className="p-3 space-y-3">
				{content}

				{/* Version badge */}
				{version && (
					<div className="flex items-center justify-between">
						<span className="text-xs text-muted-foreground">Version</span>
						<Badge
							style={{
								backgroundColor: `${versionColor}20`,
								borderColor: versionColor,
								color: versionColor,
							}}
						>
							{versionLabel} {version}
						</Badge>
					</div>
				)}

				{/* Actions */}
				<div className="flex gap-2">
					{screenshotUrl && (
						<Button
							variant="outline"
							size="sm"
							className="flex-1 text-xs"
							onClick={() => window.open(screenshotUrl, "_blank")}
						>
							<ExternalLink className="w-3 h-3 mr-1" />
							Open
						</Button>
					)}
					{displayScreenshot && (
						<Button
							variant="secondary"
							size="sm"
							className="flex-1 text-xs"
							onClick={() => setShowFullScreenshot(!showFullScreenshot)}
						>
							<ImageIcon className="w-3 h-3 mr-1" />
							{showFullScreenshot ? "Collapse" : "Expand"}
						</Button>
					)}
				</div>
			</div>
		</Card>
	);
}

export const ThumbnailPreview = memo(ThumbnailPreviewComponent);
