import clsx from "clsx";

import { PixelCard } from "@/components/pixel";

import { StatusList, type StatusItem } from "./StatusList";

export interface IntroCardProps {
  eyebrow?: string;
  title: string;
  subtitle: string;
  statuses: StatusItem[];
  className?: string;
}

export function IntroCard({ eyebrow, title, subtitle, statuses, className }: IntroCardProps) {
  return (
    <PixelCard className={clsx("h-full", className)}>
      <div className="space-y-4">
        <div className="space-y-2">
          {eyebrow ? <div className="font-pixel text-px-md leading-tight text-pixel-orange">{eyebrow}</div> : null}
          <div className="font-pixel text-[32px] leading-none text-ink-1">{title}</div>
          <div className="text-px-md leading-tight text-ink-2">{subtitle}</div>
        </div>

        <StatusList items={statuses} />
      </div>
    </PixelCard>
  );
}
