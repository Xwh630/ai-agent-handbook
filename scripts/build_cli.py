#!/usr/bin/env python3
"""构建 CLI 发布包（wheel + sdist）。

数据同步已经交给 in-tree 构建后端 ``build_backend.py`` 自动完成
（见 pyproject.toml 的 ``build-backend`` 配置），所以这里不再需要
手动预同步——直接构建即可，忘了预同步也不会再产出空壳包。

用法：
    python scripts/build_cli.py            # 构建 wheel + sdist 到 dist/ 并校验
    python scripts/build_cli.py --verify-only   # 只校验已有产物，不重新构建
"""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: wheel 里必须存在的数据文件，缺一个就说明构建配置回退了
REQUIRED_IN_WHEEL = (
    "agent_handbook/chapters/00-quickstart.md",
    "agent_handbook/chapters/28-trending-2026.md",
    "agent_handbook/data/stars.json",
)


def build() -> bool:
    """调用 python -m build 产出 wheel 与 sdist。"""
    print("开始构建（数据同步由 build_backend.py 自动完成）...")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation"], cwd=str(ROOT)
    )
    if result.returncode != 0:
        print("\n构建失败。若提示缺少 build：pip install build")
        return False
    return True


def check_artifacts() -> bool:
    """校验 wheel 内确实打包了章节数据——防止再次出现「空壳 CLI」。"""
    dist = ROOT / "dist"
    wheels = sorted(dist.glob("*.whl"))
    if not wheels:
        print("❌ dist/ 下没有 wheel")
        return False

    ok = True
    for wheel in wheels:
        size = wheel.stat().st_size / 1024
        with zipfile.ZipFile(wheel) as zf:
            names = set(zf.namelist())
        missing = [n for n in REQUIRED_IN_WHEEL if n not in names]
        print(f"  📦 {wheel.name}  ({size:.0f} KB)")
        if missing:
            ok = False
            print("     ❌ 缺少数据文件：")
            for n in missing:
                print(f"        - {n}")
        else:
            chapter_count = sum(
                1
                for n in names
                if n.startswith("agent_handbook/chapters/") and n.endswith(".md")
            )
            print(f"     ✅ 含 {chapter_count} 个章节 + stars 数据，CLI 可离线工作")

    for sdist in sorted(dist.glob("*.tar.gz")):
        size = sdist.stat().st_size / 1024
        print(f"  📦 {sdist.name}  ({size:.0f} KB)")

    if not ok:
        print("\n❌ 产物校验失败：pip install 之后 CLI 会缺数据。")
    return ok


def main() -> int:
    verify_only = "--verify-only" in sys.argv
    if not verify_only and not build():
        return 1
    if not check_artifacts():
        return 1
    print("\n✅ 校验通过。" if verify_only else "\n✅ 构建并校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
