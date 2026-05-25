import clsx from "clsx";

import { PixelCard, PixelIcon } from "@/components/pixel";

import { MilestoneList, type MilestoneItem } from "./MilestoneList";

export interface RevengeProgressMeta {
  totalRuns: number;
  deathLogCount: number;
  pressArchiveCount: number;
  unlockedCount: number;
}

interface RevengeProgressPanelProps {
  meta: Partial<RevengeProgressMeta> | null;
  milestones: MilestoneItem[];
  className?: string;
}

const resolveNumber = (value: unknown): number => {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
};

const ProgressMetric = ({
  label,
  value,
  icon,
  tone,
}: {
  label: string;
  value: string;
  icon: "star" | "rip" | "unlock";
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
  const totalRuns = resolveNumber(meta?.totalRuns);
  const deathLogCount = resolveNumber(meta?.deathLogCount);
  const pressArchiveCount = resolveNumber(meta?.pressArchiveCount);
  const unlockedCount = resolveNumber(meta?.unlockedCount);

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
            label="历史局数"
            tone="blue"
            value={totalRuns.toLocaleString("zh-CN")}
          />
          <ProgressMetric
            icon="rip"
            label="死亡记录"
            tone="green"
            value={deathLogCount.toLocaleString("zh-CN")}
          />
          <ProgressMetric
            icon="unlock"
            label="已解锁内容"
            tone="purple"
            value={unlockedCount.toLocaleString("zh-CN")}
          />
          <ProgressMetric
            icon="star"
            label="发布会档案"
            tone="blue"
            value={pressArchiveCount.toLocaleString("zh-CN")}
          />
        </div>

        <div className="min-h-0 flex-1">
          <div className="mb-px-sm flex items-center gap-px-sm border-b-2 border-stroke-ink pb-px-xs">
            <PixelIcon name="trophy" size={16} />
            <h2 className="text-px-md leading-tight">里程碑</h2>
          </div>
          {milestones.length > 0 ? (
            <MilestoneList items={milestones} />
          ) : (
            <div className="border-2 border-stroke-ink bg-panel-dim px-px-sm py-px-md text-px-sm leading-normal text-ink-2">
              暂无后端解锁记录
            </div>
          )}
        </div>
      </div>
    </PixelCard>
  );
};
