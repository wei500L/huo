import { useCallback, useEffect, useRef, useState } from "react";

import { PixelButton, PixelIcon, PixelPortrait, PixelSpeechBubble, type IconName } from "@/components/pixel";
import { createGame, loadCompanyTemplates, loadPlayerMeta } from "@/net/gameClient";
import type { CompanyTemplateDTO, MetaSummaryDTO } from "@/protocol/types";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { CompanyChoiceCard, type CompanyChoice } from "./companySelect/CompanyChoiceCard";
import type { MilestoneItem } from "./companySelect/MilestoneList";
import { RevengeProgressPanel, type RevengeProgressMeta } from "./companySelect/RevengeProgressPanel";

const CHOICE_ICONS: IconName[] = ["target", "message", "settings", "briefcase"];
const CHOICE_COLORS: CompanyChoice["brandColor"][] = ["blue", "green", "purple", "orange"];

const toCompanyChoice = (template: CompanyTemplateDTO, index: number): CompanyChoice => ({
  templateId: template.templateId,
  name: template.name,
  business: template.business,
  tag: `荒诞度 ${template.absurdity}`,
  iconName: CHOICE_ICONS[index % CHOICE_ICONS.length],
  brandColor: CHOICE_COLORS[index % CHOICE_COLORS.length],
  description: template.deathCauses[0]?.description ?? template.foundingMotto,
});

const toProgressMeta = (meta: MetaSummaryDTO | null): RevengeProgressMeta | null =>
  meta
    ? {
        totalRuns: meta.totalRuns,
        deathLogCount: meta.deathLogCount,
        pressArchiveCount: meta.pressArchiveCount,
        unlockedCount: meta.unlockedLegacies.length + meta.unlockedStyles.length,
      }
    : null;

const toMilestones = (meta: MetaSummaryDTO | null): MilestoneItem[] =>
  meta?.unlockedLegacies.map((legacy) => ({
    value: `Q${legacy.earnedAtQuarter}`,
    label: legacy.labelZh,
    achieved: true,
  })) ?? [];

export const CompanySelectScreen = () => {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [choices, setChoices] = useState<CompanyChoice[]>([]);
  const [isStarting, setIsStarting] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);
  const [metaSummary, setMetaSummary] = useState<MetaSummaryDTO | null>(null);
  const [isLoadingMeta, setIsLoadingMeta] = useState(true);
  const startPendingRef = useRef(false);
  const replace = useScreenStore((state) => state.replace);
  const setChrome = useScreenStore((state) => state.setChrome);
  const pushToast = useGameStore((state) => state.pushToast);

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  useEffect(() => {
    let cancelled = false;
    setIsLoadingTemplates(true);
    loadCompanyTemplates()
      .then((templates) => {
        if (cancelled) {
          return;
        }
        const nextChoices = templates.map(toCompanyChoice);
        setChoices(nextChoices);
        setSelectedTemplateId((current) => current ?? nextChoices[0]?.templateId ?? null);
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        pushToast({
          id: `company-template-load-${Date.now()}`,
          level: "error",
          message: "公司模板加载失败",
          hint: error instanceof Error ? error.message : "请检查后端配置",
        });
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoadingTemplates(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [pushToast]);

  useEffect(() => {
    let cancelled = false;
    setIsLoadingMeta(true);
    loadPlayerMeta()
      .then((meta) => {
        if (!cancelled) {
          setMetaSummary(meta);
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        pushToast({
          id: `player-meta-load-${Date.now()}`,
          level: "error",
          message: "玩家进度加载失败",
          hint: error instanceof Error ? error.message : "请检查后端配置",
        });
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoadingMeta(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [pushToast]);

  const selectedChoice = choices.find((choice) => choice.templateId === selectedTemplateId) ?? null;
  const progressMeta = toProgressMeta(metaSummary);
  const milestones = toMilestones(metaSummary);

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
      await createGame(selectedChoice.templateId);
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
              {isLoadingTemplates ? (
                <div className="col-span-full flex items-center justify-center border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-px-md text-ink-2">
                  公司模板加载中
                </div>
              ) : null}
              {!isLoadingTemplates && choices.length === 0 ? (
                <div className="col-span-full flex items-center justify-center border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-px-md text-ink-2">
                  暂无可选公司
                </div>
              ) : null}
              {choices.slice(0, 3).map((choice) => (
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
            {isLoadingMeta ? (
              <div className="flex min-h-[480px] items-center justify-center border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-px-md text-ink-2">
                玩家进度加载中
              </div>
            ) : (
              <RevengeProgressPanel className="min-h-[480px]" meta={progressMeta} milestones={milestones} />
            )}
          </div>
        </section>

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
