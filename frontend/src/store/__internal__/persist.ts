import type { PersistStorage, StateStorage } from "zustand/middleware";

import type {
  DeathReportBundleDTO,
  DecisionCardDTO,
  GameSnapshotDTO,
  HistoryEntryDTO,
  PressBundleDTO,
  SettlementBundleDTO,
} from "@/protocol/types";

export const GAME_STATE_STORAGE_KEY = "yb_v2_game_state";

const FORBIDDEN_KEYS = new Set([
  "hiddenSecrets",
  "hidden_secrets",
  "isTruth",
  "is_truth",
  "hiddenRisks",
  "hidden_risks",
  "internalEval",
  "internal_eval",
]);

const createMemoryStorage = (): StateStorage => {
  const memory = new Map<string, string>();
  return {
    getItem: (name) => memory.get(name) ?? null,
    setItem: (name, value) => {
      memory.set(name, value);
    },
    removeItem: (name) => {
      memory.delete(name);
    },
  };
};

const memoryStorage = createMemoryStorage();

const getBrowserStorage = (): StateStorage => {
  try {
    if (typeof globalThis !== "undefined" && globalThis.localStorage) {
      return globalThis.localStorage;
    }
  } catch {
    return memoryStorage;
  }

  return memoryStorage;
};

export interface GameStorePersistedState {
  snapshot: GameSnapshotDTO | null;
  history: HistoryEntryDTO[];
  pendingDecision: DecisionCardDTO | null;
  pendingSettlementBundle: SettlementBundleDTO | null;
  pendingDeathBundle: DeathReportBundleDTO | null;
  pressBundle: PressBundleDTO | null;
  llmDegraded: boolean;
}

export const createEmptyPersistedGameState = (): GameStorePersistedState => ({
  snapshot: null,
  history: [],
  pendingDecision: null,
  pendingSettlementBundle: null,
  pendingDeathBundle: null,
  pressBundle: null,
  llmDegraded: false,
});

export const createPersistStorage = (): PersistStorage<GameStorePersistedState> => ({
  getItem: (name) => {
    try {
      const raw = getBrowserStorage().getItem(name);
      if (typeof raw !== "string") {
        return null;
      }
      const parsed = JSON.parse(raw) as unknown;
      if (!isRecord(parsed) || !("state" in parsed)) {
        return null;
      }
      const version = typeof parsed.version === "number" ? parsed.version : 1;
      const state = sanitizePersistedGameState(
        isRecord(parsed.state)
          ? (parsed.state as unknown as GameStorePersistedState)
          : null,
      );
      return state ? { version, state } : null;
    } catch (error) {
      console.warn("[yb] failed to read persisted game state", error);
      return null;
    }
  },
  setItem: (name, value) => {
    try {
      const state = sanitizePersistedGameState(value.state) ?? createEmptyPersistedGameState();
      getBrowserStorage().setItem(name, JSON.stringify({ version: value.version ?? 1, state }));
    } catch (error) {
      console.warn("[yb] failed to persist game state", error);
    }
  },
  removeItem: (name) => {
    try {
      getBrowserStorage().removeItem(name);
    } catch (error) {
      console.warn("[yb] failed to remove persisted game state", error);
    }
  },
});

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

export const stripForbiddenFields = <T>(value: T): T => {
  if (Array.isArray(value)) {
    return value.map((item) => stripForbiddenFields(item)) as T;
  }

  if (!isRecord(value)) {
    return value;
  }

  const next: Record<string, unknown> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.has(key)) {
      continue;
    }
    next[key] = stripForbiddenFields(entry);
  }
  return next as T;
};

export const sanitizePersistedGameState = (
  state: GameStorePersistedState | null | undefined,
): GameStorePersistedState | null => {
  if (!state) {
    return null;
  }

  return {
    snapshot: state.snapshot ? stripForbiddenFields(state.snapshot) : null,
    history: stripForbiddenFields(state.history ?? []),
    pendingDecision: state.pendingDecision ? stripForbiddenFields(state.pendingDecision) : null,
    pendingSettlementBundle: state.pendingSettlementBundle
      ? stripForbiddenFields(state.pendingSettlementBundle)
      : null,
    pendingDeathBundle: state.pendingDeathBundle
      ? stripForbiddenFields(state.pendingDeathBundle)
      : null,
    pressBundle: state.pressBundle ? stripForbiddenFields(state.pressBundle) : null,
    llmDegraded: Boolean(state.llmDegraded),
  };
};
