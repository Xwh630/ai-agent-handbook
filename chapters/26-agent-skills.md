---
适配框架版本: Agent Skills 规范 2026-10（agentskills.io）
最后校验: 2026-10-06
上游变更监控: https://agentskills.io/specification
---

# 第 26 章：Agent Skills 编写实战 — 把你的经验打包成一个文件

> **Agent Skills** 是 2026 年 Agent 领域最值得投入的一件事：一份 Markdown 文件，约 100 token 的启动成本，却能在 20 多个不同客户端里复用。2026-10-01，Google 宣布弃用 Gems、全线转向 Agent Skills——这是第一次有前沿实验室在自己的全线产品上采用"竞争对手发起的开放标准"。
>
> 本章逐字段拆解 SKILL.md 规范，讲清楚它为什么能用这么低的成本换来这么高的复用率，然后手搓一个真正能发布的 skill，最后给出一套写完必过的安全与性能自检清单。

---

## 26.1 什么是 Agent Skill？先从一个场景讲起

假设你带一个新人。他聪明、学得快，但对你们团队的规矩一无所知。你会怎么做？

大概率是给他一份文档：

> 「提交 PR 前必须跑 `make lint`；commit message 用 Conventional Commits；不要直接改 `main`；我们不用 tabs 用四个空格……」

这份文档只有几百字，但它能把这个新人从"会写代码的通才"变成"能在这个团队干活的专才"。**Agent Skill 就是这份文档，只不过读它的是 Agent。**

正式地说：

> **Agent Skill 是一个可移植的能力包**——一个目录，核心是一个 `SKILL.md` 文件，可选带上脚本、参考文档和模板。它把某个领域的做事方法固化下来，让任意兼容的 Agent 客户端都能即插即用。

### 它长什么样

一个最简的 skill，**只有一个文件**：

```
my-first-skill/
└── SKILL.md          ← 就这么简单
```

一个完整的 skill：

```
release-notes/
├── SKILL.md              # 必需：frontmatter 元数据 + 指令正文
├── scripts/              # 可选：可执行脚本
│   └── collect_commits.py
├── references/           # 可选：按需加载的参考文档
│   └── style-guide.md
└── assets/               # 可选：模板与静态资源
    └── template.md
```

**没有一个字节是编译产物。** 这就是它传播得快的原因——你可以直接 `git clone`、可以直接在网页上读、可以用 diff 看版本变化。

---

## 26.2 为什么是现在？半年统一全行业的时间线

