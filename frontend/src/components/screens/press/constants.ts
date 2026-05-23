export const PRESS_KEYWORDS = [
  ["现金流", "现金", "财报", "利润", "融资", "亏损", "烧钱", "runway", "cash flow", "funding"],
  ["裁员", "组织", "团队", "人事", "离职", "优化", "人效", "layoff", "headcount"],
  ["产品", "路线图", "发布", "交付", "版本", "roadmap", "ship", "demo", "上线", "增长"],
] as const;

export const BRAND_BLACKLIST = [
  "OpenAI",
  "Google",
  "Apple",
  "Microsoft",
  "Meta",
  "Amazon",
  "ByteDance",
  "Tencent",
  "Alibaba",
  "Baidu",
  "Entropy Noodles Inc.",
  "BrothStack",
] as const;

export const PRESS_REPORTERS = [
  { outlet: "晨报财经", tone: "neutral" as const },
  { outlet: "互联八卦线", tone: "mocking" as const },
  { outlet: "产业前沿", tone: "friendly" as const },
  { outlet: "深夜自媒体", tone: "hostile" as const },
] as const;

