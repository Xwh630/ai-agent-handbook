# 第 22 章：Continue 编辑器 — 让 VSCode / JetBrains 变成 AI 编码助手

> **Continue** 是最流行的开源 AI 编程助手，支持 VSCode 和 JetBrains 系列 IDE。它允许你选择任意 LLM（OpenAI、Claude、本地模型等），通过 MCP 协议集成外部工具，并提供完整的代码补全、对话、编辑能力。

---

## 22.1 核心定位

| 特性 | 说明 |
|------|------|
| **运行环境** | VSCode / JetBrains 插件 |
| **官方模型** | 支持 OpenAI、Anthropic、DeepSeek、Ollama 等任意 LLM |
| **主要用途** | 代码补全、对话式编程、代码解释、调试辅助 |
| **集成方式** | 插件 + MCP Server 支持 |
| **开源协议** | Apache-2.0 |

> 💡 **与 Claude Code 对比**：Continue 是 IDE 插件形态，更灵活可自定义；Claude Code 是独立 CLI 工具，更专注终端场景。两者可搭配使用。

---

## 22.2 安装与配置

### 安装 Continue 插件

```bash
# VSCode：在扩展市场搜索 "Continue" 并安装
# 或命令行安装：
code --install-extension continue.continue

# JetBrains：在插件市场搜索 "Continue" 并安装
```

### 配置文件位置

```
~/.continue/config.json   # Windows: %USERPROFILE%\.continue\config.json
```

### 配置示例（OpenAI）

```json
{
  "models": [
    {
      "title": "GPT-4o",
      "provider": "openai",
      "model": "gpt-4o",
      "apiKey": "sk-..."
    }
  ],
  "tabAutocompleteModel": {
    "title": "Codex Lite",
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

### 配置示例（DeepSeek）

```json
{
  "models": [
    {
      "title": "DeepSeek Chat",
      "provider": "openai",
      "model": "deepseek-chat",
      "apiBase": "https://api.deepseek.com/v1",
      "apiKey": "sk-..."
    }
  ]
}
```

---

## 22.3 核心功能

### Tab 自动补全

- 输入时自动提示代码续写
- 支持上下文感知（读取当前文件+项目结构）
- 可按 Tab 接受提示

### Slash Commands（斜杠命令）

| 命令 | 功能 |
|------|------|
| `/explain` | 解释选中代码 |
| `/fix` | 修复选中代码的错误 |
| `/optimize` | 优化代码性能 |
| `/tests` | 为选中代码生成单元测试 |
| `/docs` | 生成文档注释 |
| `/review` | 代码审查 |

### 对话面板（Cmd/Ctrl + L）

- 选中代码后打开对话
- 支持多轮对话修改代码
- 直接在编辑器中应用生成的代码

---

## 22.4 MCP 集成

Continue 支持通过 MCP 协议连接外部工具：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

## 22.5 自定义模型与价格优化

### 使用本地模型（Ollama）

```json
{
  "models": [
    {
      "title": "Llama 3.1",
      "provider": "ollama",
      "model": "llama3.1:8b"
    },
    {
      "title": "DeepSeek R1",
      "provider": "ollama",
      "model": "deepseek-r1:7b"
    }
  ]
}
```

### 模型组合策略

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 代码补全 | gpt-4o-mini / deepseek-coder | 速度快、成本低 |
| 复杂推理 | gpt-4o / deepseek-chat | 准确率高 |
| 本地运行 | llama3.1:8b | 隐私保护、免费 |

---

## 22.6 最佳实践

1. **选择合适模型**：简单任务用小模型，复杂推理用大模型
2. **善用 Tab 补全**：减少重复输入，提升编码效率
3. **结合 Git 使用**：在对话中让 AI 帮你写 commit message
4. **配置 .continueignore**：排除不需要分析的目录

---

## 22.7 学习资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.continue.dev/ |
| GitHub 仓库 | https://github.com/continuedev/continue |
| 模型配置指南 | https://docs.continue.dev/integrations/models |
| MCP 服务器列表 | https://github.com/modelcontextprotocol/servers |

---

## 22.8 本章小结

Continue 是一个可扩展的 AI 编程助手，核心优势在于：

- ✅ **多 IDE 支持**：VSCode + JetBrains 全覆盖
- ✅ **多模型兼容**：OpenAI、Claude、DeepSeek、Ollama 均可用
- ✅ **MCP 扩展**：通过插件生态连接更多工具
- ✅ **开源免费**：可自行部署，无厂商锁定

---

> **下一章**：[第 23 章 · Aider 代码助手](./23-aider-codestory.md)
