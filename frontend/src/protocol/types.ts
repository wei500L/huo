export interface StatsDTO {
  cash: number;
  morale: number;
  board: number;
  face: number;
}

export interface DeathCauseDTO {
  category:
    | "financial"
    | "product"
    | "org"
    | "market"
    | "capital"
    | "trust"
    | "absurd";
  description: string;
}

export interface CompanyDTO {
  id: string;
  name: string;
  business: string;
  absurdity: number;
  foundingMotto: string;
  deathCauses: DeathCauseDTO[];
  foundedYear: number;
  startingPromises?: string[];
  status?: "active" | "dead" | "won";
  [key: string]: unknown;
}

export interface DecisionCardDTO {
  id: string;
  category: string;
  title: string;
  description: string;
  immediateEffect: Partial<StatsDTO>;
  flavor: string;
  longTermHint?: string | null;
  boomerangSeeds?: Array<{
    delayQuarters: 1 | 2 | 3;
    probability: number;
    description: string;
    effect: Partial<StatsDTO>;
  }>;
  [key: string]: unknown;
}

export interface GossipLeadDTO {
  id: string;
  quarter: number;
  scene:
    | "tearoom"
    | "elevator"
    | "meeting_room"
    | "workstation"
    | "rooftop"
    | "smoking_area";
  speakerId?: string | null;
  text: string;
  reliability: "RUMOR" | "LIKELY" | "CONFIRMED";
  linkedEmployeeIds: string[];
  apCost: number;
}

export interface BriefingDTO {
  quarter: number;
  marketMood: "bull" | "neutral" | "bear" | "crisis";
  headlineHint: string;
  [key: string]: unknown;
}

export interface PressInputDTO {
  quarter: number;
  pressType: string;
  mustAnswerTopics: string[];
  transcript: string;
  wordCount: number;
  flags: string[];
  submittedAt: string;
  durationS?: number | null;
  [key: string]: unknown;
}

export interface PressEvaluationDTO {
  scores: Record<string, number>;
  memorableQuote: string;
  biggestFlaw: string;
  mediaAngle: string;
  statImpact: Partial<StatsDTO>;
  [key: string]: unknown;
}

export interface MediaHeadlineDTO {
  outlet: string;
  headline: string;
  tone: "positive" | "neutral" | "negative" | "mocking";
  summary?: string | null;
  [key: string]: unknown;
}

export interface BoardReactionDTO {
  speech: string;
  patienceDelta: number;
  vote: "approve" | "oppose" | "abstain";
  [key: string]: unknown;
}

export interface EmployeeGossipDTO {
  speaker: string;
  line: string;
  mood:
    | "anxious"
    | "angry"
    | "tired"
    | "hopeful"
    | "numb"
    | "excited"
    | "in_love";
  [key: string]: unknown;
}

export interface RivalActionDTO {
  rivalName: string;
  action:
    | "price_war"
    | "poach"
    | "launch"
    | "pr_attack"
    | "wait"
    | "acquisition_rumor";
  description: string;
  expectedDamage: Partial<StatsDTO>;
  [key: string]: unknown;
}

export interface SettlementDTO {
  quarter: number;
  quarterReport: string;
  boardReaction: BoardReactionDTO;
  employeeGossip: EmployeeGossipDTO;
  rivalAction: RivalActionDTO;
  marketSignal: "bull" | "neutral" | "bear" | "crisis";
  metricsDelta: Partial<StatsDTO>;
  scheduledEventsAdded?: string[];
  [key: string]: unknown;
}

export interface HistoryEntryDTO {
  quarter: number;
  decisionId: string;
  pressBundleId?: string | null;
  statsBefore: StatsDTO;
  statsAfter: StatsDTO;
  settlementSummary: string;
  [key: string]: unknown;
}

export interface LegacyUnlockDTO {
  type: string;
  labelZh: string;
  description: string;
  effectSummary: string;
  earnedAtRunId: string;
  earnedAtQuarter: number;
  [key: string]: unknown;
}

export interface MetaSummaryDTO {
  playerId: string;
  totalRuns: number;
  unlockedLegacies: LegacyUnlockDTO[];
  unlockedStyles: string[];
  schemaVersion?: number;
  deathLogCount?: number;
  pressArchiveCount?: number;
  [key: string]: unknown;
}

export interface QuarterDTO {
  number: number;
  phase: "BRIEFING" | "GOSSIP" | "DECISION" | "PRESS" | "SETTLEMENT" | "DONE";
  briefing?: BriefingDTO | null;
  decisionCards: DecisionCardDTO[];
  selectedDecisionId?: string | null;
  gossipCollected?: string[];
  pressInput?: PressInputDTO | null;
  pressBundle?: PressBundleDTO | null;
  settlement?: SettlementDTO | null;
  apRemaining: number;
  [key: string]: unknown;
}

export interface PressBundleDTO {
  input: PressInputDTO;
  evaluation: PressEvaluationDTO;
  headlines: MediaHeadlineDTO[];
  [key: string]: unknown;
}

export interface DecisionAckDTO {
  sessionId: string;
  quarterNumber: number;
  cardId: string;
  immediateStats: StatsDTO;
  nextPhase: QuarterDTO["phase"];
  [key: string]: unknown;
}

export interface GossipResultDTO {
  sessionId: string;
  quarterNumber: number;
  lead: GossipLeadDTO;
  apRemaining: number;
  [key: string]: unknown;
}

export interface PressAckDTO {
  sessionId: string;
  quarterNumber: number;
  accepted: boolean;
  flags: string[];
  replacedCount: number;
  [key: string]: unknown;
}

export interface SettlementBundleDTO {
  sessionId: string;
  quarterNumber: number;
  settlement: SettlementDTO;
  pressBundle?: PressBundleDTO | null;
  newStats: StatsDTO;
  historyAdded: HistoryEntryDTO;
  death?: { reason: string; title: string } | null;
  llmDegraded: boolean;
  [key: string]: unknown;
}

export interface DeathReportBundleDTO {
  sessionId: string;
  obituary: string;
  biggestMistakeDecisionId?: string | null;
  lastEmployee?: { name: string; quote: string } | null;
  headlines: string[];
  legacyUnlocks: LegacyUnlockDTO[];
  stylesUnlocked: string[];
  [key: string]: unknown;
}

export interface ToastDTO {
  id?: string;
  level: "info" | "warn" | "error";
  message: string;
  hint?: string | null;
  [key: string]: unknown;
}

export interface ErrorOutboundDTO {
  code: string;
  message: string;
  retryable: boolean;
  [key: string]: unknown;
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
  [key: string]: unknown;
}

export interface PromiseDTO {
  id: string;
  quarterMade: number;
  source: string;
  text: string;
  fulfilled: boolean | null;
  judgedAtQuarter?: number | null;
  parsed?: {
    metric: string;
    targetExpr: string;
    deadlineQuarter?: number | null;
    [key: string]: unknown;
  } | null;
  [key: string]: unknown;
}

