#!/usr/bin/env python3
"""
框架 Stars 数据刷新脚本
- 抓取核心框架仓库的 star 数与最新 release tag
- 更新 data/stars.json 与 data/stars-history.csv
- 更新 README.md 中的框架速览表格
"""
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

# 监控的框架列表（与 README 框架速览表对应）
FRAMEWORKS = [
    {"name": "LangGraph", "repo": "langchain-ai/langgraph"},
    {"name": "CrewAI", "repo": "crewAIInc/crewAI"},
    {"name": "AutoGen", "repo": "microsoft/autogen"},
    {"name": "Dify", "repo": "langgenius/dify"},
    {"name": "LlamaIndex", "repo": "run-llama/llama_index"},
    {"name": "OpenAI Agents SDK", "repo": "openai/openai-agents-python"},
    {"name": "Mastra", "repo": "mastra-ai/mastra"},
    {"name": "Ollama", "repo": "ollama/ollama"},
    {"name": "MCP", "repo": "modelcontextprotocol/specification"},
    {"name": "DeepSeek Harness", "repo": "deepseek-ai/deepseek-harness"},
]


def get_repo_info(repo: str) -> dict:
    """获取 GitHub 仓库信息（star 数、最新 release）"""
    url = f"https://api.github.com/repos/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # 获取最新 release
    release_url = f"https://api.github.com/repos/{repo}/releases/latest"
    latest_release = None
    try:
        rel_resp = requests.get(release_url, headers=headers, timeout=15)
        if rel_resp.status_code == 200:
            latest_release = rel_resp.json().get("tag_name", "")
    except Exception:
        pass

    return {
        "stars": data.get("stargazers_count", 0),
        "latest_release": latest_release,
        "description": data.get("description", ""),
    }


def format_stars(n: int) -> str:
    """格式化 star 数（如 40300 -> "40.3K"）"""
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def update_readme(repo_root: Path, stars_data: list[dict]):
    """更新 README.md 中的框架速览表格"""
    readme_path = repo_root / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    # 创建 star 数查找表
    star_map = {item["name"]: item["stars"] for item in stars_data}

    # 更新框架速览表中的 star 数
    # 匹配格式：| **LangGraph** | 40.3K ⭐ |
    def replace_stars(match):
        framework = match.group(1)
        if framework in star_map:
            return f"**{framework}** | {format_stars(star_map[framework])} ⭐"
        return match.group(0)

    content = re.sub(
        r"\*\*(LangGraph|CrewAI|AutoGen \(MAF\)|Dify|LlamaIndex|OpenAI Agents SDK|Claude Agent SDK|Mastra|Ollama|MCP)\*\* \| [^|]+ ⭐",
        replace_stars,
        content,
    )

    # 更新"框架覆盖"行的 star 数
    # 格式：[LangGraph](url) 40.3K⭐
    for item in stars_data:
        name = item["name"]
        formatted = format_stars(item["stars"])
        # 匹配 [name](url) X.XK⭐
        pattern = rf"(\[{re.escape(name)}\]\([^)]+\)) \d+\.?\d*K?⭐"
        content = re.sub(pattern, rf"\1 {formatted}⭐", content)

    # 更新数据采集日期
    today = datetime.now().strftime("%Y 年 %m 月")
    content = re.sub(
        r"Stars 数据截至 \d+ 年 \d+ 月",
        f"Stars 数据截至 {today}",
        content,
    )

    readme_path.write_text(content, encoding="utf-8")
    print(f"README.md 已更新")


def main():
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    stars_data = []

    print("正在抓取框架 Stars 数据...")
    for fw in FRAMEWORKS:
        try:
            info = get_repo_info(fw["repo"])
            stars_data.append({
                "name": fw["name"],
                "repo": fw["repo"],
                "stars": info["stars"],
                "stars_formatted": format_stars(info["stars"]),
                "latest_release": info["latest_release"],
                "snapshot_date": today,
            })
            print(f"  ✅ {fw['name']}: {format_stars(info['stars'])} ({info['latest_release'] or 'no release'})")
        except Exception as e:
            print(f"  ❌ {fw['name']}: {e}")
            stars_data.append({
                "name": fw["name"],
                "repo": fw["repo"],
                "stars": 0,
                "stars_formatted": "N/A",
                "latest_release": None,
                "snapshot_date": today,
                "error": str(e),
            })

    # 保存 stars.json
    stars_json_path = data_dir / "stars.json"
    stars_json_path.write_text(
        json.dumps(stars_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n已保存: {stars_json_path}")

    # 追加 stars-history.csv
    history_path = data_dir / "stars-history.csv"
    file_exists = history_path.exists()

    with open(history_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["date"] + [item["name"] for item in stars_data]
            writer.writerow(header)
        row = [today] + [item["stars"] for item in stars_data]
        writer.writerow(row)
    print(f"已追加: {history_path}")

    # 更新 README
    try:
        update_readme(repo_root, stars_data)
    except Exception as e:
        print(f"[WARN] 更新 README 失败: {e}")

    print("\n完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
