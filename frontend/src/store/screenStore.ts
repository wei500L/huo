import { create } from "zustand";

export type ScreenId =
  | "onboarding"
  | "company-select"
  | "office"
  | "gossip"
  | "stats-dashboard"
  | "decision"
  | "press"
  | "settlement"
  | "overview"
  | "death-report"
  | "legacy-vault";

export interface ScreenStackEntry {
  id: ScreenId;
  params?: Record<string, unknown>;
}

interface ScreenState {
  current: ScreenStackEntry;
  stack: ScreenStackEntry[];
  hudVisible: boolean;
  mainBarVisible: boolean;
  push: (id: ScreenId, params?: Record<string, unknown>) => void;
  replace: (id: ScreenId, params?: Record<string, unknown>) => void;
  back: () => void;
  setChrome: (cfg: { hud?: boolean; mainBar?: boolean }) => void;
}

const MAX_STACK = 20;

export const useScreenStore = create<ScreenState>((set) => ({
  current: { id: "onboarding" },
  stack: [],
  hudVisible: true,
  mainBarVisible: true,
  push: (id, params) =>
    set((state) => {
      const nextStack = [...state.stack, state.current];
      if (state.stack.length >= MAX_STACK) {
        console.warn("screen stack capped at 20 entries");
      }
      return {
        current: { id, params },
        stack: nextStack.slice(-MAX_STACK),
      };
    }),
  replace: (id, params) => set(() => ({ current: { id, params }, stack: [] })),
  back: () =>
    set((state) => {
      if (state.stack.length === 0) return state;
      const prev = state.stack[state.stack.length - 1];
      return { current: prev, stack: state.stack.slice(0, -1) };
    }),
  setChrome: (cfg) =>
    set((state) => ({
      hudVisible: cfg.hud ?? state.hudVisible,
      mainBarVisible: cfg.mainBar ?? state.mainBarVisible,
    })),
}));
