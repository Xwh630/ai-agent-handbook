"""PEP 517 构建后端：在构建前把章节数据同步进包目录。

背景
----
``chapters/`` 与 ``data/`` 是单一数据源，位于仓库根，不在 ``src/`` 下，
因此不能直接作为包数据发布。过去的做法是打包前手动跑一次
``scripts/build_cli.py``——但这带来两个后果：

1. ``pip install git+https://github.com/Xwh630/ai-agent-handbook.git``
   装出来的是一个**没有章节数据的空壳 CLI**（``handbook list`` 直接报错）；
2. 任何忘记预同步的构建都会静默产出残缺包。

本文件是一个 in-tree 构建后端（``backend-path = ["."]``），在每个构建入口
被调用时先把 ``chapters/*.md`` 与 ``data/stars.*`` 复制进
``src/agent_handbook/``，再转交给 setuptools。这样无论从 git 安装、从
sdist 安装还是发 PyPI，拿到的包都自带完整数据，且无需任何手动前置步骤。

只在构建时运行，对仓库内开发（直接 ``python -m agent_handbook.cli``）无影响。
"""

from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import build_meta as _setuptools_backend

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "src" / "agent_handbook"

#: 需要随包发布、但源文件在仓库根的数据文件
_DATA_FILES = ("stars.json", "stars-history.csv")


def _sync_package_data() -> int:
    """把 chapters/ 与 data/ 的最新内容复制进包目录，返回复制的文件数。"""
    copied = 0

    dst_chapters = PKG / "chapters"
    if dst_chapters.exists():
        shutil.rmtree(dst_chapters)
    dst_chapters.mkdir(parents=True, exist_ok=True)
    for md in sorted((ROOT / "chapters").glob("*.md")):
        shutil.copy2(md, dst_chapters / md.name)
        copied += 1

    dst_data = PKG / "data"
    if dst_data.exists():
        shutil.rmtree(dst_data)
    dst_data.mkdir(parents=True, exist_ok=True)
    for name in _DATA_FILES:
        src = ROOT / "data" / name
        if src.exists():
            shutil.copy2(src, dst_data / name)
            copied += 1

    return copied


def _prepare() -> None:
    # 同步失败不该让构建莫名其妙地成功，直接抛出来
    count = _sync_package_data()
    if count == 0:
        raise RuntimeError(
            "构建后端没有同步到任何数据文件；请确认 chapters/ 与 data/ 存在。"
        )


# --- PEP 517 必需入口：转发给 setuptools -----------------------------------

def get_requires_for_build_wheel(config_settings=None):
    return _setuptools_backend.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(config_settings=None):
    return _setuptools_backend.get_requires_for_build_sdist(config_settings)


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    _prepare()
    return _setuptools_backend.prepare_metadata_for_build_wheel(
        metadata_directory, config_settings
    )


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _prepare()
    return _setuptools_backend.build_wheel(
        wheel_directory, config_settings, metadata_directory
    )


def build_sdist(sdist_directory, config_settings=None):
    _prepare()
    return _setuptools_backend.build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    _prepare()
    return _setuptools_backend.build_editable(
        wheel_directory, config_settings, metadata_directory
    )


# --- PEP 660 可选入口 -------------------------------------------------------

def get_requires_for_build_editable(config_settings=None):
    return _setuptools_backend.get_requires_for_build_editable(config_settings)


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    _prepare()
    return _setuptools_backend.prepare_metadata_for_build_editable(
        metadata_directory, config_settings
    )
