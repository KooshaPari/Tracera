import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:18000';

export { API_URL, getAuthHeaders };
