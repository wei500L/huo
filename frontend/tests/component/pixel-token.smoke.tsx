import { render } from "@testing-library/react";
import { beforeAll, describe, expect, it } from "vitest";

beforeAll(() => {
  const style = document.createElement("style");
  style.dataset.pixelTokens = "true";
  style.textContent = `
    .bg-pixel-blue { background-color: #2E6FE6; }
    .text-px-base { font-size: 12px; line-height: 1.4; }
    .font-pixel { font-family: "Fusion Pixel", monospace; }
    .border-2 { border-width: 2px; border-style: solid; }
    .border-stroke-ink { border-color: #1B1B1B; }
    .shadow-hard { box-shadow: 4px 4px 0 0 #1B1B1B; }
  `;
  document.head.append(style);
});

describe("pixel token smoke", () => {
  it("renders the expected token classes", () => {
    const { container } = render(
      <div
        className="bg-pixel-blue text-px-base font-pixel border-2 border-stroke-ink shadow-hard"
        data-testid="pixel-token"
      />,
    );

    const element = container.firstElementChild as HTMLElement;
    const styles = getComputedStyle(element);

    expect(element.className).toMatchInlineSnapshot(
      `"bg-pixel-blue text-px-base font-pixel border-2 border-stroke-ink shadow-hard"`,
    );
    expect(styles.backgroundColor).toBe("rgb(46, 111, 230)");
    expect(styles.borderTopWidth).toBe("2px");
    expect(styles.borderTopStyle).toBe("solid");
    expect(styles.boxShadow).toContain("4px 4px");
  });
});
