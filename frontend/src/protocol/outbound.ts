import type {
  DeathReportBundleDTO,
  DecisionAckDTO,
  ErrorOutboundDTO,
  GameSnapshotDTO,
  GossipResultDTO,
  PressAckDTO,
  SettlementBundleDTO,
  ToastDTO,
} from "./types";

export type OutboundType =
  | "game_snapshot"
  | "decision_ack"
  | "gossip_result"
  | "press_ack"
  | "settlement_bundle"
  | "death_report_bundle"
  | "toast"
  | "error"
  | "pong";

export type OutboundPayload =
  | { type: "game_snapshot"; data: GameSnapshotDTO }
  | { type: "decision_ack"; data: DecisionAckDTO }
  | { type: "gossip_result"; data: GossipResultDTO }
  | { type: "press_ack"; data: PressAckDTO }
  | { type: "settlement_bundle"; data: SettlementBundleDTO }
  | { type: "death_report_bundle"; data: DeathReportBundleDTO }
  | { type: "toast"; data: ToastDTO }
  | { type: "error"; data: ErrorOutboundDTO };
