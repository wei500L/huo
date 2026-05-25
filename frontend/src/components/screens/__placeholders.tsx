import type { FC } from "react";
import { useState } from "react";

import { PixelButton, PixelIcon } from "@/components/pixel";
import { drawDecisions, transitionState } from "@/net/gameClient";
import { useGameStore } from "@/store/gameStore";
import { selectCurrentQuarter, selectCurrentSnapshot } from "@/store/selectors";
import { useScreenStore, type ScreenId } from "@/store/screenStore";

import { CompanySelectScreen } from "./CompanySelectScreen";
import { GossipScene } from "./GossipScene";
import DecisionScreen from "./DecisionScreen";
import PressScreen from "./PressScreen";
import { OnboardingScreen } from "./OnboardingScreen";
import OverviewScreen from "./OverviewScreen";
import SettlementScreen from "./SettlementScreen";
import { StatsDashboard } from "./StatsDashboard";

function createPlaceholder(id: ScreenId): FC<Record<string, unknown>> {
  return function Placeholder() {
    return (
      <div className="space-y-px-sm p-px-lg">
        <div>[Screen: {id}]</div>
      </div>
    );
  };
}

const PHASE_LABEL = {
  BRIEFING: "简报",
  GOSSIP: "员工沟通",
  DECISION: "季度决策",
  PRESS: "发布会",
  SETTLEMENT: "结算",
  DONE: "季度完成",
} as const;

export const OfficePlaceholder: FC<Record<string, unknown>> = function OfficePlaceholder() {
  const snapshot = useGameStore(selectCurrentSnapshot);
  const quarter = useGameStore(selectCurrentQuarter);
  const replace = useScreenStore((state) => state.replace);
  const pushToast = useGameStore((state) => state.pushToast);
  const [busy, setBusy] = useState<"gossip" | "decision" | null>(null);

  const runBackendAction = async (target: "gossip" | "decision") => {
    if (!snapshot || !quarter || busy) {
      return;
    }

    setBusy(target);
    try {
      if (target === "gossip") {
        if (quarter.phase === "BRIEFING") {
          await transitionState(snapshot.sessionId, "GOSSIP");
        }
        replace("gossip");
        return;
      }

      if (quarter.phase === "BRIEFING") {
        throw new Error("请先进入员工沟通阶段");
      }
      if (quarter.phase === "GOSSIP") {
        await transitionState(snapshot.sessionId, "DECISION");
        await drawDecisions(snapshot.sessionId, quarter.number);
      } else if (quarter.phase === "DECISION" && quarter.decisionCards.length === 0) {
        await drawDecisions(snapshot.sessionId, quarter.number);
      }
      replace("decision");
    } catch (error) {
      pushToast({
        id: `office-phase-${Date.now()}`,
        level: "error",
        message: "阶段推进失败",
        hint: error instanceof Error ? error.message : "请稍后重试",
      });
    } finally {
      setBusy(null);
    }
  };

  const phase = quarter?.phase ?? null;

  return (
    <section className="flex h-full min-h-0 items-center justify-center overflow-auto bg-canvas p-px-lg text-ink-1">
      <div className="w-full max-w-[720px] border-2 border-stroke-ink bg-panel p-px-lg shadow-hard">
        <div className="mb-px-md flex items-center gap-px-sm border-b-2 border-stroke-ink pb-px-md">
          <PixelIcon name="briefcase" size={24} />
          <h1 className="text-px-xl leading-none">办公室</h1>
        </div>

        {!snapshot || !quarter ? (
          <p className="text-px-md leading-normal text-ink-2">等待后端快照</p>
        ) : (
          <div className="space-y-px-md">
            <div className="space-y-px-xs">
              <p className="text-px-sm leading-none text-ink-2">当前后端阶段</p>
              <p className="font-retro text-px-lg leading-none text-ink-1">
                {`Q${quarter.number} / ${PHASE_LABEL[quarter.phase]}`}
              </p>
            </div>

            <div className="grid gap-px-sm sm:grid-cols-2">
              <PixelButton
                fullWidth
                disabled={busy !== null || !["BRIEFING", "GOSSIP"].includes(quarter.phase)}
                icon={<PixelIcon name="users" size={24} />}
                loading={busy === "gossip"}
                size="lg"
                variant="green"
                onClick={() => void runBackendAction("gossip")}
              >
                进入员工沟通
              </PixelButton>
              <PixelButton
                fullWidth
                disabled={busy !== null || !["GOSSIP", "DECISION"].includes(quarter.phase)}
                icon={<PixelIcon name="target" size={24} />}
                loading={busy === "decision"}
                size="lg"
                variant="blue"
                onClick={() => void runBackendAction("decision")}
              >
                进入季度决策
              </PixelButton>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export const OnboardingPlaceholder: FC<Record<string, unknown>> = function OnboardingPlaceholder() {
  return <OnboardingScreen />;
};
export const CompanySelectPlaceholder: FC<Record<string, unknown>> = function CompanySelectPlaceholder() {
  return <CompanySelectScreen />;
};
export const GossipPlaceholder: FC<Record<string, unknown>> = function GossipPlaceholder(params) {
  return <GossipScene {...params} />;
};
export const StatsDashboardPlaceholder: FC<Record<string, unknown>> = function StatsDashboardPlaceholder() {
  return <StatsDashboard />;
};
export const DecisionPlaceholder: FC<Record<string, unknown>> = function DecisionPlaceholder() {
  return <DecisionScreen />;
};
export const PressPlaceholder: FC<Record<string, unknown>> = function PressPlaceholder() {
  return <PressScreen />;
};
export const SettlementPlaceholder: FC<Record<string, unknown>> = function SettlementPlaceholder() {
  return <SettlementScreen />;
};
export const OverviewPlaceholder: FC<Record<string, unknown>> = function OverviewPlaceholder() {
  return <OverviewScreen />;
};
export const DeathReportPlaceholder = createPlaceholder("death-report");
export const LegacyVaultPlaceholder = createPlaceholder("legacy-vault");
