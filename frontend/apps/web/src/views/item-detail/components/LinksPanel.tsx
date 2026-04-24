import type { ItemLink } from '@/views/item-detail/types';

import { DownstreamLinksCard } from './DownstreamLinksCard';
import { UpstreamLinksCard } from './UpstreamLinksCard';

interface LinksPanelProps {
  targetLinks: ItemLink[];
  sourceLinks: ItemLink[];
  buildLinkToItem: (id: string) => string;
}

export function LinksPanel({
  buildLinkToItem,
  sourceLinks,
  targetLinks,
}: LinksPanelProps): JSX.Element {
  return (
    <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
      <UpstreamLinksCard links={targetLinks} buildLinkToItem={buildLinkToItem} />
      <DownstreamLinksCard links={sourceLinks} buildLinkToItem={buildLinkToItem} />
    </div>
  );
}
