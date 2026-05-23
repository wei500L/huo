import { useCallback, useEffect, useMemo } from "react";

import { PixelButton, PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { createMockDataSource } from "@/net/mockAdapter";
import { makeEnvelope } from "@/protocol/envelope";
import { useScreenStore } from "@/store/screenStore";

import { IntroCard } from "./onboarding/IntroCard";
import { JourneySteps, type JourneyStepStatusLabels } from "./onboarding/JourneySteps";
import type { StatusItem } from "./onboarding/StatusList";

const dataSource = createMockDataSource();
void dataSource.connect("onboarding-ceo");

export interface OnboardingScreenProps {
  eyebrow?: string;
  title?: string;
  subtitle?: string;
  statuses?: StatusItem[];
  journeyTitle?: string;
  steps?: string[];
  currentStep?: number;
  stepStatusLabels?: JourneyStepStatusLabels;
  prompt?: string;
  primaryLabel?: string;
  backgroundLabel?: string;
  settingsLabel?: string;
}

const DEFAULT_STATUSES: StatusItem[] = [
  {
    icon: "fire",
    title: "公司现金流告急",
    subtitle: "账上只够再撑 18 天。",
    tone: "alert",
  },
  {
    icon: "users",
    title: "员工正在观望",
    subtitle: "所有人都在等你先开口。",
    tone: "warn",
  },
  {
    icon: "calendar",
    title: "今天是你上任第一天",
    subtitle: "董事会把签字笔留在了桌上。",
    tone: "info",
  },
];

const DEFAULT_STEPS = ["董事会任命", "到岗报到", "进入办公室"];

export function OnboardingScreen({
  eyebrow = "空降上任",
  title = "欢迎，新任 CEO",
  subtitle = "董事会把最后一张牌交给了你",
  statuses = DEFAULT_STATUSES,
  journeyTitle = "入职流程",
  steps = DEFAULT_STEPS,
  currentStep = 1,
  stepStatusLabels,
  prompt = "董事会把灯留给你了。先看局面，再决定怎么落子。",
  primaryLabel = "开始任职",
  backgroundLabel = "查看背景",
  settingsLabel = "设置",
}: OnboardingScreenProps) {
  const replace = useScreenStore((state) => state.replace);
  const setChrome = useScreenStore((state) => state.setChrome);

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => {
      setChrome({ hud: true, mainBar: true });
    };
  }, [setChrome]);

  const handleStart = useCallback(() => {
    void dataSource.send(makeEnvelope("create_game", { requestLegacies: true }));
    replace("company-select");
  }, [replace]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Enter" || event.repeat) {
        return;
      }

      const target = event.target as HTMLElement | null;
      if (target?.closest("button,a,input,textarea,select,[contenteditable='true']")) {
        return;
      }

      event.preventDefault();
      handleStart();
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handleStart]);

  const actions = useMemo(
    () => [
      { label: backgroundLabel, onClick: () => console.log("[TODO 22] 查看背景") },
      { label: settingsLabel, onClick: () => console.log("[TODO 22] 设置") },
    ],
    [backgroundLabel, settingsLabel],
  );

  return (
    <section className="relative flex h-full min-h-0 flex-col overflow-hidden px-4 py-4 lg:px-6">
      <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-40 border-b-2 border-stroke-ink bg-panel">
        <div className="absolute left-4 top-4 grid grid-cols-4 gap-2 opacity-90">
          <span className="h-6 w-12 border-2 border-stroke-ink bg-panel-dim" />
          <span className="h-6 w-10 border-2 border-stroke-ink bg-panel-dim" />
          <span className="h-6 w-14 border-2 border-stroke-ink bg-panel-dim" />
          <span className="h-6 w-8 border-2 border-stroke-ink bg-panel-dim" />
        </div>
        <div className="absolute right-4 top-4 grid grid-cols-3 gap-2 opacity-80">
          <span className="h-8 w-8 border-2 border-stroke-ink bg-pixel-blue" />
          <span className="h-8 w-8 border-2 border-stroke-ink bg-panel-dim" />
          <span className="h-8 w-8 border-2 border-stroke-ink bg-pixel-orange" />
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-12 border-t-2 border-stroke-ink bg-floor" />
      </div>

      <div className="relative z-10 mx-auto flex h-full w-full max-w-[1600px] flex-col gap-4">
        <div className="grid flex-1 gap-4 lg:grid-cols-12 lg:items-end">
          <div className="flex justify-center lg:col-span-5 lg:justify-start">
            <div className="relative h-[320px] w-[240px] lg:h-[384px] lg:w-[288px] xl:h-[427px] xl:w-[320px]">
              <PixelPortrait
                id="ceo_male_01"
                expression="confident"
                size="hero"
                position="left"
                className="!h-full !w-full"
              />
            </div>
          </div>

          <div className="lg:col-span-5">
            <IntroCard eyebrow={eyebrow} title={title} subtitle={subtitle} statuses={statuses} />
          </div>

          <div className="lg:col-span-2">
            <JourneySteps
              title={journeyTitle}
              steps={steps}
              currentStep={currentStep}
              statusLabels={stepStatusLabels}
            />
          </div>
        </div>

        <div className="mt-auto flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div className="w-full lg:max-w-[560px]">
            <PixelSpeechBubble tone="neutral" arrow="none" text={prompt} />
          </div>

          <div className="flex flex-col items-center gap-2">
            <div className="w-full max-w-[320px]">
              <PixelButton variant="blue" size="lg" fullWidth hotkey="Enter" onClick={handleStart}>
                {primaryLabel}
              </PixelButton>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-2">
              {actions.map((action) => (
                <PixelButton key={action.label} variant="ghost" size="md" onClick={action.onClick}>
                  {action.label}
                </PixelButton>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default OnboardingScreen;
