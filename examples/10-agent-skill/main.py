#!/usr/bin/env python3
"""
Agent Skill 规范校验器
=====================================================
把《AI Agent 实战手册》第 26.10 节的发布自检清单做成可执行工具。

为什么需要它？
  SKILL.md 的字段约束很琐碎（name 必须与目录名一致、不能连续连字符、
  description 上限 1024 字符……），肉眼检查极易漏。这个脚本一次性跑完
  20+ 项检查，并按 ERROR / WARN / INFO 分级输出。

设计要点（也示范了一个合格的 skill 脚本该怎么写）：
  1. 零第三方依赖 —— PyYAML 缺失时自动降级到内置解析器，永远不会 import 失败
  2. 错误信息友好 —— 告诉你违反了哪条约束，而不是抛 traceback
  3. 退出码语义清晰 —— 0=全部通过，1=有 ERROR，可直接接进 CI
  4. 纯静态分析 —— 不执行被检查的脚本，只读不跑，因此本身是安全的

用法：
    python3 main.py <skill-dir> [--strict] [--json]

示例：
    python3 main.py ./sample-skill
    python3 main.py ./release-notes --strict
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# ── 规范常量（来源：https://agentskills.io/specification）──────────────────
NAME_MAX = 64
DESC_MAX = 1024
COMPAT_MAX = 500
SKILL_LINES_MAX = 500
SKILL_TOKENS_MAX = 5000
REFERENCE_TOKENS_MAX = 2000
DESC_MIN_RECOMMENDED = 40

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KNOWN_LICENSES = {
    "mit", "apache-2.0", "apache 2.0", "bsd-2-clause", "bsd-3-clause",
    "gpl-3.0", "lgpl-3.0", "mpl-2.0", "unlicense", "proprietary",
}
# 危险模式：远程下载后直接执行，是 supply chain 攻击的典型形态
DANGEROUS_PATTERNS = [
    (r"curl\s+[^\n|]*\|\s*(ba)?sh", "远程下载后直接管道执行"),
    (r"wget\s+[^\n|]*\|\s*(ba)?sh", "远程下载后直接管道执行"),
    (r"eval\s*\(", "使用 eval() 执行动态代码"),
    (r"exec\s*\(", "使用 exec() 执行动态代码"),
    (r"__import__\s*\(", "动态 import"),
    (r"base64\s*\.\s*b64decode", "base64 解码（可能用于隐藏真实意图）"),
    (r"subprocess\.[a-z]+\([^)]*shell\s*=\s*True", "shell=True 存在命令注入风险"),
]
ENV_ACCESS_RE = re.compile(r"os\.environ|getenv|os\.getenv")


# ── 前置宏 steelyard ──────────────────────────────────────────────────────
class Report:
    """收集检查结果，按严重度分级。"""

    def __init__(self):
        self.items: list[dict] = []

    def add(self, level: str, code: str, msg: str, hint: str = ""):
        self.items.append({"level": level, "code": code, "msg": msg, "hint": hint})

    def error(self, code, msg, hint=""):
        self.add("ERROR", code, msg, hint)

    def warn(self, code, msg, hint=""):
        self.add("WARN", code, msg, hint)

    def info(self, code, msg, hint=""):
        self.add("INFO", code, msg, hint)

    def ok(self, msg):
        self.add("PASS", "-", msg)

    def count(self, level: str) -> int:
        return sum(1 for i in self.items if i["level"] == level)


def estimate_tokens(text: str) -> int:
    """粗估 token 数：中文按 1.5/字，英文按 1.3/词。够用且无需外部依赖。"""
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    rest = re.sub(r"[\u4e00-\u9fff]", " ", text)
    words = len(re.findall(r"[A-Za-z0-9_'-]+", rest))
    return int(cjk * 1.5 + words * 1.3)


def parse_frontmatter(content: str):
    """提取 YAML frontmatter。PyYAML 可用时用它，否则降级到简易解析器。

    降级解析器只支持 'key: value' 形式的平铺字段 —— 对 name/description/
    license/compatibility/allowed-tools 足够，metadata 嵌套会退化为字符串，
    但这不影响校验目标（我们只关心这些字段"是否存在"）。
    """
    if not content.startswith("---"):
        return None, None, "文件未以 '---' 开头，缺少 YAML frontmatter"

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, None, "frontmatter 未正确闭合（缺少第二个 '---'）"

    raw_fm = parts[1]
    body = parts[2]

    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(raw_fm)
        if not isinstance(parsed, dict):
            return None, body, "frontmatter 解析结果不是字典"
        return parsed, body, ""
    except Exception:
        pass  # PyYAML 未安装，走降级分支

    parsed = {}
    key = None
    buffer: list[str] = []
    for line in raw_fm.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            if key:
                parsed[key] = " ".join(buffer).strip()
            key = m.group(1)
            buffer = [m.group(2).strip()]
        elif key and line.strip():
            buffer.append(line.strip())
    if key:
        parsed[key] = " ".join(buffer).strip()
    if not parsed:
        return None, body, "frontmatter 为空或无法解析"
    return parsed, body, ""


# ── 各项检查 ──────────────────────────────────────────────────────────────
def check_structure(skill_dir: Path, report: Report):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.error("E001", "缺少 SKILL.md", "skill 目录下必须有 SKILL.md")
        return None
    report.ok("SKILL.md 存在")
    return skill_md


def check_frontmatter_fields(fm: dict, body: str, rep: Report):
    # name
    name = fm.get("name")
    if not name:
        rep.error("E101", "缺少必填字段 name", "name 是唯一标识，必须提供")
    else:
        name = str(name).strip()
        if len(name) > NAME_MAX:
            rep.error("E102", f"name 超过 {NAME_MAX} 字符（当前 {len(name)}）", "缩短或用连字符缩写")
        if not NAME_RE.match(name):
            rep.error("E103", f"name '{name}' 不符合命名规则",
                      "只能小写字母/数字/连字符，不能以连字符开头或结尾，不能连续连字符")
        else:
            rep.ok("name 命名规则合规")

    # description
    desc = fm.get("description")
    if not desc:
        rep.error("E201", "缺少必填字段 description", "没有它 Agent 永远无法判断是否该用你")
    else:
        desc = str(desc).strip()
        if not desc:
            rep.error("E202", "description 为空字符串", "规范明确要求非空")
        if len(desc) > DESC_MAX:
            rep.error("E203", f"description 超过 {DESC_MAX} 字符（当前 {len(desc)}）", "压到 300 字符内的甜点区")
        if len(desc) < DESC_MIN_RECOMMENDED:
            rep.warn("W201", f"description 偏短（{len(desc)} 字符）",
                     "建议同时写清「做什么」和「什么时候用」，并埋入用户真实会说的关键词")
        if not re.search(r"use when|用于|适用于|当.{0,10}时|when the user", desc, re.I):
            rep.warn("W202", "description 里看不到「什么时候用」的触发条件",
                     "这是 skill 不被调用的最常见原因；补上 'Use when ...' 之类的话")
        else:
            rep.ok("description 含触发场景描述")

    # compatibility
    compat = fm.get("compatibility")
    if compat and len(str(compat)) > COMPAT_MAX:
        rep.error("E301", f"compatibility 超过 {COMPAT_MAX} 字符", "精简环境要求描述")

    # license
    lic = fm.get("license")
    if not lic:
        rep.info("I301", "未声明 license", "若打算公开发布，建议补上")
    elif str(lic).strip().lower() not in KNOWN_LICENSES:
        rep.info("I302", f"license '{lic}' 不是常见 SPDX 标识", "确认拼写，或写成 bundled 文件名")

    # allowed-tools 拼写
    for bad, good in (("allowed_tools", "allowed-tools"), ("allowedTools", "allowed-tools")):
        if bad in fm:
            rep.error("E401", f"字段名写成了 '{bad}'", f"规范中正确写法是 '{good}'（连字符）")

    # 正文
    lines = len(body.splitlines())
    if lines > SKILL_LINES_MAX:
        rep.warn("W401", f"SKILL.md 正文 {lines} 行，超过建议的 {SKILL_LINES_MAX} 行",
                 "规范建议 <500 行；把详细资料拆到 references/")
    tokens = estimate_tokens(body)
    if tokens > SKILL_TOKENS_MAX:
        rep.warn("W402", f"SKILL.md 正文约 {tokens} token，超过建议的 {SKILL_TOKENS_MAX}",
                 "加载时会整篇进上下文，超预算会拖慢并挤占其他信息")
    else:
        rep.ok(f"正文约 {tokens} token / {lines} 行，在预算内")

    for missing in ("##", "|"):
        pass  # 占位：正文格式无强制要求
    return name, desc


def check_name_matches_dir(name, skill_dir: Path, rep: Report):
    if not name:
        return
    dirname = skill_dir.name
    if str(name) != dirname:
        rep.error("E104", f"name '{name}' 与父目录名 '{dirname}' 不一致",
                  "规范强制要求两者一致，不一致时各客户端行为未定义")
    else:
        rep.ok("name 与父目录名一致")


def check_resources(skill_dir: Path, rep: Report):
    scripts = skill_dir / "scripts"
    refs = skill_dir / "references"
    assets = skill_dir / "assets"

    if not scripts.exists():
        rep.info("I401", "无 scripts/ 目录", "纯指令型 skill 可以没有；但注意：无任何 skill 带脚本时，"
                                            "Agent 连 '可以跑脚本' 这个能力都不会被广告")
    else:
        found = list(scripts.rglob("*"))
        found = [f for f in found if f.is_file()]
        if not found:
            rep.warn("W501", "scripts/ 目录存在但为空", "空目录等同于没有脚本，建议删除或补内容")
        for f in found:
            try:
                head = f.read_text(encoding="utf-8", errors="ignore")[:200]
            except Exception:
                continue
            if f.suffix in (".py", ".sh", ".js", ".ts") and not head.startswith("#!"):
                rep.warn("W502", f"脚本 {f.name} 缺少 shebang", "首行加 #!/usr/bin/env python3 之类并 chmod +x")
            if f.suffix in (".py", ".sh") and not os.access(f, os.X_OK):
                rep.info("I402", f"脚本 {f.name} 无执行位", "chmod +x 后可被直接调用")

    if refs.exists():
        for f in sorted(refs.rglob("*.md")):
            try:
                tokens = estimate_tokens(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            if tokens > REFERENCE_TOKENS_MAX:
                rep.warn("W601", f"参考文件 {f.name} 约 {tokens} token，偏大",
                         "单个 reference 建议 <2000 token，超了按主题继续拆")
    return scripts


def check_security(skill_dir: Path, rep: Report):
    """只读不跑：对被打包的脚本做静态可疑模式扫描。"""
    scripts = skill_dir / "scripts"
    if not scripts.exists():
        return
    for f in scripts.rglob("*"):
        if not f.is_file() or f.suffix not in (".py", ".sh", ".js", ".ts", ".bash"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern, why in DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.I):
                rep.warn("S101", f"{f.name} 命中可疑模式：{why}",
                         "如果你不是刻意这么做，请重点复核；发布时要让使用者能审计这段代码")
        if ENV_ACCESS_RE.search(text):
            rep.info("S201", f"{f.name} 读取环境变量",
                     "skill 以完整用户权限运行，可能接触 API Key；建议在 SKILL.md 里声明读了哪些变量")
        if re.search(r"requests\.|urllib|fetch\(|http[s]?://", text):
            rep.info("S202", f"{f.name} 含网络访问",
                     "建议在 SKILL.md 正文明示会访问哪些域名")


def check_extras(skill_dir: Path, rep: Report):
    readme = skill_dir / "README.md"
    if not readme.exists():
        rep.info("I501", "skill 内无 README.md", "若要公开发布，建议加一句介绍")


# ── 主流程 ────────────────────────────────────────────────────────────────
LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2, "PASS": 3}
ICONS = {"ERROR": "❌", "WARN": "⚠️ ", "INFO": "ℹ️ ", "PASS": "✅"}


def validate(skill_dir: Path) -> tuple[Report, dict]:
    rep = Report()
    skill_md = check_structure(skill_dir, rep)
    meta = {}

    if skill_md:
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        fm, body, err = parse_frontmatter(content)
        if err:
            rep.error("E001", f"frontmatter 解析失败：{err}",
                      "确认 SKILL.md 以 '---' 开头、随后空一行写字段、再用 '---' 闭合")
        elif fm:
            name, desc = check_frontmatter_fields(fm, body, rep)
            check_name_matches_dir(name, skill_dir, rep)
            meta = {"name": fm.get("name"), "has_description": bool(fm.get("description"))}

    check_resources(skill_dir, rep)
    check_security(skill_dir, rep)
    check_extras(skill_dir, rep)
    return rep, meta


def render_text(rep: Report, skill_dir: Path) -> None:
    print(f"\n🔍 Agent Skill 校验报告：{skill_dir}")
    print("=" * 68)
    items = sorted(rep.items, key=lambda x: LEVEL_ORDER.get(x["level"], 9))
    for it in items:
        icon = ICONS.get(it["level"], "•")
        print(f"{icon} [{it['code']}] {it['msg']}")
        if it["hint"]:
            print(f"      └─ {it['hint']}")
    print("=" * 68)
    e, w, i, p = (rep.count(x) for x in ("ERROR", "WARN", "INFO", "PASS"))
    print(f"通过 {p}  错误 {e}  警告 {w}  提示 {i}")
    if e:
        print("❌ 存在 ERROR，未达到发布标准。")
    elif w:
        print("⚠️  无 ERROR，但有 WARN —— 建议处理后再发布。")
    else:
        print("✅ 全部通过，可以发布。")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="校验 Agent Skill 是否符合 SKILL.md 规范")
    parser.add_argument("skill_dir", help="skill 目录路径（内含 SKILL.md）")
    parser.add_argument("--strict", action="store_true", help="有 WARN 也返回非零退出码")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出，便于 CI 消费")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"error: '{skill_dir}' 不是目录或不存在", file=sys.stderr)
        sys.exit(2)

    rep, meta = validate(skill_dir)

    if args.json:
        print(json.dumps({
            "skill": str(skill_dir),
            "meta": meta,
            "counts": {lvl: rep.count(lvl) for lvl in ("ERROR", "WARN", "INFO", "PASS")},
            "items": rep.items,
        }, ensure_ascii=False, indent=2))
    else:
        render_text(rep, skill_dir)

    if rep.count("ERROR"):
        sys.exit(1)
    if args.strict and rep.count("WARN"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
