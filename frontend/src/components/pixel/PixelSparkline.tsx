import { forwardRef, useEffect, useRef, type ForwardedRef } from "react";
import clsx from "clsx";

export interface PixelSparklineProps {
  values?: number[];
  data?: number[];
  color: string;
  width?: number;
  height?: number;
  yMin?: number;
  yMax?: number;
  className?: string;
}

const clampInt = (value: number): number => Math.round(value);

const drawPoint = (ctx: CanvasRenderingContext2D, x: number, y: number, size: number, color: string): void => {
  ctx.fillStyle = color;
  ctx.fillRect(x - Math.floor(size / 2), y - Math.floor(size / 2), size, size);
};

const drawLine = (ctx: CanvasRenderingContext2D, x0: number, y0: number, x1: number, y1: number, color: string): void => {
  let cx = x0;
  let cy = y0;
  const dx = Math.abs(x1 - x0);
  const dy = Math.abs(y1 - y0);
  const sx = x0 < x1 ? 1 : -1;
  const sy = y0 < y1 ? 1 : -1;
  let err = dx - dy;

  ctx.fillStyle = color;

  while (cx !== x1 || cy !== y1) {
    ctx.fillRect(cx, cy, 1, 1);
    const twiceErr = err * 2;
    if (twiceErr > -dy) {
      err -= dy;
      cx += sx;
    }
    if (twiceErr < dx) {
      err += dx;
      cy += sy;
    }
  }

  ctx.fillRect(x1, y1, 1, 1);
};

function PixelSparklineImpl(
  { values, data, color, width = 60, height = 16, yMin, yMax, className }: PixelSparklineProps,
  ref: ForwardedRef<HTMLCanvasElement>,
) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const resolvedValues = values?.length ? values : data ?? [];
    if (!canvas || resolvedValues.length === 0) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const resolvedWidth = clampInt(width);
    const resolvedHeight = clampInt(height);
    const min = yMin ?? Math.min(...resolvedValues);
    const max = yMax ?? Math.max(...resolvedValues);
    const range = Math.max(1, max - min);
    const padX = 1;
    const padY = 1;
    const plotWidth = Math.max(1, resolvedWidth - padX * 2);
    const plotHeight = Math.max(1, resolvedHeight - padY * 2);
    const count = resolvedValues.length;
    const pointSize = 2;

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, resolvedWidth, resolvedHeight);
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, resolvedWidth, resolvedHeight);

    const points = resolvedValues.map((entry, index) => {
      const x = count === 1 ? padX + Math.floor(plotWidth / 2) : padX + Math.round((plotWidth * index) / (count - 1));
      const normalized = (entry - min) / range;
      const y = padY + Math.round(plotHeight - normalized * plotHeight);
      return { x, y };
    });

    for (let index = 1; index < points.length; index += 1) {
      const prev = points[index - 1];
      const next = points[index];
      drawLine(ctx, prev.x, prev.y, next.x, next.y, color);
    }

    for (const point of points) {
      drawPoint(ctx, point.x, point.y, pointSize, color);
    }
  }, [color, data, height, values, width, yMax, yMin]);

  return (
    <canvas
      ref={(node) => {
        canvasRef.current = node;
        if (typeof ref === "function") {
          ref(node);
        } else if (ref) {
          ref.current = node;
        }
      }}
      width={clampInt(width)}
      height={clampInt(height)}
      className={clsx("block pixel-render", className)}
      style={{ width: `${clampInt(width)}px`, height: `${clampInt(height)}px` }}
      aria-hidden="true"
    />
  );
}

PixelSparklineImpl.displayName = "PixelSparkline";

export const PixelSparkline = forwardRef(PixelSparklineImpl);
