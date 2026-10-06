# 🗺️ AI Agent 实战手册 · 更新迭代与创新计划（2026 Q4）

> 版本：v1.0（草案） · 制定日期：2026-10-06 · 适用周期：2026-10 ~ 2026-12
> 一句话目标：**把手册从「内容优秀的静态仓库」改造成「会自我保鲜的中文 Agent 知识基础设施」，并在 Q4 内达成 500 星。**

---

## 目录

- [Part 0 · 现状基线与诊断](#part-0--现状基线与诊断)
- [Part 1 · 迭代治理机制](#part-1--迭代治理机制)
- [Part 2 · 内容迭代计划](#part-2--内容迭代计划)
- [Part 3 · 版本路线图](#part-3--版本路线图)
- [Part 4 · 创新计划](#part-4--创新计划)
- [Part 5 · 增长配套动作](#part-5--增长配套动作)
- [Part 6 · 执行看板（W41–W52）](#part-6--执行看板w41w52)
- [Part 7 · 度量指标与验收](#part-7--度量指标与验收)
- [Part 8 · 风险、取舍与不做清单](#part-8--风险取舍与不做清单)

---

## Part 0 · 现状基线与诊断

### 0.1 基线数据（2026-10-06 实测）

| 维度 | 数值 | 状态 |
|------|------|------|
| Stars / Forks / Watchers | 41 / 3 / **0** | 🔴 订阅链路完全未启用 |
| Open Issues | 9 | 🟢 有真实互动，是资产 |
| 创建 / 最后提交 | 2026-08-24 / 2026-10-02 | 🟡 节奏待固化 |
| 章节数 | 25 章（编号 0–18、20–25、99，**缺 19**） | 🟡 编号断层 |
| 可运行示例 | 9 个 | 🟢 |
| 字数 / 代码行数 | 115,000+ 字 / 3,500+ 行 | 🟢 |
| 英文版 | 3 / 25 章（00、01、99） | 🔴 与「中英双语」定位不符 |
| Homepage 字段 | 空 | 🔴 MkDocs 站点已存在未填 |
| Topics | 15 个，缺 2026 热词 | 🟡 搜索发现性差 |
| 外部收录 | 0 个 awesome 清单 | 🔴 无被动曝光入口 |
| CI | docs.yml + links.yml | 🟡 只校验构建与链接 |
| 是否有 Release / Tag | 无 | 🔴 Radar「订阅更新」承诺无法兑现 |

### 0.1.1 执行进度快照（2026-10-06 晚更新）

> W41 当周完成的事项，用于追踪真实进度 vs 计划。

| 类别 | 已完成 | 进行中 | 待开始 |
|------|--------|--------|--------|
| **曝光基建** | Homepage ✅ · Topics ✅ · v1.2.0 Release ✅ · Branch Protection ✅ | Social Preview ⏳ | Discussions 🔲 |
| **CI/保鲜机制** | freshness.yml ✅ · examples-smoke.yml ✅ · stars-snapshot.yml ✅ · Check Links 修复 ✅ | — | — |
| **外部收录** | — | awesome PR 已提交 3/3（待合并） | HelloGitHub 🔲 |
| **Issue 治理** | #1–#9 全部关闭（链接修复完成） | — | — |
| **内容** | — | — | 第 11 章 MCP 重写 🔲 · 术语表 +30 词 🔲 |

### 0.2 三个核心判断

1. **内容不是瓶颈，分发是。** 全部 41 星里几乎不来自主动推广，而是自然搜索；而 Topics 缺失导致连自然搜索都没被充分命中。
2. **维护成本会随时间指数上升，现在就要把「保鲜」机制化。** Agent 领域内容半衰期约 3 个月——25 章里已有若干章的框架版本号、协议细节（尤其是第 11 章 MCP，2026-07 已转无状态核心）开始过时。
3. **最大的机会窗口是 SKILL.md。** 2026-10-01 Google 宣布弃用 Gems、全线转向 Agent Skills，SKILL.md 由此成为首个跨前沿实验室统一的 Agent 能力格式。**中文世界还没有一份系统讲 SKILL.md 的教程。**

### 0.3 北极星指标

| 指标 | 当前 | Q4 目标 | 说明 |
|------|------|---------|------|
| Stars | 41 | **500+** | 主指标 |
| Watchers | 0 | **50+** | 决定每期 Radar 的触达量 |
| 外部收录（awesome list） | 0 | **3 个** | 被动曝光的复利来源 |
| 章节总数 | 25 | **29+** | 补完 2026 技术栈缺口 |
| 示例代码 CI 通过率 | 未监控 | **100%** | 「实战手册」人设底线 |
| Radar 出刊准时率 | 已跳票 | **≥ 90%** | 周更是唯一的可信承诺 |

---

## Part 1 · 迭代治理机制

内容项目的死亡方式通常不是「写得差」，而是「停更」。所以先把机制立起来。

### 1.1 版本号规则

采用 `v主.次.修订`，语义如下：

| 变更类型 | 版本位 | 示例 |
|----------|--------|------|
| 新增整章（如第 26 章） | 次版本 +1 | v0.2 → v0.3 |
| 删章、重构目录、改变阅读路径 | 主版本 +1 | v0.x → v1.0 |
| 章节内容修订、错别字、配图、示例修复 | 修订 +1 | v0.2.0 → v0.2.1 |
| Radar 出刊 | 打 `radar-Wxx` tag | `radar-2026-W41` |

**每个 Release 的 Notes 必须包含三段**：本期新增、本期修订、下期预告。

### 1.2 每周固定节奏（一小时维护法）

| 时间 | 动作 | 耗时 | 产出 |
|------|------|------|------|
| 周一 | 跑 `scripts/refresh_stars.py`，生成本周框架星数快照 | 5 min | `data/stars.json` diff |
| 周三 | 扫一遍 Upstream：MCP / LangGraph / CrewAI / Claude Code 的 changelog | 20 min | 若 breaking change → 自动开 issue |
| 周四 | 写 Radar（用模板 `radar/TEMPLATE.md`，按数据填空） | 30 min | `radar/2026-Wxx.md` |
| 周五 | 发布：push + 打 `radar-Wxx` tag + Release draft | 5 min | 订阅者收到通知 |

> **关键点**：把 Radar 从「想到才写」变成「按模板填空」，是周更能坚持下去的唯一现实方案。

### 1.2.1 季度动作（每季度首周）

除周更外，每季度第一周额外做一次：

| 动作 | 耗时 | 说明 |
|------|------|------|
| 人工核查 `appendix/resources.md` 全部外链 | 30 min | 该文件被 `.lycheeignore` 排除（外链多 + 反爬多），必须人工点一遍，更新文件头的「最后人工核查」日期 |
| 重新跑一遍 glossary 时效性检查 | 20 min | 术语表中各框架版本号是否仍准确 |
| 检查 awesome list 收录状态 | 10 min | 之前提的 PR 是否被合并，是否有新的清单可以投 |

### 1.3 内容保鲜机制（新增 CI）

新增三条 GitHub Actions：

| Workflow | 触发 | 职责 |
|----------|------|------|
| `freshness.yml` | 每周一 03:00 UTC | 抓取各框架最新 release tag，与 `chapters/*.md` 头部声明的 `适配版本` 比对，不一致自动开 issue 并打 `stale` 标签 |
| `examples-smoke.yml` | 每周一 + 每次 PR | 在矩阵（py3.10/3.11/3.12）里 dry-run 全部 `examples/*/main.py`，挂了就打红 badge |
| `stars-snapshot.yml` | 每周五 | 自动更新 README 的「框架 Stars」表格，直接 commit & push 到 main |

**章节头部规范要求**（所有章节统一加 3 行 frontmatter）：

```markdown
---
适配框架版本: LangGraph 0.4.x
最后校验: 2026-10-06
上游变更监控: https://github.com/langchain-ai/langgraph/releases
---
```

> 这是本手册最容易被低估的差异化：**在一个人人都过时的领域里，"我知道我没过时"本身就是价值。**

### 1.4 质量红线（每次 PR 必检）

- [ ] 所有代码块至少一次真实执行通过（或显式标注「伪代码 / 示意」）
- [ ] 不出现未经核实的 star 数、性能数字（必须带采集日期）
- [ ] 新增术语必须进 `chapters/99-glossary.md`
- [ ] 中英术语首次出现处给出对照
- [ ] Mermaid 图在 GitHub 渲染下可正常显示

---

## Part 2 · 内容迭代计划

### 2.1 现有章节维护清单

按「过时风险 × 读者权重」排序，标出必须动的章节：

| 章节 | 主题 | 现状问题 | 迭代动作 | 优先级 |
|------|------|----------|----------|--------|
| **第 11 章** | MCP 协议 | 2026-07 MCP 转为完全无状态核心，去掉 `Mcp-Session-Id`；已捐给 Linux Foundation | **重写 30%**：新增无状态章节、SDK 迁移指引、Serverless 部署 | P0 |
| **第 0 章** | 新手快速入门 | 第一触点，转化率最高 | 加「3 分钟判断你该学哪条路线」决策图；加 SKILL.md 的一句话预告 | P0 |
| **第 15 章** | Token 成本优化 | 与第 27 章（上下文工程）边界重叠 | 收敛为「计费层省钱」，把压缩策略移交第 27 章，互相上调链接 | P1 |
| **第 18 章** | 选型决策树 | 未纳入 Skills / A2A 维度 | 决策树补两个分支：「要不要用 Skill」「要不要上 A2A」 | P1 |
| **第 25 章** | Harness Engineering | 已很好，但缺 Mods / Skills 新形态 | 增补一节「Harness 的三种形态：传统编排 / Skills / Mods」 | P1 |
| **第 5 章** | AutoGen | AutoGen 已演进为 Microsoft Agent Framework | 补 MAF 迁移对照表 | P1 |
| **第 9 章** | Claude Agent SDK | 8.0K 星偏低，与 Claude Code 生态脱节 | 改写成「Claude Code + Agent SDK」双轨，补 Mods 简介 | P2 |
| **第 7 章** | Dify | Langflow 已追平 | 加 Dify vs Langflow 对照小节 | P2 |
| **第 99 章** | 术语表 | 80+ 术语，缺 2026 新词 | 新增 30 词：SKILL.md、Context Engineering、Compaction、Agent Card、A2A、AG-UI、AP2、Guardrail、Evals、Harness… | P0 |
| 编号断层 | — | 缺第 19 章 | 用第 19 章填补：建议做「Agent 通用工具箱」或改为保留空号并注明 | P2 |

### 2.2 新增章节清单（补 2026 技术栈缺口）

| 编号 | 章节名 | 核心内容 | 配套示例 | 优先级 |
|------|--------|----------|----------|--------|
| **第 26 章** | **Agent Skills 编写实战** | SKILL.md 六个 frontmatter 字段与校验规则 · 目录契约（`scripts/` `references/` `assets/`）· description 写作法（写成「触发器」而非「摘要」）· 渐进式披露设计 · 手搓一个可发布 skill · 安全审查清单（读 `scripts/`、沙箱、凭证隔离） | `examples/10-agent-skill/` | **P0** |
| **第 27 章** | **上下文工程 Context Engineering** | 一次轮次的 token 构成（历史 46% / 检索 24% / 工具 18% / 系统 9% / 问题 3%）· Context Rot 原理 · Compaction · 结构化笔记 · 子 Agent 隔离（Anthropic 报告研究类评测 +90.2%）· JIT 检索 · 工具集收敛（46→15，工具定义 −67%） | `examples/11-context-lab/`（可视化 token 消耗） | **P0** |
| **第 28 章** | **A2A 与多 Agent 互联** | A2A v1.0 GA · Agent Card · 任务委派与结果交换 · 与 MCP 的分层边界 · 实战：两个不同框架的 Agent 互相调用 | `examples/12-a2a-bridge/` | P1 |
| **第 29 章** | **Agent 评测与安全治理** | GAIA / METR 长任务评测 · 黄金数据集与 LLM-as-Judge · 轨迹级评测（而非答案级）· Prompt 注入 · 最小权限 · Skill/Mods 安全审计 · 成本与步数上限策略 | `examples/13-eval-harness/` | P1 |
| **第 30 章**（备选） | Computer Use 与具身边界 | browser-use / UI-TARS 路线 · 截图到动作的稳定化技巧 · 何时不该用 GUI 自动化 | `examples/14-computer-use/` | P2 |
| **第 31 章**（备选） | 边缘与小模型 Agent | 端侧 SLM、量化、隐私场景 | 视时间 | P3 |

### 2.3 英文版策略调整

**诚实化**：主标题从「中英双语」改为「中文为主 · English in progress」，并在 `en/README.md` 顶部放翻译进度条。

**优先翻译顺序**（按国际读者搜索意图）：`00-quickstart` > `02-reaact-from-scratch`（手写 Agent，最普适）> `11-mcp` > `25-harness-engineering` > `99-glossary`。

> 理由：国际读者最想看的不是"又一个 LangGraph 教程"，而是「手写 Agent 的原理」和「Harness 工程」这两块稀缺内容。

---

## Part 3 · 版本路线图

### v0.2.0 — 保鲜与基建（2026-10 底）

**目标**：让仓库看起来「活着且被认真维护」。

- [ ] 补全 25 章的 frontmatter 版本声明
- [ ] 上线 `freshness.yml` / `examples-smoke.yml` / `stars-snapshot.yml`
- [ ] README 加三个动态 badge：CI 通过率、最后核验日期、Deps 版本
- [ ] 填补或声明第 19 章编号空缺
- [ ] 术语表补 30 个 2026 新词
- [ ] 填 Homepage、重设 Topics、开第一个 Release
- [ ] 第 11 章 MCP 重写（无状态化）

**验收**：README 首屏无任何过时信息；CI 三条全绿；出现第一个自动化保鲜 issue。

### v0.3.0 — Skills 与上下文（2026-11 中）

**目标**：吃下 2026 最大风口，产出两个别人没有的章节。

- [ ] 第 26 章 + `examples/10-agent-skill/`
- [ ] 第 27 章 + `examples/11-context-lab/`
- [ ] **创新项 C1：发布 `skills/agent-handbook` 官方 Skill 包**（详见 Part 4）
- [ ] 第 15 / 18 / 25 章联动修订
- [ ] 一键 Codespaces 环境（`.devcontainer/`）

**验收**：用户在自己的 Claude Code / Copilot 里能加载本手册 Skill；第 26 章能被至少一个 aggregator 收录或引用。

### v0.4.0 — 协作与治理（2026-11 底）

- [ ] 第 28 章 A2A + `examples/12-a2a-bridge/`
- [ ] 第 29 章评测与安全治理 + `examples/13-eval-harness/`
- [ ] **创新项 C3：横评对照数据集**发布首版
- [ ] 第 5 章 MAF 迁移、第 9 章 Claude Code 改写

**验收**：横评数据集含 ≥ 3 框架 × 5 任务的真实数据。

### v1.0.0 — 中文 Agent 知识基础设施（2026-12）

- [ ] **创新项 C2：handbook MCP Server 发布**
- [ ] 英文版补齐 5 章
- [ ] 目录重构：由「按框架」改为「按能力层」双索引（框架索引 + 能力层索引并存）
- [ ] `docs/` 升级为完整站点：搜索、版本切换、章节评分
- [ ] 治理：MAINTAINERS.md、章节所有权认领表

**验收**：非 Chinese-speaking 用户可在不看中文 README 的情况下完成入门。

---

## Part 4 · 创新计划

> 六个创新项按「差异化强度 / 实现成本」排序。前两项是本季度最值得押注的。

### 🔥 C1 · `skills/agent-handbook` — 把整本手册打包成一个 Skill

**是什么**：在本仓库内新增一个符合 Agent Skills 开放标准的 Skill 包，让任何人用一条命令就能把这套方法论装进自己的 Agent。

```
skills/
└── agent-handbook/
    ├── SKILL.md              # 入口：方法论总纲 + 渐进式路由
    ├── references/
    │   ├── framework-selection.md     # 选型决策树（按需加载）
    │   ├── context-engineering.md     # 上下文工程策略
    │   ├── harness-checklist.md       # Harness 五支柱核对表
    │   └── anti-patterns.md           # 常见反模式
    ├── scripts/
    │   ├── scaffold_agent.py          # 生成骨架工程
    │   └── estimate_context.py        # 估算当前 prompt 的 token 构成
    └── assets/
        └── decision-tree.md
```

**为什么这是最强的创新**：

1. **直接踩在 2026 最大风口上** —— Google 刚把 Gems 换成 Skills，`obra/superpowers` 295K 星、`anthropics/skills` 179K 星，市场正处于「什么是好 Skill」的认知真空。
2. **天然的双向导流** —— 每个安装者都成为潜在 star，且 Skill 本身就是最好的广告位。
3. **自我验证** —— 手册第 26 章讲"怎么写 Skill"，本仓库就是这个理论的最佳样例。教科书自带参考答案。
4. **零边际成本** —— 内容现成，只需按粒度拆成 `references/` 按需加载，反而强化了「渐进式披露」的教学主张。

**落地**：v0.3.0 首版 → 收集 issue 反馈 → v1.0.0 支持中英双语自动切换（`metadata.locale` 字段 + `references/zh/` `references/en/`）。

### 🔥 C2 · Handbook MCP Server — 让任意 Agent 能查询这本手册

**是什么**：一个 MCP Server，暴露三个能力：

| 能力 | 类型 | 说明 |
|------|------|------|
| `search_chapters` | Tool | 语义 + 关键词检索 25+ 章内容 |
| `get_chapter` | Resource | 按编号取全文 |
| `lookup_term` | Tool | 查术语表（中英对照） |

```bash
pipx install git+https://github.com/Xwh630/ai-agent-handbook#subdirectory=mcp-server
# 任意 MCP 客户端里接入后，Agent 就能回答"LangGraph 怎么做 checkpoint"并给出手册原文
```

**为什么**：本手册已有 `llms.txt`，再进一步就是让它**可被程序化查询**。这把"人读的文档"升级成"Agent 可消费的知识库"，且与第 11 章 MCP 互为样板。

**风险**：需要维护一个索引构建步骤；建议 v1.0.0 发布，避免过早分散精力。

### ⚡ C3 · 横评对照数据集 — 用真实数据替代主观推荐

**是什么**：设计 5 个标准化任务（如"带工具调用的问答"、"多步研究报告"、"失败后自恢复"），用 ≥ 3 个框架各实现一遍，公开跑出来的真实数据：

| 任务 | 框架 | 成功率 | 平均步数 | 输入 token | 输出 token | 成本(¥) | P50 延迟 |
|------|------|--------|----------|-----------|-----------|---------|----------|

**为什么**：市面上所有框架对比都是作者主观打分。**真实跑出来的对照数据是稀缺品**，会被大量引用和转载，是长尾曝光的永动机。

**落地**：v0.4.0 首版（3 框架 × 5 任务），每季度重跑一次并更新时间戳。

### 💡 C4 · 保鲜可视化 — 「本页最近核验于 X 天前」

每章顶部渲染一个由 CI 自动更新的核验状态：

```
✅ 2026-10-06 校验通过 · LangGraph 0.4.2 · 示例代码 CI 绿
```

**为什么**：Agent 教程的最大痛点是"我照着做却跑不通"。把"可信任度"做成可见的产品特性，这在中文技术文档里几乎没人做过。

### 💡 C5 · Radar 数据自动化

`scripts/refresh_stars.py` 每周抓取核心仓库 star 数与 release tag，自动生成：
- README 框架表的 diff PR
- Radar 的榜单段落
- `data/stars-history.csv`（可画 Star History 之外的时间序列）

**把「每周写 Radar」的成本从 2 小时压到 30 分钟**，是周更能坚持的工程保障。

### 💡 C6 · 术语表对外发布

把 `99-glossary.md` 拆成结构化 `terms.json`（term / en / zh / aliases / chapter / example），发布为一个可被他人引用的小数据集 + 简易查询页。

**为什么**：中英 Agent 术语至今没有事实标准。谁先提供机器可读的版本，谁的链接就会出现在别人的项目里。

---

## Part 5 · 增长配套动作

### 5.1 曝光基建（本周内，零成本）

| 动作 | 位置 | 说明 |
|------|------|------|
| 填 Homepage | Settings → About | `https://xwh630.github.io/ai-agent-handbook/` |
| 重置 Topics | Settings → Topics | **新增**：`agent-skills` `context-engineering` `a2a` `claude-code` `codex-cli` `llm-agents` `llms-txt` `agent-ops` `chinese-tutorial`；**移除**：`deep-learning` `machine-learning` |
| Social Preview | Settings → Social preview | 1280×640 OG 图，含标语与章节数 |
| 开 Watch + 首个 Release | Releases | v0.2.0，Notes 分三段 |
| 启用 Discussions | Settings | 开 Q&A / Show and tell / Radar 讨论三个分类 |

### 5.2 外部收录（长期复利）

| 目标清单 | Stars | 切入方式 | 状态 |
|----------|-------|----------|------|
| `e2b-dev/awesome-ai-agents` | 29.6K | PR：新增「Books & Handbooks」分区 | 🚧 [PR #1693](https://github.com/e2b-dev/awesome-ai-agents/pull/1693) 已提交，待合并 |
| `kyrolabs/awesome-agents` | 2.8K | PR：新增 Books & Learning Resources 分区 | 🚧 [PR #821](https://github.com/kyrolabs/awesome-agents/pull/821) 已提交，待合并 |
| `EmbraceAGI/awesome-chatgpt-zh` | 11.7K | PR：Coding Agents 学习资源表 | 🚧 [PR #106](https://github.com/EmbraceAGI/awesome-chatgpt-zh/pull/106) 已提交，待合并 |
| HelloGitHub | — | 自荐投稿，中文项目转化率高 | 🔲 待投稿 |
| 阮一峰科技周刊 | — | 自荐 | 🔲 待投稿 |

> 一次 PR ≈ 永久曝光位。**这是 ROI 最高的单一动作，优先级高于写第 27 章之外的任何内容。**

### 5.3 内容分发

| 渠道 | 形式 | 频率 |
|------|------|------|
| 掘金 / 知乎 | 从新章节拆出单篇深度文（如《SKILL.md 到底该怎么 description》） | 每章 1 篇 |
| V2EX / 小红书 | Radar 单条亮点短帖 | 每周 1-2 条 |
| Reddit r/LLMDevs、r/LocalLLaMA | 英文介绍 + 第 26 章亮点 | 每月 1 次 |
| 公众号 / 社群 | 转发 Radar | 每周 1 次 |

---

## Part 6 · 执行看板（W41–W52）

| 周次 | 日期 | 内容产出 | 工程/机制 | 增长动作 |
|------|------|----------|-----------|----------|
| **W41** ✅ | 10-06 ~ 10-12 | Radar 第 2 期（已备好）· README 重构（已备好） | `refresh_stars.py` ✅ · `freshness.yml` ✅ · `examples-smoke.yml` ✅ · `stars-snapshot.yml` ✅ · Check Links 修复 ✅ · Branch Protection ✅ | Homepage ✅ · Topics ✅ · v1.2.0 Release ✅ · Issue #1–#9 全部关闭 ✅ |
| **W42** 🚧 | 10-13 ~ 10-19 | 第 11 章 MCP 重写（无状态化）· 术语表 +30 词 | — | **awesome PR 3/3 已提交**（e2b-dev #1693 · EmbraceAGI #106 · kyrolabs #821，待合并） |
| **W43** 🔲 | 10-20 ~ 10-26 | Radar 第 3 期 · **第 26 章 Agent Skills 初稿** | — | 掘金/知乎首发 SKILL.md 长文 |
| **W44** | 10-27 ~ 11-02 | 第 26 章定稿 + `examples/10-agent-skill/` | v0.2.0 Release | HelloGitHub 投稿 |
| **W45** | 11-03 ~ 11-09 | Radar 第 4 期 · **C1 Skill 包设计与拆分** | `.devcontainer/` 一键环境 |  |
| **W46** | 11-10 ~ 11-16 | **第 27 章上下文工程** + `examples/11-context-lab/` | `stars-snapshot.yml` 上线 | 发「一次轮次 token 构成」图帖 |
| **W47** | 11-17 ~ 11-23 | Radar 第 6 期 · **C1 Skill 包发布** | v0.3.0 Release | Skill 生态自荐（提交到各 registry） |
| **W48** | 11-24 ~ 11-30 | 第 28 章 A2A + `examples/12-a2a-bridge/` |  | Reddit 英文帖 |
| **W49** | 12-01 ~ 12-07 | Radar 第 8 期 · **C3 横评数据集设计** | 评测脚本框架 |  |
| **W50** | 12-08 ~ 12-14 | 第 29 章评测与治理 · 横评首批数据 | v0.4.0 Release | 横评数据图发布 |
| **W51** | 12-15 ~ 12-21 | Radar 第 10 期 · C2 MCP Server 开发 | `mcp-server/` 目录 |  |
| **W52** | 12-22 ~ 12-28 | 英文版补至 5 章 · 目录双索引重构 | **v1.0.0 Release** | 年度盘点：一年 12 期 Radar |

> 每周 Radar 不可跳过；若某周时间不够，**优先保 Radar、延后章节**，因为"稳定更新"这个信号本身的价值高于单章内容。

---

## Part 7 · 度量指标与验收

### 7.1 指标看板（每月复盘一次）

| 类别 | 指标 | 采集方式 |
|------|------|----------|
| 增长 | Stars / Forks / Watchers | GitHub API + `scripts/refresh_stars.py` |
| 触达 | README 浏览量、克隆数 | GitHub Insights Traffic |
| 曝光 | 引荐来源（referrers） | GitHub Insights Referrers |
| 健康 | CI 通过率、stale issue 数 | Actions 面板 |
| 内容 | 章节完成数、示例可运行率 | 人工/脚本统计 |
| 社区 | Issue 响应时长、PR 合并数 | GitHub Insights |

### 7.2 阶段验收线

| 节点 | Star | 硬性验收条件 |
|------|------|--------------|
| 10 月底 | 80–100 | CI 三件套上线 + 至少 1 个 awesome 收录 + Radar 出到第 4 期 |
| 11 月底 | 200–300 | 第 26/27 章上线 + C1 Skill 包发布 + 至少 2 个 awesome 收录 |
| 12 月底 | 500+ | v1.0.0 + C2 MCP Server + 英文 5 章 + Radar 出满 12 期 |

---

## Part 8 · 风险、取舍与不做清单

### 8.1 主要风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| **周更中断** | Watchers 流失、可信度崩塌 | Radar 模板化 + 数据自动抓取，把单期成本压到 30 分钟 |
| **追新导致章节速朽** | 维护成本失控 | 用 frontmatter 版本声明 + `freshness.yml` 自动标记，而非手动追版 |
| **精力分散在太多创新项** | 全部半途而废 | 严格串行：C1 → C3 → C2，前一个上线才开下一个 |
| **英文版长期滞后** | 定位被质疑 | 明确定位为「翻译中」并按优先级只翻 5 章 |
| **示例跑不通** | 口碑反噬最严重的一项 | `examples-smoke.yml` 每周一跑，挂了就打红标 |

### 8.2 明确不做的事

- ❌ **不做付费墙 / 知识星球变现** —— 早期阶段 Star 比收入值钱得多，任何门槛都会打断传播
- ❌ **不做视频课程** —— 成本极高、复用率低；先用文字 + 图表验证选题
- ❌ **不追所有新框架** —— 新框架月月有，只收录有真实生产落地证据的
- ❌ **不为了凑数写章节** —— 宁可保持 25 章高质量，也不要 40 章注水的
- ❌ **不做中文之外的第二语言扩张（日语/西语）** —— 英文版完成前不启动

### 8.3 一句话优先级

> **如果某周只能做一件事，就做让更多陌生人看到它的事。**
> 如果只能写一件事，就写 Skills（第 26 章）—— 它同时满足「2026 最热」「中文最稀缺」「与手册定位最贴合」三个条件。

---

## 附录 A · 立即执行的 checklist

```
[ ] 1. Settings → Homepage 填 https://xwh630.github.io/ai-agent-handbook/
[ ] 2. Settings → Topics：+ agent-skills context-engineering a2a claude-code
        codex-cli llm-agents llms-txt agent-ops chinese-tutorial
        - deep-learning machine-learning
[ ] 3. Settings → Social preview 上传 1280×640 OG 图
[ ] 4. Settings → Discussions：开 Q&A / Show and tell / Radar
[ ] 5. 上传 Radar 第 2 期（radar/2026-W41.md + radar/README.md）
[ ] 6. 上传重构版 README.md 与 llms.txt
[ ] 7. 自己 Watch → Releases only
[ ] 8. Releases → 打 v0.2.0
[ ] 9. 给 e2b-dev/awesome-ai-agents 提收录 PR
[ ] 10. 开始写第 26 章
```

---

> 📄 本文件随 v0.2.0 起纳入仓库，每月最后一个周五更新一次进度。
> 维护者更新记录见 `MAINTAINERS.md`。
