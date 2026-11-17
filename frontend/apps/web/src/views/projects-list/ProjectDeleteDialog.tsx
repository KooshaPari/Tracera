import type { Project } from "@tracertm/types";
import { UnavailableProjectMutation } from "./UnavailableProjectMutation";

interface ProjectDeleteDialogProps {
  open: boolean;
  project: Project;
  onOpenChange: (open: boolean) => void;
  onClosed: () => void;
}

export function ProjectDeleteDialog({ open, onOpenChange, onClosed }: ProjectDeleteDialogProps) {
  return (
    <UnavailableProjectMutation
      open={open}
      onOpenChange={onOpenChange}
      onClosed={onClosed}
      title="Delete project"
    />
  );
}
