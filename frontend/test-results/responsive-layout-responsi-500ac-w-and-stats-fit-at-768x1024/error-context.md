# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> overview and stats fit at 768x1024
- Location: tests/e2e/responsive-layout.spec.ts:25:9

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: '处理董事会关系' })
Expected: visible
Error: strict mode violation: getByRole('button', { name: '处理董事会关系' }) resolved to 2 elements:
    1) <button type="button" class="flex min-h-[88px] w-full items-start justify-between gap-3 border-2 border-stroke-ink px-4 py-3 text-left font-pixel text-px-base leading-none shadow-hard transition-transform duration-75 ease-out bg-pixel-blue text-white hover:bg-pixel-blue/90 hover:-translate-y-0.5 active:translate-y-0.5 active:shadow-none">…</button> aka getByRole('button', { name: '处理董事会关系 主动汇报进度 处理董事会关系' })
    2) <button type="button" aria-label="处理董事会关系" class="relative flex min-h-16 min-w-0 flex-1 items-center gap-2 border-2 px-4 pr-9 font-pixel text-px-sm leading-none pixel-render sm:text-px-base lg:h-16 lg:text-px-md transition-transform duration-75 ease-out transition-shadow border-stroke-ink text-white shadow-[4px_4px_0_0_var(--stroke-ink)] hover:-translate-y-0.5 hover:shadow-[6px_6px_0_0_var(--stroke-ink)] active:translate-y-0.5 active:shadow-none bg-pixel-orange">…</button> aka getByRole('button', { name: '处理董事会关系', exact: true })

