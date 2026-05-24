# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> overview and stats fit at 1280x900
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
            - generic [ref=e31]: 健康
          - generic [ref=e33]: ¥70
          - generic [ref=e35]: "-"
      - article [ref=e37]:
        - generic [ref=e38]:
          - generic [ref=e39]:
            - img [ref=e41]:
              - img [ref=e42]
            - generic [ref=e44]: 士气
            - generic [ref=e45]: 稳定
          - generic [ref=e47]: "55"
          - generic [ref=e49]: "-"
      - article [ref=e51]:
        - generic [ref=e52]:
          - generic [ref=e53]:
            - img [ref=e55]:
              - img [ref=e56]
            - generic [ref=e58]: 董事会
            - generic [ref=e59]: 稳定
          - generic [ref=e61]: "50"
          - generic [ref=e63]: "-"
      - article [ref=e65]:
        - generic [ref=e66]:
          - generic [ref=e67]:
            - img [ref=e69]:
              - img [ref=e70]
            - generic [ref=e72]: 面子
            - generic [ref=e73]: 稳定
          - generic [ref=e75]: "40"
          - generic [ref=e77]: "-"
      - article [ref=e79]:
        - generic [ref=e80]:
          - generic [ref=e81]:
            - img [ref=e83]:
              - img [ref=e84]
            - generic [ref=e86]: SALES
          - generic [ref=e88]: v2
          - generic [ref=e90]: "-"
      - article [ref=e92]:
        - generic [ref=e93]:
          - generic [ref=e94]:
            - img [ref=e96]:
              - img [ref=e97]
            - generic [ref=e99]: MKT
          - generic [ref=e101]: v2
          - generic [ref=e103]: "-"
    - button "设置" [ref=e105] [cursor=pointer]:
      - img "settings" [ref=e106]:
        - img [ref=e107]
  - main [ref=e110]:
    - generic [ref=e113]:
      - complementary [ref=e114]:
        - generic [ref=e115]:
          - heading "公司经营总览" [level=1] [ref=e116]
          - paragraph [ref=e117]: 掌控六大核心指标，带领公司走向盈利与荣耀
        - generic [ref=e118]:
          - img "ceo_male_01 confident" [ref=e122]
          - paragraph [ref=e126]: 这周最危险的是董事会信任下滑...
      - main [ref=e127]:
        - generic [ref=e128]:
          - generic [ref=e129]:
            - generic [ref=e130]: 本周趋势
            - button "查看详细报告" [ref=e132] [cursor=pointer]:
              - img [ref=e134]:
                - img [ref=e135]
              - generic [ref=e137]: 查看详细报告
          - generic [ref=e140]:
            - generic [ref=e141]:
              - img "现金流" [ref=e143]:
                - img [ref=e144]
              - generic [ref=e146]: 现金流
            - generic [ref=e147]:
              - img "士气" [ref=e149]:
                - img [ref=e150]
              - generic [ref=e152]: 士气
            - generic [ref=e153]:
              - img "董事会信任" [ref=e155]:
                - img [ref=e156]
              - generic [ref=e158]: 董事会信任
            - generic [ref=e159]:
              - img "公司体面" [ref=e161]:
                - img [ref=e162]
              - generic [ref=e164]: 公司体面
            - generic [ref=e165]:
              - img "员工人数" [ref=e167]:
                - img [ref=e168]
              - generic [ref=e170]: 员工人数
            - generic [ref=e171]:
              - img "市场热度" [ref=e173]:
                - img [ref=e174]
              - generic [ref=e176]: 市场热度
        - region "六大核心指标" [ref=e180]:
          - generic [ref=e181]:
            - generic [ref=e183]: 现金流
            - generic [ref=e185]:
              - img "现金流" [ref=e187]:
                - img [ref=e188]
              - generic [ref=e190]:
                - generic [ref=e191]: "15"
                - generic [ref=e192]: 健康
          - generic [ref=e196]:
            - generic [ref=e198]: 士气
            - generic [ref=e200]:
              - img "士气" [ref=e202]:
                - img [ref=e203]
              - generic [ref=e205]:
                - generic [ref=e206]: "12"
                - generic [ref=e207]: 中立
          - generic [ref=e211]:
            - generic [ref=e213]: 董事会信任
            - generic [ref=e215]:
              - img "董事会信任" [ref=e217]:
                - img [ref=e218]
              - generic [ref=e220]:
                - generic [ref=e221]: "11"
                - generic [ref=e222]: 观望
          - generic [ref=e226]:
            - generic [ref=e228]: 公司体面
            - generic [ref=e230]:
              - img "公司体面" [ref=e232]:
                - img [ref=e233]
              - generic [ref=e235]:
                - generic [ref=e236]: "8"
                - generic [ref=e237]: 普通
          - generic [ref=e241]:
            - generic [ref=e243]: 员工人数
            - generic [ref=e245]:
              - img "员工人数" [ref=e247]:
                - img [ref=e248]
              - generic [ref=e250]:
                - generic [ref=e251]: "9"
                - generic [ref=e252]: v1 占位
          - generic [ref=e256]:
            - generic [ref=e258]: 市场热度
            - generic [ref=e260]:
              - img "市场热度" [ref=e262]:
                - img [ref=e263]
              - generic [ref=e265]:
                - generic [ref=e266]: "8"
                - generic [ref=e267]: v1 占位
        - generic [ref=e271]:
          - generic [ref=e274]:
            - generic [ref=e275]:
              - img "产品部" [ref=e277]:
                - img [ref=e278]
              - generic [ref=e280]:
                - generic [ref=e281]:
                  - heading "产品部" [level=3] [ref=e282]
                  - generic [ref=e283]: 稳定
                - paragraph [ref=e284]: 节奏正常，需求堆积偏多。
            - generic [ref=e285]:
              - generic [ref=e286]: "建议动作:"
              - paragraph [ref=e287]: 先砍低优先级需求
              - img "建议动作" [ref=e288]:
                - img [ref=e289]
          - generic [ref=e293]:
            - generic [ref=e294]:
              - img "市场部" [ref=e296]:
                - img [ref=e297]
              - generic [ref=e299]:
                - generic [ref=e300]:
                  - heading "市场部" [level=3] [ref=e301]
                  - generic [ref=e302]: 疲态
                - paragraph [ref=e303]: 声量偏弱，曝光还不够。
            - generic [ref=e304]:
              - generic [ref=e305]: "建议动作:"
              - paragraph [ref=e306]: 补一轮外部发声
              - img "建议动作" [ref=e307]:
                - img [ref=e308]
          - generic [ref=e312]:
            - generic [ref=e313]:
              - img "技术部" [ref=e315]:
                - img [ref=e316]
              - generic [ref=e319]:
                - generic [ref=e320]:
                  - heading "技术部" [level=3] [ref=e321]
                  - generic [ref=e322]: 健康
                - paragraph [ref=e323]: 交付稳，核心模块可控。
            - generic [ref=e324]:
              - generic [ref=e325]: "建议动作:"
              - paragraph [ref=e326]: 保持现有排期
              - img "建议动作" [ref=e327]:
                - img [ref=e328]
      - complementary [ref=e330]:
        - generic [ref=e331]:
          - generic [ref=e333]: 本周重点事项
          - generic [ref=e336]:
            - generic [ref=e337]:
              - img "董事会信任持续下滑" [ref=e339]:
                - img [ref=e340]
              - generic [ref=e342]:
                - generic [ref=e343]: 董事会信任持续下滑
                - generic [ref=e344]: 本周沟通频率不足，反馈窗口收窄。
            - generic [ref=e345]:
              - img "市场热度偏低" [ref=e347]:
                - img [ref=e348]
              - generic [ref=e350]:
                - generic [ref=e351]: 市场热度偏低
                - generic [ref=e352]: 外部关注没有跟上内部动作。
            - generic [ref=e353]:
              - img "员工申请加班" [ref=e355]:
                - img [ref=e356]
              - generic [ref=e358]:
                - generic [ref=e359]: 员工申请加班
                - generic [ref=e360]: 内部压力上升，产出波动变大。
            - generic [ref=e361]:
              - img "Q2 项目进度 62%" [ref=e363]:
                - img [ref=e364]
              - generic [ref=e366]:
                - generic [ref=e367]: Q2 项目进度 62%
                - generic [ref=e368]: 进度还在推进，但需要稳住节奏。
        - generic:
          - generic:
            - button "稳住现金流 先守底线 稳住现金流" [ref=e369] [cursor=pointer]:
              - generic [ref=e370]:
                - generic [ref=e371]: 稳住现金流
                - generic [ref=e372]: 先守底线
              - img "稳住现金流" [ref=e374]:
                - img [ref=e375]
            - button "处理董事会关系 主动汇报进度 处理董事会关系" [ref=e377] [cursor=pointer]:
              - generic [ref=e378]:
                - generic [ref=e379]: 处理董事会关系
                - generic [ref=e380]: 主动汇报进度
              - img "处理董事会关系" [ref=e382]:
                - img [ref=e383]
            - button "拉高市场热度 补一轮外部声量 拉高市场热度" [ref=e385] [cursor=pointer]:
              - generic [ref=e386]:
                - generic [ref=e387]: 拉高市场热度
                - generic [ref=e388]: 补一轮外部声量
              - img "拉高市场热度" [ref=e390]:
                - img [ref=e391]
  - contentinfo [ref=e393]:
    - generic [ref=e394]: MAIN BAR
    - generic [ref=e396]:
      - img [ref=e400]
      - paragraph [ref=e404]: "TODO: 先听风向，再定动作。"
    - generic [ref=e405]:
      - button "公司管理" [active] [ref=e406] [cursor=pointer]:
        - img [ref=e408]:
          - img [ref=e409]
        - generic [ref=e411]: 公司管理
        - generic [ref=e412]: "1"
      - button "员工沟通" [ref=e413] [cursor=pointer]:
        - img [ref=e415]:
          - img [ref=e416]
        - generic [ref=e418]: 员工沟通
        - generic [ref=e419]: "2"
      - button "处理董事会关系" [ref=e420] [cursor=pointer]:
        - img [ref=e422]:
          - img [ref=e423]
        - generic [ref=e425]: 项目推进
        - generic [ref=e426]: "3"
      - button "财务决策" [ref=e427] [cursor=pointer]:
        - img [ref=e429]:
          - img [ref=e430]
        - generic [ref=e432]: 财务决策
        - generic [ref=e433]: "4"
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