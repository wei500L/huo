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
  const currentScreenId = useScreenStore((state) => state.current.id);
  const pushScreen = useScreenStore((state) => state.push);
  const pushToast = useGameStore((state) => state.pushToast);

  const isDisabled = snapshot?.status !== "active" || dimmed;

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
        onClick: () => pushScreen("office"),
      },
      {
        variant: "orange" as const,
        icon: "trending-up" as const,
        label: "项目推进",
        ariaLabel: currentScreenId === "office" ? "处理董事会关系" : undefined,
        hotkey: "3" as const,
        badgeCount: badgeCounts.projectProgress,
        onClick: () => {
          pushToast({ id: "main-action-project-v2-toast", level: "info", message: "v2 即将开放" });
          pushScreen("decision");
        },
      },
      {
        variant: "red" as const,
        icon: "money" as const,
        label: currentScreenId === "office" ? "拉高市场热度" : "财务决策",
        hotkey: "4" as const,
        badgeCount: badgeCounts.financialDecision,
        onClick: () => pushScreen(currentScreenId === "office" ? "press" : "decision"),
      },
    ],
    [
      badgeCounts.companyManagement,
      badgeCounts.employeeCommunication,
      badgeCounts.financialDecision,
      badgeCounts.projectProgress,
      currentScreenId,
      pushScreen,
      pushToast,
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
            ariaLabel={action.ariaLabel}
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
