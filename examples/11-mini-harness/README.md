# MiniHarness —— 第 25 章可运行示例

> 把《Harness Engineering 驾驭工程》的五大支柱写成一份真正能跑的代码。
> 对应章节：[第 25 章 · Harness Engineering](../../chapters/25-harness-engineering.md)

## 它实现了什么

| 支柱 | 对应实现 | 关键文件位置 |
|------|---------|------------|
| 🎯 任务边界 | `TaskSpec` + `Budget` + `_check_budget()` | 目标、完成判据、步数/token/超时三重上限 |
| 📦 上下文管理 | `ContextBuilder` | L0 系统层 / L1 状态层 / L2 工作层 + 每 6 步压缩 |
| 💾 状态持久化 | `Checkpointer` | 每步写 `.checkpoints/<task_id>.json`，崩溃从断点恢复 |
| 🔁 失败恢复 | `classify_failure()` + 重试 | L1 指数退避重试 / L2 喂回错误自纠 / L4 升级给人类 |
| 🔐 权限体系 | `PermissionPolicy` | 🟢 自动放行 / 🟡 执行并通知 / 🔴 必须人类审批 |

内置四个工具，正好覆盖三档风险：

| 工具 | 风险 | 说明 |
|------|------|------|
| `list_dir` | 🟢 read | 列出工作目录下的文件 |
| `read_file` | 🟢 read | 读取文本文件内容（带路径越界检查） |
| `write_report` | 🟡 write | 写入 `output/` 下的报告文件，可逆 |
| `delete_path` | 🔴 dangerous | 删除文件，必须人工审批 |

## 快速开始

### 零成本先跑一遍（不需要 API Key）

```bash
python main.py --offline
```

会用内置的脚本化模型走完整个 Harness 流程：读目录 → 读文件 → 写报告 → 收尾。

### 接真实模型

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY（或 DEEPSEEK_API_KEY）
python main.py "列出当前目录下的 Markdown 文件并给出摘要"
```

任意 OpenAI 兼容接口都可以：DeepSeek、智谱 GLM、通义千问、Moonshot、OpenAI 官方，
只需在 `.env` 里换 `BASE_URL` 和 `MODEL`。

## 预期输出

```text
ℹ️  未检测到 API Key 或指定了 --offline，使用内置离线演示模型。

🎯 目标：列出当前目录下的 Markdown 文件并给出摘要
💾 检查点：.checkpoints\demo.json
------------------------------------------------------------
   [权限] 🟡 write_report 已自动执行并通知人类
------------------------------------------------------------
✅ 最终答复：已列出目录内的 Markdown 文件、抽样读取 README.md，
            并把结果写入 output/demo-report.md。
🧾 权限审计：3 条
    - list_dir [read] → allowed
    - read_file [read] → allowed
    - write_report [write] → auto+notify
```

## 动手做几个实验

这些实验比读代码更能建立直觉：

**1. 看持久化真的生效**

```bash
python main.py --task-id exp1 "读取 README.md"
# 跑到一半按 Ctrl+C → 提示已保存检查点
python main.py --task-id exp1 "读取 README.md"
# 会看到 "↩️  从第 N 步的断点恢复"
```

**2. 看权限拦截真的生效**

```bash
# 把 delete_path 加进离线脚本的计划里，或直接用 --yes 对比：
python main.py --task-id exp2 --offline            # 🔴 会停下来询问
python main.py --task-id exp2 --offline --yes      # 自动批准（仅演示，勿上生产）
```

**3. 看预算守卫真的生效**

```bash
python main.py --max-steps 2 --offline
# 步数用尽 → ⛔ 已升级给人类：已达最大步数 2，任务未完成，需人工接手
```

**4. 看上下文压缩**

把 `MiniHarness.COMPACT_EVERY` 改成 2，跑一个长任务，观察 `[上下文] 已压缩` 的输出。

## 常用参数

| 参数 | 作用 |
|------|------|
| `--offline` | 不联网，用内置脚本化模型演示 |
| `--task-id ID` | 指定检查点文件名，不同任务互不干扰 |
| `--dir PATH` | 只读工具的工作目录（默认是当前目录） |
| `--max-steps N` | 最大步数，默认 20 |
| `--yes` | 自动批准高危操作（演示用） |
| `--reset` | 忽略已有检查点，从头开始 |

## 关于 `examples/11-` 这个编号

Issue #7 原本要求放在 `examples/10-mini-harness/`，但仓库里已经存在 `examples/10-agent-skill/`
（第 26 章配套）。为避免目录编号冲突，这里顺延为 `11-mini-harness`。

## 与工业实现的对应关系

看懂这个最小的版本后，再看工业实现会非常快：

- LangGraph 的 `checkpointer` → 本例的 `Checkpointer`（第 3 章）
- Mastra 的 `storage` → 本例的持久化层（第 10 章）
- Claude Code / Codex CLI 的权限确认弹窗 → 本例的 `PermissionPolicy`
- DeepSeek Harness 的重试与降级（第 21 章）→ 本例的 `classify_failure()`

> ⚠️ 这是一个教学用的最小实现：JSON 文件当检查点、粗估 token、
> 没有并发与分布式支持。上生产请直接换 mature 框架，别照抄。
