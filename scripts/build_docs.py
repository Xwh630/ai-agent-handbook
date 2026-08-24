#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档站点暂存构建脚本
=====================
MkDocs 要求 docs_dir 是配置文件所在目录的子目录，而本仓库的文档内容
（README.md / chapters/ / docs/ / appendix/ / en/）都放在仓库根目录，
以便 GitHub 网页浏览体验最佳。

本脚本将这些内容「暂存」到 site-content/ 目录，供 mkdocs 构建使用：
    python scripts/build_docs.py        # 暂存内容
    mkdocs build / mkdocs serve / mkdocs gh-deploy

site-content/ 与 site/ 均已加入 .gitignore，不会进入版本库。
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
    ("chapters", "chapters"),
    ("docs", "docs"),
    ("appendix", "appendix"),
    ("en", "en"),
]


def main() -> int:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    for src, dst in COPIES:
        source = ROOT / src
        target = STAGE / dst
        if not source.exists():
            print(f"[跳过] 源不存在: {source}")
            continue
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        print(f"[已暂存] {src} -> site-content/{dst}")

    print("\n✅ 暂存完成，现在可以执行：")
    print("   mkdocs build      # 构建静态站点到 site/")
    print("   mkdocs serve      # 本地预览 http://127.0.0.1:8000")
    print("   mkdocs gh-deploy --force   # 部署到 GitHub Pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
