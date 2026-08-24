# 贡献指南 / Contributing Guide

首先，感谢你愿意为 **AI Agent 实战手册** 贡献力量！🎉
你的每一个 PR、Issue 或建议，都在帮助更多中文开发者进入 AI Agent 的世界。

> English version available at the bottom of this file.

---

## 🧭 项目结构速览

```
ai-agent-handbook/
├── chapters/        # 中文教程章节（01-18 + 00 快速上手 + 99 术语表）
├── en/              # 英文版（chapters/ 为已翻译章节）
├── docs/            # 参考文档（框架对比 / 工具调用 / 最佳实践）
├── appendix/        # 附录（错误排查 / 学习资源）
├── examples/        # 可运行示例代码（Python）
├── scripts/         # 工具脚本（如文档站点暂存构建）
└── mkdocs.yml       # 在线文档站点配置（GitHub Pages）
```

## 🚀 快速开始（本地开发）

```bash
# 1. 克隆仓库
git clone https://github.com/Xwh630/ai-agent-handbook.git
cd ai-agent-handbook

# 2.（可选）本地预览在线文档站点
pip install mkdocs-material
python scripts/build_docs.py     # 暂存文档内容到 site-content/
mkdocs serve                     # 打开 http://127.0.0.1:8000
```

## 📝 如何贡献

### 1. 报告 Bug / 提出问题（Issue）

- 先搜索是否已有相同 Issue，避免重复。
- 使用模板，尽量包含：**复现步骤、期望行为、实际行为、环境信息**（Python 版本、框架版本、操作系统）。
- 中文或英文皆可。

### 2. 提交代码（Pull Request）

```bash
git checkout -b feat/your-feature    # 或 fix/xxx, docs/xxx
# ... 做出你的改动 ...
git add .
git commit -m "✨ 描述你的改动"
git push origin feat/your-feature
```

然后在 GitHub 上创建 Pull Request（使用 PR 模板）。

### 3. 我们欢迎的贡献类型

| 类型 | 示例 |
|------|------|
| 📖 新增章节 | 新的框架教程、新玩法实战 |
| ✏️ 内容修正 | 错别字、过时 API、失效链接 |
| 🌐 翻译 | 将中文章节翻译为英文（见下方翻译约定） |
| 💻 示例代码 | 新增 examples/ 下的可运行 demo |
| 🛠️ 基础设施 | 文档站点、CI、Docker 配置优化 |
| 💡 想法建议 | 新框架覆盖、路线图讨论 |

## 🌐 翻译约定（English Translation）

- 英文章节放在 `en/chapters/`，文件名与中文保持一致。
- 翻译时请保持：**代码与命令不翻译、术语首次出现保留英文原词**。
- 每翻译完一章，更新 `en/TRANSLATION_STATUS.md` 的状态表。
- 中文章节末尾的"英文版"链接指向 `../en/chapters/同名文件`。

## ✅ 提交前检查清单

- [ ] 文档改动：本地 `mkdocs build` 无新警告（先运行 `python scripts/build_docs.py`）
- [ ] 代码改动：`examples/` 下示例可通过 `python 文件.py` 运行
- [ ] 链接：尽量使用相对路径链接，不用绝对 URL 指向本仓库内部文件
- [ ] 提交信息：使用约定式提交（`feat:` / `fix:` / `docs:` / `chore:` 等）

## 🤝 行为准则

- 友善、尊重、建设性。对事不对人。
- 新手友好是这本手册的第一原则——写内容时请假设读者是零基础。
- 争议内容（如框架选型观点）请标注个人倾向，避免绝对化表述。

---

## English Version

Thank you for contributing to the **AI Agent Practical Handbook**! ❤️

- **Report bugs / ask questions**: open an Issue using the templates (Chinese or English).
- **Submit changes**: fork the repo, create a branch, open a Pull Request.
- **Translations**: place English chapters under `en/chapters/` with matching filenames, and update `en/TRANSLATION_STATUS.md`.
- **Before submitting**: run `python scripts/build_docs.py && mkdocs build` for docs changes; make sure example scripts run.
- **Commit style**: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).

All contributions, big or small, are deeply appreciated. Star the repo if you find it helpful! ⭐
