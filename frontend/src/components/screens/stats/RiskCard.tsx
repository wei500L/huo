import clsx from "clsx";

import { PixelCard, PixelIcon, type IconName } from "@/components/pixel";

export interface Risk {
  id: string;
  iconName: IconName;
  title: string;
  description: string;
  level: "low" | "mid" | "high";
}

const LEVEL_META: Record<Risk["level"], { label: string; className: string }> = {
  low: {
    label: "低风险",
    className: "border-pixel-green bg-[#E8F5EA] text-pixel-green",
  },
  mid: {
    label: "中风险",
    className: "border-pixel-orange bg-[#FFF1E1] text-pixel-orange",
  },
  high: {
    label: "高风险",
    className: "border-pixel-red bg-[#FFF5F5] text-pixel-red",
  },
};

const trimDescription = (description: string): string => {
  return description.length > 50 ? description.slice(0, 50) : description;
};

const RiskLevelBadge = ({ level }: { level: Risk["level"] }) => {
  const meta = LEVEL_META[level];

  return (
    <span className={clsx("inline-flex h-6 items-center border-2 px-2 text-px-sm leading-none", meta.className)}>
      {meta.label}
    </span>
  );
};

export const RiskCard = ({ risk }: { risk: Risk }) => {
  return (
    <PixelCard
      kind="risk"
      className="transition-transform duration-75 ease-out hover:-translate-y-1"
    >
      <article className="flex min-h-[116px] flex-col gap-px-sm">
        <div className="flex items-center gap-px-sm">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim">
            <PixelIcon name={risk.iconName} size={24} ariaLabel={risk.title} />
          </span>
          <h3 className="min-w-0 flex-1 truncate text-px-md leading-tight text-ink-1">{risk.title}</h3>
        </div>

        <p className="min-h-[34px] text-px-sm leading-normal text-ink-2">
          {trimDescription(risk.description)}
        </p>

        <div className="mt-auto">
          <RiskLevelBadge level={risk.level} />
        </div>
      </article>
    </PixelCard>
  );
};
