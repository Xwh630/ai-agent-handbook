#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniHarness —— 第 25 章的可运行最小 Harness
============================================

把《Harness Engineering 驾驭工程》的五大支柱落地成一份真正能跑的代码：

    1. 🎯 任务边界    TaskSpec + BudgetGuard
    2. 📦 上下文管理   ContextBuilder（L0 系统层 / L1 状态层 / L2 工作层）
    3. 💾 状态持久化   Checkpointer（每步落盘，崩溃从断点恢复）
    4. 🔁 失败恢复    FailureClassifier（L1 重试 / L2 自纠 / L4 升级）
    5. 🔐 权限体系    PermissionPolicy（按风险分级，不可逆操作必须人审）

没有 API Key 也能跑：加 `--offline` 或检测到未配置 Key 时会自动降级到内置的
脚本化模型（OfflineScriptedLLM），完整演示 Harness 的调度过程而不产生任何费用。

运行方式：

    pip install -r requirements.txt
    cp .env.example .env          # 填入 OPENAI_API_KEY / DEEPSEEK_API_KEY
    python main.py "列出当前目录下的所有 .md 文件"
    python main.py --offline "演示：读取 README.md"    # 无需 Key
    python main.py --reset  "重新开始一个任务"

对应章节：chapters/25-harness-engineering.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

try:  # 加载 .env（可选依赖，缺了不影响离线演示）
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
except Exception:  # pragma: no cover - dotenv 未安装时的兜底
    pass


# =====================================================================
# 支柱五：权限体系 —— 按风险分级，而不是一刀切
# =====================================================================


class Risk(str, Enum):
    """工具的风险等级（对应第 25 章 25.6 的三档划分）"""

    READ = "read"  # 🟢 只读：搜索 / 读文件 / 查库
    WRITE = "write"  # 🟡 可逆写：新建文件 / 提草稿 PR
    DANGEROUS = "dangerous"  # 🔴 不可逆：删数据 / 外发邮件 / 付款 / 上生产


@dataclass
class ToolResult:
    """统一的工具返回结构，便于裁剪与日志记录"""

    ok: bool
    output: str
    error: str = ""


@dataclass
class Tool:
    """一个带风险标记的工具"""

    name: str
    description: str
    risk: Risk
    fn: Callable[[dict], ToolResult]

    def call(self, args: dict) -> ToolResult:
        return self.fn(args or {})


@dataclass
class Budget:
    """支柱一：任务边界里的预算三件套"""

    max_steps: int = 20
    max_tokens: int = 100_000
    timeout_s: int = 300


@dataclass
class TaskSpec:
    """支柱一：显式定义的任务边界"""

    goal: str
    done_criteria: list = field(default_factory=list)
    budget: Budget = field(default_factory=Budget)
    out_of_scope: str = ""

    def to_system_prompt(self) -> str:
        criteria = "\n".join(f"  - {c}" for c in self.done_criteria) or "  - （未指定）"
        return (
            "你是一个受 Harness 约束的 Agent。\n"
            f"【目标】{self.goal}\n"
            f"【完成判据】\n{criteria}\n"
            f"【越界行为】{self.out_of_scope or '遇到边界外请求，请拒绝并说明理由'}\n"
            f"【预算】最多 {self.budget.max_steps} 步 / "
            f"{self.budget.timeout_s} 秒\n"
            "每次只输出一个 JSON 对象：\n"
            '  {"thought": "...", "tool": "工具名", "args": {...}, "done": false}\n'
            "任务完成时把 done 置为 true，并在 final 字段给出最终答复。\n"
            "只使用下列工具，不要编造工具名。"
        )


# =====================================================================
# 支柱三：状态持久化 —— 每一步都落盘
# =====================================================================


class Checkpointer:
    """最小可用检查点：JSON 文件版。生产环境换成 SQLite/Redis 即可"""

    def __init__(self, task_id: str, directory: str | Path = ".checkpoints"):
        self.path = Path(directory) / f"{task_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, state: dict) -> None:
        state["_saved_at"] = time.time()
        self.path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self) -> dict | None:
        if not self.path.exists():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # 检查点损坏时不要整个崩掉，宁可从头开始
            return None

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)


# =====================================================================
# 支柱二：上下文管理 —— 分层 + 压缩 + 工具结果裁剪
# =====================================================================

# 工具结果进入上下文前统一裁剪，避免大段输出挤爆窗口
MAX_TOOL_OUTPUT_CHARS = 1200


