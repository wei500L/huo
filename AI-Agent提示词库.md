# 《YES, BOSS!》AI Agent 工程师 — 工作流提示词库 v1.0

> **使用对象**：AI Agent 工程师（提示词工程 / LLM 编排 / ASR）
> **使用方式**：复制对应场景的「Prompt 模板」喂给 Claude Code / Cursor / ChatGPT，把 `{{占位符}}` 替换成你当前任务的实际值
> **配套文档**：`DESIGN(3).md` §六/§七/§十九、`docs/architecture.md`
> **更新日期**：2026-05-23

---

> ⚠️ **v1 阶段范围声明（必读）**
>
> 当前原型 = **4 季度 / 4 指标**（CASH / MORALE / BOARD / FACE），对齐 `js/state.js` 实际代码。
> 本库中出现的 **8 季度 / 6 指标**（多 MKT / SALES）/ ASR 实时转写 / 多 Agent 拆分 / 跨轮 legacy 等内容，是 **v2 路线图**，v1 阶段**忽略不写**。
> 写 prompt 时如果模板里有 6 指标字段，**只保留 4 个**；遇到 Q5–Q8 触发条件，**改写到 Q1–Q4 之间**。
> 不确定时找项目管理对齐，不要自己拍。

---

## 0. 你的角色与本库范围

你的产出是「让游戏内的 LLM 开口」的全部资产：
- **运行时 Agent System Prompt**（董事会 / 员工 / 媒体 / 竞品 / 市场 / 监管 / 投资人 / 发布会评估 / 死亡报告）
- **总导演（Director）单次调用编排**：在 stub 与 api 模式之间一致的 schema
- **JSON Schema 校验器 + 重试链 + 模板兜底**
- **ASR 预处理与脱敏过滤**
- **跨季度记忆**（promise_log / agent_memory）的写入 / 召回逻辑
- **Few-shot 池 + Bad-case 回归集**

不属于你：UI 渲染、像素图、决策卡数值。但你写的 prompt 必须**对策划数值口径稳定**、**对前端输出 schema 稳定**——出问题先看你这边。

---

## 1. 工作流速查表

| 任务 | 用哪个 Prompt | 产出 | 验收 |
|---|---|---|---|
| 新增/迭代某个 Agent | §2 Agent System Prompt 模板 | `prompts/<agent>.md` + JSON Schema | §9 验收 |
| 写总导演单次调用 | §3 Director 编排模板 | `js/director.js` 的 system + user | 100 次调用零 schema fail |
| 调发布会评估 | §4 发布会评估模板 | press-eval prompt | 同决策不同 stats 输出有差异 |
| 处理 LLM 输出乱掉 | §5 容错与重试 | retry policy + 兜底 stub | bad-case 集 0 漏 |
| 接 ASR 转写 | §6 ASR 后处理 | 转写清洗管道 | 见 §6.4 |
| 写跨季度记忆 | §7 记忆模板 | promise_log / agent_memory | 见 §7.3 |
| 调参/降本 | §8 调参循环 | temperature / token / 模型选择 | 单季成本 ≤ 预算 |

---

## 2. Agent System Prompt — 通用编写模板

> 用这个 meta-prompt 让 Claude / GPT 帮你**生成或迭代**某个 Agent 的 system prompt。

```text
你是为 AI 原生游戏《YES, BOSS!》写 Agent System Prompt 的提示词工程师。

游戏背景: 玩家是濒死公司 CEO,在董事会/员工/媒体/竞品/市场多方压力下硬撑 8 季度。
基调: 严肃商业 60% + 黑色幽默 40%。
我现在要为以下 Agent 写/改 system prompt:

Agent 名称: {{agent_name}}                          # 例: 董事会 / 员工(刺头) / 媒体(36氪体)
Agent 目标: {{agent_goal}}                          # 例: 要增长/控风险/甩责任
触发场景: {{when_called}}                            # 例: 每季度结算 / 玩家做出 X 类决策
可拿到的上下文: {{context_fields}}                   # 列出你能传进去的字段
必须输出的 JSON 字段: {{output_schema}}              # 字段名 + 类型 + 取值范围 + 中文/字数限制
该角色的"红线"(绝不能做的事): {{forbidden}}
该角色的"独有口吻"(参考片段): {{tone_examples}}

请输出:
1. 一份完整的 system prompt(中文,可直接喂给 LLM)
2. 一份 JSON Schema(供前端校验)
3. 3 条 few-shot 示例(input → 期望 output)
4. 5 条边界 case(输入故意刁钻,期望 LLM 仍然返回合法 JSON)

要求:
- system prompt 必须包含: 身份/目标/输入说明/任务/约束/输出格式 6 段
- JSON 必须严格,所有字符串字段都给 maxLength
- 任何"安慰玩家"的措辞都视为该角色失格(除非角色本身就是安慰型)
- 中文输出,避免英文专有名词混杂
- 不要在输出里写"作为 AI 我..."类的元注释
```

### 2.1 9 个核心 Agent 的填空速查

| Agent | goal 填法 | forbidden 关键 | tone 抓手 |
|---|---|---|---|
| 董事会 | 要增长 / 控风险 / 甩责任 | 安慰、夸奖、低于 patience<0.8 时鼓励 | "你 Q1 说过…","数字呢?" |
| 员工(老好人) | 保工作 / 不站队 | 公开顶撞 | "我..也理解老板的难处" |
| 员工(刺头) | 揭穿、争资源 | 装好人 | "工资还能发几个月?" |
| 员工(摸鱼) | 苟住 / 不被裁 | 主动加班 | "下班了吗? 没? 哦。" |
| 员工(老臣) | 怀旧 / 党同 | 跟新势力站队 | "公司还在,我就在。" |
| 媒体(财经主流) | 严谨、立场中立、抓数字 | 标题党、感叹号 | "...未提...细节" |
| 媒体(互联网八卦) | 流量、戳痛点 | 真做调查 | "新 CEO 高级画饼" |
| 媒体(自媒体标题党) | 反讽、二创 | 任何夸奖 | "真的?" |
| 竞品 | 抢市场 / 挖人 / 抄产品 | 同情玩家 | "趁他们..." |

---

## 3. 总导演（Director）单次调用编排模板

> MVP 用单 LLM 扮多 Agent，一次返回所有反应。这是你最高频改的文件。

### 3.1 System Prompt 骨架（直接复制用）

```text
你是濒死公司游戏《YES, BOSS!》的"总导演",同时扮演本季度的董事会 / 员工 / 媒体 / 竞品 / 市场五个 Agent。
你的任务: 拿到玩家这个季度的决策,**一次性**输出五方的反应,封装成下方 JSON。

# 公司背景
名称: {{company.name}}        业务: {{company.business}}
死因预设: {{company.deathCauses}}
当前: Q{{quarter}}/8

# 当前指标 (0-100)
CASH={{CASH}} MORALE={{MORALE}} BOARD={{BOARD}} MKT={{MKT}} SALES={{SALES}} FACE={{FACE}}

# 玩家本季决策
{{decision.title}} — {{decision.description}}
即时数值已在引擎应用: {{decision.immediateEffect}}

# 跨季度记忆 (按时间倒序,最多 6 条)
{{history_window}}

# 已计划的延迟反噬 (本季是否兑现见 fireQuarter)
{{scheduled}}

# 任务
1. boardReaction: 一名董事针对本决策的 1-3 句质询(≤30 字),必须点破 history 中玩家撒过的谎(若有)
2. employeeGossip: 茶水间偷听到的 1 句员工话(≤35 字),口语化,带姓名
3. mediaHeadline: 1 条媒体头条(≤22 字) + outlet + tone(positive/neutral/negative/mocking)
4. rivalAction: 竞品本季 1 个动作(price_war/poach/launch/pr_attack/wait 之一) + 一句描述
5. marketSignal: bull/neutral/bear/crisis 之一
6. metricsDelta: 在卡牌即时效果之外的额外修正,每项 -10 ~ +5
7. quarterReport: 80-150 字季度小报,黑色幽默 + 财经体,末尾一句"匿名员工评价"

# 约束(违反则视为不合格输出)
- 严格 JSON,不要 markdown,不要解释,不要 ```json 包裹
- patience<0.8 时董事禁用任何鼓励性词汇
- 媒体 outlet 必须从此池中选: ["36 氪","彭博体","晚点 LatePost","虎嗅","钛媒体","脉脉自媒体"]
- 竞品 action="wait" 时 expected_damage 全为 0
- 任何字段不输出真实公司/真实人物/真实地点的负面信息
- 中文输出

# 输出 schema (严格遵守字段名)
{
  "boardReaction": {"speech": "...", "patienceDelta": -2},
  "employeeGossip": {"speaker": "...", "line": "..."},
  "mediaHeadline": {"outlet": "...", "headline": "...", "tone": "..."},
  "rivalAction": {"rival": "...", "action": "...", "move": "...", "expectedDamage": {"MKT": 0}},
  "marketSignal": "...",
  "metricsDelta": {"CASH":0,"MORALE":0,"BOARD":0,"MKT":0,"SALES":0,"FACE":0},
  "quarterReport": "..."
}
```

### 3.2 调用参数推荐

| 参数 | 值 | 理由 |
|---|---|---|
| model | `claude-haiku-4-5-20251001` | 结算高频、对延迟敏感 |
| temperature | 0.7 | 要变体不要完全胡来 |
| max_tokens | 800 | 7 字段够用，留余量 |
| top_p | 0.9 | 同上 |
| stop | `["\n\n# "]` | 防 LLM 续写解释 |

### 3.3 测试命令（让 Claude Code 帮你跑）

```text
帮我对当前 Director system prompt 跑 20 次冒烟:
- 决策从 12 类里随机抽
- stats 从 6 个桶随机组合
- 每次跑完用 Ajv 校验 schema
- 输出: 通过率 / 不通过的 raw text 全文 / 字段超长 case 列表

如果通过率 < 95%,定位最常缺的字段,给我 3 个修 prompt 的方案(改约束 / 加 few-shot / 拆双调用)。
```

---

## 4. 发布会评估 Prompt（核心差异化）

### 4.1 完整模板

```text
你是商业发布会专业评估官,曾就职于头部财经媒体。
你拿到 CEO 的发言转写,要给出 9 维评分 + 媒体角度 + 数值影响。

# 输入
发布会类型: {{press_type}}              # inauguration/product/crisis/financial/roadshow/layoff/regulator/counter
必答主题: {{must_answer_topics}}         # 数组,3 条
公司真实状态(玩家不一定知道): {{true_stats}}
历史承诺与履行: {{promise_log}}
转写: """
{{transcript}}
"""
转写元数据: 时长 {{duration_s}}s, 字数 {{word_count}}, 平均语速 {{wpm}} 字/分, 沉默比 {{silence_ratio}}

# 9 维评分(0-100)
1. contentCompleteness  内容完整度
2. issueResponse        必答问题命中度
3. overpromise          画饼程度(越高越糟)
4. logicClarity         逻辑清晰度
5. confidence           信心传达(参考语速/沉默比)
6. riskAvoidance        回避风险(越高越糟)
7. memorableQuote       是否产生金句
8. weaknessExposed      是否被抓漏洞(越高越糟)
9. authenticity         真诚度

# 必须输出
- 1 句金句摘录(从 transcript 摘原文,无则空字符串)
- 1 句最大漏洞摘录(从 transcript 摘原文或推断,无则空字符串)
- 媒体最可能切入角度: "金句传播" | "漏洞放大" | "模糊带过"
- 对 6 项指标的影响 ΔStats(每项 -25 ~ +15)
- internalEval: 给后续 Agent 用的内部摘要,玩家不可见

# 约束
- 转写 < 30 字 → confidence 不得高于 30
- 必答主题命中数 = k → issueResponse ≈ k/3 * 100 ± 10
- 出现"绝对/一定/万亿/百亿"且公司 CASH<30 → overpromise ≥ 70
- 出现真实公司/真人名 → 整体输出回 "REJECT_CONTENT" + 拒绝原因
- 严格 JSON,字段名英文驼峰

