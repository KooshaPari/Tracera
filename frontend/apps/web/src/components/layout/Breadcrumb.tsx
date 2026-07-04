import { Link, useMatches, useParams } from '@tanstack/react-router';
import { Fragment, useMemo } from 'react';

import { useItem } from '@/hooks/useItems';
import { useProject } from '@/hooks/useProjects';
import {
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  Breadcrumb as ShadcnBreadcrumb,
  Skeleton,
} from '@tracertm/ui';

interface BreadcrumbSegment {
  label: string;
  href: string;
  isLoading?: boolean;
}

export const Breadcrumbs = function Breadcrumbs() {
  const matches = useMatches();
  const params = useParams({ strict: false });
  const projectId = params.projectId as string | undefined;
  const itemId = params.itemId as string | undefined;
  const viewType = params.viewType as string | undefined;

  // Fetch project data
  const { data: project, isLoading: projectLoading } = useProject(projectId ?? '');

  // Fetch item data if itemId exists
  const { data: currentItem, isLoading: itemLoading } = useItem(itemId ?? '');

  // Generate breadcrumbs from matches with smart data fetching
  const breadcrumbs = useMemo(() => {
    const segments: BreadcrumbSegment[] = [];

    matches.forEach((match) => {
      const pathname = match?.pathname ?? '';
      if (pathname === '/' || pathname === '') {
        return;
      }

      const pathSegments = pathname.split('/').filter(Boolean);

      pathSegments.forEach((segment, index) => {
        if (segment === null || typeof segment !== 'string') {
          return;
        }
        const href = `/${pathSegments.slice(0, index + 1).join('/')}`;

        // Skip IDs and query parameters
        if (segment.match(/^[a-f0-9-]{36}$/i) || segment.startsWith('?')) {
          return;
        }

        // Skip duplicate paths
        if (segments.some((s) => s.href === href)) {
          return;
        }

        // Skip literal "null" segment (bad URL) — show fallback instead of "Null"
        if (segment.toLowerCase() === 'null') {
          if (segment === projectId) {
            segments.push({
              href,
              isLoading: projectLoading,
              label: project?.name?.trim() ?? 'Project',
            });
          } else {
            segments.push({ href, label: '—' });
          }
          return;
        }

        // Fetch project name if this is a project ID
        if (segment === projectId && project) {
          segments.push({
            href,
            isLoading: projectLoading,
            label: (project.name ?? 'Project').trim() || 'Project',
          });
          return;
        }

        // Fetch item name if this is an item ID
        if (segment === itemId && currentItem) {
          segments.push({
            href,
            isLoading: itemLoading,
            label: (currentItem.title ?? 'Item').trim() || 'Item',
          });
          return;
        }

        // Format segment label
        const label = segment
          .split(/[-_]/)
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')
          .trim();

        // Add view type with special handling
        if (segment === viewType && viewType) {
          const viewLabel = viewType
            .split('-')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
            .trim();
          segments.push({
            href,
            label: viewLabel || 'View',
          });
        } else if (!segments.some((s) => s.label === label)) {
          segments.push({
            href,
            label: label || 'Page',
          });
        }
      });
    });

    return segments;
  }, [matches, projectId, project, projectLoading, itemId, currentItem, itemLoading, viewType]);

  // De-duplicate breadcrumbs
  const uniqueBreadcrumbs = [...new Map(breadcrumbs.map((b) => [b.href, b])).values()];

  if (uniqueBreadcrumbs.length === 0) {
    return null;
  }

  const linkClassName =
    'min-w-0 truncate uppercase transition-colors text-muted-foreground hover:text-primary ' +
    'text-[clamp(9px,0.8vw,12px)] tracking-[clamp(0.12em,0.12vw,0.2em)] leading-none ' +
    'max-w-[clamp(96px,18vw,180px)]';

  const dashboardClassName = linkClassName.replace('font-medium', '').trim();

  const pageClassName =
    'min-w-0 truncate uppercase text-primary font-semibold ' +
    'text-[clamp(9px,0.8vw,12px)] tracking-[clamp(0.12em,0.12vw,0.2em)] leading-none ' +
    'max-w-[clamp(110px,22vw,320px)]';

  return (
    <ShadcnBreadcrumb
      separator='/'
      className='hidden max-w-full min-w-0 md:block'
      aria-label='breadcrumb'
      role='navigation'
    >
      <BreadcrumbList className='min-w-0'>
        <BreadcrumbItem className='min-w-0'>
          <BreadcrumbLink asChild className={`${dashboardClassName} font-bold`}>
            <Link to='/home'>Dashboard</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>

        {uniqueBreadcrumbs.map((item, index) => (
          <Fragment key={item.href}>
            <BreadcrumbSeparator className='text-muted-foreground/50' />
            <BreadcrumbItem className='min-w-0'>
              {item.isLoading ? (
                <div className='flex items-center gap-2'>
                  <Skeleton className='h-4 w-16' />
                </div>
              ) : index === uniqueBreadcrumbs.length - 1 ? (
                <BreadcrumbPage className={pageClassName}>{item.label}</BreadcrumbPage>
              ) : (
                <BreadcrumbLink asChild className={`${linkClassName} font-medium`}>
                  <Link to={item.href}>{item.label}</Link>
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
          </Fragment>
        ))}
      </BreadcrumbList>
    </ShadcnBreadcrumb>
  );
};
