from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
from functions.tools import langchain_tools_description
from models.configs.gemini import gemini
from models.configs.phi3 import phi3
from models.gemini_langchain import LangchainModelClient, LangchainMultistepClient
# from models.llamma_langchain import LangchainMultistepClient

planner = AssistantAgent(
    "Planner",
    llm_config=gemini,
    system_message=f"""If the following task needs multiple steps, make plans that can solve the problem step by step. For each plan, indicate \
    which external tool together with tool input to retrieve evidence. You can store the evidence into a \
    variable #E that can be called by later tools. (Plan, #E1, Plan, #E2, Plan, ...)

    YOU ONLY HAVE ACCESS TO THE FOLLOWING TOOLS:
    {langchain_tools_description}
    
    For example,
    Task: Thomas, Toby, and Rebecca worked a total of 157 hours in one week. Thomas worked x
    hours. Toby worked 10 hours less than twice what Thomas worked, and Rebecca worked 8 hours
    less than Toby. How many hours did Rebecca work? Send me the final answer on discord.
    Plan: Given Thomas worked x hours, translate the problem into algebraic expressions and solve
    with Wolfram Alpha. #E1 = WolframAlpha[Solve x + (2x − 10) + ((2x − 10) − 8) = 157]
    Plan: Calculate the number of hours Rebecca worked. #E2 = Calculator[(2 ∗ #E1 − 10) − 8]
    Plan: Send the final answer through discord. #E3 = DiscordMessage[Rebecca worked for #E3 hours]


    Begin! 
    Try not to create unnecessary steps. Each Plan should be followed by only one #En ToolName[<ToolInput>].
    you do not have text extraction or text formatting tools

    Task: {{task}}""",
)

# custom langchain model with tools
'''config_list = [{
    "model": "gemini_langchain",
    "model_client_cls": "LangchainModelClient",
    "n": 1,  # useless rn
    "temp": 0.3,
    "params": {
        "max_length": 1000,  # useless rn
    }
}]'''

config_list = [{
    "model": "gemini_langchain",
    "model_client_cls": "LangchainMultistepClient",
    "n": 1,  # useless rn
    "temp": 0.3,
    "params": {
        "max_length": 1000,  # useless rn
    }
}]
assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
assistant.register_model_client(model_client_cls=LangchainMultistepClient)

#result = UserProxyAgent.initiate_chat(assistant, message="hi.", max_turns=2)
