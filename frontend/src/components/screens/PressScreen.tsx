import { useCallback, useEffect, useMemo, useState } from "react";

import { PixelButton, PixelDialog } from "@/components/pixel";
import { createMockDataSource } from "@/net/mockAdapter";
import { makeEnvelope } from "@/protocol/envelope";
import type { SubmitPressPayload } from "@/protocol/inbound";
import { selectCurrentQuarter, selectInflight, selectPressDraft, selectSessionId } from "@/store/selectors";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { CameraPlaceholder } from "./press/CameraPlaceholder";
import { MustAnswerPanel } from "./press/MustAnswerPanel";
import { PRESS_REPORTERS } from "./press/constants";
import { PressTranscriptInput } from "./press/PressTranscriptInput";
import { ReporterList } from "./press/ReporterList";

const dataSource = createMockDataSource();
void dataSource.connect("press-ceo");

const MUST_ANSWER_ITEMS = [
  "这次发布会先说明现金流和财报口径。",
  "外界最关心裁员传闻，你怎么回应？",
  "产品路线图和交付节奏会不会变？",
];

const MIN_WORDS = 30;
const MAX_WORDS = 300;

const countUnits = (value: string): number => value.replace(/\s+/g, "").length;

export function PressScreen() {
  const sessionId = useGameStore(selectSessionId);
  const quarter = useGameStore(selectCurrentQuarter);
  const inflight = useGameStore(selectInflight);
  const transcript = useGameStore(selectPressDraft);
  const setInflight = useGameStore((state) => state.setInflight);
  const setPressDraft = useGameStore((state) => state.setPressDraft);
  const pushToast = useGameStore((state) => state.pushToast);
  const replace = useScreenStore((state) => state.replace);
  const setChrome = useScreenStore((state) => state.setChrome);
  const [skipDialogOpen, setSkipDialogOpen] = useState(false);
  const quarterNumber = quarter?.number;

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const wordCount = useMemo(() => countUnits(transcript), [transcript]);
  const canSubmit = wordCount >= MIN_WORDS && wordCount <= MAX_WORDS && Boolean(sessionId) && quarterNumber === 3;

  const submitPress = useCallback(() => {
    if (!canSubmit || inflight.submitPress) {
      return;
    }

    const payload: SubmitPressPayload = {
      sessionId: sessionId ?? "missing-session",
      quarterNumber: 3,
      pressType: "INAUGURATION",
      transcript,
      durationS: 47,
    };

    setInflight("submitPress", true);
    void dataSource.send(makeEnvelope("submit_press", payload)).catch((error: unknown) => {
      setInflight("submitPress", false);
      pushToast({
        id: crypto.randomUUID(),
        level: "error",
        message: error instanceof Error ? error.message : "发言提交失败",
      });
    });
  }, [canSubmit, inflight.submitPress, pushToast, sessionId, setInflight, transcript]);

  const openSkipDialog = useCallback(() => setSkipDialogOpen(true), []);
  const closeSkipDialog = useCallback(() => setSkipDialogOpen(false), []);
  const confirmSkip = useCallback(() => {
    setSkipDialogOpen(false);
    replace("settlement");
  }, [replace]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.repeat) {
        return;
      }

      if (event.key === "Escape" && !skipDialogOpen) {
        event.preventDefault();
        setSkipDialogOpen(true);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [skipDialogOpen]);

  return (
    <section className="relative h-full min-h-0 overflow-auto bg-canvas px-px-md py-px-md">
      <div className="mx-auto flex min-h-full max-w-[1600px] flex-col gap-px-md">
        <header className="flex flex-wrap items-center justify-between gap-px-sm border-2 border-stroke-ink bg-panel px-px-md py-px-sm shadow-hard">
          <h1 className="text-px-lg leading-none text-ink-1">发布会输入屏</h1>
          <p className="text-px-sm leading-none text-ink-2">文字模式先上，摄像头占位留给任务 22</p>
        </header>

        <main className="grid min-h-0 gap-px-md lg:grid-cols-12">
          <div className="min-w-0 space-y-px-md lg:col-span-7">
            <CameraPlaceholder />
            <PressTranscriptInput value={transcript} onChange={setPressDraft} minWords={MIN_WORDS} maxWords={MAX_WORDS} />
          </div>

          <div className="min-w-0 space-y-px-md lg:col-span-5">
            <MustAnswerPanel items={MUST_ANSWER_ITEMS} transcript={transcript} />
            <ReporterList items={[...PRESS_REPORTERS]} />
          </div>
        </main>

        <footer className="mt-auto flex flex-wrap items-center justify-center gap-px-sm pt-px-md">
          <div className="w-full max-w-[240px]">
            <PixelButton variant="blue" size="lg" fullWidth disabled={!canSubmit || inflight.submitPress} onClick={submitPress}>
              发言完毕
            </PixelButton>
          </div>
          <div className="w-full max-w-[260px]">
            <PixelButton variant="red" size="lg" fullWidth onClick={openSkipDialog}>
              跳过 (扣 FACE -10)
            </PixelButton>
          </div>
          <div className="w-full max-w-[220px]">
            <PixelButton variant="ghost" size="lg" fullWidth disabled>
              改用文字模式
            </PixelButton>
          </div>
        </footer>
      </div>

      <PixelDialog
        open={skipDialogOpen}
        onOpenChange={(open) => {
          if (!open) {
            closeSkipDialog();
          }
        }}
        title="确认跳过"
        description="跳过后直接进入结算阶段，这次发言不会提交。"
        primaryAction={{ label: "确认跳过", variant: "danger", onClick: confirmSkip }}
        secondaryAction={{ label: "继续发言", onClick: closeSkipDialog }}
      />
    </section>
  );
}

export default PressScreen;
