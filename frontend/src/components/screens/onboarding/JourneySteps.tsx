import clsx from "clsx";

import { PixelCard, PixelIcon } from "@/components/pixel";

export interface JourneyStepsProps {
  title?: string;
  steps: string[];
  currentStep?: number;
  statusLabels?: JourneyStepStatusLabels;
  className?: string;
}

export interface JourneyStepStatusLabels {
  completed: string;
  current: string;
  future: string;
}

const DEFAULT_STATUS_LABELS: JourneyStepStatusLabels = {
  completed: "已完成",
  current: "当前步骤",
  future: "待处理",
};

export function JourneySteps({
  title = "入职流程",
  steps,
  currentStep = 1,
  statusLabels = DEFAULT_STATUS_LABELS,
  className,
}: JourneyStepsProps) {
  return (
    <PixelCard title={title} kind="event" className={clsx("h-full", className)}>
      <ol className="relative space-y-4 pl-4">
        <span aria-hidden="true" className="absolute bottom-2 left-[13px] top-2 w-px bg-stroke-ink" />
        {steps.slice(0, 3).map((step, index) => {
          const stepNumber = index + 1;
          const isCompleted = stepNumber < currentStep;
          const isCurrent = stepNumber === currentStep;

          return (
            <li key={step} className="relative flex items-start gap-3">
              <span
                aria-hidden="true"
                className={clsx(
                  "relative z-10 mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-[999px] border-2 border-stroke-ink",
                  isCurrent && "bg-pixel-blue text-white",
                  isCompleted && "bg-panel-dim text-ink-1",
                  !isCurrent && !isCompleted && "bg-panel text-ink-2",
                )}
              >
                {isCompleted ? <PixelIcon name="check" size={16} /> : null}
              </span>

              <div className="min-w-0 flex-1 pt-1">
                <div
                  className={clsx(
                    "text-px-sm leading-tight",
                    isCurrent && "text-pixel-blue",
                    isCompleted && "text-ink-1",
                    !isCurrent && !isCompleted && "text-ink-2",
                  )}
                >
                  {step}
                </div>
                <div className="mt-1 text-[10px] leading-tight text-ink-2">
                  {isCompleted ? statusLabels.completed : isCurrent ? statusLabels.current : statusLabels.future}
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </PixelCard>
  );
}
