import { create } from "zustand";

export interface NetworkState {
  status: "idle" | "connecting" | "open" | "reconnecting" | "closed" | "error";
  lastError: string | null;
  latencyMs: number | null;
  dataSource: "ws";
  setStatus: (s: NetworkState["status"]) => void;
  setError: (e: string | null) => void;
  setLatency: (ms: number | null) => void;
  setDataSource: (ds: NetworkState["dataSource"]) => void;
}

export const useNetworkStore = create<NetworkState>((set) => ({
  status: "idle",
  lastError: null,
  latencyMs: null,
  dataSource: "ws",
  setStatus: (s) => set({ status: s }),
  setError: (e) => set({ lastError: e }),
  setLatency: (ms) => set({ latencyMs: ms }),
  setDataSource: () => set({ dataSource: "ws" }),
}));