Call log:
  - Expect "toBeVisible" with timeout 5000ms
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
    - button "设置" [ref=e75] [cursor=pointer]:
      - img "settings" [ref=e76]:
        - img [ref=e77]
  - main [ref=e80]:
    - generic [ref=e83]:
      - complementary [ref=e84]:
        - generic [ref=e85]:
          - heading "公司经营总览" [level=1] [ref=e86]
          - paragraph [ref=e87]: 掌控六大核心指标，带领公司走向盈利与荣耀
        - generic [ref=e88]:
          - img "ceo_male_01 confident" [ref=e92]
          - paragraph [ref=e96]: 这周最危险的是董事会信任下滑...
      - main [ref=e97]:
        - generic [ref=e98]:
          - generic [ref=e99]:
            - generic [ref=e100]: 本周趋势
            - button "查看详细报告" [ref=e102] [cursor=pointer]:
              - img [ref=e104]:
                - img [ref=e105]
              - generic [ref=e107]: 查看详细报告
          - generic [ref=e110]:
            - generic [ref=e111]:
              - img "现金流" [ref=e113]:
                - img [ref=e114]
              - generic [ref=e116]: 现金流
            - generic [ref=e117]:
              - img "士气" [ref=e119]:
                - img [ref=e120]
              - generic [ref=e122]: 士气
            - generic [ref=e123]:
              - img "董事会信任" [ref=e125]:
                - img [ref=e126]
              - generic [ref=e128]: 董事会信任
            - generic [ref=e129]:
              - img "公司体面" [ref=e131]:
                - img [ref=e132]
              - generic [ref=e134]: 公司体面
            - generic [ref=e135]:
              - img "员工人数" [ref=e137]:
                - img [ref=e138]
              - generic [ref=e140]: 员工人数
            - generic [ref=e141]:
              - img "市场热度" [ref=e143]:
                - img [ref=e144]
              - generic [ref=e146]: 市场热度
        - region "六大核心指标" [ref=e150]:
          - generic [ref=e151]:
            - generic [ref=e153]: 现金流
            - generic [ref=e155]:
              - img "现金流" [ref=e157]:
                - img [ref=e158]
              - generic [ref=e160]:
                - generic [ref=e161]: "13"
                - generic [ref=e162]: 健康
          - generic [ref=e166]:
            - generic [ref=e168]: 士气
            - generic [ref=e170]:
              - img "士气" [ref=e172]:
                - img [ref=e173]
              - generic [ref=e175]:
                - generic [ref=e176]: "10"
                - generic [ref=e177]: 中立
          - generic [ref=e181]:
            - generic [ref=e183]: 董事会信任
            - generic [ref=e185]:
              - img "董事会信任" [ref=e187]:
                - img [ref=e188]
              - generic [ref=e190]:
                - generic [ref=e191]: "9"
                - generic [ref=e192]: 观望
          - generic [ref=e196]:
            - generic [ref=e198]: 公司体面
            - generic [ref=e200]:
              - img "公司体面" [ref=e202]:
                - img [ref=e203]
              - generic [ref=e205]:
                - generic [ref=e206]: "7"
                - generic [ref=e207]: 普通
          - generic [ref=e211]:
            - generic [ref=e213]: 员工人数
            - generic [ref=e215]:
              - img "员工人数" [ref=e217]:
                - img [ref=e218]
              - generic [ref=e220]:
                - generic [ref=e221]: "7"
                - generic [ref=e222]: v1 占位
          - generic [ref=e226]:
            - generic [ref=e228]: 市场热度
            - generic [ref=e230]:
              - img "市场热度" [ref=e232]:
                - img [ref=e233]
              - generic [ref=e235]:
                - generic [ref=e236]: "7"
                - generic [ref=e237]: v1 占位
        - generic [ref=e241]:
          - generic [ref=e244]:
            - generic [ref=e245]:
              - img "产品部" [ref=e247]:
                - img [ref=e248]
              - generic [ref=e250]:
                - generic [ref=e251]:
                  - heading "产品部" [level=3] [ref=e252]
                  - generic [ref=e253]: 稳定
                - paragraph [ref=e254]: 节奏正常，需求堆积偏多。
            - generic [ref=e255]:
              - generic [ref=e256]: "建议动作:"
              - paragraph [ref=e257]: 先砍低优先级需求
              - img "建议动作" [ref=e258]:
                - img [ref=e259]
          - generic [ref=e263]:
            - generic [ref=e264]:
              - img "市场部" [ref=e266]:
                - img [ref=e267]
              - generic [ref=e269]:
                - generic [ref=e270]:
                  - heading "市场部" [level=3] [ref=e271]
                  - generic [ref=e272]: 疲态
                - paragraph [ref=e273]: 声量偏弱，曝光还不够。
            - generic [ref=e274]:
              - generic [ref=e275]: "建议动作:"
              - paragraph [ref=e276]: 补一轮外部发声
              - img "建议动作" [ref=e277]:
                - img [ref=e278]
          - generic [ref=e282]:
            - generic [ref=e283]:
              - img "技术部" [ref=e285]:
                - img [ref=e286]
              - generic [ref=e289]:
                - generic [ref=e290]:
                  - heading "技术部" [level=3] [ref=e291]
                  - generic [ref=e292]: 健康
                - paragraph [ref=e293]: 交付稳，核心模块可控。
            - generic [ref=e294]:
              - generic [ref=e295]: "建议动作:"
              - paragraph [ref=e296]: 保持现有排期
              - img "建议动作" [ref=e297]:
                - img [ref=e298]
      - complementary [ref=e300]:
        - generic [ref=e301]:
          - generic [ref=e303]: 本周重点事项
          - generic [ref=e306]:
            - generic [ref=e307]:
              - img "董事会信任持续下滑" [ref=e309]:
                - img [ref=e310]
              - generic [ref=e312]:
                - generic [ref=e313]: 董事会信任持续下滑
                - generic [ref=e314]: 本周沟通频率不足，反馈窗口收窄。
            - generic [ref=e315]:
              - img "市场热度偏低" [ref=e317]:
                - img [ref=e318]
              - generic [ref=e320]:
                - generic [ref=e321]: 市场热度偏低
                - generic [ref=e322]: 外部关注没有跟上内部动作。
            - generic [ref=e323]:
              - img "员工申请加班" [ref=e325]:
                - img [ref=e326]
              - generic [ref=e328]:
                - generic [ref=e329]: 员工申请加班
                - generic [ref=e330]: 内部压力上升，产出波动变大。
            - generic [ref=e331]:
              - img "Q2 项目进度 62%" [ref=e333]:
                - img [ref=e334]
              - generic [ref=e336]:
                - generic [ref=e337]: Q2 项目进度 62%
                - generic [ref=e338]: 进度还在推进，但需要稳住节奏。
        - generic:
          - generic:
            - button "稳住现金流 先守底线 稳住现金流" [ref=e339] [cursor=pointer]:
              - generic [ref=e340]:
                - generic [ref=e341]: 稳住现金流
                - generic [ref=e342]: 先守底线
              - img "稳住现金流" [ref=e344]:
                - img [ref=e345]
            - button "处理董事会关系 主动汇报进度 处理董事会关系" [ref=e347] [cursor=pointer]:
              - generic [ref=e348]:
                - generic [ref=e349]: 处理董事会关系
                - generic [ref=e350]: 主动汇报进度
              - img "处理董事会关系" [ref=e352]:
                - img [ref=e353]
            - button "拉高市场热度 补一轮外部声量 拉高市场热度" [ref=e355] [cursor=pointer]:
              - generic [ref=e356]:
                - generic [ref=e357]: 拉高市场热度
                - generic [ref=e358]: 补一轮外部声量
              - img "拉高市场热度" [ref=e360]:
                - img [ref=e361]
  - contentinfo [ref=e363]:
    - generic [ref=e364]: MAIN BAR
    - generic [ref=e366]:
      - img [ref=e370]
      - paragraph [ref=e374]: "TODO: 先听风向，再定动作。"
    - generic [ref=e375]:
      - button "公司管理" [active] [ref=e376] [cursor=pointer]:
        - img [ref=e378]:
          - img [ref=e379]
        - generic [ref=e381]: 公司管理
      - button "员工沟通" [ref=e382] [cursor=pointer]:
        - img [ref=e384]:
          - img [ref=e385]
        - generic [ref=e387]: 员工沟通
      - button "处理董事会关系" [ref=e388] [cursor=pointer]:
        - img [ref=e390]:
          - img [ref=e391]
        - generic [ref=e393]: 项目推进
      - button "财务决策" [ref=e394] [cursor=pointer]:
        - img [ref=e396]:
          - img [ref=e397]
        - generic [ref=e399]: 财务决策
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
> 32 |       await expect(page.getByRole("button", { name: "处理董事会关系" })).toBeVisible();
     |                                                                   ^ Error: expect(locator).toBeVisible() failed
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
  46 |       await page.getByRole("button", { name: "处理董事会关系" }).click();
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