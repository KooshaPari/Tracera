import { Link } from "@tanstack/react-router";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import { Input } from "@tracertm/ui/components/Input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { useState } from "react";
import { useSearch } from "../hooks/useSearch";

export function SearchView() {
	const [query, setQuery] = useState("");
	const [filters, setFilters] = useState({
		type: "",
		status: "",
		project: "",
	});

	const { results, isLoading } = useSearch({ q: query, ...filters });

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-3xl font-bold">Search</h1>
				<p className="text-muted-foreground">Find items, projects, and links</p>
			</div>

			<Card className="p-4">
				<div className="space-y-4">
					<Input
						type="search"
						placeholder="Search everything..."
						value={query}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
							setQuery((e.currentTarget as HTMLInputElement).value)
						}
						autoFocus
					/>

					<div className="flex gap-2">
						<Select
							value={filters.type || "all"}
							onValueChange={(value) =>
								setFilters({
									...filters,
									type: value === "all" ? "" : value,
								})
							}
						>
							<SelectTrigger>
								<SelectValue placeholder="All Types" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">All Types</SelectItem>
								<SelectItem value="requirement">Requirement</SelectItem>
								<SelectItem value="feature">Feature</SelectItem>
								<SelectItem value="test">Test</SelectItem>
							</SelectContent>
						</Select>
						<Select
							value={filters.status || "all"}
							onValueChange={(value) =>
								setFilters({
									...filters,
									status: value === "all" ? "" : value,
								})
							}
						>
							<SelectTrigger>
								<SelectValue placeholder="All Statuses" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="all">All Statuses</SelectItem>
								<SelectItem value="todo">To Do</SelectItem>
								<SelectItem value="in_progress">In Progress</SelectItem>
								<SelectItem value="done">Done</SelectItem>
							</SelectContent>
						</Select>
					</div>
				</div>
			</Card>

			{isLoading && <Skeleton className="h-64" />}

			{results?.items && results.items.length > 0 && (
				<div>
					<h2 className="text-xl font-semibold mb-4">
						Results ({results.items.length})
					</h2>
					<div className="space-y-3">
						{results.items.map((item) => (
							<Link key={item.id} to={`/items/${item.id}`}>
								<Card className="p-4 hover:shadow-md transition-shadow">
									<div className="flex items-start gap-3">
										<div className="flex-1">
											<div className="flex items-center gap-2 mb-1">
												<h3 className="font-medium">{item.title}</h3>
												<Badge variant="secondary">{item.type}</Badge>
											</div>
											{item.description && (
												<p className="text-sm text-muted-foreground line-clamp-2">
													{item.description}
												</p>
											)}
										</div>
									</div>
								</Card>
							</Link>
						))}
					</div>
				</div>
			)}

			{query && results && results.items?.length === 0 && (
				<Card className="p-12 text-center text-muted-foreground">
					<p>No results found for "{query}"</p>
				</Card>
			)}
		</div>
	);
}
