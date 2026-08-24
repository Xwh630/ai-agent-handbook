# 第 10 章：Mastra TypeScript Agent

> Mastra 是 Y Combinator 支持的 TypeScript 优先 Agent 框架，适合 Node.js 全栈开发者。

---

## 10.1 核心特性

| 特性 | 说明 |
|------|------|
| **TypeScript 原生** | 完整的类型支持 |
| **工作流优先** | 内置工作流引擎 |
| **多 Provider** | 支持 81+ Provider，2400+ 模型 |
| **observability** | 内置可观测性 |

---

## 10.2 环境准备

```bash
npm init -y
npm install @mastra/core @mastra/astra @mastra/rag
```

---

## 10.3 第一个 Mastra Agent

```typescript
// basic-agent.ts
import { Agent } from '@mastra/core/agent';
import { openai } from '@ai-sdk/openai';

const agent = new Agent({
  name: 'Research Assistant',
  instructions: '你是一个研究助手，帮助用户查找和总结信息。',
  model: openai('gpt-4o-mini')
});

const result = await agent.prompt('总结一下 AI Agent 的发展趋势');
console.log(result.text);
```

---

## 10.4 工具定义

```typescript
// tools.ts
import { createTool } from '@mastra/core/tools';

const searchTool = createTool({
  id: 'web-search',
  description: '搜索互联网信息',
  inputSchema: z.object({
    query: z.string().describe('搜索关键词'),
    limit: z.number().default(5)
  }),
  outputSchema: z.array(z.object({
    title: z.string(),
    url: z.string(),
    snippet: z.string()
  })),
  execute: async ({ context }) => {
    // 实现搜索逻辑
    return searchWeb(context.query, context.limit);
  }
});
```

---

## 10.5 工作流编排

```typescript
// workflow.ts
import { Workflow } from '@mastra/core/workflow';

const workflow = new Workflow({
  name: 'research-workflow',
  trigger: z.object({
    topic: z.string()
  })
});

// 添加步骤
workflow
  .step({
    id: 'research',
    execute: async (context) => {
      return { research: await doResearch(context.trigger.topic) };
    }
  })
  .step({
    id: 'synthesize',
    execute: async (context) => {
      return { summary: await synthesize(context.research) };
    }
  })
  .commit();
```

---

## 10.6 本章小结

✅ 了解了 Mastra 的核心架构

✅ 学会了工具定义和工作流编排

✅ 掌握了 TypeScript 类型安全的使用方法

---

## 下一章

[→ 第 11 章：MCP 协议完全指南](./11-mcp.md)
