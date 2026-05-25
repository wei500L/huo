import type { DecisionCardDTO, GameSnapshotDTO, HistoryEntryDTO, PromiseDTO, ToastDTO } from "@/protocol/types";

import type { PortraitId } from "@/components/pixel";

import type { GameStoreState } from "./gameStore";

const EMPTY_DECISION_CARDS: DecisionCardDTO[] = [];
const EMPTY_HISTORY: HistoryEntryDTO[] = [];
const EMPTY_PROMISE_LOG: PromiseDTO[] = [];
const EMPTY_TOASTS: ToastDTO[] = [];

export const selectCurrentSnapshot = (s: GameStoreState) => s.snapshot;
export const selectCurrentStats = (s: GameStoreState) => s.snapshot?.stats ?? null;
export const selectCurrentQuarter = (s: GameStoreState) => s.snapshot?.quarter ?? null;
export const selectCurrentStatus = (s: GameStoreState) => s.snapshot?.status ?? null;
export const selectSessionId = (s: GameStoreState) => s.snapshot?.sessionId ?? null;
export const selectPlayerId = (s: GameStoreState) => s.snapshot?.playerId ?? null;
export const selectCurrentCompany = (s: GameStoreState) => s.snapshot?.company ?? null;
export const selectMetaSummary = (s: GameStoreState) => s.snapshot?.metaSummary ?? null;
export const selectPromiseLog = (s: GameStoreState) => s.snapshot?.promiseLog ?? EMPTY_PROMISE_LOG;
export const selectHistory = (s: GameStoreState) =>
  s.history.length > 0 ? s.history : s.snapshot?.history ?? EMPTY_HISTORY;
export const selectLatestGossipLead = (s: GameStoreState) => s.latestGossipLead;
export const selectGossipNotes = (s: GameStoreState) => s.gossipNotes;
export const selectGossipTrust = (employeeId: string) => (s: GameStoreState) =>
  s.gossipTrust[employeeId] ?? 50;
export const selectPressDraft = (s: GameStoreState) => s.pressDraft;
export const selectDecisionCards = (s: GameStoreState) =>
  s.snapshot?.quarter.decisionCards ?? EMPTY_DECISION_CARDS;
export const selectSelectedDecisionId = (s: GameStoreState) =>
  s.snapshot?.quarter.selectedDecisionId ?? null;
export const selectQuarterPhase = (s: GameStoreState) => s.snapshot?.quarter.phase ?? null;
export const selectAPRemaining = (s: GameStoreState) => s.snapshot?.quarter.apRemaining ?? null;
export const selectPressInput = (s: GameStoreState) => s.snapshot?.quarter.pressInput ?? null;
export const selectQuarterSettlement = (s: GameStoreState) =>
  s.snapshot?.quarter.settlement ?? s.pendingSettlementBundle?.settlement ?? null;
export const selectPendingDecision = (s: GameStoreState) => s.pendingDecision;
export const selectPendingSettlementBundle = (s: GameStoreState) => s.pendingSettlementBundle;
export const selectPendingDeathBundle = (s: GameStoreState) => s.pendingDeathBundle;
export const selectPressBundle = (s: GameStoreState) =>
  s.pressBundle ?? s.snapshot?.quarter.pressBundle ?? null;
export const selectToasts = (s: GameStoreState) => (s.toasts.length > 0 ? s.toasts : EMPTY_TOASTS);
export const selectLatestToast = (s: GameStoreState) => s.toasts[s.toasts.length - 1] ?? null;
export const selectInflight = (s: GameStoreState) => s.inflight;
export const selectIsBusy = (s: GameStoreState) => Object.values(s.inflight).some(Boolean);
export const selectIsLLMDegraded = (s: GameStoreState) => s.llmDegraded;
export const selectIsDead = (s: GameStoreState) => s.snapshot?.status === "dead";
export const selectIsWon = (s: GameStoreState) => s.snapshot?.status === "won";

export type MainActionBarBadgeKey =
  | "companyManagement"
  | "employeeCommunication"
  | "projectProgress"
  | "financialDecision";

export interface MainActionBarBadgeCounts {
  companyManagement: number;
  employeeCommunication: number;
  projectProgress: number;
  financialDecision: number;
}

export interface MainActionBarContextHint {
  speaker?: PortraitId;
  text: string;
}

type MainActionBarSnapshot = GameSnapshotDTO & {
  mainActionBarBadges?: Partial<MainActionBarBadgeCounts>;
  unreadMessages?: number;
  pendingTodos?: number;
  ui?: {
    mainActionBarBadges?: Partial<MainActionBarBadgeCounts>;
    unreadMessages?: number;
    pendingTodos?: number;
  };
  metaSummary?: GameSnapshotDTO["metaSummary"] & {
    mainActionBarBadges?: Partial<MainActionBarBadgeCounts>;
    unreadMessages?: number;
    pendingTodos?: number;
  };
};

const clampBadgeCount = (value: unknown): number => {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.trunc(value));
};

const readBadgeSource = (snapshot: MainActionBarSnapshot): Partial<MainActionBarBadgeCounts> | null => {
  return (
    snapshot.mainActionBarBadges ??
    snapshot.ui?.mainActionBarBadges ??
    snapshot.metaSummary?.mainActionBarBadges ??
    null
  );
};

export const selectMainActionBarBadgeCounts = (s: GameStoreState): MainActionBarBadgeCounts => {
  const snapshot = s.snapshot as MainActionBarSnapshot | null;
  if (!snapshot) {
    return {
      companyManagement: 0,
      employeeCommunication: 0,
      projectProgress: 0,
      financialDecision: 0,
    };
  }

  const badgeSource = readBadgeSource(snapshot);

  return {
    companyManagement: clampBadgeCount(badgeSource?.companyManagement ?? 0),
    employeeCommunication:
      clampBadgeCount(
        badgeSource?.employeeCommunication ??
          snapshot.ui?.unreadMessages ??
          snapshot.unreadMessages ??
          0,
      ),
    projectProgress: clampBadgeCount(
      badgeSource?.projectProgress ?? snapshot.ui?.pendingTodos ?? snapshot.pendingTodos ?? 0,
    ),
    financialDecision: clampBadgeCount(badgeSource?.financialDecision ?? 0),
  };
};

export const selectMainActionBarContextHint = (s: GameStoreState): MainActionBarContextHint => {
  const snapshot = s.snapshot;
  if (!snapshot) {
    return { text: "" };
  }

  if (snapshot.status === "dead") {
    return { speaker: "board_chairman", text: s.pendingDeathBundle?.obituary ?? "" };
  }

  if (snapshot.status === "won") {
    return { speaker: "board_chairman", text: snapshot.history.at(-1)?.settlementSummary ?? "" };
  }

  switch (snapshot.quarter.phase) {
    case "BRIEFING":
      return { speaker: "advisor", text: snapshot.quarter.briefing?.headlineHint ?? "" };
    case "GOSSIP":
      return { speaker: "employee_lin_xiaoman", text: s.latestGossipLead?.text ?? "" };
    case "DECISION":
      return { speaker: "board_chairman", text: s.pendingDecision?.flavor ?? "" };
    case "PRESS":
      return { speaker: "ceo_male_02", text: snapshot.quarter.pressInput?.mustAnswerTopics.join(" / ") ?? "" };
    case "SETTLEMENT":
    case "DONE":
      return {
        speaker: "ceo_female_01",
        text: s.pendingSettlementBundle?.settlement.quarterReport ?? snapshot.quarter.settlement?.quarterReport ?? "",
      };
    default:
      return { text: "" };
  }
};
