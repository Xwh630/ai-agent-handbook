"""Harness 健康度体检 —— 把第 25 章的五支柱变成可执行检查。

为什么值得做：绝大多数「Agent 项目跑不稳」不是模型问题，而是五根支柱
少了几根。doctor 用静态扫描给你一张体检单，每根柱子都指向手册里
对应的那一节，缺什么补什么。
"""

import re
from pathlib import Path

# 五个支柱 → (显示名, 检测模式, 缺失时该看的手册小节)
PILLARS = [
    (
        "任务边界",
        [
            r"max_steps", r"max_iterations", r"step_limit", r"budget",
            r"TaskSpec", r"deadline", r"timeout", r"max_turns",
        ],
        "25.2 任务边界：给 Agent 一个明确的终点和预算",
    ),
    (
        "上下文管理",
        [
            r"compact", r"summariz", r"trim", r"compress", r"context_window",
            r"ContextBuilder", r"messages\[-\d+", r"token_budget",
        ],
        "25.3 上下文管理：分层 + 压缩，别把上下文当仓库",
    ),
    (
        "状态持久化",
        [
            r"checkpoint", r"save_state", r"load_state", r"persist",
            r"sqlite", r"redis", r"\.checkpoints", r"json\.dump",
        ],
        "25.4 状态持久化：崩溃之后还能接着干",
    ),
    (
        "失败恢复",
        [
            r"retry", r"fallback", r"recovery", r"FailureClassifier",
            r"escalat", r"except\s+\w+Error", r"backoff",
        ],
        "25.5 失败恢复：L1–L4 分级，越往上越该交给人类",
    ),
    (
        "权限体系",
        [
            r"permission", r"approv", r"allowlist", r"whitelist", r"denylist",
            r"Policy", r"confirm", r"human_in_the_loop", r"dry_run",
        ],
        "25.6 权限体系：🟢放行 / 🟡通知 / 🔴必须审批",
    ),
]

_SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".idea", ".vscode", "dist", "build", "site-packages", ".mypy_cache",
    ".pytest_cache", "output", ".checkpoints",
}


def _iter_python_files(root: Path):
    for p in sorted(root.rglob("*.py")):
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        # 生成物 / 测试固定装置也跳过
        if p.name.startswith("test_") or p.name == "conftest.py":
            continue
        yield p


def _code_lines(lines):
    """产出 (行号, 行内容)，跳过注释与三引号字符串块。

    只统计真代码 —— 否则一份把五根柱子写在 docstring 里的文件
    会拿到不该有的高分。
    """
    in_block = False
    block_mark = None
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if s.startswith("#"):
            continue
        if block_mark is None:
            for mark in ('"""', "'''"):
                # 同一行内闭合的（如 `"""x"""`）不算块
                if s.count(mark) >= 2:
                    continue
                if s.startswith(mark) or (mark in s and not s.endswith(mark)):
                    in_block = True
                    block_mark = mark
                    break
            if in_block:
                continue
        else:
            if block_mark in s:
                in_block = False
                block_mark = None
            continue
        yield i, raw


def _scan(pillar_patterns, files):
    """返回命中的证据列表 [(文件名, 行号, 匹配到的关键词)]"""
    evidence = []
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in _code_lines(lines):
            for pat in pillar_patterns:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    evidence.append((f.name, i, m.group(0)))
                    break  # 一行只记一次
    return evidence


def scan_project(root: Path):
    """返回体检结果 dict。"""
    files = list(_iter_python_files(root))
    results = []

    for name, patterns, chapter_ref in PILLARS:
        # ⚠️ 证据必须按柱子分别扫描：_scan 的入参是「这一根柱子的模式」，
        # 早期写成扫全部 PILLARS 会导致五根柱子分数永远一样。
        ev = _scan(patterns, files)
        # 不同关键词的多样性体现深度
        distinct = {e[2].lower() for e in ev}
        if not ev:
            score, status = 0, "❌ 缺失"
        elif len(distinct) >= 2:
            # 两个以上不同的实现痕迹 = 这根柱子真的被写进代码了
            score, status = 2, "✅ 扎实"
        else:
            score, status = 1, "⚠️ 薄弱"
        results.append({
            "pillar": name,
            "score": score,
            "status": status,
            "evidence": ev[:3],
            "ref": chapter_ref,
        })

    total = sum(r["score"] for r in results)
    if total >= 9:
        grade, verdict = "A", "生产级 Harness，五根柱子都在且够结实"
    elif total >= 7:
        grade, verdict = "B", "能跑，但有柱子偏薄——建议优先补最高分那根之外的短板"
    elif total >= 4:
        grade, verdict = "C", "原型水平：能演示，跑久了会出事"
    else:
        grade, verdict = "D", "裸 Agent：模型直接裸奔，崩溃/超预算/越权全靠运气"

    # 最该补的一项：分数最低且在手册里有明确章节
    weakest = min(results, key=lambda r: r["score"])

    return {
        "root": str(root),
        "files": len(files),
        "results": results,
        "total": total,
        "max": len(PILLARS) * 2,
        "grade": grade,
        "verdict": verdict,
        "weakest": weakest,
    }


def render(report) -> str:
    """把体检结果渲染成终端文本。"""
    lines = []
    lines.append("")
    lines.append(f"🩺 Harness 体检报告 · {report['root']}")
    lines.append(f"   扫描 Python 文件 {report['files']} 个")
    lines.append("")
    lines.append(f"{'支柱':<10}{'得分':<8}{'状态':<12}证据")
    lines.append("-" * 68)
    for r in report["results"]:
        ev = ", ".join(f"{n}:{ln}" for n, ln, _ in r["evidence"]) or "—"
        bar = "●" * r["score"] + "○" * (2 - r["score"])
        lines.append(f"{r['pillar']:<10}{bar:<8}{r['status']:<12}{ev}")
    lines.append("-" * 68)
    lines.append(f"总分 {report['total']}/{report['max']}  ·  评级 {report['grade']}  ·  {report['verdict']}")
    lines.append("")
    w = report["weakest"]
    if w["score"] == 2:
        lines.append("🎉 五根柱子都在。接下来该做的是压测：把步数上限砍一半看它还能不能完成任务。")
    else:
        lines.append(f"👉 最该先补：{w['pillar']} —— 看手册 {w['ref']}")
        lines.append("   在线：https://xwh630.github.io/ai-agent-handbook/")
    lines.append("")
    return "\n".join(lines)


def to_markdown(report) -> str:
    """把体检结果渲染成一段可以直接贴进 GitHub issue / PR / README 的 Markdown 表格。

    `handbook doctor . --md` 就是给「体检榜」和「给别人提 issue」用的：
    复制即引用，不用手抄分数。
    """
    out = []
    out.append(f"**🩺 Harness 体检 · {report['total']}/{report['max']} · {report['grade']} 级**")
    out.append("")
    out.append("| 支柱 | 得分 | 状态 | 证据 |")
    out.append("|------|------|------|------|")
    for r in report["results"]:
        ev = ", ".join(f"`{n}:{ln}`" for n, ln, _ in r["evidence"]) or "—"
        bar = "●" * r["score"] + "○" * (2 - r["score"])
        out.append(f"| {r['pillar']} | `{bar}` {r['score']}/2 | {r['status']} | {ev} |")
    out.append("")
    w = report["weakest"]
    if w["score"] < 2:
        out.append(f"最该先补：**{w['pillar']}** —— 手册 {w['ref']}")
    out.append("")
    out.append("> 由 [agent-handbook](https://github.com/Xwh630/ai-agent-handbook) 生成：`uvx agent-handbook doctor .`")
    return "\n".join(out)
