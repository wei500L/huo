import { create } from "zustand";

export interface NetworkState {
  status: "idle" | "connecting" | "open" | "reconnecting" | "closed" | "error";
  lastError: string | null;
  latencyMs: number | null;
  dataSource: "mock" | "ws";
  setStatus: (s: NetworkState["status"]) => void;
  setError: (e: string | null) => void;
  setLatency: (ms: number | null) => void;
  setDataSource: (ds: NetworkState["dataSource"]) => void;
}

const readDataSourceEnv = (): string | undefined => {
  const viteValue = import.meta.env.VITE_DATA_SOURCE;
  if (viteValue) {
    return viteValue;
  }

  if (typeof process !== "undefined") {
    return process.env.VITE_DATA_SOURCE;
  }

  return undefined;
};

const getDefaultDataSource = (): NetworkState["dataSource"] =>
  readDataSourceEnv() === "ws" ? "ws" : "mock";

export const useNetworkStore = create<NetworkState>((set) => ({
  status: "idle",
  lastError: null,
  latencyMs: null,
  dataSource: getDefaultDataSource(),
  setStatus: (s) => set({ status: s }),
  setError: (e) => set({ lastError: e }),
  setLatency: (ms) => set({ latencyMs: ms }),
  setDataSource: (ds) => set({ dataSource: ds }),
}));

