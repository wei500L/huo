import type { GossipLeadDTO } from "@/protocol/types";

import type { GameStoreState } from "../gameStore";

type StoreSet = (fn: (state: GameStoreState) => Partial<GameStoreState> | GameStoreState) => void;

export const createGossipActions = (set: StoreSet) => ({
  addGossipNote: (lead: GossipLeadDTO) =>
    set((state) => ({
      gossipNotes: [
        ...state.gossipNotes,
        { id: `${lead.id}-${state.gossipNotes.length + 1}`, lead, notedAt: new Date().toISOString() },
      ],
    })),
});
