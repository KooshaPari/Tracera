import { ExternalLink, Maximize2, Minimize2, MoreHorizontal } from 'lucide-react';
import { memo } from 'react';

import { Button } from '@tracertm/ui/components/Button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

interface NodeActionsProps {
  nodeId: string;
  isExpanded: boolean;
  onExpand: (nodeId: string) => void;
  onNavigate: (nodeId: string) => void;
  onShowMenu: (nodeId: string) => void;
}

export const NodeActions = memo(function NodeActions({
  nodeId,
  isExpanded,
  onExpand,
  onNavigate,
  onShowMenu,
}: NodeActionsProps) {
  return (
    <div className='flex gap-1'>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size='sm'
              variant='ghost'
              className='h-6 w-6 p-0'
              onClick={(e) => {
                e.stopPropagation();
                onExpand(nodeId);
              }}
            >
              {isExpanded ? <Minimize2 className='h-3 w-3' /> : <Maximize2 className='h-3 w-3' />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{isExpanded ? 'Collapse' : 'Expand'}</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size='sm'
              variant='ghost'
              className='h-6 w-6 p-0'
              onClick={(e) => {
                e.stopPropagation();
                onNavigate(nodeId);
              }}
            >
              <ExternalLink className='h-3 w-3' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Open details</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              size='sm'
              variant='ghost'
              className='h-6 w-6 p-0'
              onClick={(e) => {
                e.stopPropagation();
                onShowMenu(nodeId);
              }}
            >
              <MoreHorizontal className='h-3 w-3' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>More actions</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
});
