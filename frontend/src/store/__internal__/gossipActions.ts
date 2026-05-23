import type { GossipLeadDTO } from "@/protocol/types";

import type { GameStoreState } from "../gameStore";

type StoreSet = (fn: (state: GameStoreState) => Partial<GameStoreState> | GameStoreState) => void;

const clampPercent = (value: number): number => Math.min(100, Math.max(0, Math.trunc(value)));
const normalizeAPCost = (cost: number): number => (Number.isFinite(cost) ? Math.max(0, Math.trunc(cost)) : 0);

export const createGossipActions = (set: StoreSet) => ({
  addGossipNote: (lead: GossipLeadDTO) =>
    set((state) => ({
      gossipNotes: [
        ...state.gossipNotes,
        { id: `${lead.id}-${state.gossipNotes.length + 1}`, lead, notedAt: new Date().toISOString() },
      ],
    })),
  adjustGossipTrust: (employeeId: string, delta: number) =>
    set((state) => ({
      gossipTrust: {
        ...state.gossipTrust,
        [employeeId]: clampPercent((state.gossipTrust[employeeId] ?? 50) + delta),
      },
    })),
  spendGossipAP: (cost: number) => {
    const normalizedCost = normalizeAPCost(cost);
    if (normalizedCost <= 0) return;
    set((state) =>
      state.snapshot
        ? {
            snapshot: {
              ...state.snapshot,
              quarter: {
                ...state.snapshot.quarter,
                apRemaining: Math.max(0, state.snapshot.quarter.apRemaining - normalizedCost),
              },
            },
          }
        : state,
    );
  },
});
