import createClient from 'openapi-fetch';

import type { Item, Link, Project } from '@tracertm/types';

// API client configuration
const API_BASE_URL = import.meta.env?.['VITE_API_URL'] || 'http://localhost:4000';

// Create typed API client (will use generated types when available)
export const api = createClient<{
  '/api/v1/projects': {
    get: { responses: { 200: { content: { 'application/json': Project[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Project> } };
      responses: { 201: { content: { 'application/json': Project } } };
    };
  };
  '/api/v1/projects/{id}': {
    get: {
      parameters: { path: { id: string } };
      responses: { 200: { content: { 'application/json': Project } } };
    };
  };
  '/api/v1/items': {
    get: { responses: { 200: { content: { 'application/json': Item[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Item> } };
      responses: { 201: { content: { 'application/json': Item } } };
    };
  };
  '/api/v1/links': {
    get: { responses: { 200: { content: { 'application/json': Link[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Link> } };
      responses: { 201: { content: { 'application/json': Link } } };
    };
  };
}>({ baseUrl: API_BASE_URL });

// Convenience functions
export async function getProjects() {
  const { data, error } = await api.GET('/api/v1/projects');
  if (error) throw error;
  return data;
}

export async function getProject(id: string) {
  const { data, error } = await api.GET('/api/v1/projects/{id}', {
    params: { path: { id } },
  });
  if (error) throw error;
  return data;
}

export async function createProject(project: Partial<Project>) {
  const { data, error } = await api.POST('/api/v1/projects', { body: project });
  if (error) throw error;
  return data;
}

export async function getItems() {
  const { data, error } = await api.GET('/api/v1/items');
  if (error) throw error;
  return data;
}

export async function createItem(item: Partial<Item>) {
  const { data, error } = await api.POST('/api/v1/items', { body: item });
  if (error) throw error;
  return data;
}

export async function getLinks() {
  const { data, error } = await api.GET('/api/v1/links');
  if (error) throw error;
  return data;
}

export async function createLink(link: Partial<Link>) {
  const { data, error } = await api.POST('/api/v1/links', { body: link });
  if (error) throw error;
  return data;
}
