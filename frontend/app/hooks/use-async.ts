"use client";

import { useCallback, useState } from "react";

export const AsyncStatus = {
  IDLE: "idle",
  LOADING: "loading",
  SUCCESS: "success",
  ERROR: "error",
} as const;

export type AsyncStatus = (typeof AsyncStatus)[keyof typeof AsyncStatus];

interface AsyncState<T> {
  status: AsyncStatus;
  data?: T;
  error?: string;
}

/**
 * Generic loading/error/data state for any async call (fetch, etc).
 * Use this for every API call so every screen gets the same
 * IDLE → LOADING → SUCCESS/ERROR lifecycle for free.
 */
export function useAsync<T, Args extends unknown[]>(
  fn: (...args: Args) => Promise<T>
) {
  const [state, setState] = useState<AsyncState<T>>({
    status: AsyncStatus.IDLE,
  });

  const run = useCallback(
    async (...args: Args) => {
      setState({ status: AsyncStatus.LOADING });
      try {
        const data = await fn(...args);
        setState({ status: AsyncStatus.SUCCESS, data });
        return data;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Something went wrong";
        setState({ status: AsyncStatus.ERROR, error: message });
        return undefined;
      }
    },
    [fn]
  );

  const reset = useCallback(
    () => setState({ status: AsyncStatus.IDLE }),
    []
  );

  return { ...state, run, reset };
}
