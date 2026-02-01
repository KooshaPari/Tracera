// Timeline View - Horizontal version timeline with markers and zoom controls

import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	CalendarDays,
	ChevronLeft,
	ChevronRight,
	ZoomIn,
	ZoomOut,
} from "lucide-react";
import { useMemo, useState } from "react";
import type { Version } from "./TemporalNavigator";

export interface TimelineViewProps {
	versions: Version[];
	currentVersionId: string;
	onVersionChange: (versionId: string) => void;
}

export function TimelineView({
	versions,
	currentVersionId,
	onVersionChange,
}: TimelineViewProps) {
	const [zoomLevel, setZoomLevel] = useState(1);
	const [scrollOffset, setScrollOffset] = useState(0);

	const sortedVersions = useMemo(
		() =>
			[...versions].sort(
				(a, b) => a.timestamp.getTime() - b.timestamp.getTime(),
			),
		[versions],
	);

	const timeRange = useMemo(() => {
		if (sortedVersions.length === 0) {
			return { min: 0, max: 0, span: 1 };
		}
		const min = sortedVersions[0].timestamp.getTime();
		const max = sortedVersions[sortedVersions.length - 1].timestamp.getTime();
		return { min, max, span: max - min };
	}, [sortedVersions]);

	const getDaysAgo = (timestamp: Date): string => {
		const now = new Date();
		const diff = now.getTime() - timestamp.getTime();
		const days = Math.floor(diff / 86400000);

		if (days === 0) return "Today";
		if (days === 1) return "Yesterday";
		if (days < 7) return `${days} days ago`;
		if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
		if (days < 365) return `${Math.floor(days / 30)} months ago`;
		return `${Math.floor(days / 365)} years ago`;
	};

	const handleScroll = (direction: "left" | "right") => {
		const delta = 100;
		setScrollOffset((prev) =>
			direction === "left" ? Math.max(prev - delta, 0) : prev + delta,
		);
	};

	return (
		<div className="flex flex-col gap-4 p-4 bg-white dark:bg-gray-950">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<Button
						size="sm"
						variant="outline"
						onClick={() => handleScroll("left")}
						className="w-8 h-8 p-0"
					>
						<ChevronLeft className="w-4 h-4" />
					</Button>
					<span className="text-xs text-gray-600 dark:text-gray-400">
						{sortedVersions.length} versions
					</span>
					<Button
						size="sm"
						variant="outline"
						onClick={() => handleScroll("right")}
						className="w-8 h-8 p-0"
					>
						<ChevronRight className="w-4 h-4" />
					</Button>
				</div>

				<div className="flex items-center gap-2">
					<span className="text-xs text-gray-600 dark:text-gray-400">
						Zoom: {Math.round(zoomLevel * 100)}%
					</span>
					<Button
						size="sm"
						variant="outline"
						onClick={() => setZoomLevel((z) => Math.max(0.5, z - 0.1))}
						className="w-8 h-8 p-0"
					>
						<ZoomOut className="w-4 h-4" />
					</Button>
					<Button
						size="sm"
						variant="outline"
						onClick={() => setZoomLevel((z) => Math.min(2, z + 0.1))}
						className="w-8 h-8 p-0"
					>
						<ZoomIn className="w-4 h-4" />
					</Button>
				</div>
			</div>

			<div className="relative">
				<div className="absolute top-6 left-0 right-0 h-1 bg-gray-200 dark:bg-gray-700 rounded-full" />

				<div
					className="flex gap-4 overflow-x-auto pb-2"
					style={{
						transform: `translateX(-${scrollOffset}px)`,
						transition: "transform 0.3s ease-out",
					}}
				>
					{sortedVersions.map((version) => {
						const isCurrentVersion = version.id === currentVersionId;

						return (
							<div
								key={version.id}
								className="relative flex-shrink-0 pt-1"
								style={{
									minWidth: 150 * zoomLevel,
								}}
								onClick={() => onVersionChange(version.id)}
								onKeyDown={(e) => {
									if (e.key === "Enter") onVersionChange(version.id);
								}}
								role="button"
								tabIndex={0}
							>
								<div
									className={cn(
										"absolute left-1/2 top-3 w-4 h-4 rounded-full border-2 transform -translate-x-1/2 cursor-pointer transition-all",
										isCurrentVersion
											? "bg-blue-500 border-blue-600 ring-2 ring-blue-300 dark:ring-blue-700 scale-125"
											: "bg-white dark:bg-gray-800 border-gray-400 dark:border-gray-600 hover:scale-110",
									)}
								/>

								<div
									className={cn(
										"mt-8 p-3 rounded-lg border transition-all hover:shadow-md",
										isCurrentVersion
											? "bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700 shadow-md"
											: "bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600",
									)}
								>
									<div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
										{version.tag && (
											<Badge variant="outline" className="mr-1 text-xs">
												{version.tag}
											</Badge>
										)}
										{version.title}
									</div>

									<div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
										<div className="flex items-center gap-1 mt-1">
											<CalendarDays className="w-3 h-3" />
											{getDaysAgo(version.timestamp)}
										</div>
									</div>

									{version.author && (
										<div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
											by {version.author}
										</div>
									)}

									<div className="mt-2">
										<Badge
											variant={
												version.status === "published"
													? "default"
													: version.status === "draft"
														? "secondary"
														: "outline"
											}
											className="text-xs"
										>
											{version.status}
										</Badge>
									</div>

									{version.description && (
										<p className="text-xs text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
											{version.description}
										</p>
									)}
								</div>
							</div>
						);
					})}
				</div>
			</div>

			{sortedVersions.length > 0 && (
				<div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-800">
					<span>
						{sortedVersions[0].timestamp.toLocaleDateString()} -
						{sortedVersions[
							sortedVersions.length - 1
						].timestamp.toLocaleDateString()}
					</span>
					<span>
						{sortedVersions.length} version
						{sortedVersions.length === 1 ? "" : "s"}
					</span>
				</div>
			)}

			{sortedVersions.length === 0 && (
				<div className="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400">
					<p>No versions in this branch yet</p>
				</div>
			)}
		</div>
	);
}
