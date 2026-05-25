import clsx from "clsx";

import { PixelCard, PixelIcon, type IconName } from "@/components/pixel";

export interface CompanyChoice {
  templateId: string;
  name: string;
  business: string;
  tag: string;
  iconName: IconName;
  brandColor: "blue" | "green" | "purple" | "orange";
  description: string;
  currentStakePercent?: number;
}

interface CompanyChoiceCardProps {
  choice: CompanyChoice;
  selected: boolean;
  onSelect: () => void;
}

const BRAND_TEXT_CLASS: Record<CompanyChoice["brandColor"], string> = {
  blue: "text-pixel-blue",
  green: "text-pixel-green",
  purple: "text-legacy-purple",
  orange: "text-pixel-orange",
};

const formatStake = (percent: number): string => {
  const value = Number.isFinite(percent) ? percent : 0;
  return `${value.toLocaleString("zh-CN", { maximumFractionDigits: 1 })}%`;
};

export const CompanyChoiceCard = ({ choice, selected, onSelect }: CompanyChoiceCardProps) => {
  const brandTextClass = BRAND_TEXT_CLASS[choice.brandColor];

  return (
    <PixelCard
      className="h-full transition-transform duration-75 ease-out hover:-translate-y-1"
      footer={
        <div className="flex items-end justify-between gap-px-sm">
          <span className="text-px-sm leading-tight text-ink-2">当前个人持股</span>
          <span className={clsx("shrink-0 font-retro text-px-xxl leading-none", brandTextClass)}>
            {formatStake(choice.currentStakePercent ?? 0)}
          </span>
        </div>
      }
      kind="info"
      selected={selected}
      titleColor={choice.brandColor}
      onClick={onSelect}
    >
      <div className="flex h-full flex-col items-center text-center">
        <span className="sr-only">{selected ? "已选择" : "未选择"}</span>

        <div className="mb-px-md flex h-20 w-20 items-center justify-center border-2 border-stroke-ink bg-panel-dim shadow-hard-sm">
          <PixelIcon
            ariaLabel={`${choice.name} 图标`}
            className={brandTextClass}
            name={choice.iconName}
            size={64}
          />
        </div>

        <h2 className="w-full truncate text-px-lg leading-tight">{choice.name}</h2>

        <div className="mt-px-sm flex max-w-full flex-col items-center gap-px-xs">
          <span className={clsx("border-2 border-stroke-ink bg-panel px-px-sm py-[2px] text-px-sm leading-none", brandTextClass)}>
            {choice.tag}
          </span>
          <span className="max-w-full truncate text-px-xs leading-tight text-ink-2">{choice.business}</span>
        </div>

        <p className="mt-px-md min-h-[48px] text-px-sm leading-normal text-ink-2">{choice.description}</p>
      </div>
    </PixelCard>
  );
};
