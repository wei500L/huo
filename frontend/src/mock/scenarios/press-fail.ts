import { SETTLEMENT_BUNDLE_Q1, SETTLEMENT_BUNDLE_Q3_PRESS } from "../fixtures/settlementBundles";
import { DECISION_DRAWS_BY_QUARTER } from "../fixtures/decisionCards";
import type { MockScenarioDefinition } from "../scenarioTypes";
import { deepClone } from "../utils";

export const PRESS_FAIL_SCENARIO: MockScenarioDefinition = {
  name: "press-fail",
  defaultTemplateId: "C-03",
  pressRejected: true,
  settlementBundles: {
    1: SETTLEMENT_BUNDLE_Q1,
    2: {
      ...deepClone(SETTLEMENT_BUNDLE_Q1),
      quarterNumber: 2,
      settlement: {
        ...deepClone(SETTLEMENT_BUNDLE_Q1.settlement),
        quarter: 2,
        quarterReport: "第二季的执行没有变好，但还没彻底失控。",
      },
      newStats: { CASH: 50, MORALE: 45, BOARD: 44, FACE: 34 },
      historyAdded: {
        quarter: 2,
        decisionId: "q2-card-layoff",
        statsBefore: { CASH: 52, MORALE: 48, BOARD: 46, FACE: 36 },
        statsAfter: { CASH: 50, MORALE: 45, BOARD: 44, FACE: 34 },
        settlementSummary: "执行仍然吃力。",
      },
    },
    3: SETTLEMENT_BUNDLE_Q3_PRESS,
    4: {
      ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS),
      quarterNumber: 4,
      settlement: {
        ...deepClone(SETTLEMENT_BUNDLE_Q3_PRESS.settlement),
        quarter: 4,
        quarterReport: "第四季仍然没能翻盘，但你至少没有让局面更糟。",
      },
      newStats: { CASH: 38, MORALE: 40, BOARD: 48, FACE: 39 },
      historyAdded: {
        quarter: 4,
        decisionId: "q4-card-defense",
        statsBefore: { CASH: 43, MORALE: 44, BOARD: 50, FACE: 43 },
        statsAfter: { CASH: 38, MORALE: 40, BOARD: 48, FACE: 39 },
        settlementSummary: "勉强收场。",
      },
    },
  },
  deathReport: null,
};

export const PRESS_FAIL_DECISION_DRAWS_BY_QUARTER = DECISION_DRAWS_BY_QUARTER;