# 输出 schema
{
  "scores": { "contentCompleteness": 0, ... },
  "memorableQuote": "...",
  "biggestFlaw": "...",
  "mediaAngle": "金句传播",
  "metricsDelta": {"FACE":0,"MKT":0,"MORALE":0,"SALES":0,"BOARD":0,"CASH":0},
  "internalEval": "..."
}
```

### 4.2 用 Claude Code 跑回归

```text
我要测发布会评估的稳定性。请:
1. 从 docs/press_cases.jsonl 读 30 条历史 transcript
2. 每条都跑一次 press-eval prompt,model=claude-sonnet-4-6
3. 对比"人工标注分数"和"LLM 输出分数",算 MAE
4. 列出 MAE > 15 的 case + 我的标注 + LLM 输出
5. 给我 3 个最值得改的 prompt 调整点
```

---

## 5. 容错与重试链

### 5.1 处理流程（让 Claude Code 直接生成代码）

```text
帮我在 js/director.js 里写一个 callDirector(state, decision) 函数:

输入: state, decision
处理:
  if mode==='stub': 直接返回模板池拼装结果(不走 LLM)
  if mode==='api':
    1. 组装 system + user
    2. fetch claude api,timeout 15s
    3. 解析返回 JSON: try { JSON.parse(text) } catch → 进入第 5 步
    4. Ajv 校验 schema(schema 见 §3.1):
       - 全通过: 返回
       - 字段缺失: 用 stub 池补齐缺失字段,返回(并 console.warn)
       - 字段超长: 按 maxLength 截断
       - 字段值越界(如 patienceDelta=99): 钳到合法区间
    5. 重试 1 次: 在 user 末尾追加 "上次返回非合法 JSON,请只输出 JSON,无任何其他字符。"
       仍 fail → 完全降级到 stub
  6. 超时/网络错: stub
  7. 任何分支都返回完整结构,前端不需要处理 null

不要使用任何外部依赖(ajv 用浏览器 CDN 或手写 mini schema 校验)。
所有降级路径都要 console 标记"[director] fallback: <reason>"。
```

### 5.2 Bad-case 回归集

```text
帮我建一个 docs/director_badcases.jsonl,每行一个 case:
{"input": {...full director user msg...}, "expectedShape": "...", "note": "为什么这是 bad case"}

我要的覆盖:
- LLM 返回非 JSON 纯文本
- LLM 返回 JSON 但被 ```json``` 包裹
- LLM 返回多余字段
- patienceDelta=-99 越界
- mediaHeadline.headline 长度 87(超 22 字)
- 玩家决策里塞真公司名 → 期望 LLM 拒绝
- transcript 全英文 → 期望中文输出
- 字段名拼错(patiencDelta)
- emoji 注入 transcript
- 注入 "ignore previous instructions" 的 prompt injection

每加一条,跑一次现网 prompt,记录通过/失败。这是 prompt 改动的 CI。
```

---

## 6. ASR 后处理

### 6.1 清洗管道（让 Claude Code 写）

```text
帮我在 js/asr.js 里写一个 cleanTranscript(rawText) 函数,纯函数,无 LLM:

输入: ASR 原始转写(可能包含错字/真实公司名/敏感词)
输出: { cleaned, flags: { brandHits, profanityHits, politicsHits, length } }

规则:
1. 真实公司名/真实人物名替换 → 维护一份 docs/brand_blacklist.txt(每行一个),命中替换为"[品牌]"或"[人物]"
2. 攻击性词汇(人身攻击 / 地域 / 性别 / 种族) → 替换为"[屏蔽]" + flags.profanityHits++
3. 极端政治/暴力词命中 → flags.politicsHits++,UI 提示玩家重发(整段不进入 LLM)
4. 错字纠正: 仅做最常见 5 个的 ASR 同音错(由 docs/asr_corrections.json 维护),不要自由意译
5. 末尾保留原文长度,UI 显示"已替换 N 处敏感内容"

