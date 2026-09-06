/**
 * Application configuration
 * If VITE_API_URL is defined (e.g. on Vercel), it prepends the backend host.
 * If empty (local development), requests use relative paths proxied by Vite.
 */
export const API_BASE_URL: string = import.meta.env.VITE_API_URL
  ? (import.meta.env.VITE_API_URL as string).replace(/\/+$/, '')
  : '';
