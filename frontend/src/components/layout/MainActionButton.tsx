import clsx from "clsx";

import { PixelIcon, type IconName } from "@/components/pixel";

export interface Props {
  variant: "blue" | "green" | "orange" | "red";
  icon: IconName;
  label: string;
  hotkey: "1" | "2" | "3" | "4";
  badgeCount?: number;
  disabled?: boolean;
  onClick: () => void;
}

const VARIANT_CLASS: Record<Props["variant"], string> = {
  blue: "bg-pixel-blue",
  green: "bg-pixel-green",
  orange: "bg-pixel-orange",
  red: "bg-pixel-red",
};

const formatBadgeCount = (value: number): string => {
  return value > 9 ? "9+" : String(value);
};

export const MainActionButton = ({
  variant,
  icon,
  label,
  hotkey,
  badgeCount = 0,
  disabled = false,
  onClick,
}: Props) => {
  const hasBadge = badgeCount > 0;

  return (
    <button
      type="button"
      aria-label={label}
      disabled={disabled}
      onClick={disabled ? undefined : onClick}
      className={clsx(
        "relative flex min-h-16 min-w-0 flex-1 items-center gap-2 border-2 px-4 pr-9 font-pixel text-px-sm leading-none pixel-render",
        "sm:text-px-base lg:h-16 lg:text-px-md",
        "transition-transform duration-75 ease-out transition-shadow",
        disabled
          ? "cursor-not-allowed border-stroke-ink bg-panel-dim text-ink-3 shadow-none"
          : clsx(
              "border-stroke-ink text-white shadow-[4px_4px_0_0_var(--stroke-ink)]",
              "hover:-translate-y-0.5 hover:shadow-[6px_6px_0_0_var(--stroke-ink)] active:translate-y-0.5 active:shadow-none",
              VARIANT_CLASS[variant],
            ),
      )}
      >
      <span aria-hidden="true" className="flex h-6 w-6 shrink-0 items-center justify-center">
        <PixelIcon color="currentColor" name={icon} size={24} />
      </span>

      <span className="min-w-0 flex-1 truncate text-left">{label}</span>

      {hasBadge ? (
        <span
          aria-label={`${label} ${formatBadgeCount(badgeCount)}`}
          className="absolute right-1 top-1 hidden h-[14px] w-[14px] items-center justify-center border border-stroke-ink bg-alarm-red font-retro text-[8px] leading-none text-white lg:flex"
        >
          {formatBadgeCount(badgeCount)}
        </span>
      ) : null}

      <span className="absolute bottom-1 right-2 hidden font-retro text-[10px] leading-none text-current lg:block">
        {hotkey}
      </span>
    </button>
  );
};
