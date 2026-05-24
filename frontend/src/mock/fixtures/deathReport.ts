import type { DeathReportBundleDTO } from "@/protocol/types";

export const DEATH_REPORT_BUNDLE_Q4_OUST: DeathReportBundleDTO = {
  sessionId: "mock-session-001",
  obituary:
    "董事会在第四季度把这家公司从一个勉强能转身的项目，改写成了一个必须被复盘的案例。",
  biggestMistakeDecisionId: "q4-card-defense",
  lastEmployee: {
    name: "林小满",
    quote: "我已经把最后一版公关口径放进共享盘了。",
  },
  headlines: [
    "董事会罢免 CEO，项目转入重组",
    "现金告急未解，组织信心率先归零",
    "媒体开始重写这家公司的故事",
  ],
  legacyUnlocks: [
    {
      type: "MEDIA_NERVE",
      labelZh: "媒体应对经验",
      description: "在镜头前不再手忙脚乱",
      effectSummary: "FACE +1",
      earnedAtRunId: "mock-session-001",
      earnedAtQuarter: 4,
    },
    {
      type: "INDUSTRY_INTEL",
      labelZh: "危机判断",
      description: "更快识别坏信号",
      effectSummary: "BOARD +1",
      earnedAtRunId: "mock-session-001",
      earnedAtQuarter: 4,
    },
    {
      type: "ORG_KNOWHOW",
      labelZh: "失败教训手册",
      description: "把崩盘过程整理成可复用模板",
      effectSummary: "MORALE +1",
      earnedAtRunId: "mock-session-001",
      earnedAtQuarter: 4,
    },
  ],
  stylesUnlocked: ["STORY_MASTER", "SURVIVAL_PRO"],
};
