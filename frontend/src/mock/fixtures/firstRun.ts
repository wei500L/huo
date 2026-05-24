import type {
  DeathReportBundleDTO,
  DecisionAckDTO,
  GameSnapshotDTO,
  GossipLeadDTO,
  GossipResultDTO,
  PressAckDTO,
  SettlementBundleDTO,
  StatsDTO,
} from "@/protocol/types";

import { COMPANY_TEMPLATE_BY_ID } from "./companyTemplates";
import { DECISION_CARD_BY_ID, DECISION_DRAWS_BY_QUARTER } from "./decisionCards";
import { GOSSIP_LEADS_BY_SCENE } from "./gossipLeads";
import { DEATH_REPORT_BUNDLE_Q4_OUST } from "./deathReport";
import { PRESS_BUNDLE_V1 } from "./pressBundles";
import { SETTLEMENT_BUNDLE_Q1, SETTLEMENT_BUNDLE_Q3_PRESS } from "./settlementBundles";
import { getMockScenarioDefinition, getMockSettlementBundle, resolveMockScenarioName } from "../runtime";
import { deepClone } from "../utils";

export type MockScenario = ReturnType<typeof resolveMockScenarioName>;

const SESSION_ID = "mock-session-001";
const PLAYER_ID = "mock-player";

export const mockInitialStats: StatsDTO = {
  cash: 70,
  morale: 55,
  board: 50,
  face: 40,
};

const buildQuarterCards = (quarter: 1 | 2 | 3 | 4) => {
  return DECISION_DRAWS_BY_QUARTER[quarter].map((id) => deepClone(DECISION_CARD_BY_ID[id]));
};

const getDefaultSettlementBundle = (quarter: 1 | 2 | 3 | 4): SettlementBundleDTO => {
  if (quarter === 1) return deepClone(SETTLEMENT_BUNDLE_Q1);
  if (quarter === 3) return deepClone(SETTLEMENT_BUNDLE_Q3_PRESS);

  return {
    ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS),
    quarterNumber: quarter,
    settlement: {
      ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS.settlement),
      quarter,
    },
    historyAdded: {
      ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS.historyAdded),
      quarter,
    },
  };
};

export const createMockSnapshot = (overrides: Partial<GameSnapshotDTO> = {}): GameSnapshotDTO => {
  const scenario = getMockScenarioDefinition();
  const companyTemplate = COMPANY_TEMPLATE_BY_ID[scenario.defaultTemplateId] ?? COMPANY_TEMPLATE_BY_ID["C-01"];

  return {
    sessionId: SESSION_ID,
    playerId: overrides.playerId ?? PLAYER_ID,
    company: deepClone(companyTemplate.company),
    stats: deepClone(mockInitialStats),
    quarter: {
      number: 1,
      phase: "BRIEFING",
      briefing: {
        quarter: 1,
        marketMood: "neutral",
        headlineHint: "董事会要求你先证明，现金流不是幻觉。",
      },
      decisionCards: buildQuarterCards(1),
      gossipCollected: [],
      apRemaining: 3,
    },
    history: [],
    metaSummary: {
      schemaVersion: 1,
      totalRuns: 1,
      unlockedLegacies: [],
      unlockedStyles: [],
      deathLogCount: 0,
      pressArchiveCount: 0,
    },
    promiseLog: [],
    status: "active",
    ...overrides,
  };
};

export const createMockDecisionAck = (
  cardId = "q1-card-runway",
  stats: StatsDTO = mockInitialStats,
): DecisionAckDTO => {
  const card = DECISION_CARD_BY_ID[cardId];
  const nextPhase = cardId.startsWith("q3-") ? "PRESS" : "SETTLEMENT";

  return {
    sessionId: SESSION_ID,
    quarterNumber: cardId.startsWith("q3-") ? 3 : 1,
    cardId,
    immediateStats: stats,
    nextPhase,
  };
};

export const createMockGossipResult = (
  scene: GossipLeadDTO["scene"] = "tearoom",
  quarterNumber = 1,
): GossipResultDTO => {
  const pool = GOSSIP_LEADS_BY_SCENE[scene] ?? GOSSIP_LEADS_BY_SCENE.tearoom;
  const lead = deepClone(pool[Math.max(0, quarterNumber - 1) % pool.length]);
  return {
    sessionId: SESSION_ID,
    quarterNumber,
    lead,
    apRemaining: Math.max(0, 3 - lead.apCost),
  };
};

export const createMockPressAck = (accepted = true): PressAckDTO => ({
  sessionId: SESSION_ID,
  quarterNumber: 3,
  accepted,
  flags: accepted ? [] : ["word_count_too_low"],
  replacedCount: accepted ? 0 : 1,
});

export const createMockSettlementBundle = (
  scenarioName: MockScenario = resolveMockScenarioName(),
  quarterNumber: 1 | 2 | 3 | 4 = 1,
): SettlementBundleDTO => {
  const bundle = getMockSettlementBundle(scenarioName, quarterNumber);
  if (bundle) {
    return deepClone(bundle);
  }

  return getDefaultSettlementBundle(quarterNumber);
};

export const createMockDeathReport = (scenarioName: MockScenario = resolveMockScenarioName()): DeathReportBundleDTO => {
  return deepClone(getMockScenarioDefinition(scenarioName).deathReport ?? DEATH_REPORT_BUNDLE_Q4_OUST);
};

export const createMockPressBundle = () => deepClone(PRESS_BUNDLE_V1);
