import { useEffect, useMemo, useRef } from "react";

import { PixelButton, PixelIcon, PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import {
  selectCurrentQuarter,
  selectCurrentSnapshot,
  selectHistory,
  selectInflight,
  selectIsLLMDegraded,
  selectPendingDeathBundle,
  selectPendingSettlementBundle,
  selectPressBundle,
  selectPromiseLog,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { BoardCommentCard } from "./settlement/BoardCommentCard";
import { MediaQuoteCard } from "./settlement/MediaQuoteCard";
import { MetricDiffCard } from "./settlement/MetricDiffCard";
import { PromiseResultList } from "./settlement/PromiseResultList";
import { SkeletonLoading } from "./settlement/SkeletonLoading";
import {
  buildBoardComments,
  buildPromiseRows,
  METRIC_CONFIG,
  METRIC_ORDER,
  resolveEmployeeGossipTone,
  resolveMetricStatus,
} from "./settlement/settlementViewModel";

export function SettlementScreen() {
  const snapshot = useGameStore(selectCurrentSnapshot);
  const quarter = useGameStore(selectCurrentQuarter);
  const history = useGameStore(selectHistory);
  const pendingSettlementBundle = useGameStore(selectPendingSettlementBundle);
  const pendingDeathBundle = useGameStore(selectPendingDeathBundle);
  const pressBundle = useGameStore(selectPressBundle);
  const promiseLog = useGameStore(selectPromiseLog);
  const inflight = useGameStore(selectInflight);
  const llmDegraded = useGameStore(selectIsLLMDegraded);
  const replace = useScreenStore((state) => state.replace);
  const push = useScreenStore((state) => state.push);
  const setChrome = useScreenStore((state) => state.setChrome);
  const toastTimerRef = useRef<number | null>(null);
  const toastRaisedRef = useRef(false);

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const isPending = inflight.settleQuarter && pendingSettlementBundle === null;
  useEffect(() => {
    if (!isPending) {
      toastRaisedRef.current = false;
      if (toastTimerRef.current !== null) {
        window.clearTimeout(toastTimerRef.current);
        toastTimerRef.current = null;
      }
      return;
    }

    toastTimerRef.current = window.setTimeout(() => {
      if (toastRaisedRef.current) {
        return;
      }
      toastRaisedRef.current = true;
      useGameStore.getState().pushToast({
        id: `settlement-timeout-${Date.now()}`,
        level: "warn",
        message: "结算异常，请刷新",
      });
    }, 30000);

    return () => {
      if (toastTimerRef.current !== null) {
        window.clearTimeout(toastTimerRef.current);
        toastTimerRef.current = null;
      }
    };
  }, [isPending]);

  const resolvedSettlement = pendingSettlementBundle?.settlement ?? snapshot?.quarter.settlement ?? null;
  const resolvedQuarter = pendingSettlementBundle?.quarterNumber ?? quarter?.number ?? 0;
  const resolvedBefore =
    pendingSettlementBundle?.historyAdded.statsBefore ?? history[history.length - 1]?.statsBefore ?? snapshot?.stats ?? null;
  const resolvedAfter = pendingSettlementBundle?.newStats ?? snapshot?.stats ?? null;
  const resolvedPressHeadline = pendingSettlementBundle?.pressBundle?.headlines?.[0] ?? pressBundle?.headlines?.[0] ?? null;
  const hasDeath = Boolean(pendingSettlementBundle?.death ?? pendingDeathBundle);

  const metricCards = useMemo(
    () =>
      METRIC_ORDER.map((metricKey) => {
        const before = resolvedBefore?.[metricKey] ?? 0;
        const after = resolvedAfter?.[metricKey] ?? before;
        const status = resolveMetricStatus(metricKey, after - before);

        return (
          <MetricDiffCard
            key={metricKey}
            metricKey={metricKey}
            label={METRIC_CONFIG[metricKey].label}
            iconName={METRIC_CONFIG[metricKey].iconName}
            before={before}
            after={after}
            statusText={status.text}
            statusColor={status.color}
          />
        );
      }),
    [resolvedAfter, resolvedBefore],
  );

  const promiseRows = useMemo(
    () =>
      buildPromiseRows({
        promiseLog,
        metricsDelta: resolvedSettlement?.metricsDelta ?? null,
        quarter: resolvedQuarter,
      }),
    [promiseLog, resolvedQuarter, resolvedSettlement?.metricsDelta],
  );

  const boardComments = useMemo(() => buildBoardComments(resolvedSettlement), [resolvedSettlement]);
  const employeeGossipText = resolvedSettlement?.employeeGossip.line ?? "-";
  const employeeGossipTone = resolveEmployeeGossipTone(resolvedSettlement?.employeeGossip.mood);

  const handleAdvanceQuarter = () => {
    useGameStore.setState((state) => {
      if (!state.snapshot) {
        return {};
      }

      return {
        snapshot: {
          ...state.snapshot,
          stats: resolvedAfter ?? state.snapshot.stats,
          quarter: {
            ...state.snapshot.quarter,
            number: state.snapshot.quarter.number + 1,
            phase: "BRIEFING",
            settlement: undefined,
            pressBundle: undefined,
            selectedDecisionId: undefined,
            apRemaining: 3,
          },
        },
        pendingSettlementBundle: null,
        pendingDeathBundle: null,
        pendingDecision: null,
        pressBundle: null,
      };
    });
    replace("office");
  };

  if (isPending) {
    return <SkeletonLoading llmDegraded={llmDegraded} />;
  }

  return (
    <section className="relative h-full overflow-auto bg-canvas px-px-md py-px-md">
      <div className="mx-auto flex min-h-full max-w-[1600px] flex-col gap-px-lg">
        <header className="grid items-end gap-px-md lg:grid-cols-[320px_minmax(0,1fr)]">
          <div className="relative h-[180px]">
            <PixelPortrait
              className="absolute bottom-0 left-0 !h-[160px] !w-[120px]"
              expression="tired"
              id="ceo_male_02"
              position="inline"
              size="sm"
            />
          </div>

          <div className="space-y-2">
            <div className="inline-flex flex-wrap items-center gap-2 border-2 border-stroke-ink bg-panel px-3 py-2">
              <span className="font-retro text-px-lg leading-none">{`Q${resolvedQuarter} 季度结算`}</span>
              {llmDegraded ? (
                <span className="border border-stroke-ink bg-panel-dim px-2 py-1 text-px-sm leading-none text-ink-3">
                  AI 失联，已用兜底文案
                </span>
              ) : null}
            </div>
            <p className="text-px-md leading-normal text-ink-2">这一季，你又画成了几个饼？</p>
          </div>
        </header>

        <main className="grid min-h-0 grid-cols-1 gap-px-lg lg:grid-cols-12">
          <section className="min-h-0 lg:col-span-7">
            <div className="grid grid-cols-1 gap-px-md md:grid-cols-2">{metricCards}</div>

            <div className="mt-px-lg">
              <PromiseResultList items={promiseRows} />
            </div>

            <div className="mt-px-lg">
              <MediaQuoteCard headline={resolvedPressHeadline?.headline ?? "-"} source={resolvedPressHeadline?.outlet ?? "-"} />
            </div>
          </section>

          <aside className="min-h-0 lg:col-span-3">
            <div className="space-y-px-md">
              <BoardCommentCard items={boardComments} />

              <div className="border-2 border-stroke-ink bg-panel px-3 py-3 shadow-hard">
                <div className="mb-2 font-retro text-[10px] leading-none text-ink-1">员工一句话</div>
                <PixelSpeechBubble arrow="left" className="max-w-full" text={employeeGossipText} tone={employeeGossipTone} />
              </div>
            </div>
          </aside>
        </main>

        <footer className="flex flex-col items-stretch justify-center gap-3 py-2">
          <div className="grid gap-3 md:grid-cols-2">
            <PixelButton
              fullWidth
              disabled={isPending}
              icon={<PixelIcon name={hasDeath ? "rip" : "forward"} size={24} />}
              size="lg"
              variant={hasDeath ? "danger" : "blue"}
              onClick={hasDeath ? () => replace("death-report") : handleAdvanceQuarter}
            >
              {hasDeath ? "查看死亡报告" : "进入下一季度"}
            </PixelButton>

            <PixelButton fullWidth icon={<PixelIcon name="line-chart" size={24} />} size="lg" variant="ghost" onClick={() => push("stats-dashboard")}>
              查看详细评分
            </PixelButton>
          </div>
        </footer>
      </div>
    </section>
  );
}

export default SettlementScreen;
