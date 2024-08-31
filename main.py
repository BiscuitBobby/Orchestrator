from autogen import AssistantAgent, UserProxyAgent
from agents import phi3

user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

user_proxy.initiate_chat(
    phi3,
    message="What is (44232 + 13312 / (232 - 32)) * 5?",
)
