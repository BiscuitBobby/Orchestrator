from typing import Annotated, Literal
from langchain_core.tools import tool
from functions.discord_module.discord import DiscordMessage
from functions.web.search import CustomSearch

Operator = Literal["+", "-", "*", "/"]

@tool
def Calculator(operator: Annotated[Operator, "operator"], a:float, b:float) -> int:
  """A simple mathematics calculator that can add, subtract, multiply, and divide two numbers."""
  print(f"calculator({a}, {b}, {operator}")
  if operator == "+":
    return a + b
  elif operator == "-":
    return a - b
  elif operator == "*":
    return a * b
  elif operator == "/":
    return int(a / b)
  else:
    raise ValueError("Invalid operator")

langchain_tools = [CustomSearch,DiscordMessage]
langchain_tools_description = '\n'.join([f"[{tool.name}]: {tool.description}" for tool in langchain_tools])
print(langchain_tools)
print(langchain_tools_description)
