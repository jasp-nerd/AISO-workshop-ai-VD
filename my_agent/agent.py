"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent

from my_agent.tools import calculator

root_agent = llm_agent.Agent(
    model="gemini-2.5-flash-lite",
    name="agent",
    description="A helpful assistant.",
    instruction=(
        "You are a helpful assistant that answers questions directly and concisely. "
        "Always read the question carefully and answer exactly what is asked. "
        "Use the calculator tool for all arithmetic and numeric calculations — "
        "never compute numbers yourself. "
        "Do NOT use the calculator for reasoning, language, or logic puzzles."
    ),
    tools=[calculator],
    sub_agents=[],
)
