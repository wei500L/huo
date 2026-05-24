import type { PressBundleDTO } from "@/protocol/types";

export const PRESS_BUNDLE_V1: PressBundleDTO = {
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
    statImpact: { face: 8, board: 4, cash: -1, morale: -3 },
  },
  headlines: [
    { outlet: "财新小报", headline: "空降 CEO 承认公司进入艰难窗口", tone: "neutral" },
    { outlet: "第一财经", headline: "企业回应裁员传闻，但现金压力仍在", tone: "critical" },
    { outlet: "商业周刊", headline: "董事会关注的不只是交付，还有叙事", tone: "mixed" },
  ],
};
