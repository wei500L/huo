import { useGameStore } from "@/store/gameStore";
import { useNetworkStore } from "@/store/networkStore";

import type { Envelope } from "@/protocol/envelope";
import type {
  DeathReportBundleDTO,
  DecisionAckDTO,
  ErrorOutboundDTO,
  GameSnapshotDTO,
  GossipResultDTO,
  PressAckDTO,
  SettlementBundleDTO,
  ToastDTO,
} from "@/protocol/types";

export function dispatch(env: Envelope<unknown>) {
  switch (env.type) {
    case "game_snapshot":
      useGameStore.getState().ingestSnapshot(env.payload as GameSnapshotDTO);
      break;
    case "decision_ack":
      useGameStore.getState().ingestDecisionAck(env.payload as DecisionAckDTO);
      break;
    case "gossip_result":
      useGameStore.getState().ingestGossipResult(env.payload as GossipResultDTO);
      break;
    case "press_ack":
      useGameStore.getState().ingestPressAck(env.payload as PressAckDTO);
      break;
    case "settlement_bundle": {
      const bundle = env.payload as SettlementBundleDTO;
      useGameStore.getState().ingestSettlementBundle(bundle);
      useGameStore.getState().setLLMDegraded(bundle.llmDegraded);
      break;
    }
    case "death_report_bundle":
      useGameStore.getState().ingestDeathBundle(env.payload as DeathReportBundleDTO);
      break;
    case "toast":
      useGameStore.getState().pushToast(env.payload as ToastDTO);
      break;
    case "error": {
      const error = env.payload as ErrorOutboundDTO;
      useGameStore.getState().pushToast({
        level: "error",
        message: error.message,
      });
      useNetworkStore.getState().setError(error.code);
      break;
    }
    case "pong":
      break;
    default:
      console.warn("[envelopeBus] unknown type", env.type);
  }
}
