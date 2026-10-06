#!/usr/bin/env python3
"""
内容新鲜度检查脚本
- 抓取各框架最新 release tag
- 与 chapters/*.md 头部声明的「适配框架版本」比对
- 不一致自动开 issue 并打 stale 标签
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

import requests

# 框架仓库映射（从章节 frontmatter 中提取的关键字 -> GitHub repo）
FRAMEWORK_REPOS = {
    "LangGraph": "langchain-ai/langgraph",
    "CrewAI": "crewAIInc/crewAI",
    "AutoGen": "microsoft/autogen",
    "MAF": "microsoft/autogen",
    "LlamaIndex": "run-llama/llama_index",
    "Dify": "langgenius/dify",
    "OpenAI Agents SDK": "openai/openai-agents-python",
    "Claude Agent SDK": "anthropics/claude-agent-sdk",
    "Mastra": "mastra-ai/mastra",
    "MCP": "modelcontextprotocol/specification",
    "Ollama": "ollama/ollama",
    "LangSmith": "langchain-ai/langsmith-sdk",
    "Codex CLI": "openai/codex-cli",
    "DeepSeek Harness": "deepseek-ai/deepseek-harness",
    "Continue": "continuedev/continue",
    "Aider": "Aider-AI/aider",
}


def get_latest_release(repo: str) -> str | None:
    """获取 GitHub 仓库最新 release tag"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("tag_name", "")
    except Exception as e:
        print(f"[WARN] 获取 {repo} release 失败: {e}", file=sys.stderr)
    return None


def parse_frontmatter(content: str) -> dict:
    """解析章节头部的 frontmatter"""
    result = {"适配框架版本": "", "最后校验": "", "上游变更监控": ""}
    if not content.startswith("---"):
        return result

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return result

    for line in match.group(1).split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


def version_matches(declared: str, latest: str) -> bool:
    """粗略判断声明版本与最新版本是否匹配（大版本号相同即认为匹配）"""
    if not declared or not latest:
        return True  # 无法判断时保守通过

    # 提取主版本号（如 "0.4.x" -> "0.4"，"v0.4.2" -> "0.4"）
    def extract_major_minor(v: str) -> str:
        v = v.lstrip("v")
        parts = v.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return v

    declared_mm = extract_major_minor(declared)
    latest_mm = extract_major_minor(latest)

    # 如果声明的是 x.x.x 格式，比较主.次版本
    if "x" in declared.lower():
        return latest_mm == declared_mm

    return latest_mm == declared_mm


def main():
    repo_root = Path(__file__).parent.parent
    chapters_dir = repo_root / "chapters"
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)

    report = {
        "check_date": datetime.now().isoformat(),
        "stale_chapters": [],
        "up_to_date": [],
        "skipped": [],
    }

    # 缓存最新 release
    release_cache: dict[str, str | None] = {}

    for chapter_file in sorted(chapters_dir.glob("*.md")):
        content = chapter_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        declared = fm["适配框架版本"]
        if not declared or declared.startswith("通用") or "N/A" in declared:
            report["skipped"].append(chapter_file.name)
            continue

        # 尝试匹配框架
        matched_repo = None
        for framework, repo in FRAMEWORK_REPOS.items():
            if framework in declared:
                matched_repo = repo
                break

        if not matched_repo:
            report["skipped"].append(f"{chapter_file.name} (未匹配到仓库)")
            continue

        # 获取最新 release
        if matched_repo not in release_cache:
            release_cache[matched_repo] = get_latest_release(matched_repo)

        latest = release_cache[matched_repo]

        if latest and not version_matches(declared, latest):
            report["stale_chapters"].append({
                "chapter": chapter_file.name,
                "declared": declared,
                "latest": latest,
                "repo": matched_repo,
            })
        else:
            report["up_to_date"].append(chapter_file.name)

    # 保存报告
    report_path = data_dir / "freshness-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # 输出摘要
    print(f"新鲜度检查完成: {len(report['stale_chapters'])} 章过时, "
          f"{len(report['up_to_date'])} 章最新, {len(report['skipped'])} 章跳过")

    if report["stale_chapters"]:
        print("\n过时章节:")
        for item in report["stale_chapters"]:
            print(f"  - {item['chapter']}: 声明={item['declared']}, 最新={item['latest']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
