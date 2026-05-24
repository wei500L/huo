import { DEATH_REPORT_BUNDLE_Q4_OUST } from "../fixtures/deathReport";
import { SETTLEMENT_BUNDLE_Q1, SETTLEMENT_BUNDLE_Q3_PRESS } from "../fixtures/settlementBundles";
import { DECISION_DRAWS_BY_QUARTER } from "../fixtures/decisionCards";
import type { MockScenarioDefinition } from "../scenarioTypes";
import { deepClone } from "../utils";

export const HAPPY_SCENARIO: MockScenarioDefinition = {
  name: "happy",
  defaultTemplateId: "C-01",
  pressRejected: false,
  settlementBundles: {
    1: SETTLEMENT_BUNDLE_Q1,
    2: {
      ...deepClone(SETTLEMENT_BUNDLE_Q1),
      quarterNumber: 2,
      settlement: {
        ...deepClone(SETTLEMENT_BUNDLE_Q1.settlement),
        quarter: 2,
        quarterReport: "第二季的节奏稍稳，但组织已经开始对下一次大动作有了更高期待。",
      },
      newStats: { CASH: 47, MORALE: 46, BOARD: 48, FACE: 38 },
      historyAdded: {
        quarter: 2,
        decisionId: "q2-card-pivot",
        statsBefore: { CASH: 52, MORALE: 48, BOARD: 46, FACE: 36 },
        statsAfter: { CASH: 47, MORALE: 46, BOARD: 48, FACE: 38 },
        settlementSummary: "第二季继续维持。",
      },
    },
    3: SETTLEMENT_BUNDLE_Q3_PRESS,
    4: {
      ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS),
      quarterNumber: 4,
      settlement: {
        ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS.settlement),
        quarter: 4,
        quarterReport: "第四季守住了最后一口气，公司进入通关态势。",
        boardReaction: { speech: "这次先不罢免你了。", patienceDelta: 6, vote: "approve" },
      },
      newStats: { CASH: 41, MORALE: 45, BOARD: 55, FACE: 48 },
      historyAdded: {
        quarter: 4,
        decisionId: "q4-card-rescue",
        statsBefore: { CASH: 43, MORALE: 44, BOARD: 50, FACE: 43 },
        statsAfter: { CASH: 41, MORALE: 45, BOARD: 55, FACE: 48 },
        settlementSummary: "最终守住局面。",
      },
      death: undefined,
    },
  },
  deathReport: null,
};

export const HAPPY_DECISION_DRAWS_BY_QUARTER = DECISION_DRAWS_BY_QUARTER;
