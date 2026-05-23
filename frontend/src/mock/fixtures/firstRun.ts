import type {
  DeathReportBundleDTO,
  DecisionAckDTO,
  EmployeeDTO,
  GameSnapshotDTO,
  GossipResultDTO,
  PressAckDTO,
  SettlementBundleDTO,
  StatsDTO,
} from "@/protocol/types";

export type MockScenario = "happy" | "die-q1" | "press-fail";

const sessionId = "mock-session-001";
const playerId = "mock-player";

export const mockEmployees: EmployeeDTO[] = [
  employee("emp-01", "Lin Qiao", "CFO", 78, 42, 35, "ledger hawk", "finance"),
  employee("emp-02", "Mara Chen", "COO", 71, 58, 46, "calendar tyrant", "ops"),
  employee("emp-03", "Owen Xu", "CTO", 66, 51, 62, "ship-it oracle", "product"),
  employee("emp-04", "Iris Zhao", "PR Lead", 73, 64, 39, "headline sculptor", "brand"),
  employee("emp-05", "Victor Han", "Sales VP", 59, 37, 55, "quota preacher", "sales"),
  employee("emp-06", "Nina Lu", "HRBP", 62, 49, 68, "policy whisperer", "people"),
  employee("emp-07", "Sam Wu", "Legal", 81, 34, 43, "risk stapler", "legal"),
  employee("emp-08", "Jade Tang", "Design", 69, 53, 57, "pixel purist", "product"),
  employee("emp-09", "Bo Ren", "QA", 76, 61, 41, "bug archivist", "product"),
  employee("emp-10", "Mei Song", "Analyst", 72, 45, 50, "chart medium", "finance"),
  employee("emp-11", "Ken Li", "Intern", 38, 74, 22, "coffee realist", "ops"),
  employee("emp-12", "Ada Gu", "Board Liaison", 84, 28, 65, "smile auditor", "board"),
];

export const mockInitialStats: StatsDTO = {
  CASH: 70,
  MORALE: 55,
  BOARD: 50,
  FACE: 40,
};

export const createMockSnapshot = (overrides: Partial<GameSnapshotDTO> = {}): GameSnapshotDTO => ({
  sessionId,
  playerId,
  company: {
    id: "company-entropy-noodles",
    name: "Entropy Noodles Inc.",
    business: "AI-powered instant noodles for enterprise offsites",
    absurdity: 87,
    foundingMotto: "Boil fast, pivot faster.",
    deathCauses: [
      { category: "capital", description: "Runway evaporates into branded steam." },
      { category: "trust", description: "Employees stop believing the broth roadmap." },
    ],
    foundedYear: 2026,
  },
  stats: mockInitialStats,
  quarter: {
    number: 1,
    phase: "BRIEFING",
    briefing: {
      quarter: 1,
      marketMood: "neutral",
      headlineHint: "Investors want proof that noodles can scale.",
    },
    decisionCards: [
      {
        id: "q1-card-runway",
        category: "finance",
        title: "Freeze the Office Soup Bar",
        description: "Cut perks and preserve runway before the board notices the burn rate.",
        immediateEffect: { CASH: 12, MORALE: -8 },
        flavor: "The ladles are locked in a glass case labeled fiscal discipline.",
        longTermHint: "Finance will approve; hungry engineers may not.",
      },
      {
        id: "q1-card-hype",
        category: "brand",
        title: "Announce NoodleOS",
        description: "Promise a platform layer around instant lunch decisions.",
        immediateEffect: { FACE: 10, BOARD: 4 },
        flavor: "The deck contains nine diagrams and no working code.",
        longTermHint: "The press will ask what an operating system tastes like.",
      },
    ],
    apRemaining: 3,
  },
  history: [],
  metaSummary: {
    playerId,
    totalRuns: 1,
    unlockedLegacies: [],
    unlockedStyles: [],
  },
  promiseLog: [],
  status: "active",
  ...overrides,
});

export const createMockDecisionAck = (
  cardId = "q1-card-runway",
  stats: StatsDTO = { CASH: 82, MORALE: 47, BOARD: 50, FACE: 40 },
): DecisionAckDTO => ({
  sessionId,
  quarterNumber: 1,
  cardId,
  immediateStats: stats,
  nextPhase: "GOSSIP",
});

export const createMockGossipResult = (): GossipResultDTO => ({
  sessionId,
  quarterNumber: 1,
  lead: {
    id: "lead-q1-board-steam",
    quarter: 1,
    scene: "elevator",
    speakerId: "emp-12",
    text: "The board deck has a slide titled Steam Margin Sensitivity.",
    reliability: "LIKELY",
    linkedEmployeeIds: ["emp-12", "emp-01"],
    apCost: 1,
  },
  apRemaining: 2,
});

export const createMockPressAck = (): PressAckDTO => ({
  sessionId,
  quarterNumber: 3,
  accepted: true,
  flags: [],
  replacedCount: 0,
});

export const createMockSettlementBundle = (scenario: MockScenario): SettlementBundleDTO => {
  const died = scenario === "die-q1";
  const newStats: StatsDTO = died
    ? { CASH: 0, MORALE: 20, BOARD: 8, FACE: 12 }
    : { CASH: 76, MORALE: 49, BOARD: 54, FACE: 43 };

  return {
    sessionId,
    quarterNumber: 1,
    settlement: {
      quarter: 1,
      quarterReport: died
        ? "The runway spreadsheet reached zero before lunch."
        : "The quarter survives with fewer perks and a louder finance team.",
      boardReaction: {
        speech: died ? "This is not a liquidity strategy." : "Unpleasant, but legible.",
        patienceDelta: died ? -40 : 4,
        vote: died ? "oppose" : "approve",
      },
      employeeGossip: {
        speaker: "Nina Lu",
        line: died ? "The severance FAQ has a soup stain." : "People miss the soup bar.",
        mood: died ? "numb" : "anxious",
      },
      rivalAction: {
        rivalName: "BrothStack",
        action: "pr_attack",
        description: "They imply your noodles are just hot OKRs.",
        expectedDamage: { FACE: -3 },
      },
      marketSignal: died ? "crisis" : "neutral",
      metricsDelta: died ? { CASH: -82, BOARD: -42 } : { CASH: -6, MORALE: 2 },
    },
    newStats,
    historyAdded: {
      quarter: 1,
      decisionId: "q1-card-runway",
      statsBefore: mockInitialStats,
      statsAfter: newStats,
      settlementSummary: died ? "Runway collapsed." : "Runway stabilized.",
    },
    death: died ? { reason: "cash_zero", title: "Boiled Dry" } : undefined,
    llmDegraded: false,
  };
};

export const createMockDeathReport = (): DeathReportBundleDTO => ({
  sessionId,
  obituary: "Entropy Noodles promised enterprise lunch transformation and delivered an empty kettle.",
  biggestMistakeDecisionId: "q1-card-runway",
  lastEmployee: { name: "Ken Li", quote: "Should I still order cups?" },
  headlines: ["Entropy Noodles Runs Out of Steam", "Board Declares Broth Insolvent"],
  legacyUnlocks: [],
  stylesUnlocked: [],
});

function employee(
  id: string,
  name: string,
  role: string,
  competence: number,
  loyalty: number,
  stress: number,
  personalityTag: string,
  faction: string,
): EmployeeDTO {
  return {
    id,
    name,
    role,
    competence,
    loyalty,
    stress,
    personalityTag,
    faction,
    mood: stress > 60 ? "strained" : "alert",
    attitudeToPlayer: loyalty > 55 ? "curious" : "skeptical",
  };
}
