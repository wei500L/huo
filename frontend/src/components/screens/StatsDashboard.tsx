import { useEffect, useMemo } from "react";

import { PixelButton, PixelIcon, PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import {
  selectCurrentCompany,
  selectCurrentSnapshot,
  selectCurrentStats,
  selectMainActionBarContextHint,
  selectPromiseLog,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { MetricGrid } from "./stats/MetricGrid";
import { RiskPanel } from "./stats/RiskPanel";
import type { Risk } from "./stats/RiskCard";

const FALLBACK_HINT = "老板，数据比表面看起来更危险...";

const MAX_RISKS = 5;

const trimDescription = (text: string): string => (text.length > 50 ? text.slice(0, 50) : text);

const makeRisk = (risk: Risk): Risk => ({
  ...risk,
  description: trimDescription(risk.description),
});

const buildRisks = (params: {
  cash: number;
  board: number;
  promiseLog: Array<{ id: string; fulfilled: boolean | null }>;
}): Risk[] => {
  const risks: Risk[] = [];

  if (params.cash < 30) {
    risks.push(
      makeRisk({
        id: "cash-pressure",
        iconName: "money",
        title: "现金流承压",
        description: "现金储备低于安全线，短期支出会迅速放大风险。",
        level: "high",
      }),
    );
  }

  if (params.board < 50) {
    risks.push(
      makeRisk({
        id: "board-patience",
        iconName: "board",
        title: "董事会耐心下降",
        description: "董事会对当前节奏不再满意，反馈窗口正在收窄。",
        level: "mid",
      }),
    );
  }

  if (params.promiseLog.some((card) => card.fulfilled === false)) {
    risks.push(
      makeRisk({
        id: "promise-fail",
        iconName: "check",
        title: "承诺翻车",
        description: "已有承诺未兑现，后续沟通会被放大审视。",
        level: "mid",
      }),
    );
  }

  if (risks.length < 3) {
    risks.push(
      makeRisk({
        id: "project-delay",
        iconName: "trending-down",
        title: "项目延期扩大",
        description: "当前进度落后，排期一旦滑坡会连锁影响交付。",
        level: "mid",
      }),
    );
  }

  if (risks.length < 3) {
    risks.push(
      makeRisk({
        id: "market-heat",
        iconName: "fire",
        title: "市场热度波动",
        description: "外部关注不稳定，容易把内部波动放大成舆情。",
        level: "low",
      }),
    );
  }

  return risks.slice(0, MAX_RISKS);
};

export const StatsDashboard = () => {
  const snapshot = useGameStore(selectCurrentSnapshot);
  const stats = useGameStore(selectCurrentStats);
  const company = useGameStore(selectCurrentCompany);
  const promiseLog = useGameStore(selectPromiseLog);
  const hint = useGameStore(selectMainActionBarContextHint);
  const push = useScreenStore((state) => state.push);
  const pushToast = useGameStore((state) => state.pushToast);
  const setChrome = useScreenStore((state) => state.setChrome);

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const resolvedStats = stats ?? { cash: 0, morale: 0, board: 0, face: 0 };
  const history = snapshot?.history ?? [];

  const risks = useMemo(
    () =>
      buildRisks({
        cash: resolvedStats.cash,
        board: resolvedStats.board,
        promiseLog,
      }),
    [promiseLog, resolvedStats.board, resolvedStats.cash],
  );

  const hintText = hint.text || FALLBACK_HINT;

  const handleViewAllRisks = () => {
    pushToast({
      id: `stats-risks-${Date.now()}`,
      level: "info",
      message: "风险页暂未独立开放，先在同屏查看。",
    });
    push("stats-dashboard", { panel: "all-risks" });
  };

  const handleDetail = () => {
    push("overview");
  };

  return (
    <section className="flex h-full min-h-0 flex-col overflow-auto bg-canvas px-px-md py-px-md text-ink-1">
      <div className="mx-auto flex min-h-full w-full max-w-[1920px] flex-col gap-px-md">
        <div className="flex flex-wrap items-center justify-between gap-px-md">
          <div className="flex items-center gap-px-sm">
            <span className="text-px-xl leading-none text-ink-1">六大核心数据</span>
            <span className="flex items-center gap-1 text-pixel-orange" aria-hidden="true">
              <PixelIcon name="star" size={16} ariaLabel="装饰星点" />
              <PixelIcon name="star" size={16} ariaLabel="装饰星点" />
              <PixelIcon name="star" size={16} ariaLabel="装饰星点" />
            </span>
          </div>
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-1 gap-px-md xl:grid-cols-[minmax(0,1.55fr)_minmax(300px,0.85fr)]">
          <div className="flex min-w-0 flex-col gap-px-md">
            <MetricGrid stats={resolvedStats} history={history} company={company} />

            <div className="grid min-h-0 gap-px-md lg:grid-cols-[minmax(120px,160px)_minmax(0,1fr)]">
              <div className="flex justify-center lg:justify-start">
                <PixelPortrait id="advisor" size="md" className="pointer-events-none" />
              </div>

              <div className="flex min-h-[112px] items-end">
                <div className="w-full max-w-[520px]">
                  <PixelSpeechBubble tone="neutral" arrow="left" text={hintText} />
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <div className="w-full max-w-[320px]">
                <PixelButton
                  fullWidth
                  size="lg"
                  variant="blue"
                  icon={<PixelIcon name="line-chart" size={24} ariaLabel="查看详细分析" />}
                  onClick={handleDetail}
                >
                  查看详细分析
                </PixelButton>
              </div>
            </div>
          </div>

          <div className="min-w-0">
            <RiskPanel risks={risks} onViewAll={handleViewAllRisks} />
          </div>
        </div>
      </div>
    </section>
  );
};
