import { useEffect } from "react";
import type { FC } from "react";

import { AppShell } from "@/components/layout/AppShell";
import * as Screens from "@/components/screens/__placeholders";
import { useGameStore } from "@/store/gameStore";
import { selectCurrentSnapshot, selectPendingSettlementBundle } from "@/store/selectors";
import { useScreenStore, type ScreenId } from "@/store/screenStore";

const REGISTRY: Record<ScreenId, FC<Record<string, unknown>>> = {
  onboarding: Screens.OnboardingPlaceholder, "company-select": Screens.CompanySelectPlaceholder,
  office: Screens.OfficePlaceholder, gossip: Screens.GossipPlaceholder,
  "stats-dashboard": Screens.StatsDashboardPlaceholder, decision: Screens.DecisionPlaceholder,
  press: Screens.PressPlaceholder, settlement: Screens.SettlementPlaceholder,
  overview: Screens.OverviewPlaceholder, "death-report": Screens.DeathReportPlaceholder,
  "legacy-vault": Screens.LegacyVaultPlaceholder,
};

const PHASE_SCREEN: Record<string, ScreenId> = {
  BRIEFING: "office",
  GOSSIP: "gossip",
  DECISION: "decision",
  PRESS: "press",
  SETTLEMENT: "settlement",
  DONE: "settlement",
};

const PHASE_CONTROLLED_SCREENS = new Set<ScreenId>([
  "company-select",
  "office",
  "gossip",
  "decision",
  "press",
  "settlement",
]);

export default function App() {
  const current = useScreenStore((s) => s.current);
  const replace = useScreenStore((s) => s.replace);
  const setChrome = useScreenStore((s) => s.setChrome);
  const snapshot = useGameStore(selectCurrentSnapshot);
  const pendingSettlementBundle = useGameStore(selectPendingSettlementBundle);

  useEffect(() => {
    setChrome(
      current.id === "onboarding" || current.id === "death-report" || current.id === "legacy-vault"
        ? { hud: true, mainBar: false }
        : { hud: true, mainBar: true },
    );
  }, [current.id, setChrome]);

  useEffect(() => {
    if (!snapshot || !PHASE_CONTROLLED_SCREENS.has(current.id)) {
      return;
    }

    const target =
      pendingSettlementBundle !== null
        ? "settlement"
        : snapshot.status === "dead"
          ? "death-report"
          : snapshot.status === "won"
            ? "settlement"
            : PHASE_SCREEN[snapshot.quarter.phase];

    if (target && target !== current.id) {
      replace(target);
    }
  }, [current.id, pendingSettlementBundle, replace, snapshot]);

  const Screen = REGISTRY[current.id];
  return (
    <AppShell>
      <Screen {...(current.params ?? {})} />
    </AppShell>
  );
}
