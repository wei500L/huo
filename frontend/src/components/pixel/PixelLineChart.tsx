import { forwardRef, useEffect, useRef, type ForwardedRef } from "react";
import clsx from "clsx";

export interface PixelLineChartSeries {
  id: string;
  label: string;
  color: string;
  values: number[];
}

export interface PixelLineChartProps {
  width: number;
  height: number;
  series: PixelLineChartSeries[];
  xLabels: string[];
  yMin?: number;
  yMax?: number;
  yTicks?: number[];
  showGrid?: boolean;
  showLegend?: boolean;
  className?: string;
}

const clampInt = (value: number): number => Math.round(value);

const drawBlock = (ctx: CanvasRenderingContext2D, x: number, y: number, size: number, color: string): void => {
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

const drawGridLine = (ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, horizontal: boolean): void => {
  ctx.fillStyle = "#DDD";
  if (horizontal) {
    ctx.fillRect(x, y, width, 1);
  } else {
    ctx.fillRect(x, y, 1, height);
  }
};

function PixelLineChartImpl(
  { width, height, series, xLabels, yMin = 0, yMax = 100, yTicks = [0, 25, 50, 75, 100], showGrid = true, showLegend = true, className }: PixelLineChartProps,
  ref: ForwardedRef<HTMLCanvasElement>,
) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const resolvedWidth = clampInt(width);
    const resolvedHeight = clampInt(height);
    const left = 28;
    const right = showLegend ? 96 : 12;
    const top = showLegend ? 28 + Math.min(series.length, 4) * 8 : 12;
    const bottom = 20;
    const plotWidth = Math.max(1, resolvedWidth - left - right);
    const plotHeight = Math.max(1, resolvedHeight - top - bottom);
    const range = Math.max(1, yMax - yMin);
    const tickFont = "10px 'Fusion Pixel', monospace";

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, resolvedWidth, resolvedHeight);
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, resolvedWidth, resolvedHeight);
    ctx.font = tickFont;
    ctx.fillStyle = "#4A4A4A";
    ctx.textBaseline = "middle";
    ctx.textAlign = "right";

    for (const tick of yTicks) {
      const normalized = (tick - yMin) / range;
      const y = top + Math.round(plotHeight - normalized * plotHeight);
      if (showGrid) {
        drawGridLine(ctx, left, y, plotWidth, resolvedHeight - bottom - y, true);
      }
      ctx.fillText(String(Math.round(tick)), left - 4, y);
    }

    if (showGrid) {
      const labelCount = Math.max(1, xLabels.length - 1);
      for (let index = 0; index < xLabels.length; index += 1) {
        const x = left + Math.round((plotWidth * index) / labelCount);
        drawGridLine(ctx, x, top, resolvedWidth - right - x, plotHeight, false);
      }
    }

    const pointsBySeries = series.map((entry) => ({
      ...entry,
      points: entry.values.map((value, index) => {
        const xCount = Math.max(1, xLabels.length - 1);
        const x = xLabels.length === 1 ? left + Math.floor(plotWidth / 2) : left + Math.round((plotWidth * index) / xCount);
        const normalized = (value - yMin) / range;
        const y = top + Math.round(plotHeight - normalized * plotHeight);
        return { x, y, value };
      }),
    }));

    for (const entry of pointsBySeries) {
      for (let index = 1; index < entry.points.length; index += 1) {
        const prev = entry.points[index - 1];
        const next = entry.points[index];
        drawLine(ctx, prev.x, prev.y, next.x, next.y, entry.color);
      }

      for (const point of entry.points) {
        drawBlock(ctx, point.x, point.y, 3, entry.color);
      }
    }

    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    ctx.fillStyle = "#4A4A4A";
    for (let index = 0; index < xLabels.length; index += 1) {
      const x = xLabels.length === 1 ? left + Math.floor(plotWidth / 2) : left + Math.round((plotWidth * index) / Math.max(1, xLabels.length - 1));
      ctx.fillText(xLabels[index] ?? "", x, resolvedHeight - 16);
    }

    if (showLegend) {
      ctx.textBaseline = "middle";
      ctx.textAlign = "left";
      let legendY = 10;
      for (const entry of series) {
        const legendText = entry.label;
        ctx.fillStyle = entry.color;
        ctx.fillRect(resolvedWidth - right + 8, legendY - 3, 6, 6);
        ctx.fillStyle = "#4A4A4A";
        ctx.fillText(legendText, resolvedWidth - right + 18, legendY);
        legendY += 8;
      }
    }
  }, [height, series, showGrid, showLegend, width, xLabels, yMax, yMin, yTicks]);

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

PixelLineChartImpl.displayName = "PixelLineChart";

export const PixelLineChart = forwardRef(PixelLineChartImpl);
