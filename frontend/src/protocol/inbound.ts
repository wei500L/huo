import type { GossipScene, PressType } from "./types";

export type InboundType =
  | "create_game"
  | "select_decision"
  | "state_transition"
  | "draw_decisions"
  | "collect_gossip"
  | "submit_press"
  | "settle_quarter"
  | "request_snapshot"
  | "ping";

export interface CreateGamePayload {
  playerId?: string;
  requestLegacies: boolean;
  companyTemplateId?: string;
}

export interface StateTransitionPayload {
  sessionId: string;
  targetPhase: "GOSSIP" | "DECISION" | "PRESS" | "SETTLEMENT" | "DONE";
}

export interface DrawDecisionsPayload {
  sessionId: string;
  quarterNumber: number;
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
  | StateTransitionPayload
  | DrawDecisionsPayload
  | SelectDecisionPayload
  | CollectGossipPayload
  | SubmitPressPayload
  | SettleQuarterPayload
  | RequestSnapshotPayload
  | PingPayload;
