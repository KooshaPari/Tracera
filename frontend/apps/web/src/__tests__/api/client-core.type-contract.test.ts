import { beforeEach, describe, expect, it, vi } from 'vitest';

const openApiFetch = vi.hoisted(() => {
  const request = vi.fn();
  const use = vi.fn();

  return {
    createClient: vi.fn(() => ({ request, use })),
    request,
    use,
  };
});

vi.mock('openapi-fetch', () => ({ default: openApiFetch.createClient }));

import { clientCore } from '@/api/client-core';

describe('client-core legacy API helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('forwards each helper method, path, and init to the typed request boundary', async () => {
    const getInit = { params: { query: { page: 2 } } };
    const postInit = { body: { title: 'new trace' } };
    const putInit = { body: { title: 'renamed trace' } };
    const deleteInit = { params: { query: { force: true } } };

    openApiFetch.request
      .mockResolvedValueOnce({ data: { id: 'get-result' } })
      .mockResolvedValueOnce({ data: { id: 'post-result' } })
      .mockResolvedValueOnce({ data: { id: 'put-result' } })
      .mockResolvedValueOnce({ data: { id: 'delete-result' } });

    await expect(clientCore.apiClient.get('/api/traces', getInit)).resolves.toEqual({ id: 'get-result' });
    await expect(clientCore.apiClient.post('/api/traces', postInit)).resolves.toEqual({ id: 'post-result' });
    await expect(clientCore.apiClient.put('/api/traces/42', putInit)).resolves.toEqual({ id: 'put-result' });
    await expect(clientCore.apiClient.delete('/api/traces/42', deleteInit)).resolves.toEqual({
      id: 'delete-result',
    });

    expect(openApiFetch.request).toHaveBeenNthCalledWith(1, 'get', '/api/traces', getInit);
    expect(openApiFetch.request).toHaveBeenNthCalledWith(2, 'post', '/api/traces', postInit);
    expect(openApiFetch.request).toHaveBeenNthCalledWith(3, 'put', '/api/traces/42', putInit);
    expect(openApiFetch.request).toHaveBeenNthCalledWith(4, 'delete', '/api/traces/42', deleteInit);
  });

  it('unwraps data and propagates errors from the typed request boundary', async () => {
    const requestError = new Error('request rejected');

    openApiFetch.request.mockResolvedValueOnce({ data: { id: 'trace-42' } });
    await expect(clientCore.apiClient.get('/api/traces/42')).resolves.toEqual({ id: 'trace-42' });
    expect(openApiFetch.request).toHaveBeenCalledWith('get', '/api/traces/42');

    openApiFetch.request.mockResolvedValueOnce({ error: requestError });
    await expect(clientCore.apiClient.delete('/api/traces/42')).rejects.toBe(requestError);
  });
});
