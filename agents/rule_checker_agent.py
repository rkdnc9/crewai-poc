"""
Rule Checker Agent - Validates wall panels against building codes
"""
from crewai import Agent
from tools.simple_tools import check_building_codes


def create_rule_checker_agent() -> Agent:
    """
    Create the Rule Checker agent responsible for validating panels against building codes
    """
    return Agent(
        role="Building Code Compliance Expert",
        goal="Call the Rule Checker tool exactly once with the specified parameters and return its string output",
        backstory=(
            "You are a tool execution specialist. Your job is simple:\n"
            '1. Call the Rule Checker tool with parameter panel_data_file="results/panel_data.json"\n'
            "2. Take the string message it returns\n"
            "3. Return that exact message as your final answer\n"
            "4. Do nothing else\n\n"
            "IMPORTANT: Always pass the panel_data_file parameter even if it has a default value. "
            "You do NOT call the tool multiple times. You do NOT analyze the output. "
            "You do NOT try to improve or modify the result. The tool's output IS the final answer."
        ),
        tools=[check_building_codes],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=False
    )
