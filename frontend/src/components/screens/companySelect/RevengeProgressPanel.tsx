import clsx from "clsx";

import { PixelCard, PixelIcon } from "@/components/pixel";

import { MilestoneList, type MilestoneItem } from "./MilestoneList";

export interface RevengeProgressMeta {
  reputation: number;
  totalStakePercent: number;
  unlockedCount: number;
  totalUnlockCount: number;
}

interface RevengeProgressPanelProps {
  meta: Partial<RevengeProgressMeta> | null;
  milestones: MilestoneItem[];
  className?: string;
}

const resolveNumber = (value: unknown): number => {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
};

const formatPercent = (value: number): string => {
  return `${value.toLocaleString("zh-CN", { maximumFractionDigits: 1 })}%`;
};

const ProgressMetric = ({
  label,
  value,
  icon,
  tone,
}: {
  label: string;
  value: string;
  icon: "star" | "coins" | "unlock";
  tone: "blue" | "green" | "purple";
}) => {
  const toneClass = {
    blue: "text-pixel-blue",
    green: "text-pixel-green",
    purple: "text-legacy-purple",
  }[tone];
  const iconName = icon === "unlock" ? "unlock" : icon;

  return (
    <div className="flex items-center gap-px-sm border-2 border-stroke-ink bg-panel-dim px-px-sm py-px-sm shadow-hard-sm">
      <span className={clsx("flex h-9 w-9 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel", toneClass)}>
        <PixelIcon name={iconName} size={16} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-px-sm leading-tight text-ink-2">{label}</span>
        <span className={clsx("block truncate font-retro text-px-xl leading-tight", toneClass)}>{value}</span>
      </span>
    </div>
  );
};

export const RevengeProgressPanel = ({ meta, milestones, className }: RevengeProgressPanelProps) => {
  const reputation = resolveNumber(meta?.reputation);
  const totalStakePercent = resolveNumber(meta?.totalStakePercent);
  const unlockedCount = resolveNumber(meta?.unlockedCount);
  const totalUnlockCount = resolveNumber(meta?.totalUnlockCount);

  return (
    <PixelCard
      badge={<PixelIcon name="target" size={16} />}
      className={clsx("h-full", className)}
      kind="default"
      title="复仇进度"
    >
      <div className="flex h-full flex-col gap-px-md">
        <div className="space-y-px-sm">
          <ProgressMetric
            icon="star"
            label="总声望"
            tone="blue"
            value={reputation.toLocaleString("zh-CN")}
          />
          <ProgressMetric
            icon="coins"
            label="累计持股"
            tone="green"
            value={formatPercent(totalStakePercent)}
          />
          <ProgressMetric
            icon="unlock"
            label="已解锁内容"
            tone="purple"
            value={`${unlockedCount}/${totalUnlockCount}`}
          />
        </div>

        <div className="min-h-0 flex-1">
          <div className="mb-px-sm flex items-center gap-px-sm border-b-2 border-stroke-ink pb-px-xs">
            <PixelIcon name="trophy" size={16} />
            <h2 className="text-px-md leading-tight">里程碑</h2>
          </div>
          <MilestoneList items={milestones} />
        </div>
      </div>
    </PixelCard>
  );
};
