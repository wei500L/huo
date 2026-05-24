import { useCallback, useEffect, useMemo, useRef } from "react";

import { PixelPortrait, PixelSpeechBubble } from "@/components/pixel";
import { createMockDataSource } from "@/net/mockAdapter";
import { makeEnvelope } from "@/protocol/envelope";
import type { CollectGossipPayload } from "@/protocol/inbound";
import type { GossipScene as GossipSceneName } from "@/protocol/types";
import { useElementSize } from "@/hooks/useElementSize";
import { useGameStore } from "@/store/gameStore";
import {
  selectAPRemaining,
  selectCurrentQuarter,
  selectGossipNotes,
  selectGossipTrust,
  selectInflight,
  selectLatestGossipLead,
  selectSessionId,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { ActionPanel, type Action } from "./gossip/ActionPanel";
import { GossipNotesDrawer } from "./gossip/GossipNotesDrawer";
import { SceneStage } from "./gossip/SceneStage";
import { TrustBar } from "./gossip/TrustBar";

const LIN_XIAOMAN_ID = "employee_lin_xiaoman";
const AP_TOTAL = 3;
const DEFAULT_SCENE: GossipSceneName = "tearoom";
const GOSSIP_SCENES = new Set<GossipSceneName>([
  "tearoom",
  "elevator",
  "meeting_room",
  "workstation",
  "rooftop",
  "smoking_area",
]);
const INITIAL_GOSSIP_KEYS = new Set<string>();

const dataSource = createMockDataSource();
void dataSource.connect("gossip-ceo");

export interface GossipSceneProps {
  scene?: unknown;
}

const normalizeScene = (scene: unknown): GossipSceneName => {
  return typeof scene === "string" && GOSSIP_SCENES.has(scene as GossipSceneName)
    ? (scene as GossipSceneName)
    : DEFAULT_SCENE;
};

export function GossipScene({ scene }: GossipSceneProps) {
  const normalizedScene = normalizeScene(scene);
  const sessionId = useGameStore(selectSessionId);
  const quarter = useGameStore(selectCurrentQuarter);
  const currentLead = useGameStore(selectLatestGossipLead);
  const notes = useGameStore(selectGossipNotes);
  const trust = useGameStore(selectGossipTrust(LIN_XIAOMAN_ID));
  const apRemaining = useGameStore(selectAPRemaining) ?? 0;
  const inflight = useGameStore(selectInflight);
  const addGossipNote = useGameStore((state) => state.addGossipNote);
  const spendGossipAP = useGameStore((state) => state.spendGossipAP);
  const adjustGossipTrust = useGameStore((state) => state.adjustGossipTrust);
  const setInflight = useGameStore((state) => state.setInflight);
  const pushToast = useGameStore((state) => state.pushToast);
  const back = useScreenStore((state) => state.back);
  const setChrome = useScreenStore((state) => state.setChrome);
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const viewportSize = useElementSize(viewportRef);
  const scale = viewportSize.width > 0 ? Math.min(1, Math.max(0.64, (viewportSize.width - 16) / 1280)) : 1;
  const initialRequestSentRef = useRef(false);
  const apEmptyToastShownRef = useRef(false);
  const initialKey = `${sessionId ?? "no-session"}:${quarter?.number ?? "no-quarter"}:${normalizedScene}`;

  useEffect(() => {
    setChrome({ hud: true, mainBar: true });
  }, [setChrome]);

  const sendCollectGossip = useCallback(() => {
    if (!sessionId || !quarter) {
      return;
    }

    const payload: CollectGossipPayload = {
      sessionId,
      quarterNumber: quarter.number,
      scene: normalizedScene,
    };

    setInflight("collectGossip", true);
    void dataSource.send(makeEnvelope("collect_gossip", payload)).catch((error: unknown) => {
      setInflight("collectGossip", false);
      pushToast({
        id: crypto.randomUUID(),
        level: "error",
        message: error instanceof Error ? error.message : "打听消息失败",
      });
    });
  }, [normalizedScene, pushToast, quarter, sessionId, setInflight]);

  useEffect(() => {
    if (initialRequestSentRef.current || !sessionId || !quarter || INITIAL_GOSSIP_KEYS.has(initialKey)) {
      return;
    }

    INITIAL_GOSSIP_KEYS.add(initialKey);
    initialRequestSentRef.current = true;
    sendCollectGossip();
    return () => {
      setTimeout(() => INITIAL_GOSSIP_KEYS.delete(initialKey), 0);
    };
  }, [initialKey, quarter, sendCollectGossip, sessionId]);

  useEffect(() => {
    if (!quarter || apRemaining > 0) {
      apEmptyToastShownRef.current = false;
      return;
    }

    if (apEmptyToastShownRef.current) {
      return;
    }

    apEmptyToastShownRef.current = true;
    pushToast({
      id: crypto.randomUUID(),
      level: "warn",
      message: "行动点用完，去做别的吧",
    });
  }, [apRemaining, pushToast, quarter]);

  const currentCost = Math.max(0, currentLead?.apCost ?? 1);
  const canUseAPAction = apRemaining > 0 && Boolean(currentLead);

  const actions = useMemo<Action[]>(
    () => [
      {
        id: "note",
        label: "记下来",
        iconName: "save",
        variant: "blue",
        apCost: currentCost,
        disabled: !canUseAPAction,
        onClick: () => {
          if (!currentLead) {
            return;
          }

          addGossipNote(currentLead);
          spendGossipAP(currentLead.apCost);
        },
      },
      {
        id: "probe",
        label: "追问细节",
        iconName: "search",
        variant: "green",
        apCost: currentCost,
        disabled: apRemaining <= 0 || inflight.collectGossip,
        onClick: sendCollectGossip,
      },
      {
        id: "comfort",
        label: "安抚情绪",
        iconName: "heart",
        variant: "orange",
        apCost: currentCost,
        disabled: !canUseAPAction,
        onClick: () => {
          // TODO 22: v1 only changes local trust; backend trust effects are not wired.
          adjustGossipTrust(LIN_XIAOMAN_ID, 1);
          spendGossipAP(currentCost);
        },
      },
      {
        id: "leave",
        label: "离开",
        iconName: "back",
        variant: "ghost",
        apCost: 0,
        onClick: back,
      },
    ],
    [
      addGossipNote,
      adjustGossipTrust,
      apRemaining,
      back,
      canUseAPAction,
      currentCost,
      currentLead,
      inflight.collectGossip,
      sendCollectGossip,
      spendGossipAP,
    ],
  );

  return (
    <section className="relative h-full min-h-[720px] overflow-auto bg-canvas p-px-md">
      <div ref={viewportRef} className="w-full">
        <div className="mx-auto" style={{ width: `${1280 * scale}px`, height: `${640 * scale}px` }}>
          <div
            className="relative origin-top-left"
            style={{
              width: "1280px",
              height: "640px",
              transform: `scale(${scale})`,
            }}
          >
            <SceneStage />

            <div className="absolute bottom-0 left-[42px] z-10 w-[320px]">
              <PixelPortrait
                bounce
                className="drop-shadow-[4px_4px_0_var(--stroke-ink)]"
                expression="smile"
                id={LIN_XIAOMAN_ID}
                position="inline"
                size="hero"
              />
              <div className="border-2 border-stroke-ink bg-panel px-px-md py-px-sm shadow-hard">
                <div className="mb-px-sm text-px-md leading-none">林小满</div>
                <TrustBar size="md" value={trust} />
              </div>
            </div>

            <div className="absolute right-[36px] top-[96px] z-10 w-[282px]">
              <ActionPanel actions={actions} apRemaining={apRemaining} apTotal={AP_TOTAL} />
            </div>

            <div className="absolute bottom-[28px] left-[384px] z-10 w-[560px]">
              <PixelSpeechBubble
                arrow="left"
                speaker={{ name: "林小满", role: "市场部专员" }}
                text={currentLead?.text ?? "茶水间里有人压低了声音，新的传闻正在路上。"}
                tone="friendly"
                typewriter={Boolean(currentLead)}
              />
            </div>

            <GossipNotesDrawer notes={notes} />
          </div>
        </div>
      </div>
    </section>
  );
}

export default GossipScene;
