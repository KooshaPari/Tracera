import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { useState } from "react";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

export function ImpactAnalysisView() {
	const { data: itemsData, isLoading: itemsLoading } = useItems();
	const { data: linksData } = useLinks();
	const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

	const items = itemsData?.items ?? [];
	const links = linksData?.links ?? [];

	const analyzeImpact = (itemId: string) => {
		if (!links.length) return { direct: [], indirect: [] };

		const direct = new Set<string>();
		const indirect = new Set<string>();

		// Find direct dependencies
		links.forEach((link: any) => {
			if (link.sourceId === itemId) {
				direct.add(link.targetId);
			}
		});

		// Find indirect dependencies (2 levels)
		direct.forEach((directId) => {
			links.forEach((link: any) => {
				if (link.sourceId === directId && !direct.has(link.targetId)) {
					indirect.add(link.targetId);
				}
			});
		});

		return {
			direct: Array.from(direct),
			indirect: Array.from(indirect),
		};
	};

	const impact = selectedItemId ? analyzeImpact(selectedItemId) : null;
	const selectedItem = items.find((i: any) => i.id === selectedItemId);

	if (itemsLoading) return <Skeleton className="h-screen" />;

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-3xl font-bold">Impact Analysis</h1>
				<p className="text-gray-600">Analyze change impact on related items</p>
			</div>

			<div className="grid grid-cols-2 gap-6">
				<Card className="p-6">
					<h2 className="text-xl font-semibold mb-4">Select Item</h2>
					<div className="space-y-2 max-h-96 overflow-y-auto">
						{items?.map((item) => (
							<div
								key={item.id}
								onClick={() => setSelectedItemId(item.id)}
								className={`p-3 border rounded-lg cursor-pointer hover:border-blue-500 ${
									selectedItemId === item.id
										? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
										: ""
								}`}
							>
								<div className="flex items-center gap-2">
									<span className="font-medium">{item.title}</span>
									<Badge variant="secondary">{item.type}</Badge>
								</div>
							</div>
						))}
					</div>
				</Card>

				<Card className="p-6">
					<h2 className="text-xl font-semibold mb-4">Impact Assessment</h2>
					{selectedItem && impact ? (
						<div className="space-y-6">
							<div>
								<h3 className="font-semibold mb-2">Selected Item</h3>
								<div className="p-3 border rounded-lg">
									<div className="flex items-center gap-2">
										<span className="font-medium">{selectedItem.title}</span>
										<Badge variant="secondary">{selectedItem.type}</Badge>
									</div>
								</div>
							</div>

							<div>
								<h3 className="font-semibold mb-2">
									Direct Impact ({impact.direct.length})
								</h3>
								{impact.direct.length > 0 ? (
									<div className="space-y-2">
										{impact.direct.map((id) => {
											const item = items?.find((i) => i.id === id);
											return item ? (
												<div
													key={id}
													className="p-2 border rounded-lg bg-orange-50 dark:bg-orange-900/20"
												>
													<div className="flex items-center gap-2">
														<span className="text-sm">{item.title}</span>
														<Badge variant="secondary" className="text-xs">
															{item.type}
														</Badge>
													</div>
												</div>
											) : null;
										})}
									</div>
								) : (
									<p className="text-gray-500 text-sm">
										No direct dependencies
									</p>
								)}
							</div>

							<div>
								<h3 className="font-semibold mb-2">
									Indirect Impact ({impact.indirect.length})
								</h3>
								{impact.indirect.length > 0 ? (
									<div className="space-y-2">
										{impact.indirect.map((id) => {
											const item = items?.find((i) => i.id === id);
											return item ? (
												<div
													key={id}
													className="p-2 border rounded-lg bg-yellow-50 dark:bg-yellow-900/20"
												>
													<div className="flex items-center gap-2">
														<span className="text-sm">{item.title}</span>
														<Badge variant="secondary" className="text-xs">
															{item.type}
														</Badge>
													</div>
												</div>
											) : null;
										})}
									</div>
								) : (
									<p className="text-gray-500 text-sm">
										No indirect dependencies
									</p>
								)}
							</div>

							<div className="pt-4 border-t">
								<div className="text-sm text-gray-600">
									Total Impact: {impact.direct.length + impact.indirect.length}{" "}
									items
								</div>
							</div>
						</div>
					) : (
						<div className="text-center py-12 text-gray-500">
							<p>Select an item to analyze impact</p>
						</div>
					)}
				</Card>
			</div>
		</div>
	);
}
