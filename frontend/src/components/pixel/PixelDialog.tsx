import { createPortal } from "react-dom";
import { forwardRef, useEffect, useId, useRef, type MutableRefObject, type ReactNode } from "react";
import clsx from "clsx";

import { Dialog as EightBitDialog } from "@/components/ui/8bit";
import { PixelIcon } from "./PixelIcon";
import { PixelButton, type Variant } from "./PixelButton";

export interface PixelDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  title: string;
  description?: string;
  size?: "sm" | "md" | "lg";
  primaryAction?: { label: string; onClick: () => void; variant?: Variant };
  secondaryAction?: { label: string; onClick: () => void };
  children?: ReactNode;
}

const SIZE_CLASS: Record<NonNullable<PixelDialogProps["size"]>, string> = {
  sm: "w-full max-w-[320px]",
  md: "w-full max-w-[480px]",
  lg: "w-full max-w-[640px]",
};

const FOCUSABLE =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

function isVisible(element: HTMLElement): boolean {
  return element.offsetParent !== null || element.getClientRects().length > 0;
}

function getFocusable(container: HTMLElement): HTMLElement[] {
  return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(isVisible);
}

export const PixelDialog = forwardRef<HTMLDivElement, PixelDialogProps>(
  ({ open, onOpenChange, title, description, size = "md", primaryAction, secondaryAction, children }, ref) => {
    const panelRef = useRef<HTMLDivElement | null>(null);
    const titleId = useId();
    const descriptionId = useId();

    useEffect(() => {
      if (!open) {
        return;
      }

      const previous = document.activeElement as HTMLElement | null;

      const focusFirst = () => {
        const panel = panelRef.current;
        if (!panel) {
          return;
        }

        const focusables = getFocusable(panel);
        (focusables[0] ?? panel).focus();
      };

      const timeout = window.setTimeout(focusFirst, 0);
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === "Escape") {
          event.preventDefault();
          onOpenChange(false);
          return;
        }

        if (event.key !== "Tab") {
          return;
        }

        const panel = panelRef.current;
        if (!panel) {
          return;
        }

        const focusables = getFocusable(panel);
        if (!focusables.length) {
          event.preventDefault();
          panel.focus();
          return;
        }

        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        const current = document.activeElement as HTMLElement | null;

        if (event.shiftKey) {
          if (!current || current === first || !panel.contains(current)) {
            event.preventDefault();
            last.focus();
          }
          return;
        }

        if (!current || current === last || !panel.contains(current)) {
          event.preventDefault();
          first.focus();
        }
      };

      window.addEventListener("keydown", handleKeyDown);
      return () => {
        window.clearTimeout(timeout);
        window.removeEventListener("keydown", handleKeyDown);
        previous?.focus?.();
      };
    }, [open, onOpenChange]);

    if (!open || typeof document === "undefined") {
      return null;
    }

    const setPanelRef = (node: HTMLDivElement | null) => {
      panelRef.current = node;

      if (typeof ref === "function") {
        ref(node);
        return;
      }

      if (ref) {
        (ref as MutableRefObject<HTMLDivElement | null>).current = node;
      }
    };

    const dialog = (
      <div className="fixed inset-0 z-dialog flex items-center justify-center p-px-md">
        <button
          type="button"
          tabIndex={-1}
          aria-hidden="true"
          className="absolute inset-0 border-0 p-0"
          style={{ backgroundColor: "rgba(27, 27, 27, 0.6)" }}
          onClick={() => onOpenChange(false)}
        />

        <EightBitDialog
          ref={setPanelRef}
          open
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
          aria-describedby={description ? descriptionId : undefined}
          tabIndex={-1}
          className={clsx(
            "relative z-10 flex max-h-[calc(100vh-24px)] flex-col overflow-hidden border-2 border-stroke-ink bg-panel shadow-hard",
            SIZE_CLASS[size],
          )}
        >
          <div className="relative flex h-8 items-center justify-center border-b-2 border-stroke-ink bg-pixel-blue px-px-lg text-px-sm text-white leading-none">
            <span id={titleId} className="truncate">
              {title}
            </span>
            <button
              type="button"
              aria-label="Close dialog"
              className="absolute right-px-sm top-px-sm flex h-6 w-6 items-center justify-center border-2 border-stroke-ink bg-panel text-ink-1"
              onClick={() => onOpenChange(false)}
            >
              <span aria-hidden="true">
                <PixelIcon name="close-box" size={16} />
              </span>
            </button>
          </div>

          <div className="overflow-auto px-px-md py-px-md">
            {description ? (
              <p id={descriptionId} className="mb-px-md text-px-sm text-ink-2">
                {description}
              </p>
            ) : null}
            {children}
          </div>

          {primaryAction || secondaryAction ? (
            <div className="flex items-center justify-end gap-px-sm border-t-2 border-stroke-ink px-px-md py-px-sm">
              {secondaryAction ? (
                <PixelButton variant="ghost" size="sm" onClick={secondaryAction.onClick}>
                  {secondaryAction.label}
                </PixelButton>
              ) : null}
              {primaryAction ? (
                <PixelButton variant={primaryAction.variant ?? "blue"} size="sm" onClick={primaryAction.onClick}>
                  {primaryAction.label}
                </PixelButton>
              ) : null}
            </div>
          ) : null}
        </EightBitDialog>
      </div>
    );

    return createPortal(dialog, document.body);
  },
);

PixelDialog.displayName = "PixelDialog";
