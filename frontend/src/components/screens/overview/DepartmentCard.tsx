import { PixelCard, PixelIcon, type IconName } from "@/components/pixel";

export interface DepartmentCardProps {
  name: string;
  status: "healthy" | "tired" | "stable" | "alert";
  comment: string;
  suggestion: string;
  iconName: IconName;
}

const STATUS_META: Record<DepartmentCardProps["status"], { label: string; className: string }> = {
  healthy: { label: "健康", className: "border-pixel-green bg-[#E8F5EA] text-pixel-green" },
  tired: { label: "疲态", className: "border-[#F39A2B] bg-[#FFF1E1] text-[#D96A12]" },
  stable: { label: "稳定", className: "border-[#9AA0A6] bg-[#EEF0F2] text-ink-2" },
  alert: { label: "警报", className: "border-pixel-red bg-[#FCE8E6] text-pixel-red" },
};

const trim = (text: string, max = 20): string => {
  if (text.length <= max) {
    return text;
  }

  return `${text.slice(0, Math.max(0, max - 1))}…`;
};

export const DepartmentCard = ({ name, status, comment, suggestion, iconName }: DepartmentCardProps) => {
  const statusMeta = STATUS_META[status];

  return (
    <PixelCard className="h-full min-h-[156px]">
      <div className="flex h-full min-h-0 flex-col">
        <div className="flex items-start gap-2">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim">
            <PixelIcon name={iconName} size={24} ariaLabel={name} />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex min-w-0 items-center gap-2">
              <h3 className="min-w-0 truncate text-px-base leading-none text-ink-1">{name}</h3>
              <span className={`shrink-0 border px-2 py-1 text-px-xs leading-none ${statusMeta.className}`}>{statusMeta.label}</span>
            </div>
            <p className="mt-1 break-words text-px-sm leading-snug text-ink-2">{trim(comment)}</p>
          </div>
        </div>

        <div className="mt-2 flex min-h-[44px] items-start gap-2 border-2 border-stroke-ink bg-panel-dim px-2 py-2">
          <span className="shrink-0 text-px-sm leading-none text-ink-2">建议动作:</span>
          <p className="min-w-0 flex-1 break-words text-px-sm leading-snug text-ink-1">{trim(suggestion)}</p>
          <PixelIcon name="forward" size={16} ariaLabel="建议动作" className="shrink-0" />
        </div>
      </div>
    </PixelCard>
  );
};

export default DepartmentCard;
