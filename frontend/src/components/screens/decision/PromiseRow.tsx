import clsx from "clsx";
import { Check } from "pixelarticons/react/Check";
import { Clock } from "pixelarticons/react/Clock";
import { Close } from "pixelarticons/react/Close";

import type { PromiseDTO } from "@/protocol/types";

interface Props {
  promise: PromiseDTO;
}

const getStatus = (fulfilled: PromiseDTO["fulfilled"]) => {
  if (fulfilled === true) {
    return {
      icon: <Check aria-hidden="true" className="h-4 w-4" />,
      iconLabel: "check",
      label: "已兑现",
      tone: "text-pixel-green",
      subtext: "承诺已核验",
    };
  }

  if (fulfilled === false) {
    return {
      icon: <Close aria-hidden="true" className="h-4 w-4" />,
      iconLabel: "x",
      label: "已失败",
      tone: "text-pixel-red",
      subtext: "目标未达成",
    };
  }

  return {
    icon: <Clock aria-hidden="true" className="h-4 w-4" />,
    iconLabel: "clock",
    label: "进行中",
    tone: "text-pixel-orange",
    subtext: "预计剩余 7 周",
  };
};

export const PromiseRow = ({ promise }: Props) => {
  const status = getStatus(promise.fulfilled);

  return (
    <div className="grid grid-cols-[42px_minmax(0,1fr)_52px] items-center gap-px-sm border-b-2 border-panel-dim py-px-sm last:border-b-0">
      <span className="border-2 border-stroke-ink bg-panel-dim px-px-xs py-px-xs text-center font-retro text-[9px] leading-none">
        Q{promise.quarterMade}
      </span>

      <div className="min-w-0">
        <div className="flex min-w-0 items-center gap-px-xs">
          <span
            aria-label={status.iconLabel}
            className={clsx("flex h-5 w-5 shrink-0 items-center justify-center", status.tone)}
            role="img"
          >
            {status.icon}
          </span>
          <span className="min-w-0 truncate text-px-sm text-ink-1">{promise.text}</span>
        </div>
        <div className="mt-0.5 truncate pl-7 text-px-xs text-ink-3">{status.subtext}</div>
      </div>

      <span className={clsx("text-right font-retro text-[9px] leading-tight", status.tone)}>{status.label}</span>
    </div>
  );
};
