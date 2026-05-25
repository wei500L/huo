import { useCallback, useEffect, useMemo, useState } from "react";

import { PixelButton, PixelDialog } from "@/components/pixel";
import { loadPressTypes, submitPress as submitPressMessage } from "@/net/gameClient";
import type { SubmitPressPayload } from "@/protocol/inbound";
import type { PressTypeDTO } from "@/protocol/types";
import { selectCurrentQuarter, selectInflight, selectPressDraft, selectSessionId } from "@/store/selectors";
import { useGameStore } from "@/store/gameStore";
import { useScreenStore } from "@/store/screenStore";

import { CameraPlaceholder } from "./press/CameraPlaceholder";
import { MustAnswerPanel } from "./press/MustAnswerPanel";
import { PressTranscriptInput } from "./press/PressTranscriptInput";

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
  const setChrome = useScreenStore((state) => state.setChrome);
  const [skipDialogOpen, setSkipDialogOpen] = useState(false);
  const [pressTypes, setPressTypes] = useState<PressTypeDTO[]>([]);
  const [selectedPressTypeId, setSelectedPressTypeId] = useState<PressTypeDTO["id"] | null>(null);
  const [pressTypesLoading, setPressTypesLoading] = useState(true);
  const quarterNumber = quarter?.number;

  useEffect(() => {
    setChrome({ hud: true, mainBar: false });
    return () => setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  useEffect(() => {
    let cancelled = false;
    setPressTypesLoading(true);
    loadPressTypes()
      .then((items) => {
        if (!cancelled) {
          setPressTypes(items);
          setSelectedPressTypeId((current) =>
            current && items.some((item) => item.id === current) ? current : null,
          );
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        pushToast({
          id: `press-types-load-${Date.now()}`,
          level: "error",
          message: "发布会配置加载失败",
          hint: error instanceof Error ? error.message : "请检查后端配置",
        });
      })
      .finally(() => {
        if (!cancelled) {
          setPressTypesLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [pushToast]);

  const wordCount = useMemo(() => countUnits(transcript), [transcript]);
  const activePressType = pressTypes.find((item) => item.id === selectedPressTypeId) ?? null;
  const canSubmit =
    wordCount >= MIN_WORDS &&
    wordCount <= MAX_WORDS &&
    Boolean(sessionId) &&
    quarterNumber === 3 &&
    quarter?.phase === "PRESS" &&
    Boolean(activePressType);

  const submitPress = useCallback(() => {
    if (!canSubmit || inflight.submitPress || !activePressType) {
      return;
    }

    const payload: SubmitPressPayload = {
      sessionId: sessionId ?? "missing-session",
      quarterNumber: 3,
      pressType: activePressType.id,
      transcript,
    };

    setInflight("submitPress", true);
    void submitPressMessage(payload).catch((error: unknown) => {
      setInflight("submitPress", false);
      pushToast({
        id: crypto.randomUUID(),
        level: "error",
        message: error instanceof Error ? error.message : "发言提交失败",
      });
    });
  }, [activePressType, canSubmit, inflight.submitPress, pushToast, sessionId, setInflight, transcript]);

  const openSkipDialog = useCallback(() => setSkipDialogOpen(true), []);
  const closeSkipDialog = useCallback(() => setSkipDialogOpen(false), []);
  const confirmSkip = useCallback(() => {
    setSkipDialogOpen(false);
    pushToast({
      id: `press-skip-unavailable-${Date.now()}`,
      level: "warn",
      message: "跳过发布会暂未接入真实接口",
      hint: "需要后端提供跳过发布会的结算输入",
    });
  }, [pushToast]);

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
          <p className="text-px-sm leading-none text-ink-2">{quarter?.phase ?? "等待后端阶段"}</p>
        </header>

        <main className="grid min-h-0 gap-px-md lg:grid-cols-12">
          <div className="min-w-0 space-y-px-md lg:col-span-7">
            <CameraPlaceholder />
            <PressTranscriptInput value={transcript} onChange={setPressDraft} minWords={MIN_WORDS} maxWords={MAX_WORDS} />
          </div>

          <div className="min-w-0 space-y-px-md lg:col-span-5">
            <section className="border-2 border-stroke-ink bg-panel shadow-hard">
              <div className="border-b-2 border-stroke-ink bg-pixel-green px-px-md py-px-sm text-white">
                <h2 className="text-px-md leading-none">发布会类型</h2>
              </div>
              <div className="space-y-px-xs p-px-md">
                {pressTypesLoading ? (
                  <div className="border-2 border-stroke-ink bg-panel-dim px-px-sm py-px-sm text-px-sm text-ink-2">
                    发布会配置加载中
                  </div>
                ) : null}
                {!pressTypesLoading && pressTypes.length === 0 ? (
                  <div className="border-2 border-stroke-ink bg-panel-dim px-px-sm py-px-sm text-px-sm text-ink-2">
                    暂无后端发布会类型
                  </div>
                ) : null}
                {pressTypes.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={[
                      "w-full border-2 px-px-sm py-px-sm text-left text-px-sm leading-normal",
                      selectedPressTypeId === item.id
                        ? "border-stroke-ink bg-pixel-blue text-white"
                        : "border-panel-dim bg-panel-dim text-ink-2",
                    ].join(" ")}
                    onClick={() => setSelectedPressTypeId(item.id)}
                  >
                    <span className="block text-px-md leading-tight">{item.titleZh}</span>
                    <span className="mt-1 block text-px-xs leading-normal opacity-90">{item.triggerConditionText}</span>
                  </button>
                ))}
              </div>
            </section>
            <MustAnswerPanel
              items={activePressType?.mustAnswerTopics ?? []}
              transcript={transcript}
            />
          </div>
        </main>

        <footer className="mt-auto grid gap-px-sm pt-px-md md:grid-cols-3">
          <div className="w-full">
            <PixelButton variant="blue" size="lg" fullWidth disabled={!canSubmit || inflight.submitPress} onClick={submitPress}>
              {pressTypesLoading ? "加载发布会配置" : "发言完毕"}
            </PixelButton>
          </div>
          <div className="w-full">
            <PixelButton variant="red" size="lg" fullWidth onClick={openSkipDialog}>
              跳过发布会
            </PixelButton>
          </div>
          <div className="w-full">
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
