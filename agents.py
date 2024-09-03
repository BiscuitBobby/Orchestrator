from autogen import ConversableAgent, UserProxyAgent, AssistantAgent
from autogen import register_function
import json

from configs.gemini import gemini
from configs.phi3 import phi3
from models.gemini_langchain import CustomModelClient

phi3 = ConversableAgent(
    "Phi-3",
    llm_config=phi3,
    system_message="Your name is Phi and you are a very helpful assistant with multiple tools",
)

gemini = ConversableAgent(
    "assistant", llm_config=gemini,
    max_consecutive_auto_reply=3,
    system_message="You're Gemini and you are a very helpful assistant with multiple tools",
)

# custom langchain model with tools
config_list = [{
    "model": "gemini_langchain",
    "model_client_cls": "CustomModelClient",
    "n": 1,
    "temp": 0.3,
    "params": {
        "max_length": 1000,
    }
}]

assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
assistant.register_model_client(model_client_cls=CustomModelClient)

