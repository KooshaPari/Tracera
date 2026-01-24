import { Link, useNavigate, useParams } from "@tanstack/react-router";
import { Alert } from "@tracertm/ui/components/Alert";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Label } from "@tracertm/ui/components/Label";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import { useMemo, useState } from "react";
import { useDeleteItem, useItem } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

export function ItemDetailView() {
	const params = useParams({ strict: false });
	const itemId = params.itemId as string | undefined;
	const navigate = useNavigate();
	const { data: item, isLoading, error } = useItem(itemId!);
	const deleteItem = useDeleteItem();

	// Fetch links where this item is either source or target (only after item loads)
	const { data: sourceLinksData } = useLinks({
		sourceId: itemId,
		projectId: item?.projectId,
	});
	const { data: targetLinksData } = useLinks({
		targetId: itemId,
		projectId: item?.projectId,
	});

	const [isEditing, setIsEditing] = useState(false);

	// Combine source and target links, removing duplicates
	// Must be called before any early returns
	const { sourceLinks, targetLinks } = useMemo(() => {
		const sourceArray = sourceLinksData?.links ?? [];
		const targetArray = targetLinksData?.links ?? [];
		const allLinks = [...sourceArray, ...targetArray];
		const uniqueLinks = Array.from(
			new Map(allLinks.map((l) => [l.id, l])).values(),
		);
		return {
			sourceLinks: uniqueLinks.filter((l) => l.sourceId === item?.id),
			targetLinks: uniqueLinks.filter((l) => l.targetId === item?.id),
		};
	}, [sourceLinksData, targetLinksData, item?.id]);

	const handleDelete = async () => {
		if (!(itemId && confirm("Delete this item?"))) return;
		try {
			await deleteItem.mutateAsync(itemId);
			navigate({ to: "/items" });
		} catch (err) {
			console.error("Failed to delete item:", err);
		}
	};

	if (isLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<Skeleton className="h-64" />
			</div>
		);
	}

	if (error || !item) {
		return <Alert variant="destructive">Failed to load item</Alert>;
	}

	return (
		<div className="space-y-6">
			{/* Breadcrumb */}
			<div className="flex items-center text-sm text-muted-foreground">
				<Link to="/items" className="hover:text-foreground transition-colors">
					Items
				</Link>
				<span className="mx-2">/</span>
				<span className="text-foreground">{item.title}</span>
			</div>

			{/* Header */}
			<div className="flex items-start justify-between">
				<div className="flex-1">
					<div className="flex items-center gap-3 mb-2">
						<h1 className="text-3xl font-bold tracking-tight">{item.title}</h1>
						<Badge variant="secondary">{item.type}</Badge>
						<Badge variant={item.status === "done" ? "default" : "secondary"}>
							{item.status}
						</Badge>
					</div>
					{item.description && (
						<p className="mt-2 text-muted-foreground">{item.description}</p>
					)}
				</div>
				<div className="flex items-center gap-2">
					<Button onClick={() => setIsEditing(!isEditing)}>
						{isEditing ? "Cancel" : "Edit"}
					</Button>
					<Button variant="destructive" onClick={handleDelete}>
						Delete
					</Button>
				</div>
			</div>

			{/* Details */}
			<Card className="p-6">
				<Tabs defaultValue="details">
					<TabsList>
						<TabsTrigger value="details">Details</TabsTrigger>
						<TabsTrigger value="links">
							Links ({sourceLinks.length + targetLinks.length})
						</TabsTrigger>
						<TabsTrigger value="history">History</TabsTrigger>
					</TabsList>

					<TabsContent value="details">
						<div className="grid grid-cols-2 gap-6 mt-6">
							<div>
								<Label className="text-sm font-medium mb-1">Status</Label>
								<p className="text-foreground">{item.status}</p>
							</div>
							<div>
								<Label className="text-sm font-medium mb-1">Priority</Label>
								<p className="text-foreground">{item.priority || "None"}</p>
							</div>
							<div>
								<Label className="text-sm font-medium mb-1">Owner</Label>
								<p className="text-foreground">{item.owner || "Unassigned"}</p>
							</div>
							<div>
								<Label className="text-sm font-medium mb-1">Created</Label>
								<p className="text-foreground">
									{new Date(item.createdAt).toLocaleString()}
								</p>
							</div>
						</div>
					</TabsContent>

					<TabsContent value="links">
						<div className="space-y-6 mt-6">
							<div>
								<h3 className="font-semibold mb-3">
									Outgoing Links ({sourceLinks.length})
								</h3>
								{sourceLinks.length > 0 ? (
									<div className="space-y-2">
										{sourceLinks.map((link) => (
											<div key={link.id} className="p-3 border rounded-lg">
												<div className="flex items-center gap-2">
													<Badge variant="secondary">{link.type}</Badge>
													<span>→ {link.targetId}</span>
												</div>
											</div>
										))}
									</div>
								) : (
									<p className="text-muted-foreground">No outgoing links</p>
								)}
							</div>
							<div>
								<h3 className="font-semibold mb-3">
									Incoming Links ({targetLinks.length})
								</h3>
								{targetLinks.length > 0 ? (
									<div className="space-y-2">
										{targetLinks.map((link) => (
											<div key={link.id} className="p-3 border rounded-lg">
												<div className="flex items-center gap-2">
													<span>{link.sourceId} →</span>
													<Badge variant="secondary">{link.type}</Badge>
												</div>
											</div>
										))}
									</div>
								) : (
									<p className="text-muted-foreground">No incoming links</p>
								)}
							</div>
						</div>
					</TabsContent>

					<TabsContent value="history">
						<div className="mt-6">
							<p className="text-muted-foreground">
								History timeline coming soon
							</p>
						</div>
					</TabsContent>
				</Tabs>
			</Card>
		</div>
	);
}
