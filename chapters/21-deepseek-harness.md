---
适配框架版本: DeepSeek Harness 1.x
最后校验: 2026-10-06
上游变更监控: https://github.com/deepseek-ai/deepseek-harness/releases
---

# 第 21 章：DeepSeek Harness（dsh）— 2026 年度最具潜力的开源 Agent

> **DeepSeek Harness（dsh）** 由 DeepSeek 于 2026-08-13 发布，MIT 开源协议。这是第一个支持 SWE-bench 全场景评测的开源 Agent 框架，发布 30 分钟即突破 1 万 Star，目前已达 **137K+** ⭐。核心亮点：**四种运行模式 + Cordis 插件内核 + Everything-is-a-plugin 架构**。

---

## 21.1 项目定位与里程碑

### 为什么 dsh 值得关注？

```
┌─────────────────────────────────────────────────────────────┐
│  🚀 发布即爆火：30 分钟破 1 万 Star，1 小时破 3 万           │
│  🏆 唯一官方 SWE-bench 开源实现：覆盖 100% 真实开发场景      │
│  🔌 Cordis 插件内核：500+ 插件已就绪，热插拔可扩展          │
│  💰 MIT 开源：零成本、零限制、可商用                         │
│  🌐 中文友好：DeepSeek 团队维护，文档原生中文支持            │
└─────────────────────────────────────────────────────────────┘
```

### 四种运行模式

| 模式 | 全称 | 用途 | 典型场景 |
|------|------|------|----------|
| **Standard** | 完整工具链模式 | 端到端 Agent 开发 | 日常开发、测试 |
| **PTC** | Programmatic/Test Case 模式 | 批量/程序化执行 | 压力测试、CI/CD |
| **Minimal** | 最小化模式 | 纯 SWE-bench 评测 | 性能基准测试 |
| **Creative** | 创意插件模式 | 自定义扩展 | 实验性研究 |

> 💡 **快速选择建议**：
> - 想体验完整能力 → **Standard**
> - 想集成到 CI/CD → **PTC**
> - 想做 SWE-bench 评测 → **Minimal**
> - 想开发自定义插件 → **Creative**

---

## 21.2 快速安装

### 环境要求

```bash
# Python 3.10+ 推荐
python --version  # >= 3.10

# Node.js 18+（部分插件依赖）
node --version    # >= 18
```

### 安装命令

```bash
# 方式一：pip 安装（推荐）
pip install deepseek-harness

# 方式二：源码安装
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pip install -e .

# 验证安装
dsh --version
```

### 配置 API Key

```bash
# 创建配置文件
mkdir -p ~/.dsh
cat > ~/.dsh/config.toml << 'EOF'
[provider]
api_key = "sk-..."
base_url = "https://api.deepseek.com"
model = "deepseek-chat"  # 或 deepseek-reasoner
EOF

# 或使用环境变量
export DSH_API_KEY="sk-..."
export DSH_MODEL="deepseek-chat"
```

---

## 21.3 Standard 模式：完整工具链

### 基本使用

```bash
# 交互式会话
dsh standard

# 单轮对话
dsh standard --prompt "帮我写一个 FastAPI 项目"

# 带文件输入
dsh standard --input tasks/example.json
```

### 代码示例

```python
# standard_mode.py
from dsh import DeepSeekHarness
from dsh.modes import StandardMode

async def main():
    # 初始化 Harness
    harness = DeepSeekHarness(
        model="deepseek-chat",
        api_key="sk-..."
    )
    
    # 启动 Standard 模式
    mode = StandardMode(harness)
    
    # 执行任务
    result = await mode.run(
        prompt="创建一个 Python 爬虫，抓取 GitHub Trending 并保存为 CSV",
        max_steps=50,
        enable_tools=["code_interpreter", "bash", "web_search"]
    )
    
    print(f"最终输出：{result.final_output}")
    print(f"执行步骤：{result.total_steps}")
    print(f"Token 消耗：{result.total_tokens}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 输出格式

```json
{
  "final_output": "✅ 爬虫已完成，保存到 github_trending.csv",
  "total_steps": 12,
  "total_tokens": 45000,
  "tools_used": [
    {"name": "bash", "calls": 5},
    {"name": "code_interpreter", "calls": 4},
    {"name": "web_search", "calls": 3}
  ],
  "execution_log": [...]
}
```

---

## 21.4 PTC 模式：程序化批量执行

### 适用场景

- 批量处理多个任务
- CI/CD 流水线集成
- 自动化测试

### 批量任务配置

```json
// tasks/batch_jobs.json
{
  "tasks": [
    {
      "id": "task_001",
      "prompt": "写一个 Python 函数计算斐波那契数列",
      "timeout": 120
    },
    {
      "id": "task_002",
      "prompt": "创建一个 Flask 路由处理用户登录",
      "timeout": 180
    },
    {
      "id": "task_003",
      "prompt": "写一个单元测试覆盖上面的登录逻辑",
      "timeout": 120
    }
  ]
}
```

### 代码示例

```python
# ptc_batch.py
from dsh import DeepSeekHarness
from dsh.modes import PTCMode
import asyncio

