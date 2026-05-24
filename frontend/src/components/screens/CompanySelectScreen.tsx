import { useCallback, useEffect, useRef, useState } from "react";

import { PixelButton, PixelIcon, PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { createMockDataSource } from "@/net/mockAdapter";
import { makeEnvelope } from "@/protocol/envelope";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { CompanyChoiceCard, type CompanyChoice } from "./companySelect/CompanyChoiceCard";
import type { MilestoneItem } from "./companySelect/MilestoneList";
import { RevengeProgressPanel, type RevengeProgressMeta } from "./companySelect/RevengeProgressPanel";
import { ResourceShelf } from "./companySelect/ResourceShelf";

const companySelectDataSource = createMockDataSource();
void companySelectDataSource.connect("company-select-ceo");

const COMPANY_CHOICES: CompanyChoice[] = [
  {
    templateId: "C-01",
    name: "灵眸科技",
    business: "计算机视觉芯片",
    tag: "AI",
    iconName: "target",
    brandColor: "blue",
    description: "计算机视觉芯片量产前夜，烧钱、内斗和董事会压力一起爆表。",
    currentStakePercent: 12.5,
  },
  {
    templateId: "C-02",
    name: "源语互动",
    business: "独立游戏研发",
    tag: "游戏研发",
    iconName: "message",
    brandColor: "green",
    description: "独立游戏研发团队卡在上线前，玩家期待和现金流都快见底。",
    currentStakePercent: 5.1,
  },
  {
    templateId: "C-03",
    name: "钛深智能",
    business: "工业 AI 解决方案",
    tag: "工业科技",
    iconName: "settings",
    brandColor: "purple",
    description: "工业 AI 解决方案刚签大单，交付、合规和老股东都在等你翻车。",
    currentStakePercent: 0,
  },
];

const MOCK_META_PROGRESS: RevengeProgressMeta = {
  reputation: 1350,
  totalStakePercent: 18,
  unlockedCount: 3,
  totalUnlockCount: 10,
};

const MILESTONES: MilestoneItem[] = [
  { value: 30, label: "声望", achieved: true },
  { value: 50, label: "声望", achieved: true },
  { value: 100, label: "声望", achieved: true },
  { value: 200, label: "声望", achieved: true },
  { value: "10%", label: "持股", achieved: true },
  { value: "25%", label: "持股", achieved: false },
  { value: "50%", label: "持股", achieved: false },
  { value: "终极目标", label: "成为最大股东", achieved: false },
];

export const CompanySelectScreen = () => {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const startPendingRef = useRef(false);
  const replace = useScreenStore((state) => state.replace);
  const setChrome = useScreenStore((state) => state.setChrome);
  const pushToast = useGameStore((state) => state.pushToast);

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const selectedChoice = COMPANY_CHOICES.find((choice) => choice.templateId === selectedTemplateId) ?? null;

  const showComingSoon = useCallback(
    (label: "查看规则" | "读取进度", idSuffix: string) => {
      console.log(`[CompanySelectScreen] ${label}: 敬请期待`);
      pushToast({
        id: `company-select-${idSuffix}-coming-soon`,
        level: "info",
        message: "敬请期待",
      });
    },
    [pushToast],
  );

  const startGame = useCallback(async () => {
    if (!selectedChoice || startPendingRef.current) {
      return;
    }

    startPendingRef.current = true;
    setIsStarting(true);

    try {
      await companySelectDataSource.send(
        makeEnvelope("create_game", {
          requestLegacies: true,
          templateId: selectedChoice.templateId,
        }),
      );
      replace("office");
    } catch (error) {
      startPendingRef.current = false;
      setIsStarting(false);
      pushToast({
        id: `company-select-start-error-${Date.now()}`,
        level: "error",
        message: "开局失败",
        hint: error instanceof Error ? error.message : "请稍后重试",
      });
    }
  }, [pushToast, replace, selectedChoice]);

  return (
    <div className="relative h-full overflow-auto bg-canvas">
      <div className="relative mx-auto flex min-h-full max-w-[1920px] flex-col gap-4 px-4 py-4 lg:px-6 lg:py-6">
        <span className="sr-only">[Screen: company-select]</span>

        <section className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-12">
          <div className="lg:col-span-2">
            <div className="flex h-full items-end justify-center lg:justify-start">
              <PixelPortrait
                className="!aspect-[320/427] !h-auto !w-full max-w-[220px] md:max-w-[260px] lg:max-w-full"
                expression="tired"
                id="ceo_male_01"
                position="inline"
                size="hero"
              />
            </div>
          </div>

          <div className="flex min-h-0 flex-col lg:col-span-7">
            <header className="mb-px-md border-b-2 border-stroke-ink pb-px-md">
              <h1 className="font-retro text-px-xxl leading-tight text-ink-1 lg:text-px-hero">空降 CEO</h1>
              <p className="mt-px-sm text-px-md leading-normal text-ink-2">
                打工人复仇：从空降 CEO 到大股东
              </p>
            </header>

            <div className="grid min-h-0 flex-1 grid-cols-1 gap-px-md md:grid-cols-3">
              {COMPANY_CHOICES.slice(0, 3).map((choice) => (
                <CompanyChoiceCard
                  key={choice.templateId}
                  choice={choice}
                  selected={choice.templateId === selectedTemplateId}
                  onSelect={() => setSelectedTemplateId(choice.templateId)}
                />
              ))}
            </div>
          </div>

          <div className="min-h-0 lg:col-span-3">
            <RevengeProgressPanel className="min-h-[480px]" meta={MOCK_META_PROGRESS} milestones={MILESTONES} />
          </div>
        </section>

        <ResourceShelf />

        <section className="relative flex min-h-[220px] shrink-0 flex-col justify-end gap-px-md lg:block lg:min-h-[172px]">
          <div className="max-w-[min(100%,420px)] lg:absolute lg:bottom-8 lg:left-0">
            <PixelSpeechBubble
              arrow="down"
              text="董事会把这家烂公司丢给了你。先活下来，再把他们全收拾了。"
              tone="neutral"
            />
          </div>

          <div className="flex flex-wrap items-center justify-center gap-px-sm lg:absolute lg:inset-x-0 lg:bottom-0">
            <PixelButton
              disabled={!selectedChoice || isStarting}
              hotkey="Enter"
              icon={<PixelIcon name="forward" size={24} />}
              loading={isStarting}
              size="lg"
              variant="blue"
              onClick={startGame}
            >
              开始这一局
            </PixelButton>
            <PixelButton
              icon={<PixelIcon name="message" size={24} />}
              variant="ghost"
              onClick={() => showComingSoon("查看规则", "rules")}
            >
              查看规则
            </PixelButton>
            <PixelButton
              icon={<PixelIcon name="save" size={24} />}
              variant="ghost"
              onClick={() => showComingSoon("读取进度", "load")}
            >
              读取进度
            </PixelButton>
          </div>
        </section>
      </div>
    </div>
  );
};
