import type { DecisionCardDTO, HistoryEntryDTO, PromiseDTO, ToastDTO } from "@/protocol/types";

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
export const selectIsDead = (s: GameStoreState) =>
  s.snapshot ? s.snapshot.status === "dead" || s.snapshot.company.status === "dead" : false;
export const selectIsWon = (s: GameStoreState) => s.snapshot?.status === "won";

