import { NotImplemented } from "@/components/Availability";
import { Button, Dialog, DialogContent, DialogDescription, DialogTitle } from "@tracertm/ui";

export function UnavailableProjectMutation({
  open,
  onOpenChange,
  title,
  onClosed,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  onClosed?: () => void;
}) {
  const close = () => {
    onOpenChange(false);
    onClosed?.();
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>{title}</DialogTitle>
        <DialogDescription>This operation is not available yet.</DialogDescription>
        <NotImplemented />
        <Button onClick={close}>Close</Button>
      </DialogContent>
    </Dialog>
  );
}
