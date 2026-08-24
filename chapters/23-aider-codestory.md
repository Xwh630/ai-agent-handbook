# 第 23 章：Aider 代码助手 — 终端里的 AI 编程伙伴

> **Aider** 是一款运行在终端的 AI 编程助手，支持多模型（OpenAI、Anthropic、DeepSeek、Gemini 等），具备 Git 深度集成、会话恢复、多文件编辑等强大功能。它是开发者在命令行环境下的理想 AI 编程伴侣。

---

## 23.1 核心定位

| 特性 | 说明 |
|------|------|
| **运行环境** | 终端（CLI） |
| **官方模型** | 支持 OpenAI、Anthropic、DeepSeek、Google Gemini 等 |
| **主要用途** | 终端代码编辑、Git 工作流集成、会话持久化 |
| **集成方式** | 命令行工具 + Git 原生集成 |
| **开源协议** | Apache-2.0 |

> 💡 **与 Codex CLI 对比**：Aider 更专注于代码编辑和 Git 工作流，Codex CLI 功能更全面（含终端执行）。两者各有侧重，可互补使用。

---

## 23.2 安装与配置

### 安装 Aider

```bash
# 使用 pip 安装（推荐）
pip install aider-chat

# 验证安装
aider --version
```

### 配置 API Key

```bash
# 方式一：环境变量
export OPENAI_API_KEY="sk-..."

# 方式二：交互式配置
aider --model gpt-4o

# 使用 DeepSeek
export ANTHROPIC_API_KEY="sk-ant-..."  # 如果用 Claude
# 或直接指定模型
aider --model deepseek/deepseek-chat
```

### 首次运行

```bash
# 进入项目目录
cd my-project

# 启动 Aider（自动检测 Git 仓库）
aider

# 或直接指定模型运行
aider --model gpt-4o
```

---

## 23.3 核心功能

### Git 深度集成

```bash
# 自动检测 git 仓库
# 提交前自动 diff
# 支持 commit message 自动生成
# 支持 staged/unstaged 文件追踪
```

### 会话恢复

```bash
# 保存当前会话
/save my-session.md

# 恢复之前的会话
aider --resume my-session.md
```

### 多文件编辑

```
# 选中多个文件进行编辑
 aider file1.py file2.py file3.py
```

---

## 23.4 支持的模型

| 模型提供商 | 模型名称 | 配置方式 |
|-----------|---------|---------|
| OpenAI | gpt-4o、gpt-4o-mini | `--model openai/gpt-4o` |
| Anthropic | claude-sonnet-4、claude-opus-4 | `--model anthropic/claude-sonnet-4` |
| DeepSeek | deepseek-chat、deepseek-coder | `--model deepseek/deepseek-chat` |
| Google | gemini-2.0-flash | `--model google/gemini-2.0-flash` |
| Ollama | llama3.1、deepseek-coder | `--model ollama/llama3.1` |

---

## 23.5 常用命令

| 命令 | 功能 |
|------|------|
| `/add <file>` | 添加文件到会话 |
| `/drop <file>` | 从会话中移除文件 |
| `/models` | 列出可用模型 |
| `/cost` | 显示当前会话 Token 消耗 |
| `/diff` | 查看当前更改 |
| `/help` | 显示帮助信息 |

---

## 23.6 高级用法

### 自定义 Prompt

创建 `.aider.prompt` 文件：

```
# .aider.prompt
你是一个资深 Python 开发者，擅长编写干净、高效的代码。
请遵循 PEP 8 规范，并在修改代码时添加适当的注释。
```

### 插件系统

```bash
# 安装第三方插件
aider-plugin install aider-plugin-git-blame

# 查看已安装插件
aider-plugin list
```

---

## 23.7 最佳实践

1. **先备份再编辑**：Aider 会创建备份文件，但仍建议手动备份重要改动
2. **善用会话恢复**：长时间项目可分多次会话完成
3. **控制 Token 消耗**：使用 `/cost` 监控，避免意外高额费用
4. **结合 Git 使用**：利用 Aider 的 Git 集成分阶段提交代码

---

## 23.8 学习资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://aider.chat/docs/ |
| GitHub 仓库 | https://github.com/paul-gauthier/aider |
| 模型配置 | https://aider.chat/docs/config/supported-models.html |
| 插件市场 | https://github.com/paul-gauthier/aider-plugins |

---

## 23.9 本章小结

Aider 是一个强大的终端 AI 编程助手，核心优势在于：

- ✅ **多模型支持**：OpenAI、Claude、DeepSeek、Gemini 均可用
- ✅ **Git 原生集成**：自动 diff、commit、分支管理
- ✅ **会话持久化**：保存和恢复编程上下文
- ✅ **开源免费**：Apache-2.0 许可，可自行部署

---

> **下一章**：[第 24 章 · Trae IDE](./24-trae-ide.md)
