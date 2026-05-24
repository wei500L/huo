import { useCallback, useEffect, useMemo, useState } from "react";

import { PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { createMockDataSource } from "@/net/mockAdapter";
import { makeEnvelope } from "@/protocol/envelope";
import { selectCurrentQuarter, selectDecisionCards, selectPromiseLog, selectSessionId } from "@/store/selectors";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { DecisionCardGroup } from "./decision/DecisionCardGroup";
import { EffectPreview } from "./decision/EffectPreview";
import { PromiseLedger } from "./decision/PromiseLedger";
import type { DecisionCardDTO, PromiseDTO } from "@/protocol/types";

const dataSource = createMockDataSource();
void dataSource.connect("decision-ceo");

const MOCK_DECISION_CARDS: DecisionCardDTO[] = [
  {
    id: "decision-q1-fund",
    category: "finance",
    title: "融资续命",
    description: "引入新一轮投资，缓解现金流压力。",
    immediateEffect: { cash: 40000, morale: -10, board: -10, face: -10 },
    flavor: "把未来的一部分，提前卖给愿意买单的人。",
  },
  {
    id: "decision-q1-layoff",
    category: "people",
    title: "小幅裁员",
    description: "优化人员结构，提升短期效率。",
    immediateEffect: { cash: 15000, morale: -20, board: -5, face: -5 },
    flavor: "成本表会好看一点，但办公室会更安静。",
  },
  {
    id: "decision-q1-hide",
    category: "pr",
    title: "隐瞒坏消息",
    description: "对外保持乐观，延后披露负面情况。",
    immediateEffect: { cash: 5000, morale: -5, board: -15, face: -20 },
    flavor: "先把话说圆，再看能不能把账也圆过去。",
  },
];

const MOCK_PROMISES: PromiseDTO[] = [
  {
    id: "promise-q1-no-layoff",
    quarterMade: 1,
    source: "board",
    text: "Q1 不裁员",
    fulfilled: true,
    judgedAtQuarter: 1,
  },
  {
    id: "promise-q1-gmv",
    quarterMade: 1,
    source: "ceo",
    text: "Q1 Q3 GMV 翻倍",
    fulfilled: null,
    judgedAtQuarter: 3,
  },
  {
    id: "promise-q2-profit",
    quarterMade: 2,
    source: "investor",
    text: "Q2 季度内盈利",
    fulfilled: false,
    judgedAtQuarter: 2,
  },
  {
    id: "promise-q2-marketcap",
    quarterMade: 2,
    source: "board",
    text: "Q2 年底市值破 10 亿",
    fulfilled: null,
    judgedAtQuarter: 4,
  },
];

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
  const replace = useScreenStore((state) => state.replace);
  const setChrome = useScreenStore((state) => state.setChrome);
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const cards = snapshotCards.length >= 3 ? snapshotCards.slice(0, 3) : MOCK_DECISION_CARDS;
  const promiseLog = snapshotPromises.length >= 4 ? snapshotPromises.slice(0, 4) : MOCK_PROMISES;
  const selectedCard = useMemo(
    () => cards.find((card) => card.id === selectedId) ?? null,
    [cards, selectedId],
  );

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const confirmDecision = useCallback(() => {
    if (!selectedCard || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    void dataSource.send(
      makeEnvelope("select_decision", {
        sessionId: sessionId ?? "decision-screen-session",
        quarterNumber: quarter?.number ?? 1,
        cardId: selectedCard.id,
      }),
    ).catch(() => undefined);

    replace(quarter?.number === 3 ? "press" : "settlement");
  }, [isSubmitting, quarter, replace, selectedCard, sessionId]);

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
    if (!isSubmitting) {
      setSelectedId(id);
    }
  }, [isSubmitting]);

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
              <PixelSpeechBubble arrow="down" text="Q1 开局不利，是时候做出艰难决定了..." tone="neutral" />
            </div>
          </div>

          <div className="flex flex-wrap gap-px-sm justify-start lg:justify-end">
            {["专注", "创新", "结果"].map((label, index) => (
              <span
                key={label}
                className={[
                  "border-2 border-stroke-ink px-px-md py-px-sm font-retro text-[10px] leading-none text-white",
                  index === 0 ? "bg-pixel-blue" : index === 1 ? "bg-pixel-green" : "bg-pixel-orange",
                ].join(" ")}
              >
                {label}
              </span>
            ))}
          </div>
        </header>

        <main className="grid min-h-0 grid-cols-1 gap-px-lg xl:grid-cols-[minmax(0,1fr)_320px]">
          <section className="relative min-h-0">
            <div className="mb-px-md border-2 border-stroke-ink bg-pixel-blue px-px-md py-px-sm text-white">
              <h1 className="font-retro text-px-lg leading-none">Q1 季度决策</h1>
              <p className="mt-px-xs text-px-sm leading-normal">
                每个季度只能选择一项决策，选定后无法更改
              </p>
            </div>

            <DecisionCardGroup cards={cards} selectedId={selectedId} onSelect={handleSelect} />

            <div className="mt-px-lg flex items-center justify-center">
              <button
                type="button"
                disabled={!selectedCard || isSubmitting}
                className={[
                  "border-2 border-stroke-ink px-px-lg py-px-md font-pixel text-px-md leading-none shadow-hard",
                  selectedCard && !isSubmitting
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
