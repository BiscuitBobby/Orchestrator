from types import SimpleNamespace
import os
from Secrets.keys import google_api
from langchain_core.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from functions.discord_module.discord import discord_messaging
from configs.prompts import react_mem, react
from functions.tools import calculator

tools = [discord_messaging]

# -------------------------------------------------------------------------------------------------------------------- #
class CustomModelClient:
    def __init__(self, config, **kwargs):
        print(f"CustomModelClient config: {config}")
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = google_api

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )
        self.llm.temperature = config["temp"]

        # Define the tools to be used by the agent
        self.tools = tools


    def agent_init(self, memory=[]):
        if memory:
            print(f"memory initialized: {memory}")
            self.prompt = PromptTemplate.from_template(react_mem(memory))
        else:
            print("Fresh")
            self.prompt = PromptTemplate.from_template(react)
        llm_with_stop = self.llm.bind(stop=["\nObservation"])
        # Partially apply the prompt with the tools description and tool names
        prompt = self.prompt.partial(
            tools=render_text_description(self.tools),
            tool_names=", ".join([t.name for t in self.tools]),
        )

        # Define the template for tool response
        # Define the agent
        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_log_to_messages(x["intermediate_steps"]),
                }
                | prompt
                | llm_with_stop
                | ReActSingleInputOutputParser()
        )

        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True,
                                            return_intermediate_steps=True)

    def create(self, params):
        print(f"params:")
        print(params)
        num_of_responses = params.get("n", 1)
        response = SimpleNamespace()
        print(params["messages"])
        response.choices = []
        response.model = "gemini_langchain"  # should match the OAI_CONFIG_LIST registration

        for _ in range(num_of_responses):
            if len(params["messages"]) > 1:
                prompt = params["messages"][-1]["content"]
                self.agent_init((params["messages"][1::]))
            else:
                self.agent_init()
                prompt = 'Analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.\nWhen you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.\nReply "TERMINATE" in the end when everything is done.'
            print("Lemon")
            outputs = self.agent_executor.invoke({"input": prompt})
            print(outputs)
            text = outputs["output"]
            choice = SimpleNamespace()
            choice.message = SimpleNamespace()
            choice.message.content = text
            choice.message.function_call = None
            response.choices.append(choice)
        return response

    def message_retrieval(self, response):
        choices = response.choices
        return [choice.message.content for choice in choices]

    def cost(self, response) -> float:
        response.cost = 0
        return 0

    @staticmethod
    def get_usage(response):
        return {}
