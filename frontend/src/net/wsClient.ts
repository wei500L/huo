import { makeEnvelope, type Envelope } from "@/protocol/envelope";
import { useNetworkStore } from "@/store/networkStore";

import type { DataSource, DataSourceStatus } from "./dataSource";
import { dispatch } from "./envelopeBus";

type MessageHandler = (env: Envelope<unknown>) => void;

const HEARTBEAT_MS = 30_000;
const STALE_MS = 60_000;
const RECONNECT_BACKOFF_MS = [500, 1_000, 2_000, 5_000, 10_000] as const;

export function createWebSocketDataSource(wsUrl = "/api/v1/ws"): DataSource {
  return new WsClient(wsUrl);
}

class WsClient implements DataSource {
  public status: DataSourceStatus = "idle";

  private socket: WebSocket | null = null;
  private readonly listeners = new Set<MessageHandler>();
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private manuallyClosed = false;
  private playerId: string | null = null;
  private sessionId: string | undefined;
  private lastInboundAt = 0;
  private readonly wsUrl: string;

  public constructor(wsUrl: string) {
    this.wsUrl = wsUrl.replace(/\/$/, "");
  }

  public async connect(playerId: string, sessionId?: string): Promise<void> {
    this.playerId = playerId;
    this.sessionId = sessionId;
    this.manuallyClosed = false;
    this.reconnectAttempts = 0;
    this.openSocket("connecting");
  }

  public disconnect(): void {
    this.manuallyClosed = true;
    this.clearHeartbeat();
    this.clearReconnect();
    this.socket?.close();
    this.socket = null;
    this.setStatus("closed");
  }

  public async send<T>(envelope: Envelope<T>): Promise<void> {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("[wsClient] cannot send while WebSocket is not open");
    }

    this.socket.send(JSON.stringify(envelope));
  }

  public onMessage(cb: MessageHandler): void {
    this.listeners.add(cb);
  }

  private openSocket(status: DataSourceStatus): void {
    if (!this.playerId) {
      throw new Error("[wsClient] playerId is required before opening a socket");
    }

    this.clearHeartbeat();
    this.clearReconnect();
    this.setStatus(status);

    const query = this.sessionId ? `?session_id=${encodeURIComponent(this.sessionId)}` : "";
    const url = `${this.wsUrl}/${encodeURIComponent(this.playerId)}${query}`;
    const socket = new WebSocket(url);
    this.socket = socket;

    socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.lastInboundAt = Date.now();
      this.setStatus("open");
      this.startHeartbeat();
    };

    socket.onmessage = (event) => {
      this.lastInboundAt = Date.now();
      const envelope = parseEnvelope(event.data);
      if (!envelope) {
        useNetworkStore.getState().setError("invalid_envelope");
        return;
      }

      dispatch(envelope);
      for (const listener of this.listeners) {
        listener(envelope);
      }
    };

    socket.onerror = () => {
      useNetworkStore.getState().setError("websocket_error");
    };

    socket.onclose = () => {
      if (this.socket === socket) {
        this.socket = null;
      }
      this.clearHeartbeat();

      if (this.manuallyClosed) {
        this.setStatus("closed");
        return;
      }

      this.setStatus("closed");
      this.scheduleReconnect();
    };
  }

  private startHeartbeat(): void {
    this.clearHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
        return;
      }

      if (Date.now() - this.lastInboundAt >= STALE_MS) {
        this.socket.close();
        return;
      }

      const ping = makeEnvelope("ping", { sentAt: new Date().toISOString() });
      this.socket.send(JSON.stringify(ping));
    }, HEARTBEAT_MS);
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= RECONNECT_BACKOFF_MS.length) {
      this.setStatus("error");
      useNetworkStore.getState().setError("websocket_reconnect_failed");
      return;
    }

    const delayMs = RECONNECT_BACKOFF_MS[this.reconnectAttempts];
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts += 1;
      this.openSocket("reconnecting");
    }, delayMs);
  }

  private setStatus(status: DataSourceStatus): void {
    this.status = status;
    useNetworkStore.getState().setStatus(status);
  }

  private clearHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private clearReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

function parseEnvelope(data: unknown): Envelope<unknown> | null {
  if (typeof data !== "string") {
    return null;
  }

  try {
    const parsed = JSON.parse(data) as unknown;
    if (!isEnvelopeLike(parsed)) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function isEnvelopeLike(value: unknown): value is Envelope<unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    "v" in value &&
    "id" in value &&
    "ts" in value &&
    "direction" in value &&
    "type" in value &&
    "payload" in value
  );
}
