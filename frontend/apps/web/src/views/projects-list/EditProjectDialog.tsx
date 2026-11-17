import type { Project } from "@tracertm/types";
import { UnavailableProjectMutation } from "./UnavailableProjectMutation";

interface EditProjectDialogProps {
  project?: Project | undefined;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditProjectDialog({ open, onOpenChange }: EditProjectDialogProps) {
  return (
    <UnavailableProjectMutation open={open} onOpenChange={onOpenChange} title="Edit project" />
  );
}
