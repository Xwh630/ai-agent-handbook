"""31 章全文检索。

设计取舍：纯标准库、零依赖。标题命中权重高于正文，
输出「章节 + 行号 + 上下文片段」，直接可用编辑器跳过去。
"""

import re
from pathlib import Path

from ._paths import chapters_dir

# 章节标题的 emoji/前缀噪音，用于输出时清理
_NOISE = re.compile(r"^[#\s*`>]+")


def _read_lines(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []


def _chapter_title(path: Path, lines) -> str:
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def iter_chapters():
    """产出 (path, lines)，按文件名排序。"""
    d = chapters_dir()
    for p in sorted(d.glob("*.md")):
        lines = _read_lines(p)
        if lines:
            yield p, lines


def tokenize(query: str):
    """中文没有空格，直接整词匹配会漏掉正文。这里做轻量切分：
    含空格 → 按空格分；纯中文且较长 → 切 2-gram；其余整体为一个词。
    """
    q = query.strip().lower()
    if not q:
        return []
    if re.search(r"\s", q):
        return [t for t in re.split(r"\s+", q) if t]
    if re.search(r"[\u4e00-\u9fff]", q):
        if len(q) <= 2:
            return [q]
        # 2-gram：'上下文压缩' -> 上下/下文/文压/压缩
        grams = [q[i:i + 2] for i in range(len(q) - 1)]
        # 去重但保序
        seen, out = set(), []
        for g in grams:
            if g not in seen:
                seen.add(g)
                out.append(g)
        return out
    return [q]


def search(query: str, limit: int = 8, context: int = 1):
    """返回匹配列表：[{file, title, lineno, heading, text, score}]"""
    if not query.strip():
        return []

    # 支持空格分词：全部命中才计分更高
    terms = tokenize(query)
    if not terms:
        return []
    results = []
    current_heading = ""

    for path, lines in iter_chapters():
        title = _chapter_title(path, lines)
        for i, line in enumerate(lines):
            low = line.lower()
            if line.startswith("#"):
                current_heading = _NOISE.sub("", line).strip()

            if not any(t in low for t in terms):
                continue

            all_hit = all(t in low for t in terms)
            score = 0
            if line.startswith("#"):
                score += 10
            if all_hit:
                score += 5
            score += sum(low.count(t) for t in terms)
            # 表格行、代码行略微降权，正文优先
            if line.strip().startswith("|"):
                score -= 1

            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            snippet = "\n".join(lines[start:end]).strip()

            results.append({
                "file": path.name,
                "title": title,
                "lineno": i + 1,
                "heading": current_heading,
                "text": snippet,
                "score": score,
            })

    results.sort(key=lambda r: -r["score"])
    return results[:limit]


def list_chapters():
    """返回 [(filename, title, n_lines)]"""
    out = []
    for path, lines in iter_chapters():
        out.append((path.name, _chapter_title(path, lines), len(lines)))
    return out