| 时间 | 事件 |
|------|------|
| 2025-10-16 | Anthropic 推出 Agent Skills |
| 2025-12-18 | 格式作为开放标准发布（[agentskills.io](https://agentskills.io)） |
| 2026 上半年 | Cursor、GitHub Copilot、Goose、OpenHands、Amp 等陆续支持 |
| **2026-10-01** | **Google 宣布弃用 Gems，全线转向 Agent Skills** |

Google 的退场时间表已经公布：consumer Gems 2026-11 → Workspace Gems 2027-03 → Edu Gems 2027-06，现有 Gems 自动转换为 Skills。

**生态体量**（GitHub API 实测，2026-10-05）：

| 仓库 | Stars |
|------|-------|
| [obra/superpowers](https://github.com/obra/superpowers) | 295,590 ⭐ |
| [anthropics/skills](https://github.com/anthropics/skills) | 179,764 ⭐ |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 101,480 ⭐ |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)（对照组） | 91,017 ⭐ |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | 25,924 ⭐ |

> **一句话理解：MCP 统一了「Agent 怎么连工具」，SKILL.md 正在统一「Agent 怎么装知识」。前者管手，后者管脑。**

### 一个值得琢磨的现象

GitHub Trending 上有个仓库叫 `mattpocock/skills`，275K 星。它是什么？

**一个开发者把自己的 `.agents` 配置文件夹发成了仓库。**

Matt Pocock 是 TypeScript 教育者，他没写框架、没写模型，只是把自己踩过的坑整理成 skill 目录。**在 Agent 时代，"你踩过的坑"本身就是资产。**

这对本手册的读者意味着一件很实际的事：**你不需要造轮子才能在这个生态里有位置，你只需要把你的经验结构化。**

---

## 26.3 SKILL.md 规范：六个字段，逐个拆

`SKILL.md` 由两部分组成：**YAML frontmatter**（元数据）+ **Markdown 正文**（指令）。格式无魔法，但字段约束很硬。

### 26.3.1 字段总表

| 字段 | 必需 | 约束 | 作用 |
|------|------|------|------|
| `name` | ✅ | 1–64 字符，只能小写字母/数字/连字符，不能以连字符开头或结尾，不能连续连字符，**必须与父目录名一致** | skill 的唯一标识 |
| `description` | ✅ | 1–1024 字符，非空。既要说清做什么，也要说清**什么时候用** | 决定 Agent 会不会选中它 |
| `license` | ❌ | 许可证名称，或指向包内许可证文件 | 法律信息 |
| `compatibility` | ❌ | 1–500 字符，环境要求（依赖的系统包、网络访问、目标产品等） | 准入条件 |
| `metadata` | ❌ | 任意 string→string 键值对 | 客户端自定义扩展位 |
| `allowed-tools` | ❌ | 空格分隔的预授权工具列表（**实验性**，各实现支持不一） | 减少授权弹窗 |

### 26.3.2 `name`：最容易犯低级错误的地方

```yaml
# ✅ 合法
name: pdf-processing
name: data-analysis
name: code-review

# ❌ 非法：大写
name: PDF-Processing
# ❌ 非法：以连字符开头
name: -pdf
# ❌ 非法：连续连字符
name: pdf--processing
# ❌ 非法：与父目录名不一致
name: pdf-processing      # 而目录叫 pdf-tools/
```

> ⚠️ **`name` 必须与父目录名完全一致。** 这是新手最常踩的坑——客户端靠目录名发现 skill，靠 frontmatter 校验，两者不一致时行为未定义，有的客户端直接忽略，有的报错。

### 26.3.3 `description`：整个 skill 里 ROI 最高的一行

**这是最重要的一句话：`description` 是 skill 唯一的"投放开关"。**

Skill 被激活前，Agent 只看到 name + description（这就是下一节的 Advertise 阶段）。**写得不好，你的 skill 永远不会被调用，正文写得再漂亮也没用。**

```yaml
# ❌ 糟糕：Agent 判断不出什么场景该用它
description: Helps with PDFs.

# ✅ 优秀：说清做什么 + 什么时候用 + 埋了检索关键词
description: >
  Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user
  mentions PDFs, forms, or document extraction.
```

**写 description 的三条规则：**

1. **必须回答"什么时候用"** —— 只写"做什么"，Agent 缺少触发条件，会倾向于不用
2. **埋用户真实会说的词** —— Agent 是靠语义匹配找 skill 的。用户说"发票"时，你的 description 里最好有"invoice"或"发票"
3. **不要超过 1024 字符** —— 但也不用写满，150–300 字符通常是甜点区

> 💡 **一个技巧**：把你的 description 当成搜素引擎的关键词广告位。问自己——"用户遇到这个问题时，会用哪句话描述？"把那句话原样写进去。

### 26.3.4 `compatibility`：什么时候需要写

规范的原话是"大部分 skill 不需要这个字段"。只在以下情况写：

```yaml
# 需要特定运行时
compatibility: Requires Python 3.14+ and uv
# 需要系统包
compatibility: Requires git, docker, jq, and access to the internet
# 只在特定客户端有意义
compatibility: Designed for Claude Code (or similar products)
```

### 26.3.5 `metadata`：给未来的自己留扩展位

```yaml
metadata:
  author: Xwh630
  version: "1.0"
  repo: https://github.com/Xwh630/ai-agent-handbook
```

规范建议**键名要足够独特**，避免和别人的键冲突（比如别用 `mcp` 这种通用词，用 `aah_mcp` 之类）。

### 26.3.6 `allowed-tools`：实验性，别指望它跨平台

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

空格分隔，用来预先授权某些工具、减少运行时弹窗。**但规范明确标了"Experimental"，各客户端支持程度不一。** 建议：写了兜底，但正文里也要说明"若未自动授权，需用户手动批准"。

---

## 26.4 核心机制：渐进式披露（Progressive Disclosure）

这是 Skills 能用 ~100 token 启动的秘密，**也是本章最该理解的一节**。

### 四阶段加载模型

```
┌────────────────────────────────────────────────────────────────────┐
│ 第 1 阶段 · Advertise（常驻）                                       │
│   内容：所有 skill 的 name + description                            │
│   成本：每个 skill 约 100 token                                     │
│   时机：每次运行开始时就注入 system prompt                          │
│   ⇒ 20 个 skill ≈ 2,000 token 常驻，这是你唯一必付的固定成本        │
├────────────────────────────────────────────────────────────────────┤
│ 第 2 阶段 · Load（按需）                                            │
│   内容：命中任务的那个 skill 的 SKILL.md 正文                       │
│   成本：建议 < 5,000 token                                          │
│   时机：Agent 判断任务匹配后，调 load_skill                         │
├────────────────────────────────────────────────────────────────────┤
│ 第 3 阶段 · Read resources（按需）                                  │
│   内容：references/ 下的文档、assets/ 下的模板                      │
│   成本：按实际读取的文件计                                          │
│   时机：Agent 调 read_skill_resource                                │
├────────────────────────────────────────────────────────────────────┤
│ 第 4 阶段 · Run scripts（按需）                                     │
│   内容：scripts/ 下的可执行代码                                     │
│   成本：脚本本身不进上下文，只有 stdout 回来                        │
│   时机：Agent 调 run_skill_script                                   │
└────────────────────────────────────────────────────────────────────┘
```

三个工具的行为还要留意：

| 工具 | 何时被广告给 Agent |
|------|-------------------|
| `load_skill` | **始终**广告 |
| `read_skill_resource` | 仅当至少一个 skill 有 resources 时 |
| `run_skill_script` | 仅当至少一个 skill 有 scripts 时 |

> ⚠️ **这意味着：如果你的 skill 里 `scripts/` 目录是空的，Agent 连"我能跑脚本"这个能力都不知道。** 反过来，一旦你放了脚本，所有 skill 共享这个能力。设计 skill 集合时要意识到这个全局副作用。

### 一个反直觉的结论

看到这个模型，很多人第一反应是"把所有细节都塞进 SKILL.md"。**错了。正确做法是相反的：**

| 内容类型 | 应该放哪 | 理由 |
|---------|---------|------|
| 通用工作流、决策路径 | `SKILL.md` 正文 | 命中就必须要看的东西 |
| 详细 API 参考、边界条件大全 | `references/` | 只有遇到具体问题才需要 |
| 输出模板、表单样例 | `assets/` | 原文搬运，不需要"理解" |
| 确定性逻辑（解析、计算、格式转换） | `scripts/` | **交给代码执行，别让模型算** |

最后一行特别重要：**能写成脚本的，不要写成自然语言指令。** 让 LLM 手算一个复杂字符串变换，既慢又容易错；一个 30 行的 Python 脚本，零 token 成本且完全可靠。

### 硬红线

规范建议：**`SKILL.md` 保持在 500 行以内**，超出部分拆到 `references/`。

> Agent 一旦决定加载，会**整篇读进上下文**。你写的每一个字，用户都要用 token 付账。

---

## 26.5 手搓一个能发布的 skill

我们做一个真实有用的：`release-notes` —— 从 git 提交历史生成结构化的版本更新说明。

### 26.5.1 目录搭建

```
release-notes/
├── SKILL.md
├── scripts/
│   └── collect_commits.py
├── references/
│   └── style-guide.md
└── assets/
    └── template.md
```

### 26.5.2 写 `SKILL.md`

```markdown
---
name: release-notes
description: >
  Generate structured release notes from git commit history between two
  refs. Use when the user asks to write release notes, a changelog, a
  version summary, "what changed since v1.2.0", or preparing release
  announcements.
license: MIT
compatibility: Requires git and Python 3.10+
metadata:
  author: your-name
  version: "1.0"
---

# Release Notes Generator

Turn raw git history into a changelog humans actually want to read.

## Workflow

1. **确定范围**。问清或推断两个 ref；若用户没给，默认 `<latest-tag>..HEAD`。
   - 查标签：`git tag --sort=-v:refname | head -5`
   - 若仓库无标签，回退到最近 30 个提交，并明确告知用户。

2. **收集原始数据**。运行打包脚本，不要自己拼命令：

   ```bash
   python3 scripts/collect_commits.py <base-ref> <head-ref>
   ```

   脚本输出 JSON 数组，每个元素含 `hash` `author` `date` `type` `scope` `subject`。
   **脚本已经做好了 Conventional Commits 解析**，不要重复解析它的输出。

3. **归类**。按 `type` 分组，映射如下：

   | type | 章节标题 |
   |------|---------|
   | feat | ✨ 新特性 |
   | fix | 🐛 修复 |
   | perf | ⚡ 性能 |
   | docs | 📖 文档 |
   | refactor / chore / test | 🔧 内部变更（折叠在最后） |

4. **改写为读者视角**。这是本 skill 的核心价值——**不要搬运 commit subject**：
   - ❌ `fix(db): fix nil pointer when conn closed`
   - ✅ 修复了数据库连接意外关闭时的空指针崩溃

5. **套模板**。读 `assets/template.md` 获取输出骨架。

## 写作规范

正文风格、语气、Breaking Changes 的写法，见 `references/style-guide.md`。
**只在需要写 Breaking Changes 或拿不准语气时才读它。**

## Edge cases

- 若区间内没有任何提交：明确告知用户，不要生成空模板。
- 若存在合并提交且 message 为空：跳过，不要写"更新代码"。
- 若同一功能有多条相关修复：合并成一条，不要罗列。
- **永远不要编造 commit。** 脚本没返回的改动，一律不写。
```

**逐段讲讲为什么这么写：**

| 写法 | 原因 |
|------|------|
| description 里写了 5 种触发说法 | 覆盖用户真实表达方式（"changelog"/"what changed since..."/"发布公告"） |
| 明确要求用打包脚本，而不是让 Agent 自己拼 git log | 解析逻辑固化到代码，行为稳定、零幻觉 |
| 说清"不要重复解析脚本的输出" | 防止 Agent 做无用功 |
| "只在需要写 Breaking Changes 时才读 style-guide" | 控制第 3 阶段加载，给 Agent 的行为画清边界 |
| Edge cases 四条 | 覆盖了 90% 的实际翻车场景 |

### 26.5.3 写 `scripts/collect_commits.py`

```python
#!/usr/bin/env python3
"""Collect and parse commits between two refs into structured JSON.

Usage: python3 collect_commits.py <base-ref> <head-ref>
"""
import json
import re
import subprocess
import sys

SEP = "\x1f"
PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$"
)


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse(raw: str) -> list[dict]:
    commits = []
    for line in raw.strip().splitlines():
        if not line:
            continue
        hash_, author, date, subject = (line.split(SEP) + [""] * 4)[:4]
        match = PATTERN.match(subject)
        if match:
            commits.append({
                "hash": hash_[:8],
                "author": author,
                "date": date,
                "type": match.group("type"),
                "scope": match.group("scope") or "",
                "breaking": bool(match.group("breaking")),
                "subject": match.group("subject"),
            })
        else:
            # 非 Conventional Commits 格式，保留原文交给上层判断
            commits.append({
                "hash": hash_[:8], "author": author, "date": date,
                "type": "other", "scope": "", "breaking": False,
                "subject": subject,
            })
    return commits


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    base, head = sys.argv[1], sys.argv[2]
    fmt = SEP.join(["%h", "%an", "%ad", "%s"])
    raw = run(["git", "log", f"{base}..{head}",
               f"--pretty=format:{fmt}", "--date=short"])
    print(json.dumps(parse(raw), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

**这个脚本体现了 skill 脚本的四条原则：**

1. **自包含** —— 只用标准库，无第三方依赖
2. **错误信息友好** —— 告诉用户怎么修，不是抛一个 traceback
3. **边界处理** —— 非 Conventional Commits 的提交不丢弃，标记为 `other`
4. **输出结构化** —— JSON，方便 Agent 消费（也方便人 debug）

### 26.5.4 写 `references/style-guide.md`

这里放**只有写 Breaking Changes 时才需要看的**内容：语气示例、好/坏样例对比、Breaking Changes 段的固定写法。**放这里而不是正文，是为了让普通任务不付这笔 token。**

### 26.5.5 写 `assets/template.md`

```markdown
## v{version} · {title}

> 发布日期：{date} · 提交数：{count}

### ✨ 新特性
- ...

### 🐛 修复
- ...

### 💥 Breaking Changes
{若无可删除本节}

**升级指引**：...
```

---

## 26.6 Token 预算：给你的 skill 定个红线

写 skill 本质上是在做预算分配。建议的红线：

| 层级 | 预算 | 超了怎么办 |
|------|------|-----------|
| frontmatter `description` | 150–300 字符 | 精简触发词，保留最高效的说法 |
| `SKILL.md` 正文 | **< 5,000 token（约 < 500 行）** | 拆到 `references/`，正文只留入口 |
| 单个 reference 文件 | < 2,000 token | 继续拆分，按主题切 |
| 常驻总成本（N 个 skill） | N × ~100 token | 超过 30 个 skill 要考虑分组加载 |

**估算方法（无需工具）**：中文约 1 字 ≈ 1.5 token，英文约 1 词 ≈ 1.3 token。500 行中文正文大约在 3,000–5,000 token 区间，正好卡在红线上。

> ⚠️ **一个常见错误**：把整个 API 文档塞进 SKILL.md。正确做法是正文写「需要时读 `references/api.md`」，Agent 只在真正需要时才付这笔钱。

---

## 26.7 安全：SKILL.md 是说明书，`scripts/` 才是执行体

这一节请认真读，它是本章唯一可能让你付出真实代价的部分。

Snyk 扫描了 **3,984 个 skill**，结果：**36.82% 至少携带一个安全缺陷**，而且 **skill 默认不在沙箱中运行**。

### 威胁模型

```
┌────────────────────────────────────────────────────────┐
│  你读 SKILL.md    → 读的是说明书，安全                 │
│  你跑 scripts/    → 跑的是代码，等同执行任意程序       │
│                                                        │
│  skill 以你的完整用户权限运行：                        │
│   · 读写你能读写的任何文件                             │
│   · 读取全部环境变量（含 API Key）                     │
│   · 观察每一次 prompt 和工具调用                       │
│   · 发起任意网络请求                                   │
└────────────────────────────────────────────────────────┘
```

### 使用第三方 skill 的三条铁律

1. **装前先读 `scripts/` 里的代码** —— 不要只看 SKILL.md 写得专业就信任它。`SKILL.md` 是广告，`scripts/` 是产品。
2. **生产环境优先 `--safe-mode` 或容器** —— 涉及凭证的任务，绝对不要同时加载来源不明的 skill。
3. **只从可信源安装** —— star 数不等于安全性。

### 自查：如果你要发布自己的 skill

| 检查项 | 要求 |
|--------|------|
| 是否有网络请求？ | 必须在 `SKILL.md` 正文明示，说明访问哪些域名 |
| 是否读环境变量？ | 必须声明，且只允许读明确命名的变量 |
| 是否有写文件操作？ | 限制在明确目录下，禁止路径穿越 |
| 脚本是否有 `--dry-run`？ | 破坏性操作的脚本**建议提供** |

> 📖 Agent 安全的系统化治理见本手册后续的「Agent 安全治理」专章；本章聚焦 skill 这一层。

---

## 26.8 分发：装到哪些客户端、放在哪个目录

Skills 是文件系统层的开放标准，各客户端约定不同的扫描路径：

| 客户端 | 常见安装位置 |
|--------|-------------|
| Claude Code / Claude.ai | `~/.claude/skills/` 或项目级 `.claude/skills/` |
| OpenAI Codex CLI | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |
| Microsoft Agent Framework | 代码内配置 `AgentSkillsProvider` 指向任意目录 |
| 其他（Goose / OpenHands / Amp / Tabnine / Roo Code / JetBrains Junie / Qodo / Spring AI / Snowflake Cortex Code / Pulumi Neo / OpenClaw / Atlassian / Figma / Command Code） | 各自配置，参考客户端文档 |

> ⚠️ **路径会随版本变化。** 上面列出的是 2026-10 的通用约定，安装前请以客户端最新文档为准。

### 建议的仓库布局

如果你的 skill 想被别人方便安装，推荐这样组织：

```
your-skills-repo/
├── README.md                 # 目录 + 每个 skill 一句话介绍
├── release-notes/
│   └── SKILL.md
├── code-review/
│   └── SKILL.md
└── install.sh                # 软链接或复制到目标客户端目录
```

**为什么每个 skill 单独一个顶层目录？** 因为 `name` 必须与父目录名一致，而安装时用户通常是把某个目录整个拷进 skills 目录。

---

## 26.9 常见错误与排查

| 症状 | 原因 | 解法 |
|------|------|------|
| skill 完全不出现 | 目录结构错（SKILL.md 不在根目录）或 YAML 语法错 | 用 YAML 解析器验证 frontmatter |
| 出现了但从不被调用 | `description` 没写清"什么时候用" | 补触发场景词，参考 26.3.3 |
| 报 name 校验失败 | name 含大写/连续连字符/与目录名不一致 | 按 26.3.2 逐项核对 |
| 加载后上下文暴涨 | SKILL.md 过长 | 拆到 `references/`，正文留锚点 |
| 行为不稳定 | 靠模型"理解"做确定性操作 | 把那部分抽成脚本 |
| Agent 不知道能跑脚本 | `scripts/` 目录为空 | 确认目录非空且脚本有执行权限 |
| 脚本报 Permission denied | 缺 shebang 或执行位 | `chmod +x` + 首行 `#!/usr/bin/env python3` |
| description 超长被截断 | 超过 1024 字符 | 压到 300 字符内 |

---

## 26.10 发布自检清单

发布前，逐项打勾：

**规范合规**
- [ ] `SKILL.md` 存在且 YAML frontmatter 可被解析
- [ ] `name` 合法且与父目录名完全一致
- [ ] `description` 在 1024 字符内，且**明确写了触发场景**
- [ ] 可选字段拼写正确（尤其 `allowed-tools` 是连字符不是下划线）

**性能**
- [ ] `SKILL.md` 正文 < 500 行 / ~5,000 token
- [ ] 大段参考资料已移到 `references/`
- [ ] 确定性逻辑已抽成 `scripts/`，正文没有让模型做算术

**可靠性**
- [ ] 提供了至少一个完整输入/输出示例
- [ ] 列出了 3 条以上的边界情况
- [ ] 脚本自包含（或明确写了依赖），错误信息友好

**安全**
- [ ] 正文明示了网络访问和环境变量读取行为
- [ ] 无隐藏的破坏性操作
- [ ] `scripts/` 中的代码可被人工审阅（无混淆、无远程下载执行）

**可维护性**
- [ ] `metadata` 里写了 `version`
- [ ] README 里有一句话介绍

---

## 26.11 本章配套资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 官方 Skill 包 | [`skills/agent-handbook/SKILL.md`](../skills/agent-handbook/SKILL.md) | 把整本手册打包成 skill，Claude Code 等客户端可直接安装 |
| Skill 校验器 | [`examples/10-agent-skill/`](../examples/10-agent-skill/README.md) | 本章 26.10 自检清单的可执行版本，一条命令跑完 20+ 项检查 |
| 示例 skill | `examples/10-agent-skill/sample-skill/` | 符合规范的最小可用样例，可作为模板起步 |

> 💡 **一个闭环**：本手册的官方 Skill 包，就是照着本章的规范写的。**你可以直接用它当参考答案**——读完本章再逐行对照校核，比读任何描述都直观。

---

## 26.12 小结

| 记住这一点 | 为什么 |
|-----------|--------|
| `description` 是唯一的投放开关 | 写得不好，正文再好也没人看 |
| 渐进式披露四阶段 | 决定了内容该放哪一层的唯一依据 |
| 能写成脚本的别写成指令 | 零 token、零幻觉、完全可靠 |
| SKILL.md 是说明书，scripts/ 才是执行体 | 36.82% 的 skill 有安全缺陷，别只看说明书 |
| ~100 token 的启动成本 | 这是它能统一全行业的根本原因 |

> **下一章**：Skills 解决的是"装什么知识"，**[第 27 章 上下文工程](27-context-engineering.md)** 解决的是"这些知识怎么才能在有限的注意力预算里真正发挥作用"。两者是同一个问题的两面。

---

> 📖 第 26 章 · 最后校验：2026-10-06 · 规范版本：Agent Skills 2026-10
> 发现过时或有误？开 [Issue](https://github.com/Xwh630/ai-agent-handbook/issues/new?title=第26章：) 告诉我。
