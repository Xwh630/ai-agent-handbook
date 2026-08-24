# 第 18 章：选型决策树与最佳实践

> 帮助你根据具体需求选择最合适的框架和工具。

---

## 18.1 框架选型决策树

```
                    你要构建什么？
                    /        \
               快速原型       生产系统
                 |             |
            Dify/Coze    需要代码控制？
                 |         /      \
              低代码     是        否
                            |        |
                     复杂工作流   简单脚本
                    /      \         |
                  是       否    LangChain
                 /          \
           复杂流程图    简单顺序
           /      \        |
         LangGraph  CrewAI  |
          (可控)   (快速)   |
                          本地模型？
                           |
                          是       否
                           |        |
                        Ollama   云端 API
                        (隐私)    |
                                  |
                            OpenAI/Claude
```

---

## 18.2 框架对比总表

| 框架 | Stars | 学习曲线 | 灵活性 | 生产成熟度 | 适合场景 |
|------|-------|----------|--------|------------|----------|
| **LangGraph** | 33.9K | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 复杂工作流、生产级 |
| **CrewAI** | 44K | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 多角色协作、快速原型 |
| **AutoGen** | 54K | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 多Agent对话、研究 |
| **Dify** | 130K | ⭐ | ⭐⭐ | ⭐⭐⭐ | 低代码、产品验证 |
| **OpenAI SDK** | 26.9K | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 快速开发、轻量级 |
| **Mastra** | 15K | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | TypeScript 项目 |

---

## 18.3 场景化推荐

### 场景 1：个人助手

```
推荐方案：
├── 前端：Dify（快速搭建）或 Claude Code（编程辅助）
├── 后端：LangGraph（复杂逻辑）
└── 模型：Ollama 本地运行（隐私优先）
```

### 场景 2：企业知识库问答

```
推荐方案：
├── 平台：Dify（内置 RAG）
├── 向量库：Chroma / Qdrant
├── 检索：LlamaIndex
└── 部署：自托管
```

### 场景 3：多团队协作自动化

```
推荐方案：
├── 编排：CrewAI（角色化设计）
├── 工具：MCP 协议标准化
├── 监控：LangSmith
└── 部署：Docker + K8s
```

### 场景 4：研究分析报告生成

```
推荐方案：
├── 搜索：Serper API
├── 分析：CrewAI 多Agent
├── 写作：LangGraph 工作流
└── 审核：Human-in-the-loop
```

---

## 18.4 最佳实践清单

### 18.4.1 设计原则

```
✅ 单一职责：每个 Agent 只做一件事
✅ 可测试性：单元化和集成测试
✅ 可观测性：完善的日志和追踪
✅ 成本控制：合理选择模型和优化 Token
✅ 错误处理：完善的降级和重试机制
✅ 安全性：工具权限控制和输入验证
```

### 18.4.2 常见陷阱

```
❌ 过度设计：用多 Agent 解决简单问题
❌ Token 浪费：不必要地保留长对话历史
❌ 工具滥用：每个操作都调用工具
❌ 缺乏监控：出问题后无法定位
❌ 硬编码：模型和 API Key 写死在代码里
❌ 忽略成本：没有设置预算上限
```

---

## 18.5 性能优化建议

### 18.5.1 响应时间优化

```python
# 并行工具调用
async def parallel_tools():
    results = await asyncio.gather(
        call_tool("search", query),
        call_tool("database", query),
        call_tool("api", query)
    )
    return results

# 流式输出
async def streaming_response():
    async for chunk in agent.stream(query):
        yield chunk
```

### 18.5.2 成本优化

```python
# 模型路由
def smart_model_selection(task_type: str, complexity: float) -> str:
    if complexity < 0.3:
        return "gpt-4o-mini"
    elif "code" in task_type:
        return "claude-sonnet"
    else:
        return "gpt-4o"
```

---

## 18.6 本章小结

✅ 掌握了框架选型的方法论

✅ 学会了不同场景的最佳实践

✅ 了解了性能优化和成本控制技巧

---

## 附录

[→ 附录 A：框架对比总表](../docs/framework-comparison.md)
[→ 附录 B：常见错误排查手册](../appendix/error-troubleshooting.md)
[→ 附录 C：学习资源与社区](../appendix/resources.md)
