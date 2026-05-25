import { makeEnvelope } from "@/protocol/envelope";
import type {
  CollectGossipPayload,
  CreateGamePayload,
  DrawDecisionsPayload,
  RequestSnapshotPayload,
  SelectDecisionPayload,
  SettleQuarterPayload,
  StateTransitionPayload,
  SubmitPressPayload,
} from "@/protocol/inbound";
import type { CompanyTemplateDTO, MetaSummaryDTO, PressTypeDTO } from "@/protocol/types";

import { createDataSource, type DataSource } from "./dataSource";

const PLAYER_ID_STORAGE_KEY = "yb_v2_player_id";

let dataSource: DataSource | null = null;
let connectedKey: string | null = null;

const RESPONSE_TIMEOUT_MS = 10_000;

type PendingResponse = {
  expectedTypes: Set<string>;
  resolve: () => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

const pendingResponses = new Map<string, PendingResponse>();

const readEnv = (key: string): string | undefined => {
  const viteValue = import.meta.env[key];
  if (typeof viteValue === "string" && viteValue.trim()) {
    return viteValue.trim();
  }
  if (typeof process !== "undefined") {
    const nodeValue = process.env[key];
    return nodeValue?.trim() || undefined;
  }
  return undefined;
};

const trimSlash = (value: string): string => value.replace(/\/$/, "");

const apiBaseUrl = (): string => {
  const value = readEnv("VITE_API_BASE_URL");
  if (value) {
    return trimSlash(value);
  }
  throw new Error("missing VITE_API_BASE_URL");
};

const wsBaseUrl = (): string | undefined => {
  const explicit = readEnv("VITE_WS_BASE_URL");
  if (explicit) {
    return trimSlash(explicit);
  }
  const apiBase = readEnv("VITE_API_BASE_URL");
  if (!apiBase) {
    throw new Error("missing VITE_WS_BASE_URL or VITE_API_BASE_URL");
  }
  return `${trimSlash(apiBase).replace(/^http:/, "ws:").replace(/^https:/, "wss:")}/api/v1/ws`;
};

export const getPlayerId = (): string => {
  try {
    const stored = globalThis.localStorage?.getItem(PLAYER_ID_STORAGE_KEY);
    if (stored) {
      return stored;
    }
    const generated = globalThis.crypto?.randomUUID?.() ?? `player_${Date.now()}`;
    globalThis.localStorage?.setItem(PLAYER_ID_STORAGE_KEY, generated);
    return generated;
  } catch {
    return globalThis.crypto?.randomUUID?.() ?? `player_${Date.now()}`;
  }
};

const getDataSource = (): DataSource => {
  if (!dataSource) {
    dataSource = createDataSource({ wsUrl: wsBaseUrl() });
    dataSource.onMessage((env) => {
      if (!env.ackFor) {
        return;
      }

      const pending = pendingResponses.get(env.ackFor);
      if (!pending) {
        return;
      }

      if (env.type === "error") {
        const message =
          typeof env.payload === "object" && env.payload !== null && "message" in env.payload
            ? String((env.payload as { message: unknown }).message)
            : "backend_error";
        clearTimeout(pending.timer);
        pendingResponses.delete(env.ackFor);
        pending.reject(new Error(message));
        return;
      }

      if (!pending.expectedTypes.has(env.type)) {
        return;
      }

      clearTimeout(pending.timer);
      pendingResponses.delete(env.ackFor);
      pending.resolve();
    });
    connectedKey = null;
  }
  return dataSource;
};

export const connectGameClient = async (sessionId?: string): Promise<void> => {
  const source = getDataSource();
  const playerId = getPlayerId();
  const key = `${playerId}:${sessionId ?? ""}`;
  if (source.status === "open" && connectedKey === key) {
    return;
  }
  await source.connect(playerId, sessionId);
  connectedKey = key;
};

export const sendGameMessage = async <T>(
  type: string,
  payload: T,
  sessionId?: string,
  waitForTypes: string[] = [],
): Promise<void> => {
  await connectGameClient(sessionId);
  const envelope = makeEnvelope(type, payload);
  const waitForResponse =
    waitForTypes.length > 0
      ? new Promise<void>((resolve, reject) => {
          const timer = setTimeout(() => {
            pendingResponses.delete(envelope.id);
            reject(new Error(`${type}_response_timeout`));
          }, RESPONSE_TIMEOUT_MS);

          pendingResponses.set(envelope.id, {
            expectedTypes: new Set(waitForTypes),
            resolve,
            reject,
            timer,
          });
        })
      : null;

  try {
    await getDataSource().send(envelope);
    await waitForResponse;
  } catch (error) {
    const pending = pendingResponses.get(envelope.id);
    if (pending) {
      clearTimeout(pending.timer);
      pendingResponses.delete(envelope.id);
    }
    throw error;
  }
};

export const loadCompanyTemplates = async (): Promise<CompanyTemplateDTO[]> => {
  const response = await fetch(`${apiBaseUrl()}/api/v1/company-templates`);
  if (!response.ok) {
    throw new Error(`company_templates_${response.status}`);
  }
  return (await response.json()) as CompanyTemplateDTO[];
};

export const loadPressTypes = async (): Promise<PressTypeDTO[]> => {
  const response = await fetch(`${apiBaseUrl()}/api/v1/press-types`);
  if (!response.ok) {
    throw new Error(`press_types_${response.status}`);
  }
  return (await response.json()) as PressTypeDTO[];
};

export const loadPlayerMeta = async (): Promise<MetaSummaryDTO> => {
  const response = await fetch(`${apiBaseUrl()}/api/v1/players/${encodeURIComponent(getPlayerId())}/meta`);
  if (!response.ok) {
    throw new Error(`player_meta_${response.status}`);
  }
  return (await response.json()) as MetaSummaryDTO;
};

export const createGame = (companyTemplateId?: string): Promise<void> => {
  const payload: CreateGamePayload = {
    playerId: getPlayerId(),
    requestLegacies: true,
    companyTemplateId,
  };
  return sendGameMessage("create_game", payload, undefined, ["game_snapshot"]);
};

export const transitionState = (sessionId: string, targetPhase: StateTransitionPayload["targetPhase"]): Promise<void> =>
  sendGameMessage("state_transition", { sessionId, targetPhase } satisfies StateTransitionPayload, sessionId, [
    "game_snapshot",
  ]);

export const drawDecisions = (sessionId: string, quarterNumber: number): Promise<void> =>
  sendGameMessage("draw_decisions", { sessionId, quarterNumber } satisfies DrawDecisionsPayload, sessionId, [
    "game_snapshot",
  ]);

export const collectGossip = (payload: CollectGossipPayload): Promise<void> =>
  sendGameMessage("collect_gossip", payload, payload.sessionId);

export const selectDecision = (payload: SelectDecisionPayload): Promise<void> =>
  sendGameMessage("select_decision", payload, payload.sessionId);

export const submitPress = (payload: SubmitPressPayload): Promise<void> =>
  sendGameMessage("submit_press", payload, payload.sessionId);

export const settleQuarter = (payload: SettleQuarterPayload): Promise<void> =>
  sendGameMessage("settle_quarter", payload, payload.sessionId);

export const requestSnapshot = (sessionId: string): Promise<void> =>
  sendGameMessage("request_snapshot", { sessionId } satisfies RequestSnapshotPayload, sessionId, ["game_snapshot"]);
