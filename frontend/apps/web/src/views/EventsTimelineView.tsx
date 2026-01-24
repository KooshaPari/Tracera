import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import { FileText } from "lucide-react";
import { useState } from "react";

interface Event {
	id: string;
	type: "item_created" | "item_updated" | "link_created" | "project_created";
	title: string;
	description: string;
	timestamp: Date;
	user: string;
}

export function EventsTimelineView() {
	const [searchQuery, setSearchQuery] = useState("");
	const [typeFilter, setTypeFilter] = useState<string>("");

	// Mock events - replace with actual API call
	const events: Event[] = [
		{
			id: "1",
			type: "item_created",
			title: "Item created",
			description: 'New requirement "User Authentication" created',
			timestamp: new Date(),
			user: "John Doe",
		},
		{
			id: "2",
			type: "link_created",
			title: "Link created",
			description: "Connected requirement to feature",
			timestamp: new Date(Date.now() - 3600000),
			user: "Jane Smith",
		},
	];

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-3xl font-bold">Events Timeline</h1>
				<p className="text-gray-600">View activity history</p>
			</div>

			<Card className="p-4">
				<div className="flex gap-4">
					<Input
						type="search"
						placeholder="Search events..."
						value={searchQuery}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
							setSearchQuery((e.currentTarget as HTMLInputElement).value)
						}
						className="flex-1"
					/>
					<select
						value={typeFilter}
						onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
							setTypeFilter((e.currentTarget as HTMLSelectElement).value)
						}
						className="px-3 py-2 border rounded-md"
					>
						<option value="">All Types</option>
						<option value="item_created">Item Created</option>
						<option value="item_updated">Item Updated</option>
						<option value="link_created">Link Created</option>
					</select>
				</div>
			</Card>

			<div className="space-y-4">
				{events.map((event) => (
					<Card key={event.id} className="p-6">
						<div className="flex items-start gap-4">
							<div className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
								<FileText className="h-4 w-4" />
							</div>
							<div className="flex-1">
								<div className="flex items-center gap-2 mb-1">
									<h3 className="font-semibold">{event.title}</h3>
									<Badge variant="secondary">{event.type}</Badge>
								</div>
								<p className="text-gray-600 dark:text-gray-400 mb-2">
									{event.description}
								</p>
								<div className="text-sm text-gray-500">
									{event.user} • {event.timestamp.toLocaleString()}
								</div>
							</div>
						</div>
					</Card>
				))}
			</div>
		</div>
	);
}
