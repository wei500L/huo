import { create } from "zustand";
import { persist, type PersistOptions } from "zustand/middleware";

import type {
  DecisionAckDTO,
  DeathReportBundleDTO,
  GameSnapshotDTO,
  GossipLeadDTO,
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
import { createGossipActions } from "./__internal__/gossipActions";
import { useScreenStore } from "./screenStore";

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
  addGossipNote: (lead: GossipLeadDTO) => void;
  setPressDraft: (draft: string) => void;
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
          return {
            pendingDecision:
              state.snapshot?.quarter.decisionCards.find((card) => card.id === clean.cardId) ?? null,
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

          return {
            snapshot: {
              ...state.snapshot,
              quarter: {
                ...state.snapshot.quarter,
                apRemaining: clean.apRemaining,
              },
            },
            latestGossipLead: clean.lead,
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
        const rejected = !clean.accepted;
        set((state) => {
          if (rejected) {
            return {
              inflight: { ...state.inflight, submitPress: false },
              toasts: [
                ...state.toasts,
                {
                  id: createToastId(),
                  level: "error",
                  message: "发布会发言被驳回",
                },
              ],
            };
          }

          return {
            inflight: { ...state.inflight, submitPress: false },
          };
        });
        if (rejected) {
          useScreenStore.getState().replace("press");
        }
      },
      ingestSettlementBundle: (b) => {
        if (!isSettlementBundleLike(b)) {
          warnInvalid("ingestSettlementBundle", b);
          return;
        }

        const clean = deepStripForbiddenFields(b);
        set((state) => {
          return {
            pendingDecision: null,
            pendingSettlementBundle: clean,
            pressBundle: clean.pressBundle ?? state.pressBundle ?? null,
            llmDegraded: clean.llmDegraded,
            inflight: { ...state.inflight, settleQuarter: false },
          };
        });
        if (clean.death) {
          useScreenStore.getState().replace("death-report");
        }
      },
      ingestDeathBundle: (b) => {
        if (!isDeathBundleLike(b)) {
          warnInvalid("ingestDeathBundle", b);
          return;
        }

        const clean = deepStripForbiddenFields(b);
        set((state) => {
          return {
            pendingDecision: null,
            pendingDeathBundle: clean,
            inflight: { ...state.inflight, settleQuarter: false },
          };
        });
        useScreenStore.getState().replace("death-report");
      },
      pushToast: (t) => {
        if (!isToastLike(t)) {
          warnInvalid("pushToast", t);
          return;
        }

        const toast = deepStripForbiddenFields({
          ...t,
          id: createToastId(),
        }) as ToastDTO & { id: string };

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
      setPressDraft: (draft) => {
        set({
          pressDraft: draft,
        });
      },
      resetForNewRun: () => {
        set({
          ...createEmptyDataState(),
        });
      },
      ...createGossipActions(set),
    }),
    persistOptions,
  ),
);
