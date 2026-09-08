/**
 * keepAlive.ts
 *
 * On page load, immediately pings the backend /health endpoint.
 * If Render's free-tier backend is sleeping (cold-start ~30s), it retries
 * every 5 seconds for up to 2 minutes and surfaces status via callbacks
 * so the UI can show a "Backend warming up…" message instead of errors.
 */

import { API_BASE_URL } from './config';

const RETRY_INTERVAL_MS = 5_000;   // retry every 5 s
const MAX_RETRIES       = 24;      // 24 × 5 s = 2 minutes max

export type WakeStatus = 'waking' | 'ready' | 'failed';

export interface WakeCallbacks {
  onWaking?: () => void;   // called on first failed ping (backend sleeping)
  onReady?: () => void;    // called when backend responds 200
  onFailed?: () => void;   // called after all retries exhausted
}

/**
 * Wakes the backend on page load. Call this once from main.tsx.
 * Returns a cleanup function that cancels any pending retries.
 */
export function wakeBackend(callbacks: WakeCallbacks = {}): () => void {
  let cancelled = false;
  let timerId: ReturnType<typeof setTimeout> | null = null;
  let attempts = 0;

  async function tryPing(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        cache: 'no-store',
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  async function run(): Promise<void> {
    const alive = await tryPing();

    if (cancelled) return;

    if (alive) {
      callbacks.onReady?.();
      return;
    }

    // Backend is sleeping — notify UI once
    if (attempts === 0) {
      callbacks.onWaking?.();
    }

    attempts += 1;

    if (attempts >= MAX_RETRIES) {
      callbacks.onFailed?.();
      return;
    }

    timerId = setTimeout(() => {
      if (!cancelled) run();
    }, RETRY_INTERVAL_MS);
  }

  run();

  return () => {
    cancelled = true;
    if (timerId !== null) clearTimeout(timerId);
  };
}
