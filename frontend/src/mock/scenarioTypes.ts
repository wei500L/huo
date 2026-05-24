import type { DeathReportBundleDTO, SettlementBundleDTO } from "@/protocol/types";

export type MockScenarioName = "happy" | "die-q1" | "press-fail";

export interface MockScenarioDefinition {
  name: MockScenarioName;
  defaultTemplateId: string;
  pressRejected: boolean;
  settlementBundles: Partial<Record<1 | 2 | 3 | 4, SettlementBundleDTO>>;
  deathReport: DeathReportBundleDTO | null;
}
