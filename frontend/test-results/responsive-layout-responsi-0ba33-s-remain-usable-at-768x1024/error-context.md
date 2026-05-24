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
    - generic [ref=e82]:
      - generic [ref=e83]:
        - generic [ref=e84]:
          - img "ceo_male_01 tired" [ref=e86]
          - paragraph [ref=e90]: Q1 开局不利，是时候做出艰难决定了...
        - generic [ref=e92]:
          - generic [ref=e93]: 专注
          - generic [ref=e94]: 创新
          - generic [ref=e95]: 结果
      - main [ref=e96]:
        - generic [ref=e97]:
          - generic [ref=e98]:
            - heading "Q1 季度决策" [level=1] [ref=e99]
            - paragraph [ref=e100]: 每个季度只能选择一项决策，选定后无法更改
          - radiogroup "季度决策" [ref=e101]:
            - 'button "1. 融资方案 handshake 冻结办公室补汤 先砍掉最显眼的非核心开支，保住下个季度的现金线。 效果预览: money 现金流 +¥12 morale 士气 -8 board 董事会信任 +2 face 公司体面 -4" [ref=e102] [cursor=pointer]':
              - generic [ref=e104]: 1. 融资方案
              - 'radio "handshake 冻结办公室补汤 先砍掉最显眼的非核心开支，保住下个季度的现金线。 效果预览: money 现金流 +¥12 morale 士气 -8 board 董事会信任 +2 face 公司体面 -4" [ref=e106]':
                - generic [ref=e107]:
                  - img "handshake" [ref=e109]:
                    - img [ref=e110]
                  - generic [ref=e112]:
                    - heading "冻结办公室补汤" [level=3] [ref=e113]
                    - paragraph [ref=e114]: 先砍掉最显眼的非核心开支，保住下个季度的现金线。
                - generic [ref=e115]:
                  - generic [ref=e116]: "效果预览:"
                  - generic [ref=e117]:
                    - generic [ref=e118]:
                      - img "money" [ref=e119]:
                        - img [ref=e120]
                      - generic [ref=e122]: 现金流
                      - generic [ref=e123]: +¥12
                    - generic [ref=e124]:
                      - img "morale" [ref=e125]:
                        - img [ref=e126]
                      - generic [ref=e128]: 士气
                      - generic [ref=e129]: "-8"
                    - generic [ref=e130]:
                      - img "board" [ref=e131]:
                        - img [ref=e132]
                      - generic [ref=e134]: 董事会信任
                      - generic [ref=e135]: "+2"
                    - generic [ref=e136]:
                      - img "face" [ref=e137]:
                        - img [ref=e138]
                      - generic [ref=e140]: 公司体面
                      - generic [ref=e141]: "-4"
            - 'button "2. 公关方案 megaphone 宣布 NoodleOS 先把故事讲出去，再想办法把产品做出来。 效果预览: money 现金流 +¥4 morale 士气 -5 board 董事会信任 +6 face 公司体面 +10" [ref=e142] [cursor=pointer]':
              - generic [ref=e144]: 2. 公关方案
              - 'radio "megaphone 宣布 NoodleOS 先把故事讲出去，再想办法把产品做出来。 效果预览: money 现金流 +¥4 morale 士气 -5 board 董事会信任 +6 face 公司体面 +10" [ref=e146]':
                - generic [ref=e147]:
                  - img "megaphone" [ref=e149]:
                    - img [ref=e150]
                  - generic [ref=e152]:
                    - heading "宣布 NoodleOS" [level=3] [ref=e153]
                    - paragraph [ref=e154]: 先把故事讲出去，再想办法把产品做出来。
                - generic [ref=e155]:
                  - generic [ref=e156]: "效果预览:"
                  - generic [ref=e157]:
                    - generic [ref=e158]:
                      - img "money" [ref=e159]:
                        - img [ref=e160]
                      - generic [ref=e162]: 现金流
                      - generic [ref=e163]: +¥4
                    - generic [ref=e164]:
                      - img "morale" [ref=e165]:
                        - img [ref=e166]
                      - generic [ref=e168]: 士气
                      - generic [ref=e169]: "-5"
                    - generic [ref=e170]:
                      - img "board" [ref=e171]:
                        - img [ref=e172]
                      - generic [ref=e174]: 董事会信任
                      - generic [ref=e175]: "+6"
                    - generic [ref=e176]:
                      - img "face" [ref=e177]:
                        - img [ref=e178]
                      - generic [ref=e180]: 公司体面
                      - generic [ref=e181]: "+10"
            - 'button "3. board target 申请董事会缓冲 把压力摊开讲，让董事会先别做激烈动作。 效果预览: money 现金流 +¥3 morale 士气 -2 board 董事会信任 +5 face 公司体面 -3" [ref=e182] [cursor=pointer]':
              - generic [ref=e184]: 3. board
              - 'radio "target 申请董事会缓冲 把压力摊开讲，让董事会先别做激烈动作。 效果预览: money 现金流 +¥3 morale 士气 -2 board 董事会信任 +5 face 公司体面 -3" [ref=e186]':
                - generic [ref=e187]:
                  - img "target" [ref=e189]:
                    - img [ref=e190]
                  - generic [ref=e192]:
                    - heading "申请董事会缓冲" [level=3] [ref=e193]
                    - paragraph [ref=e194]: 把压力摊开讲，让董事会先别做激烈动作。
                - generic [ref=e195]:
                  - generic [ref=e196]: "效果预览:"
                  - generic [ref=e197]:
                    - generic [ref=e198]:
                      - img "money" [ref=e199]:
                        - img [ref=e200]
                      - generic [ref=e202]: 现金流
                      - generic [ref=e203]: +¥3
                    - generic [ref=e204]:
                      - img "morale" [ref=e205]:
                        - img [ref=e206]
                      - generic [ref=e208]: 士气
                      - generic [ref=e209]: "-2"
                    - generic [ref=e210]:
                      - img "board" [ref=e211]:
                        - img [ref=e212]
                      - generic [ref=e214]: 董事会信任
                      - generic [ref=e215]: "+5"
                    - generic [ref=e216]:
                      - img "face" [ref=e217]:
                        - img [ref=e218]
                      - generic [ref=e220]: 公司体面
                      - generic [ref=e221]: "-3"
          - button "确认决策" [disabled] [ref=e223]
        - complementary [ref=e224]:
          - generic [ref=e225]:
            - generic [ref=e227]: 画饼总账
            - generic [ref=e229]:
              - generic [ref=e230]:
                - generic [ref=e231]: 当前画饼评级
                - generic [ref=e232]: B+
                - generic [ref=e233]: 预期收益
                - generic [ref=e234]: +¥12,000/季度
              - generic [ref=e235]:
                - generic [ref=e236]:
                  - heading "你说过的话" [level=3] [ref=e237]
                  - generic [ref=e238]: (4/4)
                - generic [ref=e239]:
                  - generic [ref=e240]:
                    - generic [ref=e241]: Q1
                    - generic [ref=e242]:
                      - generic [ref=e243]:
                        - img "check" [ref=e244]:
                          - img [ref=e245]
                        - generic [ref=e247]: Q1 不裁员
                      - generic [ref=e248]: 承诺已核验
                    - generic [ref=e249]: 已兑现
                  - generic [ref=e250]:
                    - generic [ref=e251]: Q1
                    - generic [ref=e252]:
                      - generic [ref=e253]:
                        - img "clock" [ref=e254]:
                          - img [ref=e255]
                        - generic [ref=e257]: Q1 Q3 GMV 翻倍
                      - generic [ref=e258]: 预计剩余 7 周
                    - generic [ref=e259]: 进行中
                  - generic [ref=e260]:
                    - generic [ref=e261]: Q2
                    - generic [ref=e262]:
                      - generic [ref=e263]:
                        - img "x" [ref=e264]:
                          - img [ref=e265]
                        - generic [ref=e267]: Q2 季度内盈利
                      - generic [ref=e268]: 目标未达成
                    - generic [ref=e269]: 已失败
                  - generic [ref=e270]:
                    - generic [ref=e271]: Q2
                    - generic [ref=e272]:
                      - generic [ref=e273]:
                        - img "clock" [ref=e274]:
                          - img [ref=e275]
                        - generic [ref=e277]: Q2 年底市值破 10 亿
                      - generic [ref=e278]: 预计剩余 7 周
                    - generic [ref=e279]: 进行中
              - button "查看更多历史记录 →" [ref=e280] [cursor=pointer]
  - contentinfo [ref=e281]:
    - generic [ref=e282]: MAIN BAR
    - generic [ref=e284]:
      - img [ref=e288]
      - paragraph [ref=e292]: "TODO: 先听风向，再定动作。"
    - generic [ref=e293]:
      - button "公司管理" [ref=e294] [cursor=pointer]:
        - img [ref=e296]:
          - img [ref=e297]
        - generic [ref=e299]: 公司管理
      - button "员工沟通" [ref=e300] [cursor=pointer]:
        - img [ref=e302]:
          - img [ref=e303]
        - generic [ref=e305]: 员工沟通
      - button "处理董事会关系" [active] [ref=e306] [cursor=pointer]:
        - img [ref=e308]:
          - img [ref=e309]
        - generic [ref=e311]: 项目推进
      - button "财务决策" [ref=e312] [cursor=pointer]:
        - img [ref=e314]:
          - img [ref=e315]
        - generic [ref=e317]: 财务决策
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