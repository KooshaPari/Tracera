import { memo } from 'react';

import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from '@tracertm/ui/components/ContextMenu';

interface NodeContextMenuProps {
  children: React.ReactNode;
  nodeId: string;
  nodeType: string;
  onCopyId: (id: string) => void;
  onDuplicate: (id: string) => void;
  onDelete: (id: string) => void;
  onViewDetails: (id: string) => void;
}

export const NodeContextMenu = memo(function NodeContextMenu({
  children,
  nodeId,
  nodeType: _nodeType,
  onCopyId,
  onDuplicate,
  onDelete,
  onViewDetails,
}: NodeContextMenuProps) {
  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>{children}</ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem
          onClick={() => {
            onViewDetails(nodeId);
          }}
        >
          View Details
        </ContextMenuItem>
        <ContextMenuItem
          onClick={() => {
            onCopyId(nodeId);
          }}
        >
          Copy ID
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem
          onClick={() => {
            onDuplicate(nodeId);
          }}
        >
          Duplicate
        </ContextMenuItem>
        <ContextMenuItem
          onClick={() => {
            onDelete(nodeId);
          }}
          className='text-destructive'
        >
          Delete
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
});
