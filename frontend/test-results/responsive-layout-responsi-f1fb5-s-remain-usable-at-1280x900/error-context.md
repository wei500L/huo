# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-layout.spec.ts >> responsive layout >> decision and press remain usable at 1280x900
- Location: tests/e2e/responsive-layout.spec.ts:42:9

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: /融资续命/ })

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
    - generic [ref=e112]:
      - generic [ref=e113]:
        - generic [ref=e114]:
          - img "ceo_male_01 tired" [ref=e116]
          - paragraph [ref=e120]: Q1 开局不利，是时候做出艰难决定了...
        - generic [ref=e122]:
          - generic [ref=e123]: 专注
          - generic [ref=e124]: 创新
          - generic [ref=e125]: 结果
      - main [ref=e126]:
        - generic [ref=e127]:
          - generic [ref=e128]:
            - heading "Q1 季度决策" [level=1] [ref=e129]
            - paragraph [ref=e130]: 每个季度只能选择一项决策，选定后无法更改
          - radiogroup "季度决策" [ref=e131]:
            - 'button "1. 融资方案 handshake 冻结办公室补汤 先砍掉最显眼的非核心开支，保住下个季度的现金线。 效果预览: money 现金流 +¥12 morale 士气 -8 board 董事会信任 +2 face 公司体面 -4" [ref=e132] [cursor=pointer]':
              - generic [ref=e134]: 1. 融资方案
              - 'radio "handshake 冻结办公室补汤 先砍掉最显眼的非核心开支，保住下个季度的现金线。 效果预览: money 现金流 +¥12 morale 士气 -8 board 董事会信任 +2 face 公司体面 -4" [ref=e136]':
                - generic [ref=e137]:
                  - img "handshake" [ref=e139]:
                    - img [ref=e140]
                  - generic [ref=e142]:
                    - heading "冻结办公室补汤" [level=3] [ref=e143]
                    - paragraph [ref=e144]: 先砍掉最显眼的非核心开支，保住下个季度的现金线。
                - generic [ref=e145]:
                  - generic [ref=e146]: "效果预览:"
                  - generic [ref=e147]:
                    - generic [ref=e148]:
                      - img "money" [ref=e149]:
                        - img [ref=e150]
                      - generic [ref=e152]: 现金流
                      - generic [ref=e153]: +¥12
                    - generic [ref=e154]:
                      - img "morale" [ref=e155]:
                        - img [ref=e156]
                      - generic [ref=e158]: 士气
                      - generic [ref=e159]: "-8"
                    - generic [ref=e160]:
                      - img "board" [ref=e161]:
                        - img [ref=e162]
                      - generic [ref=e164]: 董事会信任
                      - generic [ref=e165]: "+2"
                    - generic [ref=e166]:
                      - img "face" [ref=e167]:
                        - img [ref=e168]
                      - generic [ref=e170]: 公司体面
                      - generic [ref=e171]: "-4"
            - 'button "2. 公关方案 megaphone 宣布 NoodleOS 先把故事讲出去，再想办法把产品做出来。 效果预览: money 现金流 +¥4 morale 士气 -5 board 董事会信任 +6 face 公司体面 +10" [ref=e172] [cursor=pointer]':
              - generic [ref=e174]: 2. 公关方案
              - 'radio "megaphone 宣布 NoodleOS 先把故事讲出去，再想办法把产品做出来。 效果预览: money 现金流 +¥4 morale 士气 -5 board 董事会信任 +6 face 公司体面 +10" [ref=e176]':
                - generic [ref=e177]:
                  - img "megaphone" [ref=e179]:
                    - img [ref=e180]
                  - generic [ref=e182]:
                    - heading "宣布 NoodleOS" [level=3] [ref=e183]
                    - paragraph [ref=e184]: 先把故事讲出去，再想办法把产品做出来。
                - generic [ref=e185]:
                  - generic [ref=e186]: "效果预览:"
                  - generic [ref=e187]:
                    - generic [ref=e188]:
                      - img "money" [ref=e189]:
                        - img [ref=e190]
                      - generic [ref=e192]: 现金流
                      - generic [ref=e193]: +¥4
                    - generic [ref=e194]:
                      - img "morale" [ref=e195]:
                        - img [ref=e196]
                      - generic [ref=e198]: 士气
                      - generic [ref=e199]: "-5"
                    - generic [ref=e200]:
                      - img "board" [ref=e201]:
                        - img [ref=e202]
                      - generic [ref=e204]: 董事会信任
                      - generic [ref=e205]: "+6"
                    - generic [ref=e206]:
                      - img "face" [ref=e207]:
                        - img [ref=e208]
                      - generic [ref=e210]: 公司体面
                      - generic [ref=e211]: "+10"
            - 'button "3. board target 申请董事会缓冲 把压力摊开讲，让董事会先别做激烈动作。 效果预览: money 现金流 +¥3 morale 士气 -2 board 董事会信任 +5 face 公司体面 -3" [ref=e212] [cursor=pointer]':
              - generic [ref=e214]: 3. board
              - 'radio "target 申请董事会缓冲 把压力摊开讲，让董事会先别做激烈动作。 效果预览: money 现金流 +¥3 morale 士气 -2 board 董事会信任 +5 face 公司体面 -3" [ref=e216]':
                - generic [ref=e217]:
                  - img "target" [ref=e219]:
                    - img [ref=e220]
                  - generic [ref=e222]:
                    - heading "申请董事会缓冲" [level=3] [ref=e223]
                    - paragraph [ref=e224]: 把压力摊开讲，让董事会先别做激烈动作。
                - generic [ref=e225]:
                  - generic [ref=e226]: "效果预览:"
                  - generic [ref=e227]:
                    - generic [ref=e228]:
                      - img "money" [ref=e229]:
                        - img [ref=e230]
                      - generic [ref=e232]: 现金流
                      - generic [ref=e233]: +¥3
                    - generic [ref=e234]:
                      - img "morale" [ref=e235]:
                        - img [ref=e236]
                      - generic [ref=e238]: 士气
                      - generic [ref=e239]: "-2"
                    - generic [ref=e240]:
                      - img "board" [ref=e241]:
                        - img [ref=e242]
                      - generic [ref=e244]: 董事会信任
                      - generic [ref=e245]: "+5"
                    - generic [ref=e246]:
                      - img "face" [ref=e247]:
                        - img [ref=e248]
                      - generic [ref=e250]: 公司体面
                      - generic [ref=e251]: "-3"
          - button "确认决策" [disabled] [ref=e253]
        - complementary [ref=e254]:
          - generic [ref=e255]:
            - generic [ref=e257]: 画饼总账
            - generic [ref=e259]:
              - generic [ref=e260]:
                - generic [ref=e261]: 当前画饼评级
                - generic [ref=e262]: B+
                - generic [ref=e263]: 预期收益
                - generic [ref=e264]: +¥12,000/季度
              - generic [ref=e265]:
                - generic [ref=e266]:
                  - heading "你说过的话" [level=3] [ref=e267]
                  - generic [ref=e268]: (4/4)
                - generic [ref=e269]:
                  - generic [ref=e270]:
                    - generic [ref=e271]: Q1
                    - generic [ref=e272]:
                      - generic [ref=e273]:
                        - img "check" [ref=e274]:
                          - img [ref=e275]
                        - generic [ref=e277]: Q1 不裁员
                      - generic [ref=e278]: 承诺已核验
                    - generic [ref=e279]: 已兑现
                  - generic [ref=e280]:
                    - generic [ref=e281]: Q1
                    - generic [ref=e282]:
                      - generic [ref=e283]:
                        - img "clock" [ref=e284]:
                          - img [ref=e285]
                        - generic [ref=e287]: Q1 Q3 GMV 翻倍
                      - generic [ref=e288]: 预计剩余 7 周
                    - generic [ref=e289]: 进行中
                  - generic [ref=e290]:
                    - generic [ref=e291]: Q2
                    - generic [ref=e292]:
                      - generic [ref=e293]:
                        - img "x" [ref=e294]:
                          - img [ref=e295]
                        - generic [ref=e297]: Q2 季度内盈利
                      - generic [ref=e298]: 目标未达成
                    - generic [ref=e299]: 已失败
                  - generic [ref=e300]:
                    - generic [ref=e301]: Q2
                    - generic [ref=e302]:
                      - generic [ref=e303]:
                        - img "clock" [ref=e304]:
                          - img [ref=e305]
                        - generic [ref=e307]: Q2 年底市值破 10 亿
                      - generic [ref=e308]: 预计剩余 7 周
                    - generic [ref=e309]: 进行中
              - button "查看更多历史记录 →" [ref=e310] [cursor=pointer]
  - contentinfo [ref=e311]:
    - generic [ref=e312]: MAIN BAR
    - generic [ref=e314]:
      - img [ref=e318]
      - paragraph [ref=e322]: "TODO: 先听风向，再定动作。"
    - generic [ref=e323]:
      - button "公司管理" [ref=e324] [cursor=pointer]:
        - img [ref=e326]:
          - img [ref=e327]
        - generic [ref=e329]: 公司管理
        - generic [ref=e330]: "1"
      - button "员工沟通" [ref=e331] [cursor=pointer]:
        - img [ref=e333]:
          - img [ref=e334]
        - generic [ref=e336]: 员工沟通
        - generic [ref=e337]: "2"
      - button "处理董事会关系" [active] [ref=e338] [cursor=pointer]:
        - img [ref=e340]:
          - img [ref=e341]
        - generic [ref=e343]: 项目推进
        - generic [ref=e344]: "3"
      - button "财务决策" [ref=e345] [cursor=pointer]:
        - img [ref=e347]:
          - img [ref=e348]
        - generic [ref=e350]: 财务决策
        - generic [ref=e351]: "4"
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
  46 |       await page.getByRole("button", { name: "处理董事会关系" }).click();
  47 |       await expect(page.getByText("Q1 季度决策")).toBeVisible();
> 48 |       await page.getByRole("button", { name: /融资续命/ }).click();
     |                                                        ^ Error: locator.click: Test timeout of 30000ms exceeded.
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