import { Callout } from 'fumadocs-ui/components/callout';
import defaultMdxComponents from 'fumadocs-ui/mdx';

import { Icon } from './icon-sprite';
import {
  AccordionLazy,
  AccordionsLazy,
  FileLazy,
  FilesLazy,
  FolderLazy,
  ImageZoomLazy,
  StepLazy,
  StepsLazy,
  TabLazy,
  TabsLazy,
} from './mdx-components-lazy';
import { DocImage } from './optimized-image';

/**
 * Custom MDX components for enhanced documentation
 * Extends Fumadocs default components with additional features
 *
 * PHASE 1 OPTIMIZATION: Heavy components are lazy-loaded to reduce bundle size
 */
export const mdxComponents = {
  ...defaultMdxComponents,

  // Navigation components (lazy-loaded)
  Tab: TabLazy,
  Tabs: TabsLazy,

  // Content organization (Callout is lightweight, others lazy-loaded)
  Accordion: AccordionLazy,
  Accordions: AccordionsLazy,
  Callout,

  // Media (optimized with Next.js Image)
  ImageZoom: ImageZoomLazy,
  img: (props: any) => {
    // For documentation images, use optimized component
    if (props.src && !props.src.startsWith('http')) {
      return <DocImage src={props.src} alt={props.alt || ''} />;
    }
    // For external images, use ImageZoom
    return <ImageZoomLazy {...props} />;
  },

  // File tree visualization (lazy-loaded)
  File: FileLazy,
  Folder: FolderLazy,
  Files: FilesLazy,

  // Step-by-step guides (lazy-loaded)
  Step: StepLazy,
  Steps: StepsLazy,

  // Custom link component with external link icon
  a: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => {
    const isExternal = href?.startsWith('http');

    return (
      <a
        href={href}
        {...props}
        {...(isExternal && {
          className: 'inline-flex items-center gap-1',
          rel: 'noopener noreferrer',
          target: '_blank',
        })}
      >
        {children}
        {isExternal && <Icon name='external-link' size={12} className='inline-block' />}
      </a>
    );
  },
};

export default mdxComponents;
