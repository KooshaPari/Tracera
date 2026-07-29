/** Single browser origin for the approved Tracera gateway. */
export const API_ORIGIN = (
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:18000'
).replace(/\/$/, '');

export const WS_ORIGIN = (
  import.meta.env.VITE_WS_URL ?? API_ORIGIN.replace(/^http/, 'ws')
).replace(/\/$/, '');
