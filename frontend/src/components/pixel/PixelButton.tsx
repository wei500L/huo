import { forwardRef, type ReactNode } from "react";
import clsx from "clsx";
import { Loader } from "pixelarticons/react/Loader";

import { Button as EightBitButton } from "@/components/ui/8bit";

export type Variant = "blue" | "green" | "orange" | "red" | "ghost" | "danger";
export type Size = "sm" | "md" | "lg";

export interface PixelButtonProps {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
  disabled?: boolean;
  pressed?: boolean;
  fullWidth?: boolean;
  loading?: boolean;
  children: ReactNode;
  onClick?: () => void;
  ariaLabel?: string;
  hotkey?: string;
}

const SIZE_CLASS: Record<Size, string> = {
  sm: "h-8",
  md: "h-11",
  lg: "h-14",
};

const VARIANT_CLASS: Record<Variant, string> = {
  blue: "border-stroke-ink bg-pixel-blue text-white",
  green: "border-stroke-ink bg-pixel-green text-white",
  orange: "border-stroke-ink bg-pixel-orange text-white",
  red: "border-stroke-ink bg-pixel-red text-white",
  danger: "border-stroke-ink bg-alarm-red text-white",
  ghost: "border-stroke-ink bg-panel text-ink-1",
};

const VARIANT_HOVER_CLASS: Record<Variant, string> = {
  blue: "hover:bg-pixel-blue/90",
  green: "hover:bg-pixel-green/90",
  orange: "hover:bg-pixel-orange/90",
  red: "hover:bg-pixel-red/90",
  danger: "hover:bg-alarm-red/90",
  ghost: "hover:bg-panel-dim",
};

export const PixelButton = forwardRef<HTMLButtonElement, PixelButtonProps>(
  (
    {
      variant = "blue",
      size = "md",
      icon,
      disabled = false,
      pressed = false,
      fullWidth = false,
      loading = false,
      children,
      onClick,
      ariaLabel,
      hotkey,
    },
    ref,
  ) => {
    const isDisabled = disabled || loading;
    const surfaceClass = isDisabled ? "border-stroke-ink bg-panel-dim text-ink-3" : VARIANT_CLASS[variant];
    const interactionClass = !isDisabled && !pressed && !loading
      ? `${VARIANT_HOVER_CLASS[variant]} hover:-translate-y-0.5 hover:shadow-[6px_6px_0_0_var(--stroke-ink)] active:translate-y-0.5 active:shadow-none`
      : "";
    const stateClass = disabled
      ? "shadow-none translate-y-0 cursor-not-allowed"
      : pressed
        ? "shadow-none translate-y-0.5"
        : loading
          ? "shadow-hard cursor-wait opacity-90"
          : "shadow-hard";

    return (
      <EightBitButton
        ref={ref}
        type="button"
        aria-label={ariaLabel}
        aria-busy={loading || undefined}
        aria-disabled={disabled || loading || undefined}
        disabled={isDisabled}
        onClick={isDisabled ? undefined : onClick}
        className={clsx(
          "relative inline-flex items-center justify-center gap-px-sm border-2 px-px-md py-px-sm font-pixel text-px-base leading-none",
          "transition-transform duration-75 ease-out transition-shadow pixel-render select-none",
          SIZE_CLASS[size],
          surfaceClass,
          interactionClass,
          stateClass,
          fullWidth && "w-full",
          hotkey && "pr-px-lg",
        )}
      >
        {(icon || loading) ? (
          <span aria-hidden="true" className="flex h-6 w-6 shrink-0 items-center justify-center">
            {loading ? <Loader className="h-6 w-6 animate-spin" /> : icon}
          </span>
        ) : null}
        <span className="min-w-0 flex-1 truncate text-center">{children}</span>
        {hotkey ? (
          <span className="absolute bottom-px-sm right-px-sm font-retro text-[10px] leading-none text-current">
            {hotkey}
          </span>
        ) : null}
      </EightBitButton>
    );
  },
);

PixelButton.displayName = "PixelButton";
