import { useEffect } from "react";

import { PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { CompactMetricRow } from "./overview/CompactMetricRow";
import { DepartmentCard } from "./overview/DepartmentCard";
import { HighlightsPanel } from "./overview/HighlightsPanel";
import { SuggestedActions } from "./overview/SuggestedActions";
import { TrendChartPanel } from "./overview/TrendChartPanel";

const DEPARTMENTS = [
  {
    name: "产品部",
    status: "stable" as const,
    comment: "节奏正常，需求堆积偏多。",
    suggestion: "先砍低优先级需求",
    iconName: "briefcase" as const,
  },
  {
    name: "市场部",
    status: "tired" as const,
    comment: "声量偏弱，曝光还不够。",
    suggestion: "补一轮外部发声",
    iconName: "megaphone" as const,
  },
  {
    name: "技术部",
    status: "healthy" as const,
    comment: "交付稳，核心模块可控。",
    suggestion: "保持现有排期",
    iconName: "settings" as const,
  },
];

const HIGHLIGHTS = [
  { iconName: "board" as const, title: "董事会信任持续下滑", subtitle: "本周沟通频率不足，反馈窗口收窄。" },
  { iconName: "trending-up" as const, title: "市场热度偏低", subtitle: "外部关注没有跟上内部动作。" },
  { iconName: "users" as const, title: "员工申请加班", subtitle: "内部压力上升，产出波动变大。" },
  { iconName: "target" as const, title: "Q2 项目进度 62%", subtitle: "进度还在推进，但需要稳住节奏。" },
];

export const OverviewScreen = () => {
  const setChrome = useScreenStore((state) => state.setChrome);
  const push = useScreenStore((state) => state.push);
  const pushToast = useGameStore((state) => state.pushToast);

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const makeAction = (id: string, message: string, screen: "stats-dashboard" | "decision" | "press") => () => {
    pushToast({ id, level: "info", message });
    push(screen);
  };

  return (
    <section className="h-full min-h-0 overflow-hidden bg-canvas px-2 py-2 text-ink-1">
      <div className="grid h-full min-h-0 grid-cols-12 gap-2">
        <aside className="col-span-3 flex min-w-0 flex-col gap-2 overflow-hidden">
          <div className="border-2 border-stroke-ink bg-panel px-3 py-2 shadow-hard">
            <h1 className="text-px-xl leading-none text-ink-1">公司经营总览</h1>
            <p className="mt-1 text-px-sm leading-snug text-ink-2">掌控六大核心指标，带领公司走向盈利与荣耀</p>
          </div>

          <div className="flex flex-1 min-h-0 flex-col items-center justify-between gap-2 overflow-hidden">
            <div className="relative flex w-full min-h-0 justify-center pt-1">
              <PixelPortrait id="ceo_male_01" expression="confident" size="hero" className="origin-top scale-[0.97]" />
            </div>

            <div className="w-full">
              <PixelSpeechBubble tone="neutral" arrow="none" text="这周最危险的是董事会信任下滑..." />
            </div>
          </div>
        </aside>

        <main className="col-span-6 flex min-w-0 flex-col gap-2 overflow-hidden">
          <TrendChartPanel onViewReport={makeAction("overview-report-toast", "已打开详细报告", "stats-dashboard")} />
          <CompactMetricRow />

          <div className="grid min-h-0 grid-cols-3 gap-2">
            {DEPARTMENTS.map((department) => (
              <DepartmentCard key={department.name} {...department} />
            ))}
          </div>
        </main>

        <aside className="col-span-3 flex min-w-0 flex-col gap-2 overflow-hidden">
          <HighlightsPanel items={HIGHLIGHTS} />
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
            <SuggestedActions
              items={[
                {
                  color: "green",
                  title: "稳住现金流",
                  subtitle: "先守底线",
                  onClick: makeAction("overview-cash-toast", "现金流已优先处理", "stats-dashboard"),
                },
                {
                  color: "blue",
                  title: "处理董事会关系",
                  subtitle: "主动汇报进度",
                  onClick: makeAction("overview-board-toast", "董事会沟通已安排", "decision"),
                },
                {
                  color: "red",
                  title: "拉高市场热度",
                  subtitle: "补一轮外部声量",
                  onClick: makeAction("overview-market-toast", "市场动作已触发", "press"),
                },
              ]}
            />
          </div>
        </aside>
      </div>
    </section>
  );
};

export default OverviewScreen;
