import type {
  DecisionAckDTO,
  DecisionCardDTO,
  DeathReportBundleDTO,
  GameSnapshotDTO,
  GossipLeadDTO,
  GossipResultDTO,
  HistoryEntryDTO,
  PressAckDTO,
  PressBundleDTO,
  SettlementBundleDTO,
  ToastDTO,
} from "@/protocol/types";

import {
  createEmptyPersistedGameState,
  isRecord,
  sanitizePersistedGameState,
  stripForbiddenFields,
  type GameStorePersistedState,
} from "./persist";

export interface GossipNote {
  id: string;
  lead: GossipLeadDTO;
  notedAt: string;
}

export type StoredToast = ToastDTO & { id: string };

export type GameDataState = {
  snapshot: GameSnapshotDTO | null;
  history: HistoryEntryDTO[];
  latestGossipLead: GossipLeadDTO | null;
  gossipNotes: GossipNote[];
  gossipTrust: Record<string, number>;
  pressDraft: string;
  pendingDecision: DecisionCardDTO | null;
  pendingSettlementBundle: SettlementBundleDTO | null;
  pendingDeathBundle: DeathReportBundleDTO | null;
  pressBundle: PressBundleDTO | null;
  toasts: StoredToast[];
  inflight: {
    createGame?: boolean;
    selectDecision?: boolean;
    collectGossip?: boolean;
    submitPress?: boolean;
    settleQuarter?: boolean;
  };
  llmDegraded: boolean;
};

const createEmptyInflight = (): GameDataState["inflight"] => ({
  createGame: false,
  selectDecision: false,
  collectGossip: false,
  submitPress: false,
  settleQuarter: false,
});

export const createEmptyDataState = (): GameDataState => ({
  snapshot: null,
  history: [],
  latestGossipLead: null,
  gossipNotes: [],
  gossipTrust: {
    employee_lin_xiaoman: 62,
  },
  pressDraft: "",
  pendingDecision: null,
  pendingSettlementBundle: null,
  pendingDeathBundle: null,
  pressBundle: null,
  toasts: [],
  inflight: createEmptyInflight(),
  llmDegraded: false,
});

export const toPersistedState = (state: GameDataState): GameStorePersistedState =>
  sanitizePersistedGameState({
    snapshot: state.snapshot ? stripForbiddenFields(state.snapshot) : null,
    history: stripForbiddenFields(state.history),
    pendingDecision: state.pendingDecision ? stripForbiddenFields(state.pendingDecision) : null,
    pendingSettlementBundle: state.pendingSettlementBundle
      ? stripForbiddenFields(state.pendingSettlementBundle)
      : null,
    pendingDeathBundle: state.pendingDeathBundle
      ? stripForbiddenFields(state.pendingDeathBundle)
      : null,
    pressBundle: state.pressBundle ? stripForbiddenFields(state.pressBundle) : null,
    llmDegraded: state.llmDegraded,
  }) ?? createEmptyPersistedGameState();

export const migratePersistedState = (persistedState: unknown): GameStorePersistedState => {
  if (!isRecord(persistedState)) {
    return createEmptyPersistedGameState();
  }

  const state =
    "state" in persistedState && isRecord(persistedState.state)
      ? persistedState.state
      : persistedState;

  return (
    sanitizePersistedGameState(state as unknown as GameStorePersistedState) ??
    createEmptyPersistedGameState()
  );
};

const isString = (value: unknown): value is string => typeof value === "string";
const isFiniteNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);
const isBoolean = (value: unknown): value is boolean => typeof value === "boolean";

const isStatsLike = (value: unknown): value is Record<string, unknown> =>
  isRecord(value) &&
  isFiniteNumber(value.cash) &&
  isFiniteNumber(value.morale) &&
  isFiniteNumber(value.board) &&
  isFiniteNumber(value.face);

const isQuarterLike = (value: unknown): value is Record<string, unknown> =>
  isRecord(value) &&
  isFiniteNumber(value.number) &&
  isString(value.phase) &&
  Array.isArray(value.decisionCards) &&
  isFiniteNumber(value.apRemaining);

export const isSnapshotLike = (value: unknown): value is GameSnapshotDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isString(value.playerId) &&
  isRecord(value.company) &&
  isStatsLike(value.stats) &&
  isQuarterLike(value.quarter) &&
  Array.isArray(value.history) &&
  isRecord(value.metaSummary) &&
  Array.isArray(value.promiseLog) &&
  isString(value.status);

const isHistoryEntryLike = (value: unknown): value is HistoryEntryDTO =>
  isRecord(value) &&
  isFiniteNumber(value.quarter) &&
  isString(value.decisionId) &&
  isRecord(value.statsBefore) &&
  isRecord(value.statsAfter) &&
  isString(value.settlementSummary);

export const isDecisionAckLike = (value: unknown): value is DecisionAckDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isFiniteNumber(value.quarterNumber) &&
  isString(value.cardId) &&
  isStatsLike(value.immediateStats) &&
  isString(value.nextPhase);

export const isGossipResultLike = (value: unknown): value is GossipResultDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isFiniteNumber(value.quarterNumber) &&
  isRecord(value.lead) &&
  isFiniteNumber(value.apRemaining);

export const isPressAckLike = (value: unknown): value is PressAckDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isFiniteNumber(value.quarterNumber) &&
  isBoolean(value.accepted) &&
  Array.isArray(value.flags) &&
  isFiniteNumber(value.replacedCount);

export const isSettlementBundleLike = (value: unknown): value is SettlementBundleDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isFiniteNumber(value.quarterNumber) &&
  isRecord(value.settlement) &&
  isStatsLike(value.newStats) &&
  isHistoryEntryLike(value.historyAdded) &&
  isBoolean(value.llmDegraded) &&
  (value.pressBundle === undefined || isRecord(value.pressBundle)) &&
  (value.death === undefined || isRecord(value.death) || value.death === null);

export const isDeathBundleLike = (value: unknown): value is DeathReportBundleDTO =>
  isRecord(value) &&
  isString(value.sessionId) &&
  isString(value.obituary) &&
  Array.isArray(value.headlines) &&
  Array.isArray(value.legacyUnlocks) &&
  Array.isArray(value.stylesUnlocked);

export const isToastLike = (value: unknown): value is ToastDTO =>
  isRecord(value) &&
  isString(value.level) &&
  isString(value.message) &&
  (value.id === undefined || isString(value.id));

export const createToastId = (): string =>
  globalThis.crypto?.randomUUID?.() ?? `toast_${Date.now()}_${Math.random().toString(36).slice(2)}`;

export const warnInvalid = (method: string, payload: unknown) => {
  console.warn(`[gameStore] ${method} ignored invalid payload`, payload);
};

export const resolvePendingDecision = (snapshot: GameSnapshotDTO): DecisionCardDTO | null => {
  const selectedId = snapshot.quarter.selectedDecisionId;
  if (!selectedId) {
    return null;
  }

  return snapshot.quarter.decisionCards.find((card) => card.id === selectedId) ?? null;
};
