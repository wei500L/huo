import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import App from "@/App";
import { AppShell } from "@/components/layout/AppShell";
import { useScreenStore } from "@/store/screenStore";

const resetStore = () => {
  useScreenStore.setState({
    current: { id: "onboarding" },
    stack: [],
    hudVisible: true,
    mainBarVisible: true,
  });
};

describe("App shell", () => {
  beforeEach(() => {
    resetStore();
  });

  it("renders HUDBar and MainActionBar by default", () => {
    render(
      <AppShell>
        <div>body</div>
      </AppShell>,
    );

    expect(screen.getByText("HUD")).toBeInTheDocument();
    expect(screen.getByText("MAIN BAR")).toBeInTheDocument();
  });

  it("hides the HUDBar when chrome is disabled", () => {
    render(
      <AppShell>
        <div>body</div>
      </AppShell>,
    );

    act(() => {
      useScreenStore.getState().setChrome({ hud: false });
    });

    expect(screen.queryByText("HUD")).not.toBeInTheDocument();
    expect(screen.getByText("MAIN BAR")).toBeInTheDocument();
  });

  it("switches placeholder screens through the store", () => {
    render(<App />);

    expect(screen.getByText("[Screen: onboarding]")).toBeInTheDocument();

    act(() => {
      useScreenStore.getState().push("company-select");
    });

    expect(screen.getByText("[Screen: company-select]")).toBeInTheDocument();
  });
});
