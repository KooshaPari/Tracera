import type { ReactElement } from 'react';

import { X } from 'lucide-react';
import { memo, useCallback } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  data: {
    image?: string | undefined;
    progress?: number | undefined;
    status?: string | undefined;
    description?: string | undefined;
    tags?: string[] | undefined;
    [key: string]: unknown;
  };
}

interface RichNodeDetailPanelProps {
  node: GraphNode | null;
  onClose: () => void;
  onExpand?: ((nodeId: string) => void) | undefined;
  onNavigate?: ((nodeId: string) => void) | undefined;
}

interface RichNodeDetailPanelInnerProps {
  node: GraphNode;
  onClose: () => void;
  onExpand?: ((nodeId: string) => void) | undefined;
  onNavigate?: ((nodeId: string) => void) | undefined;
}

const NodeImageSection = ({ image, label }: { image: string; label: string }): ReactElement => (
  <div className='overflow-hidden rounded-lg border'>
    <img src={image} alt={label} className='h-auto w-full' />
  </div>
);

const NodeProgressSection = ({ progress }: { progress: number }): ReactElement => (
  <div>
    <div className='mb-2 flex items-center justify-between'>
      <span className='text-muted-foreground text-sm'>Progress</span>
      <span className='text-sm font-medium'>{progress}%</span>
    </div>
    <Progress value={progress} className='h-2' />
  </div>
);

const NodeStatusSection = ({ status }: { status: string }): ReactElement => (
  <div>
    <span className='text-muted-foreground text-sm'>Status</span>
    <div className='mt-1'>
      <Badge>{status}</Badge>
    </div>
  </div>
);

const NodeDescriptionSection = ({ description }: { description: string }): ReactElement => (
  <div>
    <span className='text-muted-foreground text-sm'>Description</span>
    <p className='mt-1 text-sm'>{description}</p>
  </div>
);

const NodeTagsSection = ({ tags }: { tags: string[] }): ReactElement => (
  <div>
    <span className='text-muted-foreground text-sm'>Tags</span>
    <div className='mt-1 flex flex-wrap gap-1'>
      {tags.map((tag) => (
        <Badge key={tag} variant='outline' className='text-xs'>
          {tag}
        </Badge>
      ))}
    </div>
  </div>
);

const getNonEmptyString = (value: unknown): string | undefined => {
  if (typeof value !== 'string') {
    return undefined;
  }
  if (value.length === 0) {
    return undefined;
  }
  return value;
};

const getTags = (value: unknown): string[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((tag): tag is string => typeof tag === 'string' && tag.length > 0);
};

const buildNodeSections = (node: GraphNode): ReactElement[] => {
  const sections: ReactElement[] = [];
  const image = getNonEmptyString(node.data.image);
  const description = getNonEmptyString(node.data.description);
  const status = getNonEmptyString(node.data.status);
  const tags = getTags(node.data.tags);

  if (image !== undefined) {
    sections.push(<NodeImageSection key='image' image={image} label={node.label} />);
  }

  if (typeof node.data.progress === 'number') {
    sections.push(<NodeProgressSection key='progress' progress={node.data.progress} />);
  }

  if (status !== undefined) {
    sections.push(<NodeStatusSection key='status' status={status} />);
  }

  if (description !== undefined) {
    sections.push(<NodeDescriptionSection key='description' description={description} />);
  }

  if (tags.length > 0) {
    sections.push(<NodeTagsSection key='tags' tags={tags} />);
  }

  return sections;
};

const buildActionSection = (
  onExpand: ((nodeId: string) => void) | undefined,
  onNavigate: ((nodeId: string) => void) | undefined,
  handleExpand: () => void,
  handleNavigate: () => void,
): ReactElement | undefined => {
  const actions: ReactElement[] = [];

  if (onExpand) {
    actions.push(
      <Button key='expand' size='sm' className='flex-1' onClick={handleExpand}>
        Expand
      </Button>,
    );
  }

  if (onNavigate) {
    actions.push(
      <Button
        key='navigate'
        size='sm'
        variant='outline'
        className='flex-1'
        onClick={handleNavigate}
      >
        Navigate
      </Button>,
    );
  }

  if (actions.length === 0) {
    return undefined;
  }

  return <div className='flex gap-2 border-t pt-4'>{actions}</div>;
};

const RichNodeDetailPanelInner = ({
  node,
  onClose,
  onExpand,
  onNavigate,
}: RichNodeDetailPanelInnerProps): ReactElement => {
  const handleExpand = useCallback(() => onExpand?.(node.id), [node.id, onExpand]);
  const handleNavigate = useCallback(() => onNavigate?.(node.id), [node.id, onNavigate]);
  const sections = buildNodeSections(node);
  const actions = buildActionSection(onExpand, onNavigate, handleExpand, handleNavigate);

  return (
    <div className='bg-card fixed top-0 right-0 z-50 flex h-full w-96 flex-col border-l shadow-lg'>
      {/* Header */}
      <div className='flex items-center justify-between border-b p-4'>
        <div className='flex-1'>
          <h3 className='truncate text-lg font-semibold'>{node.label}</h3>
          <Badge variant='secondary' className='mt-1'>
            {node.type}
          </Badge>
        </div>
        <Button size='sm' variant='ghost' onClick={onClose} className='h-8 w-8 p-0'>
          <X className='h-4 w-4' />
        </Button>
      </div>

      {/* Content */}
      <div className='flex-1 overflow-y-auto'>
        <div className='space-y-4 p-4'>
          {/* Embedded image (full rich content) */}
          {sections}

          {/* Interactive buttons (full rich content) */}
          {actions}
        </div>
      </div>
    </div>
  );
};

const RichNodeDetailPanelComponent = (
  props: RichNodeDetailPanelProps,
): ReactElement | undefined => {
  if (props.node) {
    return (
      <RichNodeDetailPanelInner
        node={props.node}
        onClose={props.onClose}
        onExpand={props.onExpand}
        onNavigate={props.onNavigate}
      />
    );
  }
  return undefined;
};

const RichNodeDetailPanel = memo(RichNodeDetailPanelComponent);
RichNodeDetailPanel.displayName = 'RichNodeDetailPanel';

export { RichNodeDetailPanel };
