from autogen import AssistantAgent, UserProxyAgent
from agents import planner, assistant

result = assistant.initiate_chat(planner, message="when does Arcane's next season come out? send me the date on discord.", max_turns=2)