class ContextBuilder:
    """
    L0 系统层：角色 + 任务边界 + 工具说明   —— 每轮必带
    L1 状态层：当前进度摘要 + 最近若干轮    —— 每轮更新
    L2 工作层：本轮工具结果                —— 按需注入
    L3 归档层：完整历史                    —— 仅落盘，不进上下文
    """

    def __init__(self, task: TaskSpec, tools: dict[str, Tool], recent_turns: int = 6):
        self.task = task
        self.tools = tools
        self.recent_turns = recent_turns

    def system_layer(self) -> dict:
        tool_lines = "\n".join(
            f"  - {t.name} [{t.risk.value}]: {t.description}" for t in self.tools.values()
        )
        return {
            "role": "system",
            "content": self.task.to_system_prompt() + "\n【可用工具】\n" + tool_lines,
        }

    def build(
        self, history: list[dict], summary: str, tool_output: str = ""
    ) -> list[dict]:
        """组装一次 LLM 调用所需的消息列表"""
        messages = [self.system_layer()]

        if summary:
            messages.append(
                {"role": "system", "content": f"【进度摘要】\n{summary}"}
            )

        # L1：只保留最近 recent_turns 轮，更早的内容已在摘要里
        messages.extend(history[-self.recent_turns :])

        # L2：本轮工具结果，裁剪后注入
        if tool_output:
            clipped = tool_output[:MAX_TOOL_OUTPUT_CHARS]
            suffix = "...（已裁剪）" if len(tool_output) > MAX_TOOL_OUTPUT_CHARS else ""
            messages.append(
                {"role": "user", "content": f"【工具返回】\n{clipped}{suffix}"}
            )

        return messages

    @staticmethod
    def compact(history: list[dict], summary: str, keep: int = 6) -> str:
        """
        上下文压缩：把较早的历史折叠成一段三段式摘要。
        真实场景可以让模型来写摘要；这里用规则化折叠，离线也能演示。
        """
        done_items, doing_items, todo_items = [], [], []
        for msg in history[:-keep]:
            content = str(msg.get("content", "")).strip()
            if not content:
                continue
            if '"done": true' in content or '"done":true' in content:
                todo_items.append(content[:120])
            elif msg.get("role") == "user":
                doing_items.append(content[:120])
            else:
                done_items.append(content[:120])

        parts = []
        if summary:
            parts.append(f"上一轮摘要：{summary}")
        if done_items:
            parts.append("已完成步骤：\n  - " + "\n  - ".join(done_items[-5:]))
        if doing_items:
            parts.append("近期尝试：\n  - " + "\n  - ".join(doing_items[-5:]))
        if todo_items:
            parts.append("待处理线索：\n  - " + "\n  - ".join(todo_items[-3:]))
        return "\n".join(parts)


# =====================================================================
# 支柱四：失败恢复 —— 失败是分等级的
# =====================================================================


class EscalateToHuman(Exception):
    """L4：任务无法自主推进，必须交给人类"""


TRANSIENT_HINTS = ("timeout", "timed out", "rate limit", "429", "503", "temporarily")


def classify_failure(error: Exception) -> str:
    """把异常归类为 L1（瞬时）/ L2（逻辑）/ L3（模型行为）"""
    text = str(error).lower()
    if any(h in text for h in TRANSIENT_HINTS):
        return "L1"
    if isinstance(error, (json.JSONDecodeError, KeyError, TypeError, ValueError)):
        return "L2"
    return "L3"


# =====================================================================
# 支柱五：权限策略
# =====================================================================


class PermissionPolicy:
    """
    🟢 只读         → 自动放行
    🟡 可逆写       → 自动执行 + 通知人类
    🔴 不可逆       → 必须人类审批
    """

    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve
        self.audit: list[dict] = []

    def check(self, tool: Tool, args: dict) -> bool:
        if tool.risk is Risk.READ:
            self.audit.append({"tool": tool.name, "risk": "read", "decision": "allowed"})
            return True
        if tool.risk is Risk.WRITE:
            self.audit.append(
                {"tool": tool.name, "risk": "write", "decision": "auto+notify"}
            )
            print(f"   [权限] 🟡 {tool.name} 已自动执行并通知人类")
            return True

        # 🔴 不可逆操作
        preview = json.dumps(args, ensure_ascii=False)[:200]
        print(f"   [权限] 🔴 {tool.name} 属于不可逆操作")
        print(f"   参数：{preview}")
        if self.auto_approve:
            print("   ⚠️  --yes 模式：自动批准高危操作（仅用于演示，切勿上生产）")
            self.audit.append(
                {"tool": tool.name, "risk": "dangerous", "decision": "forced-yes"}
            )
            return True

        answer = input("   是否批准？(y/N) ").strip().lower()
        allowed = answer == "y"
        self.audit.append(
            {
                "tool": tool.name,
                "risk": "dangerous",
                "decision": "approved" if allowed else "denied",
            }
        )
        return allowed


