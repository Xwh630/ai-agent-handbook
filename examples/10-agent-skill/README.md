# 示例 10 · Agent Skill 规范校验器

把《AI Agent 实战手册》**第 26.10 节**的发布自检清单做成了可执行工具。

## 为什么需要它

SKILL.md 的字段约束很琐碎——`name` 必须与父目录名完全一致、不能有连续连字符、`description` 上限 1024 字符、`allowed-tools` 是连字符不是下划线……**肉眼检查极易漏掉其中某一条**，而漏掉任何一条都可能导致你的 skill 在某些客户端里静默失效。

这个脚本一次性跑完 20+ 项检查。

## 快速开始

```bash
# 校验随附的最小样例（全通过）
python3 main.py ./sample-skill

# 严格模式：有 WARN 也算失败，适合接 CI
python3 main.py ./sample-skill --strict

# JSON 输出，方便程序消费
python3 main.py ./sample-skill --json
```

**零依赖。** PyYAML 可选——装了就用它，没装会自动降级到内置的简易解析器，永远不会因为缺包而跑不起来。

## 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 全部通过（或严格模式下无 WARN） |
| `1` | 存在 ERROR（严格模式下 WARN 也算） |
| `2` | 参数错误 / 目录不存在 |

可以直接接进 CI：

```yaml
- name: Validate skills
  run: |
    for d in skills/*/; do
      python3 examples/10-agent-skill/main.py "$d" --strict || exit 1
    done
```

## 检查项一览

### ERROR（必须修）

| 代码 | 检查内容 |
|------|---------|
| `E001` | SKILL.md 是否存在、frontmatter 是否可解析 |
| `E101` | `name` 缺失 |
| `E102` | `name` 超过 64 字符 |
| `E103` | `name` 命名违规（大写 / 连续连字符 / 首尾连字符） |
| `E104` | `name` 与父目录名不一致 ← **新手头号坑** |
| `E201` | `description` 缺失 |
| `E202` | `description` 为空 |
| `E203` | `description` 超过 1024 字符 |
| `E301` | `compatibility` 超过 500 字符 |
| `E401` | 字段名拼错（`allowed_tools` → `allowed-tools`） |

### WARN（建议修）

| 代码 | 检查内容 |
|------|---------|
| `W201` | `description` 过短（< 40 字符） |
| `W202` | `description` 缺触发场景 ← **skill 不被调用的主因** |
| `W401` | 正文超过 500 行 |
| `W402` | 正文超过 ~5,000 token |
| `W501` | `scripts/` 存在但为空 |
| `W502` | 脚本缺 shebang |
| `W601` | 单个 reference 超过 ~2,000 token |
| `S101` | 命中可疑模式（`curl \| sh`、`eval`、`shell=True` 等） |

### INFO（供你判断）

`I301` 未声明 license · `I302` 非标准 license · `I401` 无 scripts/ · `I402` 脚本无执行位 · `I501` 无 README · `S201` 脚本读环境变量 · `S202` 脚本含网络访问

> `S201` / `S202` 不是"有罪推定"，而是提醒你：**如果你的 skill 会读环境变量或访问网络，必须在 SKILL.md 正文明示**，否则使用者无法审计。

## 目录说明

```
10-agent-skill/
├── main.py                    # 校验器（纯静态分析，只读不跑）
├── README.md                  # 本文件
└── sample-skill/              # 符合规范的最小可用样例，可作模板
    ├── SKILL.md
    ├── scripts/count_words.py
    ├── references/rules.md
    └── assets/template.md
```

### 关于 `sample-skill`

它是一个**刻意做得很小**的模板：[第 26 章](../../chapters/26-agent-skills.md)讲的所有规范点它都覆盖了，但正文只有 176 token。你可以直接复制这个目录改名字起步。

`scripts/count_words.py` 示范了什么样的逻辑该进脚本——**计数这种确定性操作，不该让模型在脑子里算**。

## 一个真实的结果

用这个校验器检查本手册自己的 Skill 包：

```
$ python3 main.py ../../skills/agent-handbook
通过 5  错误 0  警告 0  提示 2
✅ 全部通过，可以发布。
```

> 手册推荐的规范，手册自己遵守。这也是第 26.11 节说的那个"闭环"。

---

**相关章节**：[第 26 章 · Agent Skills 编写实战](../../chapters/26-agent-skills.md)
