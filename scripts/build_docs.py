#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档站点暂存构建脚本
=====================
MkDocs 要求 docs_dir 是配置文件所在目录的子目录，而本仓库的文档内容
（README.md / chapters/ / docs/ / appendix/ / en/ / radar/ / skills/）
都放在仓库根目录，以便 GitHub 网页浏览体验最佳。

本脚本将这些内容「暂存」到 site-content/ 目录，供 mkdocs 构建使用：
    python scripts/build_docs.py        # 暂存内容
    mkdocs build / mkdocs serve / mkdocs gh-deploy

site-content/ 与 site/ 均已加入 .gitignore，不会进入版本库。

维护提示：
  mkdocs.yml 的 nav 里出现的任何目录，都必须出现在下面的 COPIES 列表中，
  否则构建时该页面会被 mkdocs 报 "not found" 警告。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "site-content"

# (源相对路径, 目标相对路径) —— 保持仓库结构与导航路径一致
COPIES = [
    ("README.md", "README.md"),
    ("CONTRIBUTING.md", "CONTRIBUTING.md"),
    ("chapters", "chapters"),
    ("docs", "docs"),
    ("appendix", "appendix"),
    ("en", "en"),
    ("radar", "radar"),        # Agent Radar 周刊栏目（nav 引用，必须暂存）
    ("skills", "skills"),      # 官方 Agent Skill 包
]


def main() -> int:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    missing = []
    for src, dst in COPIES:
        source = ROOT / src
        target = STAGE / dst
        if not source.exists():
            print(f"[跳过] 源不存在: {source}")
            missing.append(src)
            continue
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        print(f"[已暂存] {src} -> site-content/{dst}")

    # 校验：nav 引用的路径必须都已暂存，避免 mkdocs 构建警告
    nav_targets = ["README.md", "chapters", "docs", "appendix", "en", "radar"]
    absent = [t for t in nav_targets if not (STAGE / t).exists()]
    if absent:
        print(f"\n⚠️  nav 引用的路径未被暂存：{', '.join(absent)}")
        print("    对应的 mkdocs 页面会缺失。")

    print("\n✅ 暂存完成，现在可以执行：")
    print("   mkdocs build      # 构建静态站点到 site/")
    print("   mkdocs serve      # 本地预览")
    return 0


if __name__ == "__main__":
    sys.exit(main())
