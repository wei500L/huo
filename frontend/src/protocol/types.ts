export interface StatsDTO {
  cash: number;
  morale: number;
  board: number;
  face: number;
}

export type QuarterPhase = "BRIEFING" | "GOSSIP" | "DECISION" | "PRESS" | "SETTLEMENT" | "DONE";

export type GossipScene =
  | "tearoom"
  | "elevator"
  | "meeting_room"
  | "workstation"
  | "rooftop"
  | "smoking_area";

export type GossipReliability = "RUMOR" | "LIKELY" | "CONFIRMED";

export type PressType =
  | "INAUGURATION"
  | "CRISIS"
  | "PRODUCT"
  | "FINANCIAL"
  | "ROADSHOW"
  | "LAYOFF_EXPLAIN"
  | "REGULATOR"
  | "COUNTER";

export interface DeathCauseDTO {
  category: string;
  description: string;
}

export interface CompanyDTO {
  id: string;
  name: string;
  business: string;
  absurdity: number;
  foundingMotto: string;
  deathCauses: DeathCauseDTO[];
  startingPromises: string[];
  foundedYear: number;
}

export interface CompanyTemplateDTO {
  templateId: string;
  name: string;
  namePool: string[];
  business: string;
  absurdity: number;
  foundingMotto: string;
  foundedYear: number;
  startingPromises: string[];
  deathCauses: DeathCauseDTO[];
}

export interface EmployeeDTO {
  id: string;
  name: string;
  role: string;
  competence: number;
  loyalty: number;
  stress: number;
  personalityTag: string;
  faction: string;
  mood: string;
  attitudeToPlayer: string;
}

export interface DecisionCardDTO {
  id: string;
  category: string;
  title: string;
  description: string;
  immediateEffect: Partial<StatsDTO>;
  flavor: string;
  longTermHint?: string;
  boomerangSeeds?: { delayQuarters: number; probability: number; description: string; effect: Partial<StatsDTO> }[];
}

export interface GossipLeadDTO {
  id: string;
  quarter: number;
  scene: GossipScene;
  speakerId?: string;
  text: string;
  reliability: GossipReliability;
  linkedEmployeeIds: string[];
  apCost: number;
}

export interface BriefingDTO {
  quarter: number;
  marketMood: string;
  headlineHint: string;
}

export interface PressInputDTO {
  quarter: number;
  pressType: PressType;
  mustAnswerTopics: string[];
  transcript: string;
  wordCount: number;
  flags: string[];
  submittedAt: string;
}

export interface PressTypeDTO {
  id: PressType;
  titleZh: string;
  triggerConditionText: string;
  mustAnswerTopics: string[];
  difficulty: number;
  pressKeywords: string[];
}

export interface PressEvaluationDTO {
  scores: Record<string, number>;
  memorableQuote: string;
  biggestFlaw: string;
  mediaAngle: string;
  statImpact: Partial<StatsDTO>;
}

export interface MediaHeadlineDTO {
  outlet: string;
  headline: string;
  tone: string;
  summary?: string;
}

export interface PressBundleDTO {
  input: PressInputDTO;
  evaluation: PressEvaluationDTO;
  headlines: MediaHeadlineDTO[];
}

export interface BoardReactionDTO {
  speech: string;
  patienceDelta: number;
  vote: "approve" | "oppose" | "abstain";
}

export interface EmployeeGossipDTO {
  speaker: string;
  line: string;
  mood: string;
}

export interface RivalActionDTO {
  rivalName: string;
  action: string;
  description: string;
  expectedDamage: Partial<StatsDTO>;
}

export interface SettlementDTO {
  quarter: number;
  quarterReport: string;
  boardReaction: BoardReactionDTO;
  employeeGossip: EmployeeGossipDTO;
  rivalAction: RivalActionDTO;
  marketSignal: string;
  metricsDelta: Partial<StatsDTO>;
  scheduledEventsAdded?: string[];
}

export interface HistoryEntryDTO {
  quarter: number;
  decisionId: string;
  pressBundleId?: string;
  statsBefore: StatsDTO;
  statsAfter: StatsDTO;
  settlementSummary: string;
}

export interface PromiseDTO {
  id: string;
  quarterMade: number;
  source: string;
  text: string;
  fulfilled: boolean | null;
  judgedAtQuarter?: number;
  parsed?: {
    metric: string;
    targetExpr: string;
    deadlineQuarter?: number;
  };
}

export interface LegacyUnlockDTO {
  type: string;
  labelZh: string;
  description: string;
  effectSummary: string;
  earnedAtRunId: string;
  earnedAtQuarter: number;
}

export interface MetaSummaryDTO {
  schemaVersion: number;
  totalRuns: number;
  unlockedLegacies: LegacyUnlockDTO[];
  unlockedStyles: string[];
  deathLogCount: number;
  pressArchiveCount: number;
}

export interface QuarterDTO {
  number: number;
  phase: QuarterPhase;
  briefing?: BriefingDTO;
  decisionCards: DecisionCardDTO[];
  selectedDecisionId?: string;
  gossipCollected: string[];
  pressInput?: PressInputDTO;
  pressBundle?: PressBundleDTO;
  settlement?: SettlementDTO;
  apRemaining: number;
}

export interface GameSnapshotDTO {
  sessionId: string;
  playerId: string;
  company: CompanyDTO;
  stats: StatsDTO;
  quarter: QuarterDTO;
  history: HistoryEntryDTO[];
  metaSummary: MetaSummaryDTO;
  promiseLog: PromiseDTO[];
  status: "active" | "dead" | "won";
}

export interface DecisionAckDTO {
  sessionId: string;
  quarterNumber: number;
  cardId: string;
  immediateStats: StatsDTO;
  nextPhase: QuarterPhase;
}

export interface GossipResultDTO {
  sessionId: string;
  quarterNumber: number;
  lead: GossipLeadDTO;
  apRemaining: number;
}

export interface PressAckDTO {
  sessionId: string;
  quarterNumber: number;
  accepted: boolean;
  flags: string[];
  replacedCount: number;
}

export interface SettlementBundleDTO {
  sessionId: string;
  quarterNumber: number;
  settlement: SettlementDTO;
  pressBundle?: PressBundleDTO;
  newStats: StatsDTO;
  historyAdded: HistoryEntryDTO;
  death?: { code: string; labelZh: string } | null;
  llmDegraded: boolean;
}

export interface DeathReportBundleDTO {
  sessionId: string;
  obituary: string;
  biggestMistakeDecisionId?: string;
  lastEmployee?: { name: string; quote: string };
  headlines: string[];
  legacyUnlocks: LegacyUnlockDTO[];
  stylesUnlocked: string[];
}

export interface ToastDTO {
  id?: string;
  level: "info" | "warn" | "error";
  message: string;
  hint?: string;
}

export interface ErrorOutboundDTO {
  code: string;
  message: string;
  retryable: boolean;
}
