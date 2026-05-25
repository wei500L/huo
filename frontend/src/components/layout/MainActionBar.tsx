import { useEffect, useMemo } from "react";
import { shallow } from "zustand/shallow";

import { useGameStore } from "@/store/gameStore";
import {
  selectCurrentSnapshot,
  selectMainActionBarBadgeCounts,
  selectMainActionBarContextHint,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { ContextHint } from "./contextHint/ContextHint";
import { MainActionButton } from "./MainActionButton";

export interface MainActionBarProps {
  dimmed?: boolean;
}

const isEditableTarget = (target: EventTarget | null): boolean => {
  if (!(target instanceof HTMLElement)) {
    return false;
  }

  return target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target.isContentEditable;
};

export const MainActionBar = ({ dimmed = false }: MainActionBarProps) => {
  const snapshot = useGameStore(selectCurrentSnapshot);
  const badgeCounts = useGameStore(selectMainActionBarBadgeCounts, shallow);
  const contextHint = useGameStore(selectMainActionBarContextHint, shallow);
  const pushScreen = useScreenStore((state) => state.push);

  const isDisabled = snapshot?.status !== "active" || dimmed;
  const phase = snapshot?.quarter.phase;
  const phaseScreen =
    phase === "GOSSIP"
      ? "gossip"
      : phase === "DECISION"
        ? "decision"
        : phase === "PRESS"
          ? "press"
          : phase === "SETTLEMENT" || phase === "DONE"
            ? "settlement"
            : "office";

  const actions = useMemo(
    () => [
      {
        variant: "blue" as const,
        icon: "briefcase" as const,
        label: "公司管理",
        hotkey: "1" as const,
        badgeCount: badgeCounts.companyManagement,
        onClick: () => pushScreen("overview"),
      },
      {
        variant: "green" as const,
        icon: "users" as const,
        label: "员工沟通",
        hotkey: "2" as const,
        badgeCount: badgeCounts.employeeCommunication,
        onClick: () => pushScreen(phase === "GOSSIP" ? "gossip" : "office"),
      },
      {
        variant: "orange" as const,
        icon: "trending-up" as const,
        label: "当前阶段",
        hotkey: "3" as const,
        badgeCount: badgeCounts.projectProgress,
        onClick: () => pushScreen(phaseScreen),
      },
      {
        variant: "red" as const,
        icon: "money" as const,
        label: "决策/发布会",
        hotkey: "4" as const,
        badgeCount: badgeCounts.financialDecision,
        onClick: () => pushScreen(phase === "DECISION" || phase === "PRESS" ? phaseScreen : "office"),
      },
    ],
    [
      badgeCounts.companyManagement,
      badgeCounts.employeeCommunication,
      badgeCounts.financialDecision,
      badgeCounts.projectProgress,
      phase,
      phaseScreen,
      pushScreen,
    ],
  );

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (isDisabled || event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }

      if (isEditableTarget(event.target)) {
        return;
      }

      const action = actions[Number.parseInt(event.key, 10) - 1];
      if (!action) {
        return;
      }

      event.preventDefault();
      action.onClick();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [actions, isDisabled]);

  return (
    <footer
      className={[
        "flex flex-col gap-3 overflow-hidden border-t-2 border-stroke-ink bg-canvas px-3 py-3 sm:px-4",
        "lg:h-[88px] lg:flex-row lg:items-center lg:py-0",
        dimmed ? "bg-panel-dim opacity-70 grayscale" : "",
      ].join(" ")}
    >
      <span className="sr-only">MAIN BAR</span>

      {contextHint.text ? (
        <div className="shrink-0">
          <ContextHint speaker={contextHint.speaker} text={contextHint.text} />
        </div>
      ) : null}

      <div className="grid min-w-0 flex-1 grid-cols-2 gap-3 lg:flex lg:grid-cols-none">
        {actions.map((action) => (
          <MainActionButton
            key={action.label}
            badgeCount={action.badgeCount}
            disabled={isDisabled}
            icon={action.icon}
            hotkey={action.hotkey}
            label={action.label}
            variant={action.variant}
            onClick={action.onClick}
          />
        ))}
      </div>
    </footer>
  );
};
