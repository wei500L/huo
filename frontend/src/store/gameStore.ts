import { create } from "zustand";
import { persist, type PersistOptions } from "zustand/middleware";

import type {
  DecisionAckDTO,
  DeathReportBundleDTO,
  GameSnapshotDTO,
  GossipResultDTO,
  PressAckDTO,
  SettlementBundleDTO,
  ToastDTO,
} from "@/protocol/types";

import {
  GAME_STATE_STORAGE_KEY,
  createPersistStorage,
  stripForbiddenFields as deepStripForbiddenFields,
} from "./__internal__/persist";
import {
  createEmptyDataState,
  createToastId,
  isDeathBundleLike,
  isDecisionAckLike,
  isGossipResultLike,
  isPressAckLike,
  isSettlementBundleLike,
  isSnapshotLike,
  isToastLike,
  migratePersistedState,
  resolvePendingDecision,
  toPersistedState,
  warnInvalid,
  type GameDataState,
} from "./__internal__/gameStoreUtils";

export interface GameStoreState extends GameDataState {
  ingestSnapshot: (s: GameSnapshotDTO) => void;
  ingestDecisionAck: (a: DecisionAckDTO) => void;
  ingestGossipResult: (r: GossipResultDTO) => void;
  ingestPressAck: (a: PressAckDTO) => void;
  ingestSettlementBundle: (b: SettlementBundleDTO) => void;
  ingestDeathBundle: (b: DeathReportBundleDTO) => void;
  pushToast: (t: ToastDTO) => void;
  dismissToast: (id: string) => void;
  setInflight: (key: keyof GameStoreState["inflight"], v: boolean) => void;
  setLLMDegraded: (v: boolean) => void;
  resetForNewRun: () => void;
}

const persistOptions: PersistOptions<GameStoreState, ReturnType<typeof toPersistedState>> = {
  name: GAME_STATE_STORAGE_KEY,
  storage: createPersistStorage(),
  version: 1,
  partialize: (state) => toPersistedState(state),
  migrate: migratePersistedState,
};

export const useGameStore = create<GameStoreState>()(
  persist(
    (set) => ({
      ...createEmptyDataState(),
      ingestSnapshot: (s) => {
        if (!isSnapshotLike(s)) {
          warnInvalid("ingestSnapshot", s);
          return;
        }

        const clean = deepStripForbiddenFields(s);
        const history = deepStripForbiddenFields(clean.history);
        const pressBundle = clean.quarter.pressBundle ?? null;
        const pendingDecision = resolvePendingDecision(clean);

        set({
          snapshot: {
            ...clean,
            history,
          },
          history,
          pendingDecision,
          pressBundle,
        });
      },
      ingestDecisionAck: (a) => {
        if (!isDecisionAckLike(a)) {
          warnInvalid("ingestDecisionAck", a);
          return;
        }

        const clean = deepStripForbiddenFields(a);
        set((state) => {
          const snapshot = state.snapshot
            ? {
                ...state.snapshot,
                stats: clean.immediateStats,
                quarter: {
                  ...state.snapshot.quarter,
                  selectedDecisionId: clean.cardId,
                  phase: clean.nextPhase,
                },
              }
            : state.snapshot;

          return {
            snapshot,
            pendingDecision:
              snapshot?.quarter.decisionCards.find((card) => card.id === clean.cardId) ?? null,
            inflight: { ...state.inflight, selectDecision: false },
          };
        });
      },
      ingestGossipResult: (r) => {
        if (!isGossipResultLike(r)) {
          warnInvalid("ingestGossipResult", r);
          return;
        }

        const clean = deepStripForbiddenFields(r);
        set((state) => {
          if (!state.snapshot || state.snapshot.quarter.number !== clean.quarterNumber) {
            return {
              inflight: { ...state.inflight, collectGossip: false },
            };
          }

          const collected = state.snapshot.quarter.gossipCollected ?? [];
          const gossipCollected = collected.includes(clean.lead.id)
            ? collected
            : [...collected, clean.lead.id];

          return {
            snapshot: {
              ...state.snapshot,
              quarter: {
                ...state.snapshot.quarter,
                apRemaining: clean.apRemaining,
                gossipCollected,
              },
            },
            inflight: { ...state.inflight, collectGossip: false },
          };
        });
      },
      ingestPressAck: (a) => {
        if (!isPressAckLike(a)) {
          warnInvalid("ingestPressAck", a);
          return;
        }

        const clean = deepStripForbiddenFields(a);
        set((state) => {
          if (!state.snapshot || state.snapshot.quarter.number !== clean.quarterNumber) {
            return {
              inflight: { ...state.inflight, submitPress: false },
            };
          }

          const pressInput = state.snapshot.quarter.pressInput
            ? {
                ...state.snapshot.quarter.pressInput,
                flags: clean.flags,
              }
            : state.snapshot.quarter.pressInput;

          return {
            snapshot: {
              ...state.snapshot,
              quarter: {
                ...state.snapshot.quarter,
                pressInput,
              },
            },
            inflight: { ...state.inflight, submitPress: false },
          };
        });
      },
      ingestSettlementBundle: (b) => {
        if (!isSettlementBundleLike(b)) {
          warnInvalid("ingestSettlementBundle", b);
          return;
        }

        const clean = deepStripForbiddenFields(b);
        set((state) => {
          const history = [...state.history, clean.historyAdded];
          const nextSnapshot = state.snapshot
            ? {
                ...state.snapshot,
                status: clean.death ? "dead" : state.snapshot.status,
                stats: clean.newStats,
                history,
                quarter: {
                  ...state.snapshot.quarter,
                  phase: "DONE" as const,
                  settlement: clean.settlement,
                  pressBundle: clean.pressBundle ?? state.pressBundle ?? null,
                },
              }
            : state.snapshot;

          return {
            snapshot: nextSnapshot,
            history,
            pendingDecision: null,
            pendingSettlementBundle: clean,
            pressBundle: clean.pressBundle ?? state.pressBundle ?? null,
            llmDegraded: clean.llmDegraded,
            inflight: { ...state.inflight, settleQuarter: false },
          };
        });
      },
      ingestDeathBundle: (b) => {
        if (!isDeathBundleLike(b)) {
          warnInvalid("ingestDeathBundle", b);
          return;
        }

        const clean = deepStripForbiddenFields(b);
        set((state) => {
          const snapshot = state.snapshot
            ? {
                ...state.snapshot,
                status: "dead" as const,
                quarter: {
                  ...state.snapshot.quarter,
                  phase: "DONE" as const,
                },
              }
            : state.snapshot;

          return {
            snapshot,
            pendingDecision: null,
            pendingDeathBundle: clean,
            inflight: { ...state.inflight, settleQuarter: false },
          };
        });
      },
      pushToast: (t) => {
        if (!isToastLike(t)) {
          warnInvalid("pushToast", t);
          return;
        }

        const toast = deepStripForbiddenFields({
          ...t,
          id: t.id && t.id.length > 0 ? t.id : createToastId(),
        }) as ToastDTO;

        set((state) => ({
          toasts: [...state.toasts, toast],
        }));
      },
      dismissToast: (id) => {
        set((state) => ({
          toasts: state.toasts.filter((toast) => toast.id !== id),
        }));
      },
      setInflight: (key, v) => {
        set((state) => ({
          inflight: {
            ...state.inflight,
            [key]: v,
          },
        }));
      },
      setLLMDegraded: (v) => {
        set({
          llmDegraded: v,
        });
      },
      resetForNewRun: () => {
        set({
          ...createEmptyDataState(),
        });
      },
    }),
    persistOptions,
  ),
);
