from typing import Annotated, Literal
from langchain_core.tools import tool


Operator = Literal["+", "-", "*", "/"]

@tool
def calculator(operator: Annotated[Operator, "operator"], a:float, b:float) -> int:
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

  discord_messaging = DiscordBot(bot_token)
