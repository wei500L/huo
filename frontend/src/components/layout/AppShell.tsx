import type { ReactNode } from "react";

import { useScreenStore } from "@/store/screenStore";

import { HUDBar } from "./HUDBar";
import { MainActionBar } from "./MainActionBar";

interface Props {
  children: ReactNode;
}

export const AppShell = ({ children }: Props) => {
  const hudVisible = useScreenStore((state) => state.hudVisible);
  const mainBarVisible = useScreenStore((state) => state.mainBarVisible);

  return (
    <div className="flex min-h-dvh flex-col bg-canvas font-pixel text-ink-1">
      {hudVisible && <HUDBar />}
      <main className="relative flex-1 overflow-hidden">{children}</main>
      {mainBarVisible && <MainActionBar />}
    </div>
  );
};
