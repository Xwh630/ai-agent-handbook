/**
 * Mastra TypeScript Agent 示例
 *
 * 运行前：
 *   npm install @mastra/core @ai-sdk/openai
 *   export OPENAI_API_KEY=your-key
 */
const { Mastra, Agent } = require('@mastra/core');

// 初始化 Mastra
const mastra = new Mastra({
  agents: {
    researcher: new Agent({
      name: 'Researcher',
      instructions: `You are a research assistant.
      Search for information and provide comprehensive answers.`,
      // 模型字符串格式：<provider>/<model>
      model: 'openai/gpt-4o-mini',
    }),
  },
});

// 使用示例
async function main() {
  const agent = mastra.getAgent('researcher');

  // 新版统一使用 generate()（旧版 prompt() 已废弃）
  const result = await agent.generate('什么是 LangGraph？');
  console.log(result.text);
}

main().catch(console.error);
