import { forwardRef, type ButtonHTMLAttributes, type HTMLAttributes, type ReactNode } from "react";
import clsx from "clsx";

export type EightBitButtonProps = ButtonHTMLAttributes<HTMLButtonElement>;
export type EightBitCardProps = HTMLAttributes<HTMLDivElement>;
export type EightBitDialogProps = HTMLAttributes<HTMLDivElement> & { open?: boolean; children?: ReactNode };

export const Button = forwardRef<HTMLButtonElement, EightBitButtonProps>(
  ({ className, type = "button", ...props }, ref) => {
    return <button ref={ref} type={type} className={clsx(className)} {...props} />;
  },
);

Button.displayName = "EightBitButton";

export const Card = forwardRef<HTMLDivElement, EightBitCardProps>(({ className, ...props }, ref) => {
  return <div ref={ref} className={clsx(className)} {...props} />;
});

Card.displayName = "EightBitCard";

export const Dialog = forwardRef<HTMLDivElement, EightBitDialogProps>(({ className, open: _open, ...props }, ref) => {
  return <div ref={ref} className={clsx(className)} {...props} />;
});

Dialog.displayName = "EightBitDialog";
