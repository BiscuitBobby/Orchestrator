from autogen import AssistantAgent, UserProxyAgent
from agents import phi3, assistant

result = assistant.initiate_chat(phi3, message="look up when the next season of Arcane comes out and send it to me through discord.", max_turns=2)