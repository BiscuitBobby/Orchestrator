from autogen import ConversableAgent, UserProxyAgent
from autogen import register_function
from functions.discord_module.discord import discord_messenger
from models.phi3 import phi3
from models.gemini import gemini
from functions.tools import calculator

phi3 = ConversableAgent(
    "Phi-3",
    llm_config=phi3,
    system_message="Your name is Phi and you are a very helpful assistant with multiple tools",
)

assistant = ConversableAgent(
    "assistant", llm_config=gemini,
    max_consecutive_auto_reply=3,
    system_message="You're Gemini and you are a very helpful assistant with multiple tools",
)

user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

register_function(
    calculator,
    caller=phi3,  # The assistant agent can suggest calls to the calculator.
    executor=user_proxy,  # The user proxy agent can execute the calculator calls.
    name="calculator",  # By default, the function name is used as the tool name.
    description="A simple calculator",  # A description of the tool.
)
chat_result = user_proxy.initiate_chat(phi3, message="send a hi via discord")

#print(chat_result)