async def main():
    harness = DeepSeekHarness(model="deepseek-chat")
    mode = PTCMode(harness)
    
    # 加载批量任务
    tasks = await mode.load_tasks("tasks/batch_jobs.json")
    
    # 执行所有任务
    results = await mode.run_batch(tasks)
    
    # 生成报告
    for result in results:
        print(f"[{result.id}] 状态：{result.status}")
        print(f"输出：{result.output[:200]}...")
        print("---")
    
    # 保存汇总报告
    await mode.save_report(results, "output/batch_report.json")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 21.5 Minimal 模式：SWE-bench 评测

### 什么是 SWE-bench？

SWE-bench 是评估 AI Agent 在真实软件开发任务中能力的基准测试集，包含：
- **1,000+** 真实 GitHub issue
- **9 个流行 Python 项目**（Django、Flask、Scikit-learn 等）
- **完整测试套件**用于自动评分

### 运行评测

```bash
# 查看支持的 benchmark
dsh minimal list-benchmarks

# 运行单个 benchmark
dsh minimal run --benchmark swebench/hard

# 批量运行
dsh minimal run --benchmarks swebench/hard,swebench/verified

# 带模型配置
dsh minimal run --model deepseek-reasoner --max-steps 100
```

### 评测结果分析

```python
# minimal_eval.py
from dsh import DeepSeekHarness
from dsh.modes import MinimalMode

async def main():
    harness = DeepSeekHarness(model="deepseek-reasoner")
    mode = MinimalMode(harness)
    
    # 运行 SWE-bench 评测
    result = await mode.run_swebench(
        dataset="swebench/hard",
        max_instances=10,  # 先测试 10 个案例
        timeout=300  # 每个案例 5 分钟
    )
    
    # 分析结果
    print(f"解决率：{result.resolution_rate:.2%}")
    print(f"修复率：{result.fix_rate:.2%}")
    print(f"平均步骤：{result.avg_steps:.1f}")
    
    # 导出详细结果
    result.export_csv("output/swebench_results.csv")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 21.6 Creative 模式：插件开发

### 插件架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                    Creative Mode                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Code Gen   │  │  Web Search │  │  Custom     │         │
│  │  Plugin     │  │  Plugin     │  │  Plugin     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                    ↓                                        │
│           ┌─────────────────┐                               │
│           │  Cordis Kernel  │ ← 插件调度引擎                │
│           └─────────────────┘                               │
│                    ↓                                        │
│           ┌─────────────────┐                               │
│           │  DeepSeek Model │                               │
│           └─────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### 开发自定义插件

```python
# plugins/my_search_plugin.py
from dsh.plugins import BasePlugin
from typing import Dict, Any

class MySearchPlugin(BasePlugin):
    """自定义搜索插件示例"""
    
    name = "my_search"
    description = "使用我的 API 进行搜索"
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """执行搜索逻辑"""
        # 调用你的搜索 API
        results = await self.fetch_from_api(query)
        
        return {
            "status": "success",
            "data": results,
            "count": len(results)
        }
    
    async def fetch_from_api(self, query: str):
        # 实现你的搜索逻辑
        pass

# 注册插件
if __name__ == "__main__":
    from dsh import DeepSeekHarness
    harness = DeepSeekHarness()
    harness.register_plugin(MySearchPlugin)
```

### 热插拔使用

```python
# creative_hotplug.py
from dsh import DeepSeekHarness
from dsh.modes import CreativeMode
from my_plugins import MySearchPlugin, MyCodeGenerator

async def main():
    harness = DeepSeekHarness(model="deepseek-chat")
    
    # 注册多个插件
    harness.register_plugin(MySearchPlugin)
    harness.register_plugin(MyCodeGenerator)
    
    # 启动 Creative 模式
    mode = CreativeMode(harness)
    
    # 动态切换插件
    result = await mode.execute(
        prompt="搜索最新的 AI 新闻并生成报告",
        plugins=["my_search", "my_code_generator"]
    )
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 21.7 插件市场

### 官方插件库

```bash
# 浏览可用插件
dsh plugin search --keyword "search"

# 安装插件
dsh plugin install deepseek/plugin-web-search
dsh plugin install deepseek/plugin-code-interpreter
dsh plugin install deepseek/plugin-file-manager

# 列出已安装插件
dsh plugin list

# 更新所有插件
dsh plugin update --all
```

### 热门插件推荐

| 插件名 | 功能 | 来源 |
|--------|------|------|
| `plugin-web-search` | 网页搜索 | DeepSeek 官方 |
| `plugin-code-interpreter` | 代码执行沙箱 | DeepSeek 官方 |
| `plugin-file-manager` | 文件管理 | DeepSeek 官方 |
| `plugin-docker` | Docker 容器操作 | 社区贡献 |
| `plugin-git` | Git 操作 | 社区贡献 |

### 使用插件示例

