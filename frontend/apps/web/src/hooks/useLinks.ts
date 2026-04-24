import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import type { Link, LinkType } from '@tracertm/types';

import { client } from '@/api/client';
import { QUERY_CONFIGS, queryKeys } from '@/lib/queryConfig';
import { useAuthStore } from '@/stores/authStore';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

interface LinkFilters {
  projectId?: string | undefined;
  sourceId?: string | undefined;
  targetId?: string | undefined;
  type?: LinkType | undefined;
  limit?: number | undefined;
  offset?: number | undefined;
  excludeTypes?: LinkType[] | undefined; // ✅ NEW: Filter out specific link types
}

async function fetchLinks(filters: LinkFilters = {}): Promise<{ links: Link[]; total: number }> {
  const params = new URLSearchParams();
  if (filters.projectId) {
    params.set('project_id', filters.projectId);
  }
  if (filters.sourceId) {
    params.set('source_id', filters.sourceId);
  }
  if (filters.targetId) {
    params.set('target_id', filters.targetId);
  }
  if (filters.type) {
    params.set('type', filters.type);
  }
  if (filters.limit) {
    params.set('limit', String(filters.limit));
  }
  if (filters.offset) {
    params.set('offset', String(filters.offset));
  }

  // ✅ NEW: Send excluded types to API for server-side filtering
  if (filters.excludeTypes?.length) {
    params.set('exclude_types', filters.excludeTypes.join(','));
  }

  const res = await fetch(`${API_URL}/api/v1/links?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch links');
  }
  const data = await res.json();
  // API returns { total: number, links: Link[] } or array
  const linksArray = Array.isArray(data) ? data : (data['links'] ?? []);
  // Transform snake_case to camelCase for frontend compatibility
  const transformedLinks = linksArray.map((link: any) => ({
    ...link,
    sourceId: link.source_id ?? link.sourceId,
    targetId: link.target_id ?? link.targetId,
    projectId: link.project_id ?? link.projectId,
  }));
  return {
    links: transformedLinks,
    total: data['total'] ?? (Array.isArray(data) ? data.length : linksArray.length),
  };
}

interface CreateLinkData {
  projectId: string;
  sourceId: string;
  targetId: string;
  type: LinkType;
  description?: string;
}

async function createLink(data: CreateLinkData): Promise<Link> {
  const res = await fetch(`${API_URL}/api/v1/links`, {
    body: JSON.stringify({
      description: data['description'],
      project_id: data['projectId'],
      source_id: data['sourceId'],
      target_id: data['targetId'],
      type: data.type,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create link');
  }
  return res.json() as Promise<Link>;
}

async function deleteLink(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/links/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete link');
  }
}

export function useLinks(filters: LinkFilters = {}) {
  const token = useAuthStore((s) => s.token);
  const key = filters.projectId
    ? [
        ...queryKeys.links.list(filters.projectId),
        filters.sourceId ?? null,
        filters.targetId ?? null,
        filters.type ?? null,
        filters.limit ?? null,
        filters.excludeTypes ?? null, // ✅ NEW: Include in cache key
      ]
    : [
        'links',
        filters.sourceId ?? null,
        filters.targetId ?? null,
        filters.type ?? null,
        filters.limit ?? null,
        filters.excludeTypes ?? null, // ✅ NEW: Include in cache key
      ];
  return useQuery({
    queryKey: key,
    queryFn: async () => fetchLinks(filters),
    enabled: Boolean(token),
    ...QUERY_CONFIGS.dynamic, // Links change frequently
  });
}

export function useCreateLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createLink,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['links'] });
    },
  });
}

export function useDeleteLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteLink,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['links'] });
    },
  });
}

// Graph data hook for visualization
export function useTraceabilityGraph(projectId: string) {
  // ✅ NEW: Limit initial edge rendering
  const MAX_EDGES_INITIAL = 500;
  const [visibleEdgeCount, setVisibleEdgeCount] = useState(MAX_EDGES_INITIAL);

  const { data: items } = useQuery<{ id: string; title: string; view: string; status: string }[]>({
    queryKey: queryKeys.items.list(projectId),
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/items?project_id=${projectId}`, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) {
        throw new Error('Failed to fetch items');
      }
      return res.json() as Promise<{ id: string; title: string; view: string; status: string }[]>;
    },
    enabled: Boolean(projectId),
    ...QUERY_CONFIGS.graph, // Graph data is expensive, cache longer
  });

  // ✅ FIXED: Fetch links with filtering + reasonable limit
  const { data: linksData } = useLinks({
    projectId,
    limit: 10_000, // ✅ NEW: API limit to prevent massive responses
    excludeTypes: ['implements'], // ✅ NEW: Filter out 84% redundant links
  });

  const allLinks = linksData?.links ?? [];

  // ✅ NEW: Progressive loading - only render first N edges
  const visibleLinks = allLinks.slice(0, visibleEdgeCount);
  const canLoadMore = visibleEdgeCount < allLinks.length;

  // Load more handler
  const onLoadMore = () => {
    setVisibleEdgeCount((prev) => Math.min(prev + 500, allLinks.length));
  };

  return {
    canLoadMore,
    edges: visibleLinks.map((link) => ({
      data: {
        id: link.id,
        source: link.sourceId,
        target: link.targetId,
        type: link.type,
      },
    })),
    isLoading: !(items && allLinks),
    nodes: (items ?? []).map((item) => ({
      data: {
        id: item.id,
        label: item.title,
        status: item.status,
        type: item.view.toLowerCase(),
      },
    })),
    onLoadMore,
    totalEdges: allLinks.length,
    visibleEdges: visibleLinks.length,
  };
}
