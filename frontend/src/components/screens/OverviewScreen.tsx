import { useEffect } from "react";

import { PixelPortrait, PixelSpeechBubble, type IconName } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import { selectCurrentSnapshot } from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { CompactMetricRow } from "./overview/CompactMetricRow";
import { HighlightsPanel, type HighlightsItem } from "./overview/HighlightsPanel";
import { SuggestedActions } from "./overview/SuggestedActions";
import { TrendChartPanel } from "./overview/TrendChartPanel";

const PHASE_SCREEN = {
  BRIEFING: "office",
  GOSSIP: "gossip",
  DECISION: "decision",
  PRESS: "press",
  SETTLEMENT: "settlement",
  DONE: "settlement",
} as const;

const buildHighlights = (snapshot: ReturnType<typeof selectCurrentSnapshot>): HighlightsItem[] => {
  if (!snapshot) {
    return [];
  }

  const items: HighlightsItem[] = [];
  if (snapshot.quarter.briefing?.headlineHint) {
    items.push({
      iconName: "news" as IconName,
      title: `Q${snapshot.quarter.number} 简报`,
      subtitle: snapshot.quarter.briefing.headlineHint,
    });
  }

  for (const cause of snapshot.company.deathCauses.slice(0, 2)) {
    items.push({
      iconName: "alarm" as IconName,
      title: cause.category,
      subtitle: cause.description,
    });
  }

  for (const promise of snapshot.promiseLog.filter((item) => item.fulfilled === false).slice(0, 2)) {
    items.push({
      iconName: "check" as IconName,
      title: `承诺未兑现 Q${promise.quarterMade}`,
      subtitle: promise.text,
    });
  }

  return items;
};

export const OverviewScreen = () => {
  const setChrome = useScreenStore((state) => state.setChrome);
  const push = useScreenStore((state) => state.push);
  const snapshot = useGameStore(selectCurrentSnapshot);

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const highlights = buildHighlights(snapshot);
  const phaseScreen = snapshot ? PHASE_SCREEN[snapshot.quarter.phase] : "office";

  return (
    <section className="flex h-full min-h-0 flex-col overflow-auto bg-canvas px-3 py-3 text-ink-1 sm:px-4 sm:py-4">
      <div className="mx-auto flex min-h-full w-full max-w-[1920px] flex-col gap-4 xl:gap-5">
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 xl:grid-cols-[minmax(280px,0.88fr)_minmax(0,1.7fr)_minmax(320px,1fr)]">
          <aside className="flex min-w-0 flex-col gap-4">
            <div className="border-2 border-stroke-ink bg-panel px-3 py-2 shadow-hard">
              <h1 className="text-px-xl leading-none text-ink-1">公司经营总览</h1>
              <p className="mt-1 text-px-sm leading-snug text-ink-2">
                {snapshot ? snapshot.company.name : "等待后端公司快照"}
              </p>
            </div>

            <div className="flex min-h-0 flex-1 flex-col items-center gap-4 overflow-hidden xl:items-start">
              <div className="relative flex w-full flex-1 justify-center pt-1 xl:justify-start">
                <div className="relative h-[clamp(280px,24vw,440px)] w-[clamp(210px,18vw,340px)]">
                  <PixelPortrait
                    id="ceo_male_01"
                    expression="confident"
                    size="hero"
                    className="!h-full !w-full origin-top scale-[0.97]"
                  />
                </div>
              </div>

              <div className="w-full max-w-[460px]">
                <PixelSpeechBubble
                  tone="neutral"
                  arrow="none"
                  text={snapshot?.quarter.briefing?.headlineHint ?? snapshot?.company.foundingMotto ?? "等待后端简报"}
                />
              </div>
            </div>
          </aside>

          <main className="flex min-w-0 flex-col gap-4">
            <TrendChartPanel onViewReport={() => push("stats-dashboard")} />
            <CompactMetricRow />

            <div className="border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-center text-px-md leading-normal text-ink-2">
              后端快照未提供部门状态
            </div>
          </main>

          <aside className="flex min-w-0 flex-col gap-4">
            <HighlightsPanel items={highlights} />
            <div className="flex min-h-0 flex-1 flex-col">
              <SuggestedActions
                items={[
                  {
                    color: "green",
                    title: "查看指标",
                    subtitle: "来自后端快照",
                    onClick: () => push("stats-dashboard"),
                  },
                  {
                    color: "blue",
                    title: "返回当前阶段",
                    subtitle: snapshot?.quarter.phase ?? "等待后端阶段",
                    onClick: () => push(phaseScreen),
                  },
                ]}
              />
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
};

export default OverviewScreen;
