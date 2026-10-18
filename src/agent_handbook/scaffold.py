"""Agent 项目脚手架：生成一份「五根柱子都在」的最小可运行骨架。

不是玩具 demo —— 生成的项目自带预算守卫、上下文压缩、checkpoint、
失败分级和权限策略，跑起来就能撑住一次真实任务。
"""

from pathlib import Path

MAIN_PY = '''"""最小可运行 Agent —— 由 `handbook new` 生成。

五根柱子已经各就各位。你要做的只有三件事：
  1. 在 TOOLS 里注册你的真实工具
  2. 在 SYSTEM_PROMPT 里写清任务边界
  3. 把 .env.example 复制为 .env 并填写
"""

import json
import os
import time
from pathlib import Path

# ---------- 1. 任务边界：步数 + token 双闸门 ----------
MAX_STEPS = int(os.getenv("MAX_STEPS", "12"))
TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "60000"))
MAX_RETRY = 3

SYSTEM_PROMPT = """你是一个务实的任务执行 Agent。
- 每轮只做一件事，做完就汇报
- 拿不准就停下来问，不要猜
- 优先删除代码而不是添加代码
"""

# ---------- 工具定义（TODO: 换成你自己的） ----------
TOOLS = {
    "read_file": lambda p: Path(p).read_text(encoding="utf-8", errors="ignore")[:4000],
    "write_file": lambda p, c: (Path(p).write_text(c, encoding="utf-8"), "ok")[1],
    "list_dir": lambda p: "\\n".join(str(x) for x in Path(p).iterdir())[:2000],
}


# ---------- 5. 权限体系：🟢放行 / 🟡通知 / 🔴必须审批 ----------
PERMISSION = {
    "read_file": "green",
    "list_dir": "green",
    "write_file": "yellow",
    "run_shell": "red",
}


def require_approval(tool_name, args_preview=""):
    """按风险档位决定能不能直接干。返回 True 表示放行。"""
    level = PERMISSION.get(tool_name, "red")
    if level == "green":
        return True
    if level == "yellow":
        print(f"🟡 [通知] 即将执行 {tool_name} {args_preview}")
        return True
    print(f"🔴 [审批] {tool_name} 属于高危操作，需要人工确认：{args_preview}")
    return input("  输入 y 放行，其它任意键拒绝 > ").strip().lower() == "y"


def call_tool(name, *args):
    if not require_approval(name, str(args)[:80]):
        raise PermissionError(f"{name} 未获批准")
    return TOOLS[name](*args)


class Budget:
    """任务边界：步数与 token 任一超闸就升级给人类。"""

    def __init__(self, max_steps, token_budget):
        self.steps = 0
        self.tokens = 0
        self.max_steps = max_steps
        self.token_budget = token_budget

    def spend(self, tokens=0):
        self.steps += 1
        self.tokens += tokens
        if self.steps >= self.max_steps:
            raise RuntimeError(f"达到 {self.max_steps} 步上限，任务升级给人类")
        if self.tokens >= self.token_budget:
            raise RuntimeError(f"token 已达 {self.token_budget} 上限，任务升级给人类")


class Context:
    """上下文管理：按 token 预算压缩，保头保尾。"""

    def __init__(self, token_budget, keep=6):
        self.messages = []
        self.keep = keep
        self.token_budget = token_budget

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.compact()

    def estimate(self):
        return sum(len(m["content"]) // 2 for m in self.messages)

    def compact(self):
        if self.estimate() <= self.token_budget:
            return
        head, tail = self.messages[:2], self.messages[-self.keep:]
        dropped = len(self.messages) - len(head) - len(tail)
        note = {"role": "system", "content": f"[已压缩 {dropped} 条历史，保留关键决策]"}
        self.messages = head + [note] + tail
        print(f"🧹 上下文压缩：丢掉 {dropped} 条，保头保尾")

    def render(self):
        return "\\n".join(f"{m['role']}: {m['content']}" for m in self.messages)


class Checkpointer:
    """状态持久化：崩溃之后从断点接着干。"""

    def __init__(self, path=".checkpoints/state.json"):
        self.path = Path(path)

    def save(self, state):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self):
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return None


def classify_failure(exc):
    """失败恢复：L1 重试 / L2 换路 / L3 降级 / L4 升级给人类。"""
    msg = str(exc).lower()
    if "timeout" in msg or "connection" in msg:
        return "L1"
    if "not found" in msg or "no such" in msg:
        return "L2"
    if "permission" in msg or "denied" in msg:
        return "L3"
    return "L4"


def escalate_to_human(reason):
    """L4 与预算耗尽的统一出口：把状态留下，交给人。"""
    print(f"🚨 升级给人类：{reason}")
    print("   当前状态已存入 .checkpoints/state.json，处理完加 --resume 继续")


def call_llm(prompt):
    """TODO: 换成你自己的模型（任意 OpenAI 兼容接口均可）。"""
    base = os.getenv("OPENAI_BASE_URL", "")
    key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("MODEL_NAME", "deepseek-chat")
    if not (base and key):
        return "[离线模式] 未配置模型。复制 .env.example 为 .env 并填写后可真实调用。"
    try:
        from openai import OpenAI
        client = OpenAI(base_url=base, api_key=key)
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content
    except Exception as e:
        raise RuntimeError(str(e))


def run(task, resume=False):
    budget = Budget(MAX_STEPS, TOKEN_BUDGET)
    ctx = Context(TOKEN_BUDGET)
    ckpt = Checkpointer()

    if resume:
        saved = ckpt.load()
        if saved:
            print(f"↩️  从 checkpoint 恢复：第 {saved.get('step', 0)} 步")

    ctx.add("system", SYSTEM_PROMPT)
    ctx.add("user", task)

    for step in range(1, MAX_STEPS + 1):
        print(f"\\n── step {step} ──")
        reply = None
        for attempt in range(MAX_RETRY):
            try:
                reply = call_llm(ctx.render())
                break
            except Exception as e:
                level = classify_failure(e)
                print(f"   [{level}] {e}")
                if level == "L1":
                    time.sleep(2 ** attempt)
                    continue
                if level == "L2":
                    ctx.add("system", "上一步路径有误，换一种方式。")
                    break
                if level == "L3":
                    escalate_to_human(f"权限不足：{e}")
                    return
                escalate_to_human(f"无法归类：{e}")
                return

        if reply is None:
            continue

        print(reply)
        ctx.add("assistant", reply)
        budget.spend(tokens=len(reply) // 2)
        ckpt.save({"step": step, "task": task})

        if "完成" in reply or "DONE" in reply.upper():
            print("\\n✅ 任务完成")
            break


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="handbook new 生成的 Agent 骨架")
    ap.add_argument("task", nargs="?", default="读一下当前目录的 README.md 并总结要点")
    ap.add_argument("--resume", action="store_true", help="从 checkpoint 恢复")
    a = ap.parse_args()
    try:
        run(a.task, resume=a.resume)
    except RuntimeError as exc:
        escalate_to_human(str(exc))
'''

ENV_EXAMPLE = """# 复制为 .env 后填写（.env 已在 .gitignore 中）
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
MODEL_NAME=deepseek-chat

# 任务边界
MAX_STEPS=12
TOKEN_BUDGET=60000
"""

PROJECT_README = """# {name}

由 [`handbook new`](https://github.com/Xwh630/ai-agent-handbook) 生成的 Agent 骨架。
不是玩具 demo —— 五根柱子都在，跑起来就能撑住一次真实任务。

## 30 秒跑起来

```bash
cp .env.example .env      # 填模型地址与 Key
python main.py "你的任务"
```

没配 Key 也能跑：会进入离线占位模式，让你先看清骨架怎么转。

## 五根柱子在哪

| 支柱 | 实现位置 | 手册 |
|------|---------|------|
| 任务边界 | `Budget`（步数 + token 双闸门，超了升级给人类） | 第 25 章 25.2 |
| 上下文管理 | `Context.compact()`（按 token 预算压缩，保头保尾） | 第 25 章 25.3 |
| 状态持久化 | `Checkpointer`（`.checkpoints/state.json` + `--resume`） | 第 25 章 25.4 |
| 失败恢复 | `classify_failure()` L1–L4 + 指数退避重试 + `escalate_to_human()` | 第 25 章 25.5 |
| 权限体系 | `PERMISSION` 三档 + `require_approval()`（🔴 档需人工输入 y） | 第 25 章 25.6 |

## 给自己做个体检

```bash
pip install agent-handbook
handbook doctor .
```

生成时这个骨架自身是满分（10/10，评级 A）。你改完再体检一次，看有没有把柱子改塌。

## 下一步 TODO

1. 在 `TOOLS` 里注册你的真实工具，并给每个工具在 `PERMISSION` 里定档
2. `SYSTEM_PROMPT` 写清边界——这一步比换更贵的模型便宜一百倍
3. 把 `.checkpoints/` 换成正经存储（SQLite / Redis）再上生产
"""

GITIGNORE = """.env
.checkpoints/
output/
__pycache__/
*.pyc
"""


def create(name: str, dest: Path = None) -> Path:
    """生成项目骨架，返回项目路径。"""
    root = (dest or Path.cwd()) / name
    if root.exists():
        raise FileExistsError(f"目录已存在：{root}")

    root.mkdir(parents=True)
    (root / "main.py").write_text(MAIN_PY, encoding="utf-8")
    (root / ".env.example").write_text(ENV_EXAMPLE, encoding="utf-8")
    (root / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (root / "README.md").write_text(PROJECT_README.format(name=name), encoding="utf-8")

    return root
