"""
Mastra TypeScript Agent 示例
"""
const { Agent, Memory, PostgresStore } = require('@mastra/core');
const { OpenAI } = require('@mastra/openai');

// 初始化 Mastra
const mastra = new Mastra({
  workflows: {},
  agents: {
    researcher: new Agent({
      name: 'Researcher',
      instructions: `You are a research assistant. 
      Search for information and provide comprehensive answers.`,
      model: 'openai:gpt-4o-mini',
    }),
  },
});

// 使用示例
async function main() {
  const agent = mastra.getAgent('researcher');
  
  const result = await agent.generate('什么是 LangGraph？');
  console.log(result.text);
}

main().catch(console.error);
