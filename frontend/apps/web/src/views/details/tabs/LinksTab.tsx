/**
 * LinksTab - Shared component for displaying item relationships
 * Shows upstream and downstream links in a consistent format
 */

import { Link } from "@tanstack/react-router";
import type { Link as LinkType } from "@tracertm/types";
import { Card } from "@tracertm/ui";
import { ArrowLeft, ExternalLink } from "lucide-react";

export interface LinksTabProps {
	sourceLinks: LinkType[];
	targetLinks: LinkType[];
	buildItemLink: (id: string) => string;
}

export function LinksTab({
	sourceLinks,
	targetLinks,
	buildItemLink,
}: LinksTabProps) {
	return (
		<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
			{/* Upstream links */}
			<Card className="border-0 bg-muted/40 p-4 space-y-3">
				<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
					Upstream Dependencies
				</h3>
				<div className="space-y-2">
					{targetLinks.length > 0 ? (
						targetLinks.map((link) => (
							<Link
								key={link.id}
								to={buildItemLink(link.sourceId)}
								className="flex items-center gap-3 rounded-xl border bg-card/50 px-3 py-2 hover:bg-muted/60 transition-colors"
							>
								<div className="h-8 w-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
									<ArrowLeft className="h-4 w-4 text-orange-500" />
								</div>
								<div className="flex-1 min-w-0">
									<p className="text-[10px] font-black text-muted-foreground uppercase">
										{link.type}
									</p>
									<p className="text-xs font-bold truncate">{link.sourceId}</p>
								</div>
								<ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
							</Link>
						))
					) : (
						<p className="text-xs text-muted-foreground italic text-center py-4">
							No upstream dependencies
						</p>
					)}
				</div>
			</Card>

			{/* Downstream links */}
			<Card className="border-0 bg-muted/40 p-4 space-y-3">
				<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
					Downstream Impact
				</h3>
				<div className="space-y-2">
					{sourceLinks.length > 0 ? (
						sourceLinks.map((link) => (
							<Link
								key={link.id}
								to={buildItemLink(link.targetId)}
								className="flex items-center gap-3 rounded-xl border bg-card/50 px-3 py-2 hover:bg-muted/60 transition-colors"
							>
								<div className="h-8 w-8 rounded-lg bg-sky-500/10 flex items-center justify-center">
									<ArrowLeft className="h-4 w-4 text-sky-500 rotate-180" />
								</div>
								<div className="flex-1 min-w-0">
									<p className="text-[10px] font-black text-muted-foreground uppercase">
										{link.type}
									</p>
									<p className="text-xs font-bold truncate">{link.targetId}</p>
								</div>
								<ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
							</Link>
						))
					) : (
						<p className="text-xs text-muted-foreground italic text-center py-4">
							No downstream impact
						</p>
					)}
				</div>
			</Card>
		</div>
	);
}
