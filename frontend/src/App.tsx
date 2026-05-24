import { useEffect } from "react";
import type { FC } from "react";

import { AppShell } from "@/components/layout/AppShell";
import * as Screens from "@/components/screens/__placeholders";
import { useScreenStore, type ScreenId } from "@/store/screenStore";

const REGISTRY: Record<ScreenId, FC<Record<string, unknown>>> = {
  onboarding: Screens.OnboardingPlaceholder, "company-select": Screens.CompanySelectPlaceholder,
  office: Screens.OfficePlaceholder, gossip: Screens.GossipPlaceholder,
  "stats-dashboard": Screens.StatsDashboardPlaceholder, decision: Screens.DecisionPlaceholder,
  press: Screens.PressPlaceholder, settlement: Screens.SettlementPlaceholder,
  overview: Screens.OverviewPlaceholder, "death-report": Screens.DeathReportPlaceholder,
  "legacy-vault": Screens.LegacyVaultPlaceholder,
};

export default function App() {
  const current = useScreenStore((s) => s.current);
  const setChrome = useScreenStore((s) => s.setChrome);

  useEffect(() => {
    setChrome(
      current.id === "onboarding" || current.id === "death-report" || current.id === "legacy-vault"
        ? { hud: true, mainBar: false }
        : { hud: true, mainBar: true },
    );
  }, [current.id, setChrome]);

  const Screen = REGISTRY[current.id];
  return (
    <AppShell>
      <Screen {...(current.params ?? {})} />
    </AppShell>
  );
}
