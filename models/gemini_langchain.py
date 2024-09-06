from pprint import pprint
from types import SimpleNamespace
import os
import re
from typing import List, TypedDict
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
from functions.tools import langchain_tools
from models.configs.prompts import react_mem, react, solve_prompt

tools = langchain_tools
regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"


class ReWOO(TypedDict):
    task: str
    plan_string: str
    steps: List
    results: dict
    result: str


# -------------------------------------------------------------------------------------------------------------------- #
class LangchainModelClient:
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

            if prompt != '':
                outputs = self.agent_executor.invoke({"input": prompt})
            else:
                return "TERMINATE"
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

class LangchainMultistepClient:
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

        self.tools = tools
        self.task = ''
        self.steps_dict = {}

    def agent_init(self, plan, memory=[]):
        if memory:
            print(f"memory initialized: {memory}")
            self.prompt = PromptTemplate.from_template(solve_prompt)
        else:
            print("Fresh")
            self.prompt = PromptTemplate.from_template(react)
        llm_with_stop = self.llm.bind(stop=["\nObservation"])
        # Partially apply the prompt with the tools description and tool names
        prompt = self.prompt.partial(
            tools=render_text_description(self.tools),
            tool_names=", ".join([t.name for t in self.tools]),
            plan=plan,
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
    def extract_plan_details(self, input_string: str) -> ReWOO:
        matches = re.findall(regex_pattern, input_string)

        output: ReWOO = {
            "task": self.task,
            "plan_string": input_string,
            "steps": matches,
            "results": {},
            "result": ""
        }

        return output

    def _get_current_task(self, state: ReWOO):
        if state["results"] is None:
            return 1
        if len(state["results"]) == len(state["steps"]):
            return None
        else:
            return len(state["results"]) + 1

    def tool_execution(self, state: ReWOO):
        _step = self._get_current_task(state)

        for i in range(len(state["steps"])):
            _, step_name, tool_name, tool_input = state["steps"][i]
            self.steps_dict[step_name] = {
                "tool_name": tool_name,
                "tool_input": tool_input,
                "action": _,
                "output": None
            }

        #pprint(self.steps_dict)
        for i in state["steps"]:
            current_plan = ''
            current_task=''
            #pprint(i)

            for j in state["steps"]:
                _, step_name, tool_name, tool_input = j
                step_name = step_name
                tool_name = self.steps_dict[step_name]["tool_name"]
                tool_input = self.steps_dict[step_name]["tool_input"]
                tool_output = self.steps_dict[step_name]["output"]

                # Check if this is the current task
                if j == i:
                    #print(f"Current task: {tool_name}[{tool_input}] {step_name} = {tool_output}")
                    current_plan += f"Current task: {tool_name}[{tool_input}] {step_name} = {tool_output}\n"
                    current_task = step_name  # self.steps_dict[step_name]["action"]

                else:
                    #print(f"{tool_name}[{tool_input}] {step_name} = {tool_output}")
                    current_plan += f"{tool_name}[{tool_input}] {step_name} = {tool_output}\n"

            print(current_plan)
            self.agent_init(current_plan)
            print(f"action to be taken: {self.steps_dict[current_task]["action"]}\n")
            tool = self.steps_dict[current_task]["tool_name"]
            input = self.steps_dict[current_task]["tool_input"]
            action = self.steps_dict[current_task]["action"]
            prompt = f"{tool}[{input}]: {action}"
            self.steps_dict[current_task]["output"] = self.agent_executor.invoke({"input": prompt})

            state["results"][step_name] = (self.steps_dict[current_task]["output"])
            result = self.steps_dict[current_task]["output"]

        state["result"] = result
        return result

    def create(self, params):
        print(f"params:")
        print(params)
        num_of_responses = params.get("n", 1)
        response = SimpleNamespace()
        print(params["messages"])
        response.choices = []
        response.model = "LangchainMultistepClient"  # should match the OAI_CONFIG_LIST registration

        for _ in range(num_of_responses):
            if len(params["messages"]) > 1:
                prompt = params["messages"][-1]["content"]
            else:
                output = 'Analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.\nWhen you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.\nReply "TERMINATE" in the end when everything is done.'

            if prompt != '':
                state = self.extract_plan_details(prompt)
                print(state)
                output = self.tool_execution(state)
            else:
                return "TERMINATE"
            print(output)
            text = output["output"]
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