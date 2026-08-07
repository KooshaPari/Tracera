import { client } from '@/api/client';
import { API_ORIGIN } from '@/config/api-origin';

const { getAuthHeaders } = client;

const API_URL = API_ORIGIN;

export { API_URL, getAuthHeaders };
