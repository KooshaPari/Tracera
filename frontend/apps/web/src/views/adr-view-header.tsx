/* eslint-disable react/jsx-filename-extension */
/* eslint-disable react/jsx-max-depth */

import { Button, Tabs, TabsList, TabsTrigger } from "@tracertm/ui";
import { History, LayoutList, Plus } from "lucide-react";
import React from "react";

interface ADRViewHeaderProps {
	onCreate: () => void;
	onViewChange: (nextView: "list" | "timeline") => void;
	viewMode: "list" | "timeline";
}

const ADRViewHeader = ({
	onCreate,
	onViewChange,
	viewMode,
}: ADRViewHeaderProps): JSX.Element => {
	const handleValueChange = React.useCallback(
		(nextValue: string) => {
			if (nextValue === "list") {
				onViewChange("list");
				return;
			}

			if (nextValue === "timeline") {
				onViewChange("timeline");
			}
		},
		[onViewChange],
	);

	return (
		<div className="flex justify-between items-center">
			<div>
				<h1 className="text-2xl font-bold">Architecture Decisions</h1>
				<p className="text-muted-foreground">
					Log and track architectural choices (MADR 4.0).
				</p>
			</div>
			<div className="flex gap-2">
				<Tabs value={viewMode} onValueChange={handleValueChange}>
					<TabsList>
						<TabsTrigger value="list">
							<LayoutList className="w-4 h-4" />
						</TabsTrigger>
						<TabsTrigger value="timeline">
							<History className="w-4 h-4" />
						</TabsTrigger>
					</TabsList>
				</Tabs>
				<Button onClick={onCreate}>
					<Plus className="w-4 h-4 mr-2" />
					New ADR
				</Button>
			</div>
		</div>
	);
};

// eslint-disable-next-line import/no-default-export
export default ADRViewHeader;
