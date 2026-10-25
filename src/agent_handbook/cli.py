"""命令行入口。设计原则：每条命令都要在 30 秒内给出可见价值。"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__, __repo__, __site__
from ._paths import chapters_dir, data_dir
from . import doctor as doctor_mod
from . import scaffold
from . import search as search_mod

BANNER = "📖 agent-handbook CLI v{}  ——  {}".format(__version__, __repo__)


def cmd_search(args):
    hits = search_mod.search(args.query, limit=args.limit)
    if not hits:
        print(f"没找到「{args.query}」。试试更短的词，或 `handbook list` 看全部章节。")
        return 1
    print(f"\n🔍 「{args.query}」命中 {len(hits)} 处：\n")
    for h in hits:
        print(f"  📄 {h['file']}:{h['lineno']}  （{h['title'][:40]}）")
        body = h["text"].replace("\n", "\n     ")
        print(f"     {body}\n")
    return 0


def cmd_list(args):
    rows = search_mod.list_chapters()
    if not rows:
        print("没找到 chapters/ 目录。")
        return 1
    print(f"\n共 {len(rows)} 章：\n")
    total = 0
    for fn, title, n in rows:
        total += n
        print(f"  {fn:<34} {n:>5} 行   {title[:44]}")
    print(f"\n  合计 {total} 行")
    return 0


def cmd_open(args):
    key = args.chapter.strip()
    d = chapters_dir()
    target = None
    for p in sorted(d.glob("*.md")):
        if p.stem == key or p.stem.startswith(key) or p.name == key:
            target = p
            break
    if not target:
        for p in sorted(d.glob("*.md")):
            if key.lstrip("0") in p.stem or key in p.name:
                target = p
                break
    if not target:
        print(f"没找到第 {key} 章。`handbook list` 看编号。")
        return 1
    slug = target.stem
    print(f"📄 {target.name}")
    print(f"   本地：{target}")
    print(f"   在线：{__site__}{'chapters/' + slug if not slug.startswith('99') else 'chapters/' + slug}")
    print(f"   原文：{__repo__}/blob/main/chapters/{target.name}")
    return 0


def cmd_doctor(args):
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"路径不存在：{root}")
        return 1
    report = doctor_mod.scan_project(root)
    print(doctor_mod.render(report))
    if args.json:
        print(json.dumps({
            "total": report["total"],
            "grade": report["grade"],
            "pillars": {r["pillar"]: r["score"] for r in report["results"]},
        }, ensure_ascii=False, indent=2))
    return 0


def cmd_new(args):
    try:
        root = scaffold.create(args.name, Path(args.dir).resolve() if args.dir else None)
    except FileExistsError as e:
        print(f"❌ {e}")
        return 1
    print(f"\n✅ 已生成 {root}\n")
    for f in sorted(root.iterdir()):
        print(f"   {f.name}")
    print("\n下一步：")
    print(f"   cd {root}")
    print("   cp .env.example .env    # 填上模型地址与 Key")
    print('   python main.py "你的任务"')
    print("   handbook doctor .       # 体检一下骨架本身")
    return 0


def cmd_stars(args):
    p = data_dir() / "stars.json"
    if not p.exists():
        print("没有找到 data/stars.json（每周五自动刷新）。")
        return 1
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print("读取失败：", e)
        return 1
    print("\n⭐ 框架热度（%s 快照）\n" % (data[0].get("snapshot_date", "?") if data else "?"))
    print(f"{'项目':<20}{'Stars':>12}   最新版本")
    print("-" * 52)
    for item in sorted(data, key=lambda x: -x.get("stars", 0)):
        rel = item.get("latest_release") or "—"
        print(f"{item['name']:<20}{item.get('stars_formatted', 'N/A'):>12}   {rel}")
    print()
    return 0


def build_parser():
    ap = argparse.ArgumentParser(
        prog="handbook",
        description="AI Agent 实战手册命令行工具：检索 31 章、给 Agent 项目体检、生成 Harness 骨架",
    )
    ap.add_argument("-v", "--version", action="version", version=BANNER)
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("search", help="31 章全文检索")
    p.add_argument("query", help="关键词，空格分词")
    p.add_argument("-n", "--limit", type=int, default=8)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="列出全部章节")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("open", help="给出某章的本地路径与在线地址")
    p.add_argument("chapter", help="章节号，如 25 / 07 / 99")
    p.set_defaults(func=cmd_open)

    p = sub.add_parser("doctor", help="按 Harness 五支柱给 Agent 项目体检")
    p.add_argument("path", nargs="?", default=".", help="项目路径，默认当前目录")
    p.add_argument("--json", action="store_true", help="额外输出机器可读结果")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("new", help="生成一个自带 Harness 的 Agent 项目")
    p.add_argument("name", help="项目名")
    p.add_argument("-d", "--dir", default=None, help="生成到哪个目录，默认当前")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("stars", help="打印框架热度表")
    p.set_defaults(func=cmd_stars)

    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        print("\n💡 先试这两条：")
        print("   handbook search 上下文压缩")
        print("   handbook doctor .\n")
        return 0
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
