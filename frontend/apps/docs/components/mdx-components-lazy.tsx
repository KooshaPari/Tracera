/**
 * Lazy-loaded MDX Components
 *
 * Phase 1: Bundle Optimization
 * Heavy components are dynamically imported to reduce initial bundle size
 */
'use client';

import dynamic from 'next/dynamic';

// Loading skeleton component
const LoadingSkeleton = () => <div className='animate-pulse bg-muted rounded-md h-20 w-full' />;

// Dynamically import heavy components
export const TabsLazy = dynamic(
  () => import('fumadocs-ui/components/tabs').then((mod) => mod.Tabs),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const TabLazy = dynamic(() => import('fumadocs-ui/components/tabs').then((mod) => mod.Tab), {
  loading: () => <LoadingSkeleton />,
  ssr: true,
});

export const AccordionsLazy = dynamic(
  () => import('fumadocs-ui/components/accordion').then((mod) => mod.Accordions),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const AccordionLazy = dynamic(
  () => import('fumadocs-ui/components/accordion').then((mod) => mod.Accordion),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const ImageZoomLazy = dynamic(
  () => import('fumadocs-ui/components/image-zoom').then((mod) => mod.ImageZoom),
  {
    loading: () => <div className='animate-pulse bg-muted rounded-md aspect-video w-full' />,
    ssr: false, // Image zoom doesn't need SSR
  },
);

export const FilesLazy = dynamic(
  () => import('fumadocs-ui/components/files').then((mod) => mod.Files),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const FolderLazy = dynamic(
  () => import('fumadocs-ui/components/files').then((mod) => mod.Folder),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const FileLazy = dynamic(
  () => import('fumadocs-ui/components/files').then((mod) => mod.File),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const StepsLazy = dynamic(
  () => import('fumadocs-ui/components/steps').then((mod) => mod.Steps),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);

export const StepLazy = dynamic(
  () => import('fumadocs-ui/components/steps').then((mod) => mod.Step),
  {
    loading: () => <LoadingSkeleton />,
    ssr: true,
  },
);
