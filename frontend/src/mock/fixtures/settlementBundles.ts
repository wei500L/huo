import type { SettlementBundleDTO } from "@/protocol/types";

export const SETTLEMENT_BUNDLE_Q1: SettlementBundleDTO = {
  sessionId: "mock-session-001",
  quarterNumber: 1,
  settlement: {
    quarter: 1,
    quarterReport: "第一季把最危险的现金口子暂时堵上了，但组织已经开始出现裂缝。",
    boardReaction: { speech: "先活下来，别再画更大的饼。", patienceDelta: -4, vote: "abstain" },
    employeeGossip: { speaker: "林小满", line: "至少这次没有把锅甩给大家。", mood: "anxious" },
    rivalAction: {
      rivalName: "BrothStack",
      action: "price_cut",
      description: "对手开始压价抢客户。",
      expectedDamage: { FACE: -2 },
    },
    marketSignal: "neutral",
    metricsDelta: { CASH: -18, MORALE: -7, BOARD: -3, FACE: -4 },
  },
  newStats: { CASH: 52, MORALE: 48, BOARD: 46, FACE: 36 },
  historyAdded: {
    quarter: 1,
    decisionId: "q1-card-runway",
    statsBefore: { CASH: 70, MORALE: 55, BOARD: 50, FACE: 40 },
    statsAfter: { CASH: 52, MORALE: 48, BOARD: 46, FACE: 36 },
    settlementSummary: "现金止血，但组织承压。",
  },
  llmDegraded: false,
};

export const SETTLEMENT_BUNDLE_Q3_PRESS: SettlementBundleDTO = {
  sessionId: "mock-session-001",
  quarterNumber: 3,
  settlement: {
    quarter: 3,
    quarterReport: "发布会后，市场对公司有了更清晰的预期，但也更苛刻。",
    boardReaction: { speech: "至少你没有在镜头前失控。", patienceDelta: 3, vote: "approve" },
    employeeGossip: { speaker: "赵澜", line: "媒体终于给了我们一次像样的声音。", mood: "hopeful" },
    rivalAction: {
      rivalName: "BrothStack",
      action: "counter_program",
      description: "对手用更便宜的套餐回应。",
      expectedDamage: { FACE: -1 },
    },
    marketSignal: "bear",
    metricsDelta: { CASH: -9, MORALE: -4, BOARD: 5, FACE: 7 },
  },
  pressBundle: {
    input: {
      quarter: 3,
      pressType: "CRISIS",
      mustAnswerTopics: ["现金流", "裁员传闻", "产品路线"],
      transcript:
        "我们承认这是一季度最困难的窗口，但公司仍然有明确的产品节奏、现金管理和对外沟通机制。",
      wordCount: 36,
      flags: ["clarity", "calm"],
      submittedAt: "2026-05-23T10:00:00.000Z",
    },
    evaluation: {
      scores: {
        contentCompleteness: 78,
        confidence: 72,
        authenticity: 68,
        mediaControl: 74,
        empathy: 61,
        specificity: 70,
        pace: 66,
        vision: 57,
        mediaFit: 69,
      },
      memorableQuote: "我们不会用愿景替代现金表。",
      biggestFlaw: "回答仍然偏保守，没把增长逻辑讲透。",
      mediaAngle: "市场会把这场发布会读成一次止损宣言。",
      statImpact: { FACE: 8, BOARD: 4, CASH: -1, MORALE: -3 },
    },
    headlines: [
      { outlet: "财新小报", headline: "空降 CEO 承认公司进入艰难窗口", tone: "neutral" },
      { outlet: "第一财经", headline: "企业回应裁员传闻，但现金压力仍在", tone: "critical" },
      { outlet: "商业周刊", headline: "董事会关注的不只是交付，还有叙事", tone: "mixed" },
    ],
  },
  newStats: { CASH: 43, MORALE: 44, BOARD: 50, FACE: 43 },
  historyAdded: {
    quarter: 3,
    decisionId: "q3-card-press-safe",
    pressBundleId: "press-q3-crisis",
    statsBefore: { CASH: 52, MORALE: 48, BOARD: 46, FACE: 36 },
    statsAfter: { CASH: 43, MORALE: 44, BOARD: 50, FACE: 43 },
    settlementSummary: "发布会挽回了一点面子。",
  },
  llmDegraded: false,
};

