import { forwardRef, useEffect, useRef, type ForwardedRef } from "react";
import clsx from "clsx";

import type { PixelLineChartSeries } from "./PixelLineChart";

export interface PixelBarChartProps {
  width: number;
  height: number;
  series?: PixelLineChartSeries[];
  values?: number[];
  xLabels?: string[];
  labels?: string[];
  color?: string;
  legendLabel?: string;
  yMin?: number;
  yMax?: number;
  yTicks?: number[];
  showGrid?: boolean;
  showLegend?: boolean;
  className?: string;
}

const clampInt = (value: number): number => Math.round(value);

const darkStroke = "#1B1B1B";

const drawGridLine = (ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, horizontal: boolean): void => {
  ctx.fillStyle = "#DDD";
  if (horizontal) {
    ctx.fillRect(x, y, width, 1);
  } else {
    ctx.fillRect(x, y, 1, height);
  }
};

const formatNumber = (value: number): string => new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(value));

function PixelBarChartImpl(
  { width, height, series, values, xLabels, labels, color, legendLabel, yMin = 0, yMax = 100, yTicks = [0, 25, 50, 75, 100], showGrid = true, showLegend = true, className }: PixelBarChartProps,
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

    const resolvedSeries = series?.length
      ? series
      : values?.length
        ? [
            {
              id: "series-0",
              label: legendLabel ?? "Value",
              color: color ?? "#2E6FE6",
              values,
            },
          ]
        : [];
    const resolvedLabels = xLabels ?? labels ?? resolvedSeries[0]?.values.map((_, index) => String(index + 1)) ?? [];
    const resolvedWidth = clampInt(width);
    const resolvedHeight = clampInt(height);
    const left = 28;
    const right = showLegend ? 96 : 12;
    const top = showLegend ? 24 + Math.min(resolvedSeries.length, 4) * 8 : 12;
    const bottom = 22;
    const plotWidth = Math.max(1, resolvedWidth - left - right);
    const plotHeight = Math.max(1, resolvedHeight - top - bottom);
    const range = Math.max(1, yMax - yMin);
    const totalBars = Math.max(1, resolvedSeries.length * Math.max(1, resolvedLabels.length));
    const barWidth = Math.max(1, Math.floor(plotWidth / totalBars));

    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, resolvedWidth, resolvedHeight);
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, resolvedWidth, resolvedHeight);
    ctx.font = "10px 'Fusion Pixel', monospace";
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

    const totalGroupWidth = barWidth * totalBars;
    const offsetX = left + Math.max(0, Math.floor((plotWidth - totalGroupWidth) / 2));
    let barIndex = 0;

    for (let labelIndex = 0; labelIndex < resolvedLabels.length; labelIndex += 1) {
      for (const entry of resolvedSeries) {
        const value = entry.values[labelIndex] ?? yMin;
        const normalized = (value - yMin) / range;
        const barHeight = Math.max(1, Math.round(normalized * plotHeight));
        const x = offsetX + barIndex * barWidth;
        const y = top + plotHeight - barHeight;

        ctx.fillStyle = entry.color;
        ctx.fillRect(x, y, barWidth, barHeight);
        ctx.fillStyle = darkStroke;
        ctx.fillRect(x, y, barWidth, 1);
        ctx.fillStyle = "#4A4A4A";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        ctx.fillText(formatNumber(value), x + Math.floor(barWidth / 2), Math.max(top + 8, y - 2));

        barIndex += 1;
      }
    }

    if (showGrid) {
      for (let index = 0; index < resolvedLabels.length; index += 1) {
        const groupX = offsetX + Math.round((index * resolvedSeries.length + resolvedSeries.length / 2) * barWidth);
        drawGridLine(ctx, groupX, top, 1, plotHeight, false);
      }
    }

    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    for (let index = 0; index < resolvedLabels.length; index += 1) {
      const groupX = offsetX + Math.round((index * resolvedSeries.length + resolvedSeries.length / 2) * barWidth);
      ctx.fillStyle = "#4A4A4A";
      ctx.fillText(resolvedLabels[index] ?? "", groupX, resolvedHeight - 16);
    }

    if (showLegend) {
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      let legendY = 10;
      for (const entry of resolvedSeries) {
        ctx.fillStyle = entry.color;
        ctx.fillRect(resolvedWidth - right + 8, legendY - 3, 6, 6);
        ctx.fillStyle = "#4A4A4A";
        ctx.fillText(entry.label, resolvedWidth - right + 18, legendY);
        legendY += 8;
      }
    }
  }, [color, height, labels, legendLabel, series, showGrid, showLegend, values, width, xLabels, yMax, yMin, yTicks]);

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

PixelBarChartImpl.displayName = "PixelBarChart";

export const PixelBarChart = forwardRef(PixelBarChartImpl);
