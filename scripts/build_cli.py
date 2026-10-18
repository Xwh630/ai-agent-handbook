#!/usr/bin/env python3
"""构建 CLI 发布包。

chapters/ 与 data/ 是单一数据源，不在 src/ 下，所以打包前先把它们
复制进包目录，让 pip install 之后 search / doctor / stars 能离线工作。

用法：
    python scripts/build_cli.py            # 只复制数据
    python scripts/build_cli.py --wheel    # 复制数据后打 wheel + sdist
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PKG = ROOT / "src" / "agent_handbook"


def sync_data():
    """把 chapters/*.md 与 data/stars.{json,csv} 复制进包目录。"""
    copied = 0

    dst_ch = PKG / "chapters"
    if dst_ch.exists():
        shutil.rmtree(dst_ch)
    dst_ch.mkdir(parents=True)
    for md in sorted((ROOT / "chapters").glob("*.md")):
        shutil.copy2(md, dst_ch / md.name)
        copied += 1

    dst_data = PKG / "data"
    if dst_data.exists():
        shutil.rmtree(dst_data)
    dst_data.mkdir(parents=True)
    for f in ("stars.json", "stars-history.csv"):
        src = ROOT / "data" / f
        if src.exists():
            shutil.copy2(src, dst_data / f)
            copied += 1

    print(f"已同步 {copied} 个数据文件到 {PKG.relative_to(ROOT)}/")
    return copied


def build():
    """调用 python -m build 产出 wheel 与 sdist。"""
    print("\n开始构建...")
    r = subprocess.run([sys.executable, "-m", "build"], cwd=str(ROOT))
    if r.returncode != 0:
        print("\n构建失败。若提示缺少 build：pip install build")
        return False
    dist = ROOT / "dist"
    for f in sorted(dist.glob("*")):
        size = f.stat().st_size / 1024
        print(f"  📦 {f.name}  ({size:.0f} KB)")
    return True


def main():
    sync_data()
    if "--wheel" in sys.argv:
        ok = build()
        sys.exit(0 if ok else 1)
    print("\n提示：加 --wheel 直接构建。")


if __name__ == "__main__":
    main()
