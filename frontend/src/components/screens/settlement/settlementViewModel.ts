import type { SettlementDTO, PromiseDTO } from "@/protocol/types";

import type { BoardCommentItem } from "./BoardCommentCard";
import type { PromiseResultItem } from "./PromiseResultList";

export type MetricKey = "cash" | "morale" | "board" | "face";

export const METRIC_ORDER: MetricKey[] = ["cash", "morale", "board", "face"];

export const METRIC_CONFIG: Record<MetricKey, { label: string; iconName: "money" | "morale" | "board" | "face" }> = {
  cash: { label: "现金流", iconName: "money" },
  morale: { label: "士气", iconName: "morale" },
  board: { label: "董事会信任", iconName: "board" },
  face: { label: "公司体面", iconName: "face" },
};

export const isMetricKey = (value: string | undefined): value is MetricKey => {
  return value === "cash" || value === "morale" || value === "board" || value === "face";
};

export const formatMetricValue = (metricKey: MetricKey, value: number): string => {
  const formatted = Math.trunc(value).toLocaleString("zh-CN");
  return metricKey === "cash" ? `¥${formatted}` : formatted;
};

export const formatMetricDelta = (metricKey: MetricKey, delta: number): string => {
  const sign = delta > 0 ? "+" : "";
  return `${sign}${formatMetricValue(metricKey, delta)}`;
};

export const clampQuote = (value: string | undefined | null): string => {
  const text = (value ?? "").trim();
  return text.length > 30 ? text.slice(0, 30) : text;
};

export const resolveMetricStatus = (
  metricKey: MetricKey,
  delta: number,
): { text: string; color: "green" | "yellow" | "red" } => {
  if (delta === 0) {
    if (metricKey === "cash") return { text: "表现平稳", color: "yellow" };
    if (metricKey === "morale") return { text: "士气稳定", color: "yellow" };
    if (metricKey === "board") return { text: "信任持平", color: "yellow" };
    return { text: "体面持平", color: "yellow" };
  }

  if (delta > 0) {
    if (metricKey === "cash") return { text: "表现良好", color: "green" };
    if (metricKey === "morale") return { text: "士气回升", color: "green" };
    if (metricKey === "board") return { text: "信任回升", color: "green" };
    return { text: "体面回暖", color: "green" };
  }

  if (metricKey === "morale") return { text: "士气下滑", color: "red" };
  if (metricKey === "board") return { text: "信任下降", color: "red" };
  if (metricKey === "face") return { text: "体面受损", color: "red" };
  return { text: "表现下滑", color: "red" };
};

export const metricDeltaSummary = (metricsDelta: Partial<Record<MetricKey, number>> | null): string => {
  if (!metricsDelta) {
    return "";
  }

  const parts = METRIC_ORDER.flatMap((metricKey) => {
    const value = metricsDelta[metricKey];
    if (typeof value !== "number" || !Number.isFinite(value) || value === 0) {
      return [];
    }

    return [`${metricKey} ${formatMetricDelta(metricKey, value)}`];
  });

  return parts.join(" / ");
};

export const buildPromiseRows = (params: {
  promiseLog: PromiseDTO[];
  metricsDelta: Partial<Record<MetricKey, number>> | null;
  quarter: number;
}): PromiseResultItem[] => {
  const rows = params.promiseLog.slice(0, 4).map((promise, index) => {
    const status = promise.fulfilled === true ? "fulfilled" : promise.fulfilled === false ? "failed" : "in_progress";
    const parsedMetric = promise.parsed?.metric?.toLowerCase();
    const metricKey: MetricKey = isMetricKey(parsedMetric) ? parsedMetric : METRIC_ORDER[index] ?? "cash";
    const deltaValue = params.metricsDelta?.[metricKey];
    const delta = typeof deltaValue === "number" ? formatMetricDelta(metricKey, deltaValue) : undefined;

    return {
      quarter: `Q${promise.quarterMade}`,
      status,
      text: clampQuote(promise.text),
      expected: clampQuote(promise.parsed?.targetExpr),
      result: status === "fulfilled" ? "已兑现" : status === "failed" ? "已翻车" : "进行中",
      delta,
    } satisfies PromiseResultItem;
  });

  return rows.slice(0, 4);
};

export const buildBoardComments = (resolvedSettlement: SettlementDTO | null): BoardCommentItem[] => {
  if (!resolvedSettlement) {
    return [];
  }

  return [
    {
      name: resolvedSettlement.boardReaction.vote,
      portraitId: "board_chairman" as const,
      comment: clampQuote(resolvedSettlement.boardReaction.speech),
    },
  ].filter((item) => item.comment);
};

export const resolveEmployeeGossipTone = (mood?: string): "rip" | "thinking" | "neutral" => {
  if (mood === "numb") {
    return "rip";
  }
  if (mood === "anxious") {
    return "thinking";
  }
  return "neutral";
};
