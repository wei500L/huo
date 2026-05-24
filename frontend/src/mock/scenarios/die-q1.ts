import { DEATH_REPORT_BUNDLE_Q4_OUST } from "../fixtures/deathReport";
import { DECISION_DRAWS_BY_QUARTER } from "../fixtures/decisionCards";
import type { MockScenarioDefinition } from "../scenarioTypes";

export const DIE_Q1_SCENARIO: MockScenarioDefinition = {
  name: "die-q1",
  defaultTemplateId: "C-02",
  pressRejected: false,
  settlementBundles: {
    1: {
      sessionId: "mock-session-001",
      quarterNumber: 1,
      settlement: {
        quarter: 1,
        quarterReport: "第一季的现金线直接坠穿，董事会开始讨论更换 CEO。",
        boardReaction: { speech: "我们不能继续这样烧下去。", patienceDelta: -45, vote: "oppose" },
        employeeGossip: { speaker: "韩维", line: "人事已经在问离职流程了。", mood: "numb" },
        rivalAction: {
          rivalName: "BrothStack",
          action: "attack",
          description: "对手放出更便宜的替代方案。",
          expectedDamage: { face: -6 },
        },
        marketSignal: "crisis",
        metricsDelta: { cash: -70, morale: -20, board: -40, face: -28 },
      },
      newStats: { cash: 0, morale: 35, board: 8, face: 12 },
      historyAdded: {
        quarter: 1,
        decisionId: "q1-card-runway",
        statsBefore: { cash: 70, morale: 55, board: 50, face: 40 },
        statsAfter: { cash: 0, morale: 35, board: 8, face: 12 },
        settlementSummary: "现金归零，董事会发难。",
      },
      death: { code: "cash_zero", labelZh: "董事会罢免 CEO" },
      llmDegraded: false,
    },
  },
  deathReport: DEATH_REPORT_BUNDLE_Q4_OUST,
};

export const DIE_Q1_DECISION_DRAWS_BY_QUARTER = DECISION_DRAWS_BY_QUARTER;
