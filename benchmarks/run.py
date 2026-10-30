#!/usr/bin/env python3
"""体检榜的自动化跑分器。

用法：
    python benchmarks/run.py                 # 克隆 + 体检，写 benchmarks/bench-results.json
    python benchmarks/run.py --table         # 额外打印 Markdown 表格
    python benchmarks/run.py --only 5        # 只跑前 5 个（先小样本试水）
    python benchmarks/run.py --use-local DIR # 不联网：对已有本地目录批量体检

设计原则：
1. 只用标准库 + git 命令，不装任何依赖（和 doctor 一致）。
2. 结果写进 JSON，README 里的表格由它渲染，**不手抄分数**（手抄必然漂移）。
3. 跳过非 Python 项目并明确标注，而不是给 0 分——那会误导读者。
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_handbook import doctor  # noqa: E402

# 候选清单：知名、开源、有真实 Agent 运行时代码的项目。
# 挑的都是「有 loop / 有工具调用」的，纯 SDK 和纯文档项目不算。
TARGETS = [
    ("OpenHands", "All-Hands-AI/OpenHands"),
    ("SWE-agent", "SWE-agent/SWE-agent"),
    ("AutoGen", "microsoft/autogen"),
    ("CrewAI", "crewAIInc/crewAI"),
    ("LangGraph", "langchain-ai/langgraph"),
    ("LlamaIndex", "run-llama/llama_index"),
    ("OpenAI Agents SDK", "openai/openai-agents-python"),
    ("Claude Agent SDK", "anthropics/claude-agent-sdk-python"),
    ("MetaGPT", "geekan/MetaGPT"),
    ("AutoGPT", "Significant-Gravitas/AutoGPT"),
    ("Dify", "langgenius/dify"),
    ("Langflow", "langflow-ai/langflow"),
    ("smolagents", "huggingface/smolagents"),
    ("AgentScope", "agentscope-ai/agentscope"),
    ("agno", "agno-agi/agno"),
    ("PydanticAI", "pydantic/pydantic-ai"),
    ("Camel", "camel-ai/camel"),
    ("SuperAGI", "TransformerOptimus/SuperAGI"),
    ("Qwen-Agent", "QwenLM/Qwen-Agent"),
    ("Open Interpreter", "openinterpreter/open-interpreter"),
]


# 下载镜像：直连 GitHub 在国内常被限到几十 KB/s，加一层加速前缀。
# 顺序=从快到慢，逐个 fallback；任何一个通了就停。
MIRRORS = [
    "https://ghfast.top/https://github.com/{repo}/archive/refs/heads/{branch}.tar.gz",
    "https://gh-proxy.com/https://github.com/{repo}/archive/refs/heads/{branch}.tar.gz",
    "https://codeload.github.com/{repo}/tar.gz/refs/heads/{branch}",
]


def _via_tarball(repo: str, dest: Path) -> bool:
    """下源码包再解压。git clone 在受限网络下基本走不通，这条路更稳。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tar_path = dest.with_suffix(".tar.gz")
    for branch in ("main", "master"):
        for tpl in MIRRORS:
            url = tpl.format(repo=repo, branch=branch)
            r = subprocess.run(
                ["curl", "-sSL", "--retry", "1", "-m", "600", "-o", str(tar_path),
                 "-w", "%{http_code}", url],
                capture_output=True, text=True, timeout=660,
            )
            size = tar_path.stat().st_size if tar_path.exists() else 0
            if r.stdout.strip().endswith("200") and size > 1024:
                dest.mkdir(parents=True, exist_ok=True)
                subprocess.run(["tar", "-xzf", str(tar_path), "-C", str(dest),
                                "--strip-components=1"], check=True, timeout=300)
                tar_path.unlink(missing_ok=True)
                return True
    return False


def clone(repo: str, dest: Path) -> bool:
    """取一份最小源码。失败返回 False（网络问题很常见，不打分就是最诚实的处理）。"""
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    try:
        if _via_tarball(repo, dest):
            return True
    except Exception as e:  # noqa: BLE001
        print(f"  [跳过] {repo} 下载异常：{e}", file=sys.stderr)
        return False
    print(f"  [跳过] {repo} 下载失败", file=sys.stderr)
    return False


