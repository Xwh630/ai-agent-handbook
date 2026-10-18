"""数据路径解析：pip 安装后用包内数据，仓库内开发时用仓库数据。"""

import os
from pathlib import Path

_PKG_DIR = Path(__file__).parent


def chapters_dir() -> Path:
    """返回 chapters/ 目录。优先仓库（内容更新），其次包内副本。"""
    # 1) 包内（pip 安装时打包进去）
    bundled = _PKG_DIR / "chapters"
    if bundled.is_dir() and any(bundled.glob("*.md")):
        return bundled
    # 2) 仓库根（开发模式：src/agent_handbook -> 根）
    repo = _PKG_DIR.parent.parent / "chapters"
    if repo.is_dir():
        return repo
    # 3) 当前工作目录下
    cwd = Path.cwd() / "chapters"
    if cwd.is_dir():
        return cwd
    return bundled


def data_dir() -> Path:
    """返回 data/ 目录（stars.json 等）。"""
    bundled = _PKG_DIR / "data"
    if bundled.is_dir() and (bundled / "stars.json").exists():
        return bundled
    repo = _PKG_DIR.parent.parent / "data"
    if (repo / "stars.json").exists():
        return repo
    cwd = Path.cwd() / "data"
    if (cwd / "stars.json").exists():
        return cwd
    return bundled


def repo_root() -> Path:
    """尽量推断仓库根目录，找不到就返回包目录。"""
    candidate = _PKG_DIR.parent.parent
    if (candidate / "chapters").is_dir() and (candidate / "README.md").exists():
        return candidate
    return Path(os.getcwd())
