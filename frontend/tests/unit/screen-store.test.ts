import { beforeEach, describe, expect, it, vi } from "vitest";

import { useScreenStore } from "@/store/screenStore";

const resetStore = () => {
  useScreenStore.setState({
    current: { id: "onboarding" },
    stack: [],
    hudVisible: true,
    mainBarVisible: true,
  });
};

describe("screen store", () => {
  beforeEach(() => {
    resetStore();
  });

  it("pushes history entries and switches current screen", () => {
    useScreenStore.getState().push("company-select", { from: "onboarding" });

    const state = useScreenStore.getState();
    expect(state.current.id).toBe("company-select");
    expect(state.current.params).toEqual({ from: "onboarding" });
    expect(state.stack).toHaveLength(1);
    expect(state.stack[0].id).toBe("onboarding");
  });

  it("replaces the current screen and clears history", () => {
    useScreenStore.getState().push("company-select");
    useScreenStore.getState().replace("office", { seed: 1 });

    const state = useScreenStore.getState();
    expect(state.current.id).toBe("office");
    expect(state.current.params).toEqual({ seed: 1 });
    expect(state.stack).toHaveLength(0);
  });

  it("backs up one entry without throwing on empty history", () => {
    useScreenStore.getState().back();
    expect(useScreenStore.getState().current.id).toBe("onboarding");

    useScreenStore.getState().push("company-select");
    useScreenStore.getState().push("office");
    useScreenStore.getState().back();

    const state = useScreenStore.getState();
    expect(state.current.id).toBe("company-select");
    expect(state.stack).toHaveLength(1);
  });

  it("updates only the requested chrome flags", () => {
    useScreenStore.getState().setChrome({ hud: false });
    expect(useScreenStore.getState().hudVisible).toBe(false);
    expect(useScreenStore.getState().mainBarVisible).toBe(true);

    useScreenStore.getState().setChrome({ mainBar: false });
    expect(useScreenStore.getState().hudVisible).toBe(false);
    expect(useScreenStore.getState().mainBarVisible).toBe(false);
  });

  it("caps history at 20 entries and warns", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);

    for (let index = 0; index < 21; index += 1) {
      useScreenStore.getState().push(index % 2 === 0 ? "company-select" : "office");
    }

    expect(useScreenStore.getState().stack).toHaveLength(20);
    expect(warnSpy).toHaveBeenCalled();
    warnSpy.mockRestore();
  });
});
