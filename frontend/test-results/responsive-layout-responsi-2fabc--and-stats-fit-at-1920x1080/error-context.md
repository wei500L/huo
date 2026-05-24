# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> overview and stats fit at 1920x1080
- Location: tests/e2e/responsive-layout.spec.ts:25:9

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: '设置' })

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
    - generic [ref=e104]:
      - generic [ref=e105]:
        - img "users" [ref=e106]:
          - img [ref=e107]
        - generic [ref=e109]: 112/20
      - button "Open stats dashboard" [ref=e110] [cursor=pointer]:
        - img "settings" [ref=e111]:
          - img [ref=e112]
  - main [ref=e115]:
    - generic [ref=e118]:
      - complementary [ref=e119]:
        - generic [ref=e120]:
          - heading "公司经营总览" [level=1] [ref=e121]
          - paragraph [ref=e122]: 掌控六大核心指标，带领公司走向盈利与荣耀
        - generic [ref=e123]:
          - img "ceo_male_01 confident" [ref=e127]
          - paragraph [ref=e131]: 这周最危险的是董事会信任下滑...
      - main [ref=e132]:
        - generic [ref=e133]:
          - generic [ref=e134]:
            - generic [ref=e135]: 本周趋势
            - button "查看详细报告" [ref=e137] [cursor=pointer]:
              - img [ref=e139]:
                - img [ref=e140]
              - generic [ref=e142]: 查看详细报告
          - generic [ref=e145]:
            - generic [ref=e146]:
              - img "现金流" [ref=e148]:
                - img [ref=e149]
              - generic [ref=e151]: 现金流
            - generic [ref=e152]:
              - img "士气" [ref=e154]:
                - img [ref=e155]
              - generic [ref=e157]: 士气
            - generic [ref=e158]:
              - img "董事会信任" [ref=e160]:
                - img [ref=e161]
              - generic [ref=e163]: 董事会信任
            - generic [ref=e164]:
              - img "公司体面" [ref=e166]:
                - img [ref=e167]
              - generic [ref=e169]: 公司体面
            - generic [ref=e170]:
              - img "员工人数" [ref=e172]:
                - img [ref=e173]
              - generic [ref=e175]: 员工人数
            - generic [ref=e176]:
              - img "市场热度" [ref=e178]:
                - img [ref=e179]
              - generic [ref=e181]: 市场热度
        - region "六大核心指标" [ref=e185]:
          - generic [ref=e186]:
            - generic [ref=e188]: 现金流
            - generic [ref=e190]:
              - img "现金流" [ref=e192]:
                - img [ref=e193]
              - generic [ref=e195]:
                - generic [ref=e196]: "70"
                - generic [ref=e197]: 健康
          - generic [ref=e201]:
            - generic [ref=e203]: 士气
            - generic [ref=e205]:
              - img "士气" [ref=e207]:
                - img [ref=e208]
              - generic [ref=e210]:
                - generic [ref=e211]: "55"
                - generic [ref=e212]: 中立
          - generic [ref=e216]:
            - generic [ref=e218]: 董事会信任
            - generic [ref=e220]:
              - img "董事会信任" [ref=e222]:
                - img [ref=e223]
              - generic [ref=e225]:
                - generic [ref=e226]: "50"
                - generic [ref=e227]: 观望
          - generic [ref=e231]:
            - generic [ref=e233]: 公司体面
            - generic [ref=e235]:
              - img "公司体面" [ref=e237]:
                - img [ref=e238]
              - generic [ref=e240]:
                - generic [ref=e241]: "40"
                - generic [ref=e242]: 普通
          - generic [ref=e246]:
            - generic [ref=e248]: 员工人数
            - generic [ref=e250]:
              - img "员工人数" [ref=e252]:
                - img [ref=e253]
              - generic [ref=e255]:
                - generic [ref=e256]: "42"
                - generic [ref=e257]: v1 占位
          - generic [ref=e261]:
            - generic [ref=e263]: 市场热度
            - generic [ref=e265]:
              - img "市场热度" [ref=e267]:
                - img [ref=e268]
              - generic [ref=e270]:
                - generic [ref=e271]: "39"
                - generic [ref=e272]: v1 占位
        - generic [ref=e276]:
          - generic [ref=e279]:
            - generic [ref=e280]:
              - img "产品部" [ref=e282]:
                - img [ref=e283]
              - generic [ref=e285]:
                - generic [ref=e286]:
                  - heading "产品部" [level=3] [ref=e287]
                  - generic [ref=e288]: 稳定
                - paragraph [ref=e289]: 节奏正常，需求堆积偏多。
            - generic [ref=e290]:
              - generic [ref=e291]: "建议动作:"
              - paragraph [ref=e292]: 先砍低优先级需求
              - img "建议动作" [ref=e293]:
                - img [ref=e294]
          - generic [ref=e298]:
            - generic [ref=e299]:
              - img "市场部" [ref=e301]:
                - img [ref=e302]
              - generic [ref=e304]:
                - generic [ref=e305]:
                  - heading "市场部" [level=3] [ref=e306]
                  - generic [ref=e307]: 疲态
                - paragraph [ref=e308]: 声量偏弱，曝光还不够。
            - generic [ref=e309]:
              - generic [ref=e310]: "建议动作:"
              - paragraph [ref=e311]: 补一轮外部发声
              - img "建议动作" [ref=e312]:
                - img [ref=e313]
          - generic [ref=e317]:
            - generic [ref=e318]:
              - img "技术部" [ref=e320]:
                - img [ref=e321]
              - generic [ref=e324]:
                - generic [ref=e325]:
                  - heading "技术部" [level=3] [ref=e326]
                  - generic [ref=e327]: 健康
                - paragraph [ref=e328]: 交付稳，核心模块可控。
            - generic [ref=e329]:
              - generic [ref=e330]: "建议动作:"
              - paragraph [ref=e331]: 保持现有排期
              - img "建议动作" [ref=e332]:
                - img [ref=e333]
      - complementary [ref=e335]:
        - generic [ref=e336]:
          - generic [ref=e338]: 本周重点事项
          - generic [ref=e341]:
            - generic [ref=e342]:
              - img "董事会信任持续下滑" [ref=e344]:
                - img [ref=e345]
              - generic [ref=e347]:
                - generic [ref=e348]: 董事会信任持续下滑
                - generic [ref=e349]: 本周沟通频率不足，反馈窗口收窄。
            - generic [ref=e350]:
              - img "市场热度偏低" [ref=e352]:
                - img [ref=e353]
              - generic [ref=e355]:
                - generic [ref=e356]: 市场热度偏低
                - generic [ref=e357]: 外部关注没有跟上内部动作。
            - generic [ref=e358]:
              - img "员工申请加班" [ref=e360]:
                - img [ref=e361]
              - generic [ref=e363]:
                - generic [ref=e364]: 员工申请加班
                - generic [ref=e365]: 内部压力上升，产出波动变大。
            - generic [ref=e366]:
              - img "Q2 项目进度 62%" [ref=e368]:
                - img [ref=e369]
              - generic [ref=e371]:
                - generic [ref=e372]: Q2 项目进度 62%
                - generic [ref=e373]: 进度还在推进，但需要稳住节奏。
        - generic:
          - generic:
            - button "稳住现金流 先守底线 稳住现金流" [ref=e374] [cursor=pointer]:
              - generic [ref=e375]:
                - generic [ref=e376]: 稳住现金流
                - generic [ref=e377]: 先守底线
              - img "稳住现金流" [ref=e379]:
                - img [ref=e380]
            - button "处理董事会关系 主动汇报进度 处理董事会关系" [ref=e382] [cursor=pointer]:
              - generic [ref=e383]:
                - generic [ref=e384]: 处理董事会关系
                - generic [ref=e385]: 主动汇报进度
              - img "处理董事会关系" [ref=e387]:
                - img [ref=e388]
            - button "拉高市场热度 补一轮外部声量 拉高市场热度" [ref=e390] [cursor=pointer]:
              - generic [ref=e391]:
                - generic [ref=e392]: 拉高市场热度
                - generic [ref=e393]: 补一轮外部声量
              - img "拉高市场热度" [ref=e395]:
                - img [ref=e396]
  - contentinfo [ref=e398]:
    - generic [ref=e399]: MAIN BAR
    - generic [ref=e401]:
      - img [ref=e405]
      - paragraph [ref=e409]: "TODO: 先听风向，再定动作。"
    - generic [ref=e410]:
      - button "公司管理" [active] [ref=e411] [cursor=pointer]:
        - img [ref=e413]:
          - img [ref=e414]
        - generic [ref=e416]: 公司管理
        - generic [ref=e417]: "1"
      - button "员工沟通" [ref=e418] [cursor=pointer]:
        - img [ref=e420]:
          - img [ref=e421]
        - generic [ref=e423]: 员工沟通
        - generic [ref=e424]: "2"
      - button "项目推进" [ref=e425] [cursor=pointer]:
        - img [ref=e427]:
          - img [ref=e428]
        - generic [ref=e430]: 项目推进
        - generic [ref=e431]: "3"
      - button "财务决策" [ref=e432] [cursor=pointer]:
        - img [ref=e434]:
          - img [ref=e435]
        - generic [ref=e437]: 财务决策
        - generic [ref=e438]: "4"
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
> 36 |       await page.getByRole("button", { name: "设置" }).click();
     |                                                      ^ Error: locator.click: Test timeout of 30000ms exceeded.
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