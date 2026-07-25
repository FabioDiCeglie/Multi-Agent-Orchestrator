"use client";

import { useCallback, useEffect, useRef, useState } from "react";

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
 *
 * `fn` receives an AbortSignal that's aborted when a new run starts or
 * the component unmounts, so a stale/cancelled request can never
 * overwrite more recent state.
 */
export function useAsync<T, Arg>(
  fn: (arg: Arg, signal: AbortSignal) => Promise<T>
) {
  const [state, setState] = useState<AsyncState<T>>({
    status: AsyncStatus.IDLE,
  });
  const controllerRef = useRef<AbortController | null>(null);

  // Abort any in-flight request when the component unmounts.
  useEffect(() => {
    return () => controllerRef.current?.abort();
  }, []);

  const run = useCallback(
    async (arg: Arg) => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;

      setState({ status: AsyncStatus.LOADING });
      try {
        const data = await fn(arg, controller.signal);
        if (controller.signal.aborted) return undefined;
        setState({ status: AsyncStatus.SUCCESS, data });
        return data;
      } catch (err) {
        if (controller.signal.aborted) return undefined; // cancelled — don't surface as an error
        const message =
          err instanceof Error ? err.message : "Something went wrong";
        setState({ status: AsyncStatus.ERROR, error: message });
        return undefined;
      }
    },
    [fn]
  );

  const cancel = useCallback(() => {
    controllerRef.current?.abort();
    setState({ status: AsyncStatus.IDLE });
  }, []);

  return { ...state, run, cancel, reset: cancel };
}
