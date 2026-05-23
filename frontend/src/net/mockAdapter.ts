import {
  createMockDeathReport,
  createMockDecisionAck,
  createMockGossipResult,
  createMockPressAck,
  createMockSettlementBundle,
  createMockSnapshot,
  type MockScenario,
} from "@/mock/fixtures/firstRun";
import { makeEnvelope, type Envelope } from "@/protocol/envelope";
import type {
  CreateGamePayload,
  RequestSnapshotPayload,
  SelectDecisionPayload,
  SettleQuarterPayload,
  SubmitPressPayload,
} from "@/protocol/inbound";
import { useNetworkStore } from "@/store/networkStore";

import type { DataSource, DataSourceStatus } from "./dataSource";
import { dispatch } from "./envelopeBus";

type MessageHandler = (env: Envelope<unknown>) => void;

export interface MockDataSource extends DataSource {
  setScenario: (scenario: MockScenario) => void;
}

export function createMockDataSource(): MockDataSource {
  return new MockAdapter();
}

class MockAdapter implements MockDataSource {
  public status: DataSourceStatus = "idle";

  private readonly listeners = new Set<MessageHandler>();
  private readonly timers = new Set<ReturnType<typeof setTimeout>>();
  private scenario: MockScenario = "happy";
  private playerId = "mock-player";
  private latestSnapshot = createMockSnapshot();

  public async connect(playerId: string, _sessionId?: string): Promise<void> {
    this.playerId = playerId;
    this.latestSnapshot = createMockSnapshot({ playerId });
    this.setStatus("open");
  }

  public disconnect(): void {
    this.clearTimers();
    this.setStatus("closed");
  }

  public async send<T>(envelope: Envelope<T>): Promise<void> {
    if (this.status !== "open") {
      throw new Error("[mockAdapter] cannot send while data source is not open");
    }

    switch (envelope.type) {
      case "create_game":
        this.handleCreateGame(envelope as Envelope<CreateGamePayload>);
        break;
      case "select_decision":
        this.handleSelectDecision(envelope as Envelope<SelectDecisionPayload>);
        break;
      case "collect_gossip":
        this.emit("gossip_result", createMockGossipResult(), envelope.id);
        break;
      case "submit_press":
        this.handleSubmitPress(envelope as Envelope<SubmitPressPayload>);
        break;
      case "settle_quarter":
        this.handleSettleQuarter(envelope as Envelope<SettleQuarterPayload>);
        break;
      case "request_snapshot":
        this.handleRequestSnapshot(envelope as Envelope<RequestSnapshotPayload>);
        break;
      case "ping":
        this.emit("pong", { receivedAt: new Date().toISOString() }, envelope.id);
        break;
      default:
        this.emit(
          "error",
          { code: "mock_unknown_inbound", message: `Unsupported mock inbound: ${envelope.type}`, retryable: false },
          envelope.id,
        );
    }
  }

  public onMessage(cb: MessageHandler): void {
    this.listeners.add(cb);
  }

  public setScenario(scenario: MockScenario): void {
    this.scenario = scenario;
  }

  private handleCreateGame(envelope: Envelope<CreateGamePayload>): void {
    this.latestSnapshot = createMockSnapshot({
      playerId: envelope.payload.playerId ?? this.playerId,
    });
    this.emit("game_snapshot", this.latestSnapshot, envelope.id);
  }

  private handleSelectDecision(envelope: Envelope<SelectDecisionPayload>): void {
    const ack = createMockDecisionAck(envelope.payload.cardId);
    this.latestSnapshot = {
      ...this.latestSnapshot,
      stats: ack.immediateStats,
      quarter: {
        ...this.latestSnapshot.quarter,
        phase: ack.nextPhase,
        selectedDecisionId: ack.cardId,
      },
    };
    this.emit("decision_ack", ack, envelope.id);
  }

  private handleSubmitPress(envelope: Envelope<SubmitPressPayload>): void {
    void envelope;
    this.emit("press_ack", createMockPressAck(), envelope.id);
  }

  private handleSettleQuarter(envelope: Envelope<SettleQuarterPayload>): void {
    const bundle = createMockSettlementBundle(this.scenario);
    this.emit("settlement_bundle", bundle, envelope.id, 1500);
    if (this.scenario === "die-q1") {
      this.emit("death_report_bundle", createMockDeathReport(), envelope.id, 1650);
    }
  }

  private handleRequestSnapshot(envelope: Envelope<RequestSnapshotPayload>): void {
    void envelope;
    this.emit("game_snapshot", this.latestSnapshot, envelope.id);
  }

  private emit<T>(type: string, payload: T, ackFor?: string, delayMs = randomLatencyMs()): void {
    const timer = setTimeout(() => {
      this.timers.delete(timer);
      const outbound = {
        ...makeEnvelope(type, payload, ackFor),
        direction: "outbound" as const,
      };
      dispatch(outbound);
      for (const listener of this.listeners) {
        listener(outbound);
      }
    }, delayMs);

    this.timers.add(timer);
  }

  private setStatus(status: DataSourceStatus): void {
    this.status = status;
    useNetworkStore.getState().setStatus(status);
  }

  private clearTimers(): void {
    for (const timer of this.timers) {
      clearTimeout(timer);
    }
    this.timers.clear();
  }
}

const randomLatencyMs = (): number => 50 + Math.floor(Math.random() * 151);