def has_python(path: Path) -> bool:
    for p in path.rglob("*.py"):
        if any(part in doctor._SKIP_DIRS for part in p.parts):
            continue
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="store_true", help="打印 Markdown 表格")
    ap.add_argument("--only", type=int, default=0, help="只跑前 N 个")
    ap.add_argument("--jobs", type=int, default=3, help="并发下载数，默认 3（太高会被镜像限流）")
    ap.add_argument("--use-local", metavar="DIR", help="不联网：把 DIR 下的每个子目录当成一个项目体检")
    ap.add_argument("--keep", action="store_true", help="保留临时下载目录")
    args = ap.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="hb-bench-"))

    if args.use_local:
        base = Path(args.use_local).resolve()
        if not base.is_dir():
            print(f"目录不存在：{base}", file=sys.stderr)
            return 1
        local = [d for d in sorted(base.iterdir()) if d.is_dir() and not d.name.startswith(".")]
        targets = [(d.name, "") for d in local]
        dests = {name: d for (name, _), d in zip(targets, local)}
        print(f"本地模式：{len(targets)} 个目录", flush=True)
    else:
        targets = TARGETS[: args.only] if args.only else TARGETS
        dests = {}

    # 先并发下载，再串行体检：下载是网络瓶颈（国内镜像几十~几百 KB/s），
    # 体检是纯本地 CPU，串行反而更快且不会互相拖慢。
    if not args.use_local:
        print(f"并下载 {len(targets)} 个仓库（jobs={args.jobs}）…", flush=True)
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futs = {
                pool.submit(clone, repo, workdir / repo.split("/")[-1]): (name, repo)
                for name, repo in targets
            }
            for fut in as_completed(futs):
                name, repo = futs[fut]
                ok = False
                try:
                    ok = fut.result()
                except Exception as e:  # noqa: BLE001
                    print(f"  [跳过] {repo} 异常：{e}", file=sys.stderr)
                if ok:
                    dests[repo] = workdir / repo.split("/")[-1]
                    print(f"  ✓ {name}", flush=True)

    rows = []
    for name, repo in targets:
        print(f"→ {name} ({repo or '本地'})", flush=True)
        dest = dests.get(repo) or dests.get(name)
        if dest is None:
            rows.append({"name": name, "repo": repo, "status": "clone_failed"})
            continue
        if not has_python(dest):
            rows.append({"name": name, "repo": repo, "status": "no_python"})
            continue
        report = doctor.scan_project(dest)
        rows.append({
            "name": name,
            "repo": repo,
            "status": "ok",
            "total": report["total"],
            "grade": report["grade"],
            "files": report["files"],
            "pillars": {r["pillar"]: r["score"] for r in report["results"]},
            "weakest": report["weakest"]["pillar"],
        })
        print(f"  {report['total']}/10  {report['grade']}  最缺：{report['weakest']['pillar']}", flush=True)

    out = ROOT / "benchmarks" / "bench-results.json"
    payload = {"snapshot": date.today().isoformat(), "tool": "agent-handbook doctor", "rows": rows}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {out.relative_to(ROOT)}")

    ok = [r for r in rows if r["status"] == "ok"]
    if ok:
        avg = sum(r["total"] for r in ok) / len(ok)
        print(f"有效样本 {len(ok)} 个，平均分 {avg:.1f}/10")

    if args.table:
        print("\n| # | 项目 | 总分 | 任务边界 | 上下文 | 状态 | 恢复 | 权限 | 最缺 |")
        print("|---|------|------|---------|--------|------|------|------|------|")
        for i, r in enumerate(sorted(ok, key=lambda x: -x["total"]), 1):
            p = r["pillars"]
            label = f"[{r['name']}](https://github.com/{r['repo']})" if r["repo"] else r["name"]
            print(f"| {i} | {label} | **{r['total']}** | "
                  f"{p['任务边界']} | {p['上下文管理']} | {p['状态持久化']} | "
                  f"{p['失败恢复']} | {p['权限体系']} | {r['weakest']} |")

    if not args.keep:
        shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