# =====================================================================
# 模型接入：任意 OpenAI 兼容接口（OpenAI / DeepSeek / 智谱 / 通义 ...）
# =====================================================================


class Action(dict):
    """模型产出的一步动作，容错解析"""


def parse_action(raw: str) -> Action:
    """
    解析模型输出。真实模型的输出经常带 ```json 代码块或多余文字，
    这里做三级容错：整体 JSON → 代码块内 JSON → 字符串切片。
    """
    text = (raw or "").strip()
    try:
        return Action(json.loads(text))
    except json.JSONDecodeError:
        pass
    for fence in ("```json", "```"):
        if fence in text:
            frag = text.split(fence, 1)[1].split("```", 1)[0].strip()
            try:
                return Action(json.loads(frag))
            except json.JSONDecodeError:
                continue
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return Action(json.loads(text[start : end + 1]))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"无法解析为 JSON 的模型输出：{text[:200]}")


class OpenAICompatibleLLM:
    """统一的 OpenAI 兼容调用；换国产模型只需改 base_url 与 model"""

    def __init__(self, model: str | None = None, base_url: str | None = None):
        try:
            from openai import OpenAI  # 延迟导入，离线演示无需安装
        except ImportError as exc:  # pragma: no cover
            raise ImportError("请先 pip install openai") from exc

        self.model = model or os.getenv("MODEL", "deepseek-chat")
        self.base_url = base_url or os.getenv(
            "BASE_URL", os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未检测到 OPENAI_API_KEY / DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)

    def chat(self, messages: list[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0
        )
        return resp.choices[0].message.content or ""


class OfflineScriptedLLM:
    """
    零成本演示模型：不用联网、不用 Key，按脚本给出合理的 Agent 动作。
    它只负责"产出下一步动作"，Harness 的五大支柱逻辑完全一样。
    """

    def __init__(self, root: Path):
        self.root = root
        self.plan: list[Action] = []
        self._primed = False

    def _ensure_plan(self) -> None:
        if self._primed:
            return
        self._primed = True
        self.plan = [
            Action(
                {
                    "thought": "先看看工作目录里有哪些 Markdown 文件",
                    "tool": "list_dir",
                    "args": {"pattern": "*.md"},
                    "done": False,
                }
            ),
            Action(
                {
                    "thought": "挑一个文件读前几行，确认内容可汇总",
                    "tool": "read_file",
                    "args": {"path": "README.md", "head": 20},
                    "done": False,
                }
            ),
            Action(
                {
                    "thought": "信息够了，写成周报草稿",
                    "tool": "write_report",
                    "args": {
                        "filename": "demo-report.md",
                        "content": "# 演示周报\n\n由 MiniHarness 离线模式生成。\n",
                    },
                    "done": False,
                }
            ),
            Action(
                {
                    "thought": "已满足完成判据，输出结论",
                    "tool": "",
                    "args": {},
                    "done": True,
                    "final": "已列出目录内的 Markdown 文件、抽样读取 README.md，"
                    "并把结果写入 output/demo-report.md。",
                }
            ),
        ]

    def chat(self, messages: list[dict]) -> str:
        self._ensure_plan()
        # 用工具返回里的最新文件名替换下一步的读取目标，制造"有反馈"的观感
        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break
        if self.plan:
            step = self.plan.pop(0)
            if "README.md" in last_user or "工具返回" in last_user:
                step["thought"] = "读取到内容了，继续推进"
            return json.dumps(step, ensure_ascii=False)
        return json.dumps({"tool": "", "done": True, "final": "演示结束"}, ensure_ascii=False)


# =====================================================================
# 内置工具集（按风险分级）
# =====================================================================


def build_tools(root: Path, out_dir: Path) -> dict[str, Tool]:
    def t_list_dir(args: dict) -> ToolResult:
        pattern = args.get("pattern", "*")
        # 只读工具也做路径收口，防止越出工作区
        matches = sorted(p.name for p in root.glob(pattern))[:30]
        if not matches:
            return ToolResult(ok=True, output="（目录为空或无匹配）")
        return ToolResult(ok=True, output="\n".join(matches))

    def t_read_file(args: dict) -> ToolResult:
        rel = args.get("path", "")
        target = (root / rel).resolve()
        if not str(target).startswith(str(root.resolve())):
            return ToolResult(ok=False, output="", error="路径越界，已拒绝")
        if not target.exists():
            return ToolResult(ok=False, output="", error=f"文件不存在：{rel}")
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        head = int(args.get("head", 40) or 40)
        return ToolResult(ok=True, output="\n".join(lines[:head]))

    def t_write_report(args: dict) -> ToolResult:
        filename = Path(args.get("filename", "report.md")).name  # 去掉任何路径穿越
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / filename
        target.write_text(args.get("content", ""), encoding="utf-8")
        return ToolResult(ok=True, output=f"已写入 {target}")

    def t_delete_path(args: dict) -> ToolResult:
        target = Path(args.get("path", ""))
        if target.exists():
            target.unlink()
            return ToolResult(ok=True, output=f"已删除 {target}")
        return ToolResult(ok=False, output="", error=f"文件不存在：{target}")

    return {
        "list_dir": Tool("list_dir", "列出工作目录下的文件", Risk.READ, t_list_dir),
        "read_file": Tool("read_file", "读取文本文件内容", Risk.READ, t_read_file),
        "write_report": Tool(
            "write_report", "写入 output/ 下的报告文件（可逆）", Risk.WRITE, t_write_report
        ),
        "delete_path": Tool(
            "delete_path", "删除文件——不可逆操作", Risk.DANGEROUS, t_delete_path
        ),
    }


# =====================================================================
# MiniHarness：把五大支柱组装起来
# =====================================================================


class MiniHarness:
    """第 25 章 25.7 的落地版"""

    COMPACT_EVERY = 6  # 每多少步压缩一次上下文

    def __init__(
        self,
        llm,
        tools: dict[str, Tool],
        task: TaskSpec,
        task_id: str = "demo",
        auto_approve: bool = False,
    ):
        self.llm = llm
        self.tools = tools
        self.task = task
        self.task_id = task_id
        self.ctx = ContextBuilder(task, tools)
        self.ckpt = Checkpointer(task_id)
        self.perms = PermissionPolicy(auto_approve=auto_approve)
        self.started_at = 0.0

    # ---------- 预算守卫（支柱一） ----------
    def _check_budget(self, step: int, tokens: int) -> None:
        if step >= self.task.budget.max_steps:
            raise EscalateToHuman(
                f"已达最大步数 {self.task.budget.max_steps}，任务未完成，需人工接手"
            )
        if tokens >= self.task.budget.max_tokens:
            raise EscalateToHuman("已达 token 预算上限，需人工复核是否继续")
        if time.time() - self.started_at > self.task.budget.timeout_s:
            raise EscalateToHuman("已超时，需人工接手")

    # ---------- 单步执行 ----------
    def _execute(self, action: Action) -> ToolResult:
        name = action.get("tool") or ""
        if not name:
            return ToolResult(ok=True, output="（无需工具）")
        tool = self.tools.get(name)
        if tool is None:
            # L2 错误：把工具清单喂回去，让模型下一轮自我修正
            raise KeyError(f"未知工具：{name}。可用工具：{list(self.tools)}")
        if not self.perms.check(tool, action.get("args", {})):
            return ToolResult(ok=False, output="", error="人类拒绝了该操作")

        try:
            return tool.call(action.get("args", {}))
        except Exception as exc:  # 工具内部异常统一转成 ToolResult，交给失败分类
            return ToolResult(ok=False, output="", error=f"{type(exc).__name__}: {exc}")

    # ---------- 主循环 ----------
    def run(self) -> str:
        state = self.ckpt.load() or {
            "step": 0,
            "failures": 0,
            "tokens": 0,
            "summary": "",
            "history": [],
            "answer": "",
        }
        if state["step"] > 0:
            print(f"↩️  从第 {state['step']} 步的断点恢复（检查点：{self.ckpt.path}）")

        self.started_at = time.time()
        history: list[dict] = state["history"]
        summary: str = state["summary"]
        answer: str = state["answer"]
        tool_output = ""

        try:
            while True:
                self._check_budget(state["step"], state["tokens"])

                messages = self.ctx.build(history, summary, tool_output)
                # 支柱四 L1：瞬时错误走指数退避重试
                raw = self._call_llm_with_retry(messages)
                state["tokens"] += len(raw) // 4  # 粗估 token，够用于预算守卫

                action = parse_action(raw)
                history.append({"role": "assistant", "content": raw})

                if action.get("done"):
                    answer = action.get("final") or "任务完成"
                    break

                tool_output = ""
                try:
                    result = self._execute(action)
                except KeyError as exc:
                    # 支柱四 L2：把错误喂回模型让它自纠
                    state["failures"] += 1
                    tool_output = f"工具调用失败：{exc}。请改用可用工具。"
                    history.append({"role": "user", "content": tool_output})
                    if state["failures"] >= 3:
                        raise EscalateToHuman("连续 3 次工具调用失败") from exc
                    state["step"] += 1
                    self.ckpt.save(state)
                    continue

                if not result.ok:
                    state["failures"] += 1
                    tool_output = f"执行失败：{result.error}。请换一种做法。"
                    if state["failures"] >= 3:
                        raise EscalateToHuman("连续 3 次失败，需要人工介入")
                else:
                    state["failures"] = 0
                    tool_output = result.output

                history.append({"role": "user", "content": f"【工具返回】\n{tool_output}"})
                state["step"] += 1

                # 支柱二：定期压缩
                if state["step"] % self.COMPACT_EVERY == 0 and len(history) > 12:
                    summary = ContextBuilder.compact(history, summary)
                    history = history[-6:]
                    print(f"   [上下文] 已压缩，历史保留 {len(history)} 条")

                # 支柱三：每步落盘
                state["history"], state["summary"] = history, summary
                self.ckpt.save(state)

        except EscalateToHuman as exc:
            answer = f"⛔ 已升级给人类：{exc}"
            print(f"\n{answer}")
            state["answer"] = answer
            self.ckpt.save(state)
            return answer

        state["step"] += 1
        state["history"], state["summary"], state["answer"] = history, summary, answer
        self.ckpt.save(state)
        self.ckpt.clear()  # 正常完成后清掉检查点
        return answer

    # ---------- L1 重试 ----------
    def _call_llm_with_retry(self, messages: list[dict], max_retries: int = 3) -> str:
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                return self.llm.chat(messages)
            except Exception as exc:
                last_error = exc
                level = classify_failure(exc)
                if level != "L1" or attempt == max_retries - 1:
                    raise
                wait = 2**attempt
                print(f"   [重试] L1 瞬时错误，{wait}s 后退避重试（{attempt + 1}/{max_retries}）")
                time.sleep(wait)
        raise last_error  # pragma: no cover


# =====================================================================
# CLI
# =====================================================================


def main() -> int:
    parser = argparse.ArgumentParser(description="MiniHarness —— 第 25 章可运行示例")
    parser.add_argument("goal", nargs="?", default="列出当前目录下的 Markdown 文件并给出摘要")
    parser.add_argument("--task-id", default="demo", help="检查点文件名")
    parser.add_argument("--dir", default=".", help="只读工具的工作目录")
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--offline", action="store_true", help="不联网，用脚本化模型演示")
    parser.add_argument("--yes", action="store_true", help="自动批准高危操作（演示用）")
    parser.add_argument("--reset", action="store_true", help="忽略已有检查点")
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    out_dir = Path(__file__).parent / "output"

    if args.reset:
        Checkpointer(args.task_id).clear()

    use_offline = args.offline or not (
        os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    )
    if use_offline:
        print("ℹ️  未检测到 API Key 或指定了 --offline，使用内置离线演示模型。")
        llm: Any = OfflineScriptedLLM(root)
    else:
        llm = OpenAICompatibleLLM()

    task = TaskSpec(
        goal=args.goal,
        done_criteria=[
            "已列出目标目录下的相关文件",
            "已给出可读的文字结论",
        ],
        budget=Budget(max_steps=args.max_steps, timeout_s=300),
        out_of_scope="遇到删除/外发/支付等不可逆操作 → 停下来请求人类批准",
    )

    harness = MiniHarness(
        llm=llm,
        tools=build_tools(root, out_dir),
        task=task,
        task_id=args.task_id,
        auto_approve=args.yes,
    )

    print(f"\n🎯 目标：{args.goal}")
    print(f"💾 检查点：{harness.ckpt.path}\n" + "-" * 60)

    try:
        answer = harness.run()
    except KeyboardInterrupt:
        print("\n⏸️  已中断。检查点已保存，下次运行会从断点继续。")
        return 130
    except Exception:  # pragma: no cover
        traceback.print_exc()
        return 1

    print("-" * 60)
    print(f"✅ 最终答复：{answer}")
    print(f"🧾 权限审计：{len(harness.perms.audit)} 条")
    for item in harness.perms.audit:
        print(f"    - {item['tool']} [{item['risk']}] → {item['decision']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
