#!/usr/bin/env python3
"""把 31 章手册渲染成一本可离线阅读的 PDF。

流程：chapters/*.md → 单个带目录的 HTML → Edge headless 打印成 PDF。
选 Edge 而不是 pandoc/weasyprint 的原因：CSS 全支持、中文不挑字体、
无系统级依赖，Windows 上开箱即用。

用法：
    python scripts/build_pdf.py                 # 生成 dist/AI-Agent-实战手册.pdf
    python scripts/build_pdf.py --out 自定义路径.pdf
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).parent.parent
CHAPTERS = ROOT / "chapters"
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif;
       font-size: 10.5pt; line-height: 1.65; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #2563eb; padding-bottom: 6px;
     margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; color: #1e40af; margin-top: 20px; }
h3 { font-size: 12pt; color: #334155; }
pre { background: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 8.5pt;
      white-space: pre-wrap; word-break: break-all; page-break-inside: avoid; }
code { font-family: "Consolas", "Cascadia Code", monospace; background: #f1f5f9;
       padding: 1px 4px; border-radius: 3px; font-size: 9pt; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 10px 0; }
th, td { border: 1px solid #cbd5e1; padding: 5px 8px; text-align: left; }
th { background: #eff6ff; }
blockquote { border-left: 3px solid #2563eb; margin: 10px 0; padding: 4px 12px;
             background: #f8fafc; color: #475569; }
img { max-width: 100%; }
a { color: #2563eb; text-decoration: none; }
.toc { page-break-after: always; }
.toc h1 { page-break-before: avoid; }
.toc ol { list-style: none; padding-left: 0; }
.toc li { padding: 3px 0; font-size: 10pt; }
.cover { text-align: center; padding-top: 120px; page-break-after: always; }
.cover h1 { border: none; font-size: 30pt; page-break-before: avoid; }
.cover .meta { color: #64748b; margin-top: 24px; font-size: 11pt; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 14px 0; }
"""


def find_edge() -> Path:
    for c in EDGE_CANDIDATES:
        p = Path(c)
        if p.exists():
            return p
    raise SystemExit("找不到 Microsoft Edge。装一个 Edge 或用 --html 只出 HTML。")


def strip_front_matter(text: str) -> str:
    """去掉 YAML front matter 与 UTF-8 BOM。"""
    text = text.lstrip("\ufeff")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_html(out_html: Path) -> int:
    files = sorted(CHAPTERS.glob("*.md"))
    if not files:
        raise SystemExit(f"没找到章节：{CHAPTERS}")

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

    cover = f"""
<div class="cover">
  <h1>AI Agent 实战手册</h1>
  <p style="font-size:14pt;color:#475569;">从零基础到生产部署 · 31 章 · 11 个可运行示例</p>
  <div class="meta">
    <p>在线版：https://xwh630.github.io/ai-agent-handbook/</p>
    <p>仓库：https://github.com/Xwh630/ai-agent-handbook</p>
    <p>CLI：pip install git+https://github.com/Xwh630/ai-agent-handbook.git &nbsp;→&nbsp; handbook doctor .</p>
    <p>生成日期：{datetime.now().strftime('%Y-%m-%d')}</p>
  </div>
</div>
"""

    toc = ['<div class="toc"><h1>目录</h1><ol>']
    for f in files:
        text = strip_front_matter(f.read_text(encoding="utf-8", errors="ignore"))
        toc.append(f"<li>{title_of(text, f.stem)}</li>")
    toc.append("</ol></div>")
    toc_html = "\n".join(toc)

    body = [cover, toc_html]
    for f in files:
        text = strip_front_matter(f.read_text(encoding="utf-8", errors="ignore"))
        md.reset()
        body.append(md.convert(text))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>AI Agent 实战手册</title><style>{CSS}</style></head>
<body>{''.join(body)}</body></html>"""

    out_html.write_text(html, encoding="utf-8")
    return len(files)


def html_to_pdf(edge: Path, html: Path, pdf: Path) -> bool:
    # Edge 对非 ASCII 输出路径会静默失败：先写 ASCII 临时文件，成功后再改名
    tmp_pdf = Path(tempfile.gettempdir()) / "handbook_build.pdf"
    if tmp_pdf.exists():
        tmp_pdf.unlink()

    # Edge 对 file:/// URI 支持不佳，用 C:/... 形式的 POSIX 路径最稳
    cmd = [
        str(edge),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--virtual-time-budget=30000",
        f"--print-to-pdf={tmp_pdf.as_posix()}",
        "--no-pdf-header-footer",
        html.as_posix(),
    ]
    subprocess.run(cmd, capture_output=True, timeout=300)

    if not (tmp_pdf.exists() and tmp_pdf.stat().st_size > 1024):
        print(f"Edge 未产出 PDF（临时路径 {tmp_pdf}）")
        return False

    pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tmp_pdf, pdf)
    return pdf.exists() and pdf.stat().st_size > 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "AI-Agent-实战手册.pdf"))
    ap.add_argument("--html", action="store_true", help="只生成 HTML，不转 PDF")
    a = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="hb_pdf_"))
    html = tmp / "handbook.html"
    n = build_html(html)
    print(f"已合并 {n} 章 → {html}  ({html.stat().st_size/1024:.0f} KB)")

    if a.html:
        print("--html 模式，跳过 PDF 转换")
        return

    pdf = Path(a.out)
    edge = find_edge()
    ok = html_to_pdf(edge, html, pdf)
    if ok:
        print(f"✅ PDF 已生成：{pdf}  ({pdf.stat().st_size/1048576:.1f} MB)")
    else:
        print("❌ PDF 生成失败。可先 python scripts/build_pdf.py --html 检查 HTML")
        sys.exit(1)


if __name__ == "__main__":
    main()
