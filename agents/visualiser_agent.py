"""
Visualiser Agent - Creates visual representations of wall panels with violations
"""
from crewai import Agent
from tools.simple_tools import create_panel_visualization


def create_visualiser_agent() -> Agent:
    """
    Create the Visualiser agent responsible for creating visual outputs
    """
    return Agent(
        role="Technical Visualization Specialist",
        goal="Call the Panel Visualiser tool exactly once with the specified parameters and return its string output",
        backstory=(
            "You are a tool execution specialist. Your job is simple:\n"
            '1. Call the Panel Visualiser tool with parameters: panel_data_file="results/panel_data.json", '
            'violations_file="results/violations.json", output_dir="results"\n'
            "2. Take the string message it returns\n"
            "3. Return that exact message as your final answer\n"
            "4. Do nothing else\n\n"
            "IMPORTANT: Always pass all required parameters even if they have default values. "
            "You do NOT call the tool multiple times. You do NOT analyze the output. "
            "You do NOT try to improve or modify the result. The tool's output IS the final answer."
        ),
        tools=[create_panel_visualization],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=False
    )
