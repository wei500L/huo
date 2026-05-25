import type { Envelope } from "@/protocol/envelope";

import { createWebSocketDataSource } from "./wsClient";

export type DataSourceStatus =
  | "idle"
  | "connecting"
  | "open"
  | "reconnecting"
  | "closed"
  | "error";

export interface DataSource {
  connect: (playerId: string, sessionId?: string) => Promise<void>;
  disconnect: () => void;
  send: <T>(envelope: Envelope<T>) => Promise<void>;
  onMessage: (cb: (env: Envelope<unknown>) => void) => void;
  status: DataSourceStatus;
}

export function createDataSource(config: { wsUrl?: string }): DataSource {
  return createWebSocketDataSource(config.wsUrl);
}
