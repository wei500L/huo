import { useEffect, useRef, useState } from "react";

const clampInteger = (value: number): number => Math.round(value);

export function useNumberRoll(target: number, durationMs = 400): number {
  const [value, setValue] = useState(0);
  const valueRef = useRef(0);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const nextTarget = clampInteger(target);
    const startValue = valueRef.current;
    const distance = Math.abs(nextTarget - startValue);

    if (frameRef.current !== null) {
      cancelAnimationFrame(frameRef.current);
      frameRef.current = null;
    }

    if (distance === 0 || durationMs <= 0) {
      valueRef.current = nextTarget;
      setValue(nextTarget);
      return undefined;
    }

    const stepMs = durationMs / Math.max(1, distance);
    const direction = nextTarget >= startValue ? 1 : -1;
    const startedAt = performance.now();

    const tick = (now: number): void => {
      const elapsed = now - startedAt;
      const steps = Math.min(distance, Math.floor(elapsed / stepMs));
      const current = startValue + direction * steps;

      if (valueRef.current !== current) {
        valueRef.current = current;
        setValue(current);
      }

      if (steps < distance) {
        frameRef.current = requestAnimationFrame(tick);
      } else {
        frameRef.current = null;
      }
    };

    frameRef.current = requestAnimationFrame(tick);

    return () => {
      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
    };
  }, [durationMs, target]);

  useEffect(() => {
    valueRef.current = value;
  }, [value]);

  return value;
}