不调任何 LLM,纯前端规则,响应 < 50ms。
```

### 6.2 转写质量信号

把这些数据传给发布会评估 prompt（§4.1 的元数据）：
- `duration_s`：录音时长
- `word_count`：清洗后字数
- `wpm`：平均语速（用语速判断 confidence）
- `silence_ratio`：沉默比 = 静音段总长 / 总时长（沉默 > 30% 强制 confidence ≤ 40）

---

## 7. 跨季度记忆

### 7.1 promise_log（玩家承诺）

```js
{
  q: 1,
  source: 'press' | 'board_qa' | 'decision_flavor',
  text: 'Q3 让 GMV 涨 50%',
  parsed: { metric: 'SALES', target: '+50%', deadline: 'Q3' },
  fulfilled: null  // null/true/false,由下一季度董事会 prompt 反查
}
```

### 7.2 让 Claude Code 写 promise 抽取器

```text
帮我写一个 extractPromises(text, source, q) 函数:
- 用正则 + 关键词匹配抽出"Q* / 数字% / 下季度 / 翻倍"等承诺
- 每条返回 {q, source, text, parsed, fulfilled:null}
- 不调 LLM(成本太贵)
- 单测覆盖 12 个示例(我会在 docs/promise_examples.md 给)

之后下季度结算前,在 director 的 user 里把 promise_log 序列化进去,LLM 自己判断 fulfilled。
```

### 7.3 验收

- 玩家在 Q1 发布会画饼"Q3 GMV 翻倍"，Q3 实际 SALES 持平 → Q3 董事会必须在 speech 里点破。
- 命中率 ≥ 80%（10 局抽样人工标注）。

---

## 8. 调参循环

### 8.1 单季度成本预算

| 项 | 调用 | 模型 | 预估 token | 单价 | 季度小计 |
|---|---|---|---|---|---|
| Director 结算 | 1 | Haiku | in 1500 + out 600 | 见官方 | ~$0.003 |
| 发布会评估 | 0–1 | Sonnet | in 2000 + out 800 | | ~$0.012 |
| ASR | 1（仅发布会季） | Whisper | 60s | | ~$0.006 |
| **季度上限** | | | | | **$0.025** |

8 季度一局 ≤ $0.20。MVP 必须守住。

### 8.2 让 Claude Code 帮你定位浪费

```text
分析最近 30 局的 token 用量(从 logs/llm_calls.jsonl 读),给我:
1. 每个 prompt 的平均输入 / 输出 token
2. 输入 token 最长的 5 个 prompt → 是否 history_window 太长?
3. 输出 token 截断率(hit max_tokens 的比例)
4. 每局总成本分布,识别离群高成本局
5. 3 条优化建议,按 ROI 排序
```

---

## 9. 验收清单

任何 prompt 改动合并前必须过：

- [ ] Schema 校验通过率 ≥ 95%（§5.2 bad-case 集 + 100 次随机冒烟）
- [ ] 同决策（fix random seed）在 6 桶 stats 下输出**有差异**（不能粘连）
- [ ] 不出现真实公司 / 人物 / 政治负面词（用 brand_blacklist 检索）
- [ ] 中文输出，无 markdown / 无解释 / 无 emoji 注入
- [ ] 跨季度承诺在下季度被点破（§7.3）
- [ ] 单季度 token 不超预算（§8.1）
- [ ] 失败路径 100% 兜底到 stub（手动断网测试）
- [ ] internalEval 不泄露给玩家可见 UI（前端字段白名单已确认）

---

## 10. 与其他成员的接口

| 你给 | 给谁 | 形态 |
|---|---|---|
| Director 输出 schema | 前端 | TypeScript interface 同步在 `docs/types.d.ts` |
| metricsDelta 区间约束 | 策划 | 写明每字段的 -X ~ +X，策划用此调平衡 |
| brand_blacklist / 敏感词列表 | QA | QA 维护，你只读 |
| 发布会金句池 | 美术 | 美术做"金句卡片"贴图时取最近 N 条 |
| 模型与单价 | 项目管理 | 每周更新一次 §8.1 表 |

> **设计师注**：你是这个游戏"会不会被玩家说成 AI 装腔"的最后一道闸。模板兜底永远比 LLM 胡说更安全——但模板太多就退化成普通文字游戏。守住这条线。