```python
# with_plugins.py
from dsh import DeepSeekHarness
from dsh.modes import StandardMode

async def main():
    harness = DeepSeekHarness(model="deepseek-chat")
    
    # 加载预装插件
    harness.load_plugins([
        "plugin-web-search",
        "plugin-code-interpreter", 
        "plugin-git"
    ])
    
    mode = StandardMode(harness)
    
    result = await mode.run(
        prompt="搜索 Python Asyncio 最佳实践，并在当前目录初始化 Git 仓库",
        max_steps=30
    )
    
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 21.8 实战：构建完整项目

### 场景：自动化 Bug 修复工作流

```python
# swebench_auto_fix.py
"""
自动化 Bug 修复工作流：
1. 从 GitHub Issue 获取问题描述
2. 使用 dsh 分析并修复代码
3. 运行测试验证
4. 提交 Pull Request
"""

from dsh import DeepSeekHarness
from dsh.modes import PTCMode
import asyncio
import github  # PyGithub

async def auto_fix_issue(repo_name: str, issue_number: int) -> dict:
    harness = DeepSeekHarness(model="deepseek-reasoner")
    mode = PTCMode(harness)
    
    # 1. 获取 Issue 详情
    gh = github.Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(repo_name)
    issue = repo.get_issue(issue_number)
    
    # 2. 构建 Prompt
    prompt = f"""
    问题描述：{issue.title}
    详细描述：{issue.body}
    
    请在对应仓库中修复此 bug，并确保所有测试通过。
    """
    
    # 3. 执行修复
    result = await mode.run(
        prompt=prompt,
        enable_tools=["code_interpreter", "bash", "git"],
        max_steps=100
    )
    
    # 4. 提交 PR
    if result.status == "success":
        pr = repo.create_pull(
            title=f"Fix #{issue_number}: {issue.title}",
            body=f"自动修复 Issue #{issue_number}",
            head="auto-fix-branch",
            base="main"
        )
        return {
            "issue": issue_number,
            "pr": pr.number,
            "steps": result.total_steps,
            "tokens": result.total_tokens
        }
    
    return {"issue": issue_number, "status": result.status}

if __name__ == "__main__":
    # 使用示例
    result = asyncio.run(auto_fix_issue("django/django", 12345))
    print(f"PR #{result['pr']} 已创建，使用了 {result['steps']} 步")
```

---

## 21.9 性能对比

### dsh vs Claude Code vs Codex CLI

| 指标 | dsh Standard | Claude Code | Codex CLI |
|------|--------------|-------------|-----------|
| **安装复杂度** | ⭐ 低 | ⭐⭐ 中 | ⭐ 低 |
| **批处理支持** | ✅ PTC 模式 | ❌ 需脚本 | ❌ |
| **SWE-bench 支持** | ✅ 官方 | ⚠️ 需适配 | ❌ |
| **插件系统** | ✅ 500+ | ⚠️ 有限 | ✅ 少量 |
| **中文文档** | ✅ 原生 | ⚠️ 部分 | ❌ |
| **学习曲线** | 低 | 中 | 低 |
| **推荐指数** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

> 💡 **结论**：如果你需要批量处理、SWE-bench 评测或中文支持，**dsh 是目前最优选择**。

---

## 21.10 常见问题排查

### Q1：安装失败 `ModuleNotFoundError`

**解决**：
```bash
# 检查 Python 版本
python --version  # 需要 >= 3.10

# 使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install deepseek-harness
```

### Q2：API Key 认证失败

**解决**：
```bash
# 检查配置
cat ~/.dsh/config.toml

# 重置配置
dsh config reset
dsh config set api_key "sk-..."
```

### Q3：插件加载失败

**解决**：
```bash
# 查看插件日志
dsh plugin logs

# 重新安装插件
dsh plugin install deepseek/plugin-web-search --force
```

### Q4：SWE-bench 评测超时

**解决**：
```bash
# 增加超时时间
dsh minimal run --timeout 600 --benchmark swebench/hard

# 或降低难度
dsh minimal run --benchmark swebench/easy
```

---

## 21.11 学习资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.deepseek.ai/harness |
| GitHub 仓库 | https://github.com/deepseek-ai/deepseek-harness |
| 插件市场 | https://plugins.deepseek.ai |
| SWE-bench 评测 | https://www.swebench.com |
| 中文教程 | https://deepseek.ai/zh/harness-tutorial |

---

## 21.12 总结

DeepSeek Harness 是 2026 年最值得关注的开源 Agent 框架之一：

- ✅ **四种模式**覆盖从开发到评测的全场景
- ✅ **Cordis 插件内核**支持 500+ 插件热插拔
- ✅ **原生 SWE-bench** 支持，唯一官方实现
- ✅ **中文友好**，文档和社区支持完善
- ✅ **MIT 开源**，完全免费商用

无论你是个人开发者还是企业团队，dsh 都能提供强大的 Agent 开发能力。

---

> **恭喜！** 你已经完成了全部 21 章的学习。现在你可以：
> - 🚀 使用 **dsh** 进行批量任务自动化
> - 🧪 在 **SWE-bench** 上评测你的 Agent 性能
> - 🔌 开发自定义 **插件** 扩展能力
