import type { FC } from "react";

import { useScreenStore, type ScreenId } from "@/store/screenStore";

import { CompanySelectScreen } from "./CompanySelectScreen";
import { OnboardingScreen } from "./OnboardingScreen";

const SCREEN_ORDER: ScreenId[] = [
  "onboarding",
  "company-select",
  "office",
  "gossip",
  "stats-dashboard",
  "decision",
  "press",
  "settlement",
  "overview",
  "death-report",
  "legacy-vault",
];

const NEXT_SCREEN: Record<ScreenId, ScreenId> = {
  onboarding: "company-select",
  "company-select": "office",
  office: "gossip",
  gossip: "stats-dashboard",
  "stats-dashboard": "decision",
  decision: "press",
  press: "settlement",
  settlement: "overview",
  overview: "death-report",
  "death-report": "legacy-vault",
  "legacy-vault": "onboarding",
};

function createPlaceholder(id: ScreenId): FC<Record<string, unknown>> {
  return function Placeholder() {
    const push = useScreenStore((state) => state.push);

    return (
      <div className="space-y-px-sm p-px-lg">
        <div>[Screen: {id}]</div>
        <button
          type="button"
          className="border-2 border-stroke-ink bg-panel px-px-md py-px-sm shadow-hard"
          onClick={() => push(NEXT_SCREEN[id])}
        >
          跳下一屏
        </button>
      </div>
    );
  };
}

export const OnboardingPlaceholder: FC<Record<string, unknown>> = function OnboardingPlaceholder() {
  return <OnboardingScreen />;
};
export const CompanySelectPlaceholder: FC<Record<string, unknown>> = function CompanySelectPlaceholder() {
  return <CompanySelectScreen />;
};
export const OfficePlaceholder = createPlaceholder(SCREEN_ORDER[2]);
export const GossipPlaceholder = createPlaceholder(SCREEN_ORDER[3]);
export const StatsDashboardPlaceholder = createPlaceholder(SCREEN_ORDER[4]);
export const DecisionPlaceholder = createPlaceholder(SCREEN_ORDER[5]);
export const PressPlaceholder = createPlaceholder(SCREEN_ORDER[6]);
export const SettlementPlaceholder = createPlaceholder(SCREEN_ORDER[7]);
export const OverviewPlaceholder = createPlaceholder(SCREEN_ORDER[8]);
export const DeathReportPlaceholder = createPlaceholder(SCREEN_ORDER[9]);
export const LegacyVaultPlaceholder = createPlaceholder(SCREEN_ORDER[10]);
