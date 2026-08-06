/** Single browser origin for the approved Tracera gateway. */
const configuredApiOrigin = import.meta.env.VITE_API_URL?.trim();
const browserOrigin = typeof window === 'undefined' ? '' : window.location.origin;

export const API_ORIGIN = (configuredApiOrigin || browserOrigin).replace(/\/$/, '');

const configuredWsOrigin = import.meta.env.VITE_WS_URL?.trim();
export const WS_ORIGIN = (configuredWsOrigin || API_ORIGIN.replace(/^http/, 'ws')).replace(/\/$/, '');
