import type { GossipScene, PressType } from "./types";

export type InboundType =
  | "create_game"
  | "select_decision"
  | "collect_gossip"
  | "submit_press"
  | "settle_quarter"
  | "request_snapshot"
  | "ping";

export interface CreateGamePayload {
  playerId?: string;
  requestLegacies: boolean;
}

export interface SelectDecisionPayload {
  sessionId: string;
  quarterNumber: number;
  cardId: string;
}

export interface CollectGossipPayload {
  sessionId: string;
  quarterNumber: number;
  scene: GossipScene;
}

export interface SubmitPressPayload {
  sessionId: string;
  quarterNumber: 3;
  pressType: PressType;
  transcript: string;
  durationS?: number;
}

export interface SettleQuarterPayload {
  sessionId: string;
  quarterNumber: number;
}

export interface RequestSnapshotPayload {
  sessionId: string;
}

export interface PingPayload {
  sentAt: string;
}

export type InboundPayload =
  | CreateGamePayload
  | SelectDecisionPayload
  | CollectGossipPayload
  | SubmitPressPayload
  | SettleQuarterPayload
  | RequestSnapshotPayload
  | PingPayload;
