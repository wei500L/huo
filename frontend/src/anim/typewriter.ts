import { useCallback, useEffect, useRef, useState } from "react";

export function useTypewriter(
  text: string,
  enabled: boolean,
  speedMs = 30,
): { display: string; isDone: boolean; skip: () => void; reset: () => void } {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [session, setSession] = useState(0);
  const [display, setDisplay] = useState(() => (enabled ? "" : text));
  const [isDone, setIsDone] = useState(() => !enabled || speedMs <= 5);

  const clearTimer = useCallback(() => {
    if (intervalRef.current === null) {
      return;
    }

    clearInterval(intervalRef.current);
    intervalRef.current = null;
  }, []);

  const complete = useCallback(
    (nextDisplay: string) => {
      clearTimer();
      setDisplay(nextDisplay);
      setIsDone(true);
    },
    [clearTimer],
  );

  const skip = useCallback(() => {
    complete(text);
  }, [complete, text]);

  const reset = useCallback(() => {
    clearTimer();
    setDisplay(enabled && speedMs > 5 ? "" : text);
    setIsDone(!enabled || speedMs <= 5 || text.length === 0);
    setSession((value) => value + 1);
  }, [clearTimer, enabled, speedMs, text]);

  useEffect(() => {
    clearTimer();

    if (!enabled || speedMs <= 5) {
      setDisplay(text);
      setIsDone(true);
      return;
    }

    if (text.length === 0) {
      setDisplay("");
      setIsDone(true);
      return;
    }

    setDisplay("");
    setIsDone(false);

    let index = 0;
    intervalRef.current = setInterval(() => {
      index += 1;

      if (index >= text.length) {
        complete(text);
        return;
      }

      setDisplay(text.slice(0, index));
    }, speedMs);

    return clearTimer;
  }, [clearTimer, complete, enabled, session, speedMs, text]);

  useEffect(() => {
    return () => {
      clearTimer();
    };
  }, [clearTimer]);

  return { display, isDone, skip, reset };
}
