import type { DecisionCardDTO } from "@/protocol/types";

export const DECISION_CARDS_V1: DecisionCardDTO[] = [
  {
    id: "q1-card-runway",
    category: "finance",
    title: "冻结办公室补汤",
    description: "先砍掉最显眼的非核心开支，保住下个季度的现金线。",
    immediateEffect: { cash: 12, morale: -8, board: 2, face: -4 },
    flavor: "一锅热汤，换一张更冷静的现金表。",
    longTermHint: "财务团队会松一口气，但办公室会更安静。",
  },
  {
    id: "q1-card-hype",
    category: "brand",
    title: "宣布 NoodleOS",
    description: "先把故事讲出去，再想办法把产品做出来。",
    immediateEffect: { cash: 4, morale: -5, board: 6, face: 10 },
    flavor: "九页幻灯片，零个可执行原型。",
    longTermHint: "媒体会问你，面条系统到底长什么样。",
  },
  {
    id: "q1-card-board",
    category: "board",
    title: "申请董事会缓冲",
    description: "把压力摊开讲，让董事会先别做激烈动作。",
    immediateEffect: { cash: 3, morale: -2, board: 5, face: -3 },
    flavor: "先稳住桌面上的杯子，再谈风向。",
  },
  {
    id: "q2-card-pivot",
    category: "product",
    title: "转向企业食堂",
    description: "把产品定位改成更容易成交的企业餐饮方案。",
    immediateEffect: { cash: 9, morale: -4, board: 4, face: -1 },
    flavor: "从理想菜单切到能签单的菜单。",
  },
  {
    id: "q2-card-layoff",
    category: "people",
    title: "小幅裁员止血",
    description: "删掉冗余岗位，换取更长的 runway。",
    immediateEffect: { cash: 16, morale: -15, board: 1, face: -6 },
    flavor: "账面轻一点，办公室重一点。",
  },
  {
    id: "q2-card-hr",
    category: "people",
    title: "集中安抚团队",
    description: "开诚布公地解释现状，压住离职波动。",
    immediateEffect: { cash: -2, morale: 9, board: 0, face: 2 },
    flavor: "先把人心稳住，再谈增长幻觉。",
  },
  {
    id: "q3-card-press-safe",
    category: "pr",
    title: "用事实压住发布会",
    description: "尽量少承诺，只回答能验证的问题。",
    immediateEffect: { cash: 1, morale: -3, board: 4, face: 6 },
    flavor: "每个句子都像审计报表一样保守。",
  },
  {
    id: "q3-card-press-bold",
    category: "pr",
    title: "强硬回击质疑",
    description: "主动抢节奏，把媒体压力改写成攻势。",
    immediateEffect: { cash: -1, morale: -4, board: 6, face: 9 },
    flavor: "话锋很硬，后续风险也很硬。",
  },
  {
    id: "q3-card-roadshow",
    category: "sales",
    title: "临时路演融资",
    description: "把发布会包装成再融资前的信号场。",
    immediateEffect: { cash: 10, morale: -6, board: 5, face: -2 },
    flavor: "讲故事的速度比烧钱的速度更快。",
  },
  {
    id: "q4-card-rescue",
    category: "finance",
    title: "寻求救援合并",
    description: "主动找更大的玩家接盘，换取团队续命。",
    immediateEffect: { cash: 8, morale: -8, board: 7, face: -5 },
    flavor: "体面地把方向盘交出去。",
  },
  {
    id: "q4-card-defense",
    category: "board",
    title: "正面回击罢免",
    description: "试着说服董事会，最后再给一次窗口。",
    immediateEffect: { cash: -3, morale: -6, board: 8, face: 4 },
    flavor: "你和董事会都知道，这是一场最后的拉扯。",
  },
  {
    id: "q4-card-reset",
    category: "strategy",
    title: "重新定义胜利",
    description: "把终局目标写成更现实的版本。",
    immediateEffect: { cash: 2, morale: 4, board: 2, face: 1 },
    flavor: "不是翻盘，是重新找一个能活的版本。",
  },
];

export const DECISION_DRAWS_BY_QUARTER: Record<1 | 2 | 3 | 4, string[]> = {
  1: ["q1-card-runway", "q1-card-hype", "q1-card-board"],
  2: ["q2-card-pivot", "q2-card-layoff", "q2-card-hr"],
  3: ["q3-card-press-safe", "q3-card-press-bold", "q3-card-roadshow"],
  4: ["q4-card-rescue", "q4-card-defense", "q4-card-reset"],
};

export const DECISION_CARD_BY_ID = Object.fromEntries(
  DECISION_CARDS_V1.map((card) => [card.id, card]),
) as Record<string, DecisionCardDTO>;
