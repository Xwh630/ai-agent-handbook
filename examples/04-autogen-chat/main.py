"""
AutoGen 多智能体对话示例
"""
import os
from dotenv import load_dotenv
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager

load_dotenv()

# 配置 LLM
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# 创建 Agent
assistant = ConversableAgent(
    name="Assistant",
    llm_config={"config_list": config_list},
    system_message="你是一个 helpful assistant，帮助用户完成任务。"
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    llm_config=False,
    code_execution_config={"work_dir": "coding"}
)

# 启动对话
chat_result = user_proxy.initiate_chat(
    assistant,
    message="帮我写一个 Python 函数，计算斐波那契数列前10项"
)

print("\n对话总结:")
print(chat_result.summary)
