# 🧪 读者项目 · Community Projects

> 用这本手册做出东西之后，把项目放进这里——这是「Co-creation」机制：
> **你的项目成为下一个读者的起点**，也是这本手册活着的证明。

对标一下天花板：Datawhale 的 [hello-agents](https://github.com/datawhalechina/hello-agents)
（83.5K ⭐）正是靠这个机制拿到 **10,350 个 fork**——不是靠点赞，是靠真的有人在上面盖东西。

---

## 怎么收录你的项目

### 1. 命名规范

目录名 = `你的GitHub用户名-项目名`，例如：

```
projects/
├── Xwh630-mini-harness-demo/     ← 本仓库作者的示范
└── yourname-your-agent/          ← 你的项目
```

### 2. 提一个 PR，包含两样东西

1. 上面那个目录，里面放你的项目（或一个 README 指向你的仓库）
2. 一个 `PROJECT.md`，按下面的模板填

### 3. 通过后

你的项目会出现在本文件下方的列表里，并在 Radar 周刊的「社区精选」中展示。

---

## 收录模板（PROJECT.md）

复制下面这段，填完随 PR 提交：

```markdown
# 项目名

- **作者**：[@yourname](https://github.com/yourname)
- **仓库**：https://github.com/yourname/your-project
- **一句话**：它解决什么问题

## 用到了手册哪些内容

| 手册章节 | 你是怎么用的 |
|---------|-------------|
| 第 X 章 | ... |

## 体检分数

```bash
pip install git+https://github.com/Xwh630/ai-agent-handbook.git
handbook doctor .
```

> 总分 __/10，评级 __

## 踩过的坑 / 想对后来的读者说什么

（这一段最有价值——别人会在这里少走弯路）
```

---

## 已收录项目

| 项目 | 作者 | 用到的章节 | 体检 |
|------|------|-----------|------|
| *等待第一个读者提交* | — | — | — |

> 🥚 **第一个提交者有额外好处**：你的项目会被写进下一期 Radar 周刊的「社区精选」头条，
> 并在 README 的致谢墙留名。
