import createOpenApiClient from 'openapi-fetch';

import type { Item, Link, Project } from '@tracertm/types';

const API_BASE_URL = import.meta.env?.['VITE_API_URL'] || 'http://localhost:4000';
const HTTP_OK = 200;
const HTTP_CREATED = 201;

export const api = createOpenApiClient<{
  '/api/v1/projects': {
    get: { responses: { [HTTP_OK]: { content: { 'application/json': Project[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Project> } };
      responses: { [HTTP_CREATED]: { content: { 'application/json': Project } } };
    };
  };
  '/api/v1/projects/{id}': {
    get: {
      parameters: { path: { id: string } };
      responses: { [HTTP_OK]: { content: { 'application/json': Project } } };
    };
  };
  '/api/v1/items': {
    get: { responses: { [HTTP_OK]: { content: { 'application/json': Item[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Item> } };
      responses: { [HTTP_CREATED]: { content: { 'application/json': Item } } };
    };
  };
  '/api/v1/links': {
    get: { responses: { [HTTP_OK]: { content: { 'application/json': Link[] } } } };
    post: {
      requestBody: { content: { 'application/json': Partial<Link> } };
      responses: { [HTTP_CREATED]: { content: { 'application/json': Link } } };
    };
  };
}>({ baseUrl: API_BASE_URL });
const apiGet = api['GET'].bind(api);
const apiPost = api['POST'].bind(api);

export async function getProjects(): Promise<Project[] | undefined> {
  const { data, error } = await apiGet('/api/v1/projects');
  if (error) {
    throw error;
  }

  return data;
}

export async function getProject(id: string): Promise<Project | undefined> {
  const { data, error } = await apiGet('/api/v1/projects/{id}', {
    params: { path: { id } },
  });
  if (error) {
    throw error;
  }

  return data;
}

export async function createProject(project: Partial<Project>): Promise<Project | undefined> {
  const { data, error } = await apiPost('/api/v1/projects', { body: project });
  if (error) {
    throw error;
  }

  return data;
}

export async function getItems(): Promise<Item[] | undefined> {
  const { data, error } = await apiGet('/api/v1/items');
  if (error) {
    throw error;
  }

  return data;
}

export async function createItem(item: Partial<Item>): Promise<Item | undefined> {
  const { data, error } = await apiPost('/api/v1/items', { body: item });
  if (error) {
    throw error;
  }

  return data;
}

export async function getLinks(): Promise<Link[] | undefined> {
  const { data, error } = await apiGet('/api/v1/links');
  if (error) {
    throw error;
  }

  return data;
}

export async function createLink(link: Partial<Link>): Promise<Link | undefined> {
  const { data, error } = await apiPost('/api/v1/links', { body: link });
  if (error) {
    throw error;
  }

  return data;
}
