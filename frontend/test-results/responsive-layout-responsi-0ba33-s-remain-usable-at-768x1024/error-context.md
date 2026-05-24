# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> decision and press remain usable at 768x1024
- Location: tests/e2e/responsive-layout.spec.ts:42:9

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: '处理董事会关系' })

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - generic [ref=e5]: HUD
    - generic [ref=e6]:
      - generic [ref=e8]: YES,BOSS!
      - img [ref=e10]
    - article [ref=e13]:
      - img "calendar" [ref=e15]:
        - img [ref=e16]
      - generic [ref=e18]:
        - generic [ref=e19]: 第1天 09:15
        - generic [ref=e20]: 周一 2025/05/26
    - generic [ref=e21]:
      - article [ref=e23]:
        - generic [ref=e24]:
          - generic [ref=e25]:
            - img [ref=e27]:
              - img [ref=e28]
            - generic [ref=e30]: 现金流
          - generic [ref=e32]: ¥70
          - generic [ref=e34]: "-"
      - article [ref=e36]:
        - generic [ref=e37]:
          - generic [ref=e38]:
            - img [ref=e40]:
              - img [ref=e41]
            - generic [ref=e43]: 士气
          - generic [ref=e45]: "55"
          - generic [ref=e47]: "-"
      - article [ref=e49]:
        - generic [ref=e50]:
          - generic [ref=e51]:
            - img [ref=e53]:
              - img [ref=e54]
            - generic [ref=e56]: 董事会
          - generic [ref=e58]: "50"
          - generic [ref=e60]: "-"
      - article [ref=e62]:
        - generic [ref=e63]:
          - generic [ref=e64]:
            - img [ref=e66]:
              - img [ref=e67]
            - generic [ref=e69]: 面子
          - generic [ref=e71]: "40"
          - generic [ref=e73]: "-"
    - generic [ref=e74]:
      - generic [ref=e75]:
        - img "users" [ref=e76]:
          - img [ref=e77]
        - generic [ref=e79]: 112/20
      - button "Open stats dashboard" [ref=e80] [cursor=pointer]:
        - img "settings" [ref=e81]:
          - img [ref=e82]
  - main [ref=e85]:
    - generic [ref=e86]:
      - generic [ref=e87]: "[Screen: office]"
      - button "跳下一屏" [ref=e88] [cursor=pointer]
  - contentinfo [ref=e89]:
    - generic [ref=e90]: MAIN BAR
    - generic [ref=e92]:
      - img [ref=e96]
      - paragraph [ref=e100]: "TODO: 先听风向，再定动作。"
    - generic [ref=e101]:
      - button "公司管理" [ref=e102] [cursor=pointer]:
        - img [ref=e104]:
          - img [ref=e105]
        - generic [ref=e107]: 公司管理
      - button "员工沟通" [ref=e108] [cursor=pointer]:
        - img [ref=e110]:
          - img [ref=e111]
        - generic [ref=e113]: 员工沟通
      - button "项目推进" [ref=e114] [cursor=pointer]:
        - img [ref=e116]:
          - img [ref=e117]
        - generic [ref=e119]: 项目推进
      - button "财务决策" [ref=e120] [cursor=pointer]:
        - img [ref=e122]:
          - img [ref=e123]
        - generic [ref=e125]: 财务决策
```

# Test source

```ts
  1  | import { expect, test, type Page } from "@playwright/test";
  2  | 
  3  | const VIEWPORTS = [
  4  |   { width: 375, height: 900 },
  5  |   { width: 768, height: 1024 },
  6  |   { width: 1280, height: 900 },
  7  |   { width: 1920, height: 1080 },
  8  | ];
  9  | 
  10 | const assertNoHorizontalOverflow = async (page: Page) => {
  11 |   const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  12 |   expect(hasOverflow).toBeFalsy();
  13 | };
  14 | 
  15 | const reachOffice = async (page: Page) => {
  16 |   await page.goto("/");
  17 |   await page.getByRole("button", { name: "开始任职" }).click();
  18 |   await page.getByRole("button", { name: /灵眸科技/ }).click();
  19 |   await page.getByRole("button", { name: "开始这一局" }).click();
  20 |   await expect(page.getByRole("button", { name: "公司管理" })).toBeVisible();
  21 | };
  22 | 
  23 | test.describe("responsive layout", () => {
  24 |   for (const viewport of VIEWPORTS) {
  25 |     test(`overview and stats fit at ${viewport.width}x${viewport.height}`, async ({ page }) => {
  26 |       await page.setViewportSize(viewport);
  27 |       await reachOffice(page);
  28 | 
  29 |       await page.getByRole("button", { name: "公司管理" }).click();
  30 |       await expect(page.getByText("公司经营总览")).toBeVisible();
  31 |       await expect(page.getByRole("button", { name: "稳住现金流" })).toBeVisible();
  32 |       await expect(page.getByRole("button", { name: "处理董事会关系" })).toBeVisible();
  33 |       await expect(page.getByRole("button", { name: "拉高市场热度" })).toBeVisible();
  34 |       await assertNoHorizontalOverflow(page);
  35 | 
  36 |       await page.getByRole("button", { name: "设置" }).click();
  37 |       await expect(page.getByText("六大核心数据")).toBeVisible();
  38 |       await expect(page.getByRole("button", { name: "查看详细分析" })).toBeVisible();
  39 |       await assertNoHorizontalOverflow(page);
  40 |     });
  41 | 
  42 |     test(`decision and press remain usable at ${viewport.width}x${viewport.height}`, async ({ page }) => {
  43 |       await page.setViewportSize(viewport);
  44 |       await reachOffice(page);
  45 | 
> 46 |       await page.getByRole("button", { name: "处理董事会关系" }).click();
     |                                                           ^ Error: locator.click: Test timeout of 30000ms exceeded.
  47 |       await expect(page.getByText("Q1 季度决策")).toBeVisible();
  48 |       await page.getByRole("button", { name: /融资续命/ }).click();
  49 |       await expect(page.getByText("预计即时变化")).toBeVisible();
  50 |       await assertNoHorizontalOverflow(page);
  51 | 
  52 |       await page.getByRole("button", { name: "确认决策" }).click();
  53 |       await expect(page.getByText(/季度结算|发布会输入屏/)).toBeVisible();
  54 | 
  55 |       await page.goto("/");
  56 |       await reachOffice(page);
  57 |       await page.getByRole("button", { name: "拉高市场热度" }).click();
  58 |       await expect(page.getByText("发布会输入屏")).toBeVisible();
  59 |       await expect(page.getByRole("button", { name: "发言完毕" })).toBeVisible();
  60 |       await assertNoHorizontalOverflow(page);
  61 |     });
  62 | 
  63 |     test(`gossip scene scales at ${viewport.width}x${viewport.height}`, async ({ page }) => {
  64 |       await page.setViewportSize(viewport);
  65 |       await reachOffice(page);
  66 | 
  67 |       await page.getByRole("button", { name: "跳下一屏" }).click();
  68 |       await expect(page.getByText("茶水间 TEA ROOM")).toBeVisible();
  69 |       await assertNoHorizontalOverflow(page);
  70 |     });
  71 |   }
  72 | });
  73 | 
```