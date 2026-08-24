# 📖 项目使用说明

> 本文档面向**项目作者（维护者）**与**读者（使用者）**，说明如何维护、使用与推广本仓库。

---

## 一、读者快速上手（0 成本）

| 方式 | 说明 | 入口 |
|------|------|------|
| 🌐 在线阅读 | 无需克隆，浏览器直接看，支持搜索/明暗切换 | https://xwh630.github.io/ai-agent-handbook/ |
| 🐳 Docker 一键跑 | 含 Ollama 本地大模型，克隆即用 | 见 README「Docker 一键启动」 |
| 💻 克隆到本地 | 跟随章节逐步动手 | `git clone https://github.com/Xwh630/ai-agent-handbook.git` |
| 📚 按路线学 | 新手 → 入门 → 进阶 → 高级，18 章循序渐进 | 见 README「学习路线」 |

**推荐阅读顺序（零基础）**：`00 快速入门 → 01 基础 → 02 手写 ReAct → 07 工具调用 → 12 实战一 → 99 术语表`。

---

## 二、作者维护指南

### 2.1 日常更新章节内容

```bash
cd "C:/TRAE WORK/GUTHUB/ai-agent-handbook"
git add -A
git commit -m "📝 更新第 X 章：... "
git push
```

推送到 `main` 后，GitHub Actions 会自动：
1. 重新构建 MkDocs 站点并部署到 `gh-pages` 分支（约 1-2 分钟）
2. 在线文档站自动更新，**无需手动操作**

### 2.2 修改文档站配置

- 站点结构配置：`mkdocs.yml`（导航、主题、插件）
- 构建暂存逻辑：`scripts/build_docs.py`（新增根目录文件记得加进 `COPIES` 列表）

本地预览：
```bash
python scripts/build_docs.py && mkdocs serve
# 浏览器打开 http://127.0.0.1:8000
```

### 2.3 发布新版本 Release

1. 更新 README 版本号与变更记录
2. 打标签并推送：
```bash
git tag v1.1.0
git push origin v1.1.0
```
3. 在 GitHub 仓库页面 → Releases → 基于该标签创建 Release，填写中文更新说明

### 2.4 处理 Issue / PR

- 贡献者提交 PR 后，CI 会自动检查**死链**（lychee）与构建是否通过
- 合并前请确认：PR 检查清单勾选、`python scripts/build_docs.py && mkdocs build` 通过
- 模板已就绪：Bug 报告 / 功能建议（`.github/ISSUE_TEMPLATE/`）

### 2.5 英文版同步（en/）

- 翻译文件放 `en/chapters/`（与原章节同名）
- 翻译进度记录在 `en/TRANSLATION_STATUS.md`
- 更新翻译时记得同步更新该状态表

---

## 三、推广清单（需作者本人操作）

以下事项依赖你的个人账号/平台，**AI 无法代劳**，建议按优先级推进：

### 🔥 高优先级（见效快）

- [ ] **B 站发布视频**：录制 1-2 个「零基础用 LangGraph 5 分钟写第一个 Agent」实操视频，简介挂仓库链接
- [ ] **掘金 / 知乎 / 公众号发文**：把 README 的「从零手写 ReAct」章节改写为系列文章，文末附仓库链接
- [ ] **微信/QQ 技术群分享**：在 AI 开发群、大模型交流群分享仓库（注意群规，避免被认为广告）
- [ ] **GitHub 提交 awesome 列表 PR**：向以下列表提交收录申请（需在列表中写明教程/学习类条目）
  - `e2b-dev/awesome-ai-agents`（29.6K⭐，需确认教程区块）
  - `EmbraceAGI/awesome-chatgpt-zh`（11.7K⭐，其 Agent_First.md 偏工具清单，契合度一般，可考虑在教程类列表申请）
  - `kyrolabs/awesome-agents`（2.8K⭐，无教程区块，谨慎）

### 📌 中优先级（持续积累）

- [ ] **回复 GitHub 上的相关讨论**：在 AI Agent 相关 Issue/讨论中自然提及本项目
- [ ] **Hacker News / V2EX 发布**：英文可在 HN Show HN，中文在 V2EX 的「分享创造」板块
- [ ] **制作目录/合集页**：把 18 章做成知乎专栏/CSDN 合集，互相引流

### 🌱 长期维护

- [ ] 每周更新 1 次内容（新框架动态、示例补充）
- [ ] 及时回复 Issue 与 PR，提升社区活跃度（活跃度是 star 增长的关键信号）
- [ ] 积累 3-5 个真实用户案例后，补充「用户实践」章节

---

## 四、项目现状一览（2026-08-24）

| 项目 | 状态 | 地址 |
|------|------|------|
| 主仓库 | ✅ 已推送 | https://github.com/Xwh630/ai-agent-handbook |
| 在线文档站 | ✅ 已上线 | https://xwh630.github.io/ai-agent-handbook/ |
| v1.0.0 Release | ✅ 已发布 | https://github.com/Xwh630/ai-agent-handbook/releases/tag/v1.0.0 |
| 个人 Profile 仓库 | ✅ 已装修 | https://github.com/Xwh630 |
| 自动部署 CI | ✅ 运行中 | main 推送 → 自动更新在线文档 |
| 链接检查 CI | ✅ 运行中 | 每周日 + PR/push 触发 |
| 社区协作文件 | ✅ 就绪 | CONTRIBUTING + Issue/PR 模板 |
| 生态联动 | ✅ 已添加 | README 官方仓库/awesome 清单链接 |

---

*本文件由 AI 辅助生成，随项目持续更新。*
