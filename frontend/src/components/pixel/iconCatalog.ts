export const ICON_MAP = {
  money: () => import("pixelarticons/react/Money"), // 钱
  morale: () => import("pixelarticons/react/Smile"), // 笑脸
  board: () => import("pixelarticons/react/Shield"), // 董事会
  face: () => import("pixelarticons/react/Sunglasses"), // 面子
  calendar: () => import("pixelarticons/react/Calendar"), // 日历
  users: () => import("pixelarticons/react/Users"), // 人员
  fire: () => import("pixelarticons/react/Fire"), // 危机
  trophy: () => import("pixelarticons/react/Trophy"), // 奖杯
  alarm: () => import("pixelarticons/react/SquareAlert"), // 警报
  "trending-up": () => import("pixelarticons/react/Chart"), // 上升
  "trending-down": () => import("pixelarticons/react/ChartColumnDecreasing"), // 下降
  check: () => import("pixelarticons/react/Check"), // 确认
  "close-box": () => import("pixelarticons/react/Close"), // 关闭
  loader: () => import("pixelarticons/react/Loader"), // 加载
  message: () => import("pixelarticons/react/Message"), // 消息
  briefcase: () => import("pixelarticons/react/Briefcase"), // 公文包
  edit: () => import("pixelarticons/react/MagicEdit"), // 编辑
  search: () => import("pixelarticons/react/Search"), // 搜索
  heart: () => import("pixelarticons/react/Heart"), // 心
  rip: () => import("pixelarticons/react/Skull"), // 死亡报告
  news: () => import("pixelarticons/react/Article"), // 新闻
  speech: () => import("pixelarticons/react/MessageText"), // 说话
  settings: () => import("pixelarticons/react/Settings2"), // 设置
  save: () => import("pixelarticons/react/Save"), // 保存
  menu: () => import("pixelarticons/react/Menu"), // 菜单
  back: () => import("pixelarticons/react/ChevronLeft"), // 返回
  forward: () => import("pixelarticons/react/ChevronRight"), // 前进
  lock: () => import("pixelarticons/react/Lock"), // 锁定
  unlock: () => import("pixelarticons/react/Unlock"), // 解锁
  scissors: () => import("pixelarticons/react/Scissors"), // 裁员
  handshake: () => import("pixelarticons/react/Hand"), // 融资
  megaphone: () => import("pixelarticons/react/Volume3"), // 隐瞒坏消息
} as const;

export type IconName = keyof typeof ICON_MAP;

export const ICON_EXPORT_NAMES: Record<IconName, string> = {
  money: "Money",
  morale: "Smile",
  board: "Shield",
  face: "Sunglasses",
  calendar: "Calendar",
  users: "Users",
  fire: "Fire",
  trophy: "Trophy",
  alarm: "SquareAlert",
  "trending-up": "Chart",
  "trending-down": "ChartColumnDecreasing",
  check: "Check",
  "close-box": "Close",
  loader: "Loader",
  message: "Message",
  briefcase: "Briefcase",
  edit: "MagicEdit",
  search: "Search",
  heart: "Heart",
  rip: "Skull",
  news: "Article",
  speech: "MessageText",
  settings: "Settings2",
  save: "Save",
  menu: "Menu",
  back: "ChevronLeft",
  forward: "ChevronRight",
  lock: "Lock",
  unlock: "Unlock",
  scissors: "Scissors",
  handshake: "Hand",
  megaphone: "Volume3",
};

export const EMOJI_FALLBACK: Record<IconName, string> = {
  money: "💰",
  morale: "😊",
  board: "🛡️",
  face: "😎",
  calendar: "📅",
  users: "👥",
  fire: "🔥",
  trophy: "🏆",
  alarm: "⚠️",
  "trending-up": "📈",
  "trending-down": "📉",
  check: "✅",
  "close-box": "❌",
  loader: "⏳",
  message: "💬",
  briefcase: "💼",
  edit: "✏️",
  search: "🔎",
  heart: "❤️",
  rip: "🪦",
  news: "📰",
  speech: "🗣️",
  settings: "⚙️",
  save: "💾",
  menu: "☰",
  back: "◀️",
  forward: "▶️",
  lock: "🔒",
  unlock: "🔓",
  scissors: "✂️",
  handshake: "🤝",
  megaphone: "📣",
};
