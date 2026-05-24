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
          expectedDamage: { FACE: -6 },
        },
        marketSignal: "crisis",
        metricsDelta: { CASH: -70, MORALE: -20, BOARD: -40, FACE: -28 },
      },
      newStats: { CASH: 0, MORALE: 35, BOARD: 8, FACE: 12 },
      historyAdded: {
        quarter: 1,
        decisionId: "q1-card-runway",
        statsBefore: { CASH: 70, MORALE: 55, BOARD: 50, FACE: 40 },
        statsAfter: { CASH: 0, MORALE: 35, BOARD: 8, FACE: 12 },
        settlementSummary: "现金归零，董事会发难。",
      },
      death: { reason: "cash_zero", title: "董事会罢免 CEO" },
      llmDegraded: false,
    },
  },
  deathReport: DEATH_REPORT_BUNDLE_Q4_OUST,
};

export const DIE_Q1_DECISION_DRAWS_BY_QUARTER = DECISION_DRAWS_BY_QUARTER;
