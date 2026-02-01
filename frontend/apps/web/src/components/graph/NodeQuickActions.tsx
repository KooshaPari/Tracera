import { Button } from "@tracertm/ui/components/Button";
import { Input } from "@tracertm/ui/components/Input";
import { Label } from "@tracertm/ui/components/Label";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@tracertm/ui/components/Popover";
import { FileEdit, Link2, Tag } from "lucide-react";
import { memo, useState } from "react";

interface NodeQuickActionsProps {
	nodeId: string;
	onAddLink: (nodeId: string, targetId: string) => void;
	onAddTag: (nodeId: string, tag: string) => void;
	onEditNote: (nodeId: string, note: string) => void;
}

export const NodeQuickActions = memo(function NodeQuickActions({
	nodeId,
	onAddLink,
	onAddTag,
	onEditNote,
}: NodeQuickActionsProps) {
	const [linkTarget, setLinkTarget] = useState("");
	const [tag, setTag] = useState("");
	const [note, setNote] = useState("");

	return (
		<div className="flex gap-1" role="group" aria-label="Node quick actions">
			{/* Add Link */}
			<Popover>
				<PopoverTrigger asChild>
					<Button
						size="sm"
						variant="ghost"
						className="h-6 w-6 p-0"
						aria-label="Add link to another node"
						title="Add link to another node"
					>
						<Link2 className="h-3 w-3" aria-hidden="true" />
					</Button>
				</PopoverTrigger>
				<PopoverContent className="w-64">
					<div className="space-y-2">
						<Label htmlFor="link-target">Link to node</Label>
						<div className="flex gap-2">
							<Input
								id="link-target"
								placeholder="Node ID"
								value={linkTarget}
								onChange={(e) => setLinkTarget(e.target.value)}
								aria-required="true"
								aria-label="Target node ID for link"
							/>
							<Button
								size="sm"
								onClick={() => {
									onAddLink(nodeId, linkTarget);
									setLinkTarget("");
								}}
								aria-label="Confirm link addition"
							>
								Add
							</Button>
						</div>
					</div>
				</PopoverContent>
			</Popover>

			{/* Add Tag */}
			<Popover>
				<PopoverTrigger asChild>
					<Button
						size="sm"
						variant="ghost"
						className="h-6 w-6 p-0"
						aria-label="Add tag to node"
						title="Add tag to node"
					>
						<Tag className="h-3 w-3" aria-hidden="true" />
					</Button>
				</PopoverTrigger>
				<PopoverContent className="w-64">
					<div className="space-y-2">
						<Label htmlFor="tag">Add tag</Label>
						<div className="flex gap-2">
							<Input
								id="tag"
								placeholder="Tag name"
								value={tag}
								onChange={(e) => setTag(e.target.value)}
								aria-required="true"
								aria-label="Tag name for node"
							/>
							<Button
								size="sm"
								onClick={() => {
									onAddTag(nodeId, tag);
									setTag("");
								}}
								aria-label="Confirm tag addition"
							>
								Add
							</Button>
						</div>
					</div>
				</PopoverContent>
			</Popover>

			{/* Edit Note */}
			<Popover>
				<PopoverTrigger asChild>
					<Button
						size="sm"
						variant="ghost"
						className="h-6 w-6 p-0"
						aria-label="Edit note for node"
						title="Edit note for node"
					>
						<FileEdit className="h-3 w-3" aria-hidden="true" />
					</Button>
				</PopoverTrigger>
				<PopoverContent className="w-64">
					<div className="space-y-2">
						<Label htmlFor="note">Quick note</Label>
						<div className="flex gap-2">
							<Input
								id="note"
								placeholder="Add note..."
								value={note}
								onChange={(e) => setNote(e.target.value)}
								aria-label="Quick note for node"
							/>
							<Button
								size="sm"
								onClick={() => {
									onEditNote(nodeId, note);
									setNote("");
								}}
								aria-label="Save node note"
							>
								Save
							</Button>
						</div>
					</div>
				</PopoverContent>
			</Popover>
		</div>
	);
});
