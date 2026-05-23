import { forwardRef, type ButtonHTMLAttributes, type HTMLAttributes } from "react";
import clsx from "clsx";

type MaybeModule<T> = {
  default?: T;
  [key: string]: unknown;
};

const buttonModules = import.meta.glob("./button.tsx", { eager: true }) as Record<string, MaybeModule<unknown>>;
const cardModules = import.meta.glob("./card.tsx", { eager: true }) as Record<string, MaybeModule<unknown>>;
const dialogModules = import.meta.glob("./dialog.tsx", { eager: true }) as Record<string, MaybeModule<unknown>>;

const pickExport = <T,>(modules: Record<string, MaybeModule<T>>, exportName: string): T | null => {
  const mod = Object.values(modules)[0];
  if (!mod) {
    return null;
  }

  return (mod[exportName] as T | undefined) ?? mod.default ?? null;
};

const BaseButton = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, type = "button", ...props }, ref) => (
    <button ref={ref} type={type} className={clsx("inline-flex items-center justify-center", className)} {...props} />
  ),
);
BaseButton.displayName = "EightBitButtonFallback";

const BaseCard = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => (
  <div ref={ref} className={clsx("relative", className)} {...props} />
));
BaseCard.displayName = "EightBitCardFallback";

const BaseDialog = forwardRef<HTMLDivElement, { open?: boolean } & HTMLAttributes<HTMLDivElement>>(
  ({ open = true, className, children, ...props }, ref) => {
    if (!open) {
      return null;
    }

    return (
      <div ref={ref} className={clsx("relative", className)} {...props}>
        {children}
      </div>
    );
  },
);
BaseDialog.displayName = "EightBitDialogFallback";

export const Button = (pickExport(buttonModules, "Button") ?? BaseButton) as typeof BaseButton;
export const Card = (pickExport(cardModules, "Card") ?? BaseCard) as typeof BaseCard;
export const Dialog = (pickExport(dialogModules, "Dialog") ?? BaseDialog) as typeof BaseDialog;
