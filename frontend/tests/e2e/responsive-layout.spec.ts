import { expect, test, type Page } from "@playwright/test";

const VIEWPORTS = [
  { width: 375, height: 900 },
  { width: 768, height: 1024 },
  { width: 1280, height: 900 },
  { width: 1920, height: 1080 },
];

const assertNoHorizontalOverflow = async (page: Page) => {
  const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(hasOverflow).toBeFalsy();
};

const reachOffice = async (page: Page) => {
  await page.goto("/");
  await page.getByRole("button", { name: "开始任职" }).click();
  await page.getByRole("button", { name: /灵眸科技/ }).click();
  await page.getByRole("button", { name: "开始这一局" }).click();
  await expect(page.getByRole("button", { name: "公司管理" })).toBeVisible();
};

test.describe("responsive layout", () => {
  for (const viewport of VIEWPORTS) {
    test(`overview and stats fit at ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await reachOffice(page);

      await page.getByRole("button", { name: "公司管理" }).click();
      await expect(page.getByText("公司经营总览")).toBeVisible();
      await expect(page.getByRole("button", { name: "稳住现金流" })).toBeVisible();
      await expect(page.getByRole("button", { name: "处理董事会关系" })).toBeVisible();
      await expect(page.getByRole("button", { name: "拉高市场热度" })).toBeVisible();
      await assertNoHorizontalOverflow(page);

      await page.getByRole("button", { name: "设置" }).click();
      await expect(page.getByText("六大核心数据")).toBeVisible();
      await expect(page.getByRole("button", { name: "查看详细分析" })).toBeVisible();
      await assertNoHorizontalOverflow(page);
    });

    test(`decision and press remain usable at ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await reachOffice(page);

      await page.getByRole("button", { name: "处理董事会关系" }).click();
      await expect(page.getByText("Q1 季度决策")).toBeVisible();
      await page.getByRole("button", { name: /融资续命/ }).click();
      await expect(page.getByText("预计即时变化")).toBeVisible();
      await assertNoHorizontalOverflow(page);

      await page.getByRole("button", { name: "确认决策" }).click();
      await expect(page.getByText(/季度结算|发布会输入屏/)).toBeVisible();

      await page.goto("/");
      await reachOffice(page);
      await page.getByRole("button", { name: "拉高市场热度" }).click();
      await expect(page.getByText("发布会输入屏")).toBeVisible();
      await expect(page.getByRole("button", { name: "发言完毕" })).toBeVisible();
      await assertNoHorizontalOverflow(page);
    });

    test(`gossip scene scales at ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await reachOffice(page);

      await page.getByRole("button", { name: "跳下一屏" }).click();
      await expect(page.getByText("茶水间 TEA ROOM")).toBeVisible();
      await assertNoHorizontalOverflow(page);
    });
  }
});
