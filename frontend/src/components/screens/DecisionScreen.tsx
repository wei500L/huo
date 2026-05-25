import { useCallback, useEffect, useMemo, useState } from "react";

import { PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { selectDecision } from "@/net/gameClient";
import { selectCurrentQuarter, selectDecisionCards, selectInflight, selectPromiseLog, selectSessionId } from "@/store/selectors";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { DecisionCardGroup } from "./decision/DecisionCardGroup";
import { EffectPreview } from "./decision/EffectPreview";
import { PromiseLedger } from "./decision/PromiseLedger";
const isEditableTarget = (target: EventTarget | null): boolean => {
  return target instanceof HTMLElement
    ? Boolean(target.closest("input,textarea,select,[contenteditable='true']"))
    : false;
};

export function DecisionScreen() {
  const snapshotCards = useGameStore(selectDecisionCards);
  const snapshotPromises = useGameStore(selectPromiseLog);
  const sessionId = useGameStore(selectSessionId);
  const quarter = useGameStore(selectCurrentQuarter);
  const inflight = useGameStore(selectInflight);
  const setChrome = useScreenStore((state) => state.setChrome);
  const setInflight = useGameStore((state) => state.setInflight);
  const pushToast = useGameStore((state) => state.pushToast);
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  const cards = snapshotCards.slice(0, 3);
  const promiseLog = snapshotPromises.slice(0, 4);
  const selectedCard = useMemo(
    () => cards.find((card) => card.id === selectedId) ?? null,
    [cards, selectedId],
  );

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const confirmDecision = useCallback(() => {
    if (!selectedCard || !sessionId || !quarter || quarter.phase !== "DECISION" || inflight.selectDecision) {
      return;
    }

    setInflight("selectDecision", true);
    void selectDecision({
        sessionId,
        quarterNumber: quarter.number,
        cardId: selectedCard.id,
      }).catch((error: unknown) => {
        setInflight("selectDecision", false);
        pushToast({
          id: `decision-select-${Date.now()}`,
          level: "error",
          message: "决策提交失败",
          hint: error instanceof Error ? error.message : "请稍后重试",
        });
      });
  }, [inflight.selectDecision, pushToast, quarter, selectedCard, sessionId, setInflight]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (
        event.defaultPrevented ||
        event.metaKey ||
        event.ctrlKey ||
        event.altKey ||
        isEditableTarget(event.target)
      ) {
        return;
      }

      if (event.key === "Enter") {
        event.preventDefault();
        confirmDecision();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [confirmDecision]);

  const handleSelect = useCallback((id: string) => {
    if (quarter?.phase === "DECISION") {
      setSelectedId(id);
    }
  }, [quarter?.phase]);

  const isReady = Boolean(sessionId && quarter?.phase === "DECISION");
  const headerText = quarter?.briefing?.headlineHint ?? selectedCard?.flavor ?? "等待后端决策快照";

  return (
    <section className="relative h-full overflow-auto bg-canvas px-px-md py-px-md">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[152px] border-b-2 border-stroke-ink bg-panel">
        <div className="absolute left-3 top-3 grid grid-cols-6 gap-1">
          {["bg-panel-dim", "bg-pixel-blue", "bg-panel-dim", "bg-pixel-orange", "bg-panel-dim", "bg-pixel-green"].map((className, index) => (
            <span key={`${className}-${index}`} className={`h-6 w-6 border-2 border-stroke-ink ${className}`} />
          ))}
        </div>
        <div className="absolute inset-x-0 bottom-0 h-10 border-t-2 border-stroke-ink bg-floor" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-full max-w-[1600px] flex-col gap-px-md">
        <header className="grid items-end gap-px-md lg:grid-cols-[320px_minmax(0,1fr)]">
          <div className="relative h-[180px]">
            <PixelPortrait
              className="absolute bottom-0 left-0 !h-[160px] !w-[120px]"
              expression="tired"
              id="ceo_male_01"
              position="inline"
              size="sm"
            />
            <div className="absolute left-[88px] top-4 w-[240px] max-w-[calc(100vw-112px)] sm:w-[320px]">
              <PixelSpeechBubble arrow="down" text={headerText} tone="neutral" />
            </div>
          </div>

          <div className="flex justify-start lg:justify-end" />
        </header>

        <main className="grid min-h-0 grid-cols-1 gap-px-lg xl:grid-cols-[minmax(0,1fr)_320px]">
          <section className="relative min-h-0">
            <div className="mb-px-md border-2 border-stroke-ink bg-pixel-blue px-px-md py-px-sm text-white">
              <h1 className="font-retro text-px-lg leading-none">
                {quarter ? `Q${quarter.number} 季度决策` : "季度决策"}
              </h1>
              <p className="mt-px-xs text-px-sm leading-normal">
                每个季度只能选择一项决策，选定后无法更改
              </p>
            </div>

            {!isReady ? (
              <div className="border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-center text-px-md text-ink-2">
                等待后端进入决策阶段
              </div>
            ) : cards.length > 0 ? (
              <DecisionCardGroup cards={cards} selectedId={selectedId} onSelect={handleSelect} />
            ) : (
              <div className="border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-center text-px-md text-ink-2">
                暂无后端决策卡
              </div>
            )}

            <div className="mt-px-lg flex items-center justify-center">
              <button
                type="button"
                disabled={!selectedCard || !isReady || inflight.selectDecision}
                className={[
                  "border-2 border-stroke-ink px-px-lg py-px-md font-pixel text-px-md leading-none shadow-hard",
                  selectedCard && isReady && !inflight.selectDecision
                    ? "bg-pixel-blue text-white hover:bg-pixel-blue/90"
                    : "cursor-not-allowed bg-panel-dim text-ink-3 shadow-none",
                ].join(" ")}
                onClick={confirmDecision}
              >
                确认决策
              </button>
            </div>
          </section>

          <aside className="flex min-w-0 flex-col gap-px-md">
            <EffectPreview card={selectedCard} />
            <PromiseLedger promises={promiseLog} />
          </aside>
        </main>
      </div>
    </section>
  );
}

export default DecisionScreen;
