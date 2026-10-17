import type { Project } from "@tracertm/types";
import { UnavailableProjectMutation } from "./UnavailableProjectMutation";

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated?: (project: Project) => void;
}

export function CreateProjectDialog({ open, onOpenChange }: CreateProjectDialogProps) {
  return (
    <UnavailableProjectMutation open={open} onOpenChange={onOpenChange} title="Create project" />
  );
}
