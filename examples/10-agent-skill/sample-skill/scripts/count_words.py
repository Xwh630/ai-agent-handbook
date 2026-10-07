#!/usr/bin/env python3
"""Count words / CJK characters in a file or stdin.

A deliberately tiny script that demonstrates what belongs in scripts/:
deterministic work that a model should not do by hand.

Usage:
    python3 count_words.py <file>
    echo "hello 世界" | python3 count_words.py
"""
import re
import sys


def count(text: str) -> dict:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z0-9_'-]+", text))
    lines = len(text.splitlines())
    return {"cjk_chars": cjk, "latin_words": words, "lines": lines}


def main() -> None:
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"error: cannot read {path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("error: input is empty", file=sys.stderr)
        sys.exit(1)

    r = count(text)
    print(f"CJK chars : {r['cjk_chars']}")
    print(f"Latin words: {r['latin_words']}")
    print(f"Lines     : {r['lines']}")


if __name__ == "__main__":
    main()
