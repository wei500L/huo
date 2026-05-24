# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> overview and stats fit at 375x900
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
    - generic [ref=e88]:
      - complementary [ref=e89]:
        - generic [ref=e90]:
          - heading "公司经营总览" [level=1] [ref=e91]
          - paragraph [ref=e92]: 掌控六大核心指标，带领公司走向盈利与荣耀
        - generic [ref=e93]:
          - img "ceo_male_01 confident" [ref=e97]
          - paragraph [ref=e101]: 这周最危险的是董事会信任下滑...
      - main [ref=e102]:
        - generic [ref=e103]:
          - generic [ref=e104]:
            - generic [ref=e105]: 本周趋势
            - button "查看详细报告" [ref=e107] [cursor=pointer]:
              - img [ref=e109]:
                - img [ref=e110]
              - generic [ref=e112]: 查看详细报告
          - generic [ref=e115]:
            - generic [ref=e116]:
              - img "现金流" [ref=e118]:
                - img [ref=e119]
              - generic [ref=e121]: 现金流
            - generic [ref=e122]:
              - img "士气" [ref=e124]:
                - img [ref=e125]
              - generic [ref=e127]: 士气
            - generic [ref=e128]:
              - img "董事会信任" [ref=e130]:
                - img [ref=e131]
              - generic [ref=e133]: 董事会信任
            - generic [ref=e134]:
              - img "公司体面" [ref=e136]:
                - img [ref=e137]
              - generic [ref=e139]: 公司体面
            - generic [ref=e140]:
              - img "员工人数" [ref=e142]:
                - img [ref=e143]
              - generic [ref=e145]: 员工人数
            - generic [ref=e146]:
              - img "市场热度" [ref=e148]:
                - img [ref=e149]
              - generic [ref=e151]: 市场热度
        - region "六大核心指标" [ref=e155]:
          - generic [ref=e156]:
            - generic [ref=e158]: 现金流
            - generic [ref=e160]:
              - img "现金流" [ref=e162]:
                - img [ref=e163]
              - generic [ref=e165]:
                - generic [ref=e166]: "70"
                - generic [ref=e167]: 健康
          - generic [ref=e171]:
            - generic [ref=e173]: 士气
            - generic [ref=e175]:
              - img "士气" [ref=e177]:
                - img [ref=e178]
              - generic [ref=e180]:
                - generic [ref=e181]: "55"
                - generic [ref=e182]: 中立
          - generic [ref=e186]:
            - generic [ref=e188]: 董事会信任
            - generic [ref=e190]:
              - img "董事会信任" [ref=e192]:
                - img [ref=e193]
              - generic [ref=e195]:
                - generic [ref=e196]: "50"
                - generic [ref=e197]: 观望
          - generic [ref=e201]:
            - generic [ref=e203]: 公司体面
            - generic [ref=e205]:
              - img "公司体面" [ref=e207]:
                - img [ref=e208]
              - generic [ref=e210]:
                - generic [ref=e211]: "40"
                - generic [ref=e212]: 普通
          - generic [ref=e216]:
            - generic [ref=e218]: 员工人数
            - generic [ref=e220]:
              - img "员工人数" [ref=e222]:
                - img [ref=e223]
              - generic [ref=e225]:
                - generic [ref=e226]: "42"
                - generic [ref=e227]: v1 占位
          - generic [ref=e231]:
            - generic [ref=e233]: 市场热度
            - generic [ref=e235]:
              - img "市场热度" [ref=e237]:
                - img [ref=e238]
              - generic [ref=e240]:
                - generic [ref=e241]: "39"
                - generic [ref=e242]: v1 占位
        - generic [ref=e246]:
          - generic [ref=e249]:
            - generic [ref=e250]:
              - img "产品部" [ref=e252]:
                - img [ref=e253]
              - generic [ref=e255]:
                - generic [ref=e256]:
                  - heading "产品部" [level=3] [ref=e257]
                  - generic [ref=e258]: 稳定
                - paragraph [ref=e259]: 节奏正常，需求堆积偏多。
            - generic [ref=e260]:
              - generic [ref=e261]: "建议动作:"
              - paragraph [ref=e262]: 先砍低优先级需求
              - img "建议动作" [ref=e263]:
                - img [ref=e264]
          - generic [ref=e268]:
            - generic [ref=e269]:
              - img "市场部" [ref=e271]:
                - img [ref=e272]
              - generic [ref=e274]:
                - generic [ref=e275]:
                  - heading "市场部" [level=3] [ref=e276]
                  - generic [ref=e277]: 疲态
                - paragraph [ref=e278]: 声量偏弱，曝光还不够。
            - generic [ref=e279]:
              - generic [ref=e280]: "建议动作:"
              - paragraph [ref=e281]: 补一轮外部发声
              - img "建议动作" [ref=e282]:
                - img [ref=e283]
          - generic [ref=e287]:
            - generic [ref=e288]:
              - img "技术部" [ref=e290]:
                - img [ref=e291]
              - generic [ref=e294]:
                - generic [ref=e295]:
                  - heading "技术部" [level=3] [ref=e296]
                  - generic [ref=e297]: 健康
                - paragraph [ref=e298]: 交付稳，核心模块可控。
            - generic [ref=e299]:
              - generic [ref=e300]: "建议动作:"
              - paragraph [ref=e301]: 保持现有排期
              - img "建议动作" [ref=e302]:
                - img [ref=e303]
      - complementary [ref=e305]:
        - generic [ref=e306]:
          - generic [ref=e308]: 本周重点事项
          - generic [ref=e311]:
            - generic [ref=e312]:
              - img "董事会信任持续下滑" [ref=e314]:
                - img [ref=e315]
              - generic [ref=e317]:
                - generic [ref=e318]: 董事会信任持续下滑
                - generic [ref=e319]: 本周沟通频率不足，反馈窗口收窄。
            - generic [ref=e320]:
              - img "市场热度偏低" [ref=e322]:
                - img [ref=e323]
              - generic [ref=e325]:
                - generic [ref=e326]: 市场热度偏低
                - generic [ref=e327]: 外部关注没有跟上内部动作。
            - generic [ref=e328]:
              - img "员工申请加班" [ref=e330]:
                - img [ref=e331]
              - generic [ref=e333]:
                - generic [ref=e334]: 员工申请加班
                - generic [ref=e335]: 内部压力上升，产出波动变大。
            - generic [ref=e336]:
              - img "Q2 项目进度 62%" [ref=e338]:
                - img [ref=e339]
              - generic [ref=e341]:
                - generic [ref=e342]: Q2 项目进度 62%
                - generic [ref=e343]: 进度还在推进，但需要稳住节奏。
        - generic:
          - generic:
            - button "稳住现金流 先守底线 稳住现金流" [ref=e344] [cursor=pointer]:
              - generic [ref=e345]:
                - generic [ref=e346]: 稳住现金流
                - generic [ref=e347]: 先守底线
              - img "稳住现金流" [ref=e349]:
                - img [ref=e350]
            - button "处理董事会关系 主动汇报进度 处理董事会关系" [ref=e352] [cursor=pointer]:
              - generic [ref=e353]:
                - generic [ref=e354]: 处理董事会关系
                - generic [ref=e355]: 主动汇报进度
              - img "处理董事会关系" [ref=e357]:
                - img [ref=e358]
            - button "拉高市场热度 补一轮外部声量 拉高市场热度" [ref=e360] [cursor=pointer]:
              - generic [ref=e361]:
                - generic [ref=e362]: 拉高市场热度
                - generic [ref=e363]: 补一轮外部声量
              - img "拉高市场热度" [ref=e365]:
                - img [ref=e366]
  - contentinfo [ref=e368]:
    - generic [ref=e369]: MAIN BAR
    - generic [ref=e371]:
      - img [ref=e375]
      - paragraph [ref=e379]: "TODO: 先听风向，再定动作。"
    - generic [ref=e380]:
      - button "公司管理" [active] [ref=e381] [cursor=pointer]:
        - img [ref=e383]:
          - img [ref=e384]
        - generic [ref=e386]: 公司管理
      - button "员工沟通" [ref=e387] [cursor=pointer]:
        - img [ref=e389]:
          - img [ref=e390]
        - generic [ref=e392]: 员工沟通
      - button "项目推进" [ref=e393] [cursor=pointer]:
        - img [ref=e395]:
          - img [ref=e396]
        - generic [ref=e398]: 项目推进
      - button "财务决策" [ref=e399] [cursor=pointer]:
        - img [ref=e401]:
          - img [ref=e402]
        - generic [ref=e404]: 财务决策
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