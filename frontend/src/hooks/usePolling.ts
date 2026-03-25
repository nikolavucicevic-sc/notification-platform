import { useEffect, useRef } from 'react';

/**
 * Hook for polling an API endpoint at regular intervals
 *
 * @param callback - Function to call on each interval
 * @param interval - Polling interval in milliseconds (default: 5000)
 * @param enabled - Whether polling is enabled (default: true)
 */
export function usePolling(
  callback: () => void | Promise<void>,
  interval: number = 5000,
  enabled: boolean = true
) {
  const savedCallback = useRef(callback);

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    if (!enabled) return;

    const tick = async () => {
      await savedCallback.current();
    };

    // Call immediately on mount
    tick();

    // Then set up interval
    const id = setInterval(tick, interval);

    return () => clearInterval(id);
  }, [interval, enabled]);
}
