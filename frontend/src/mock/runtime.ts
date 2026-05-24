import type { SettlementBundleDTO } from "@/protocol/types";

import { DIE_Q1_SCENARIO } from "./scenarios/die-q1";
import { HAPPY_SCENARIO } from "./scenarios/happy";
import { PRESS_FAIL_SCENARIO } from "./scenarios/press-fail";
import type { MockScenarioDefinition, MockScenarioName } from "./scenarioTypes";

const SCENARIOS: Record<MockScenarioName, MockScenarioDefinition> = {
  happy: HAPPY_SCENARIO,
  "die-q1": DIE_Q1_SCENARIO,
  "press-fail": PRESS_FAIL_SCENARIO,
};

const normalizeScenarioName = (value: unknown): MockScenarioName => {
  return value === "die-q1" || value === "press-fail" ? value : "happy";
};

export const resolveMockScenarioName = (): MockScenarioName => {
  const globalScenario = (globalThis as Window & { __YES_BOSS_MOCK_SCENARIO__?: unknown }).__YES_BOSS_MOCK_SCENARIO__;
  if (typeof globalScenario === "string") {
    return normalizeScenarioName(globalScenario);
  }

  const query = typeof window !== "undefined" ? new URL(window.location.href).searchParams.get("mockScenario") : null;
  if (query) {
    return normalizeScenarioName(query);
  }

  const viteValue = import.meta.env.VITE_MOCK_SCENARIO;
  if (typeof viteValue === "string") {
    return normalizeScenarioName(viteValue);
  }

  return "happy";
};

export const getMockScenarioDefinition = (scenario?: MockScenarioName): MockScenarioDefinition => {
  return SCENARIOS[scenario ?? resolveMockScenarioName()];
};

export const getMockScenarioByName = (scenario: MockScenarioName): MockScenarioDefinition => {
  return SCENARIOS[scenario];
};

export const getMockSettlementBundle = (scenario: MockScenarioName, quarterNumber: 1 | 2 | 3 | 4): SettlementBundleDTO | null => {
  return SCENARIOS[scenario].settlementBundles[quarterNumber] ?? null;
};
