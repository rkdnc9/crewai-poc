"""
Parser Agent - Extracts wall panel data from IFC files
"""
from crewai import Agent
from tools.simple_tools import parse_ifc_file


def create_parser_agent() -> Agent:
    """
    Create the Parser agent responsible for extracting wall panel data from IFC files
    """
    return Agent(
        role="IFC Parser Specialist",
        goal="Call the IFC Parser tool exactly once and return its string output",
        backstory=(
            "You are a tool execution specialist. Your job is simple:\n"
            "1. Call the IFC Parser tool with the provided file path\n"
            "2. Take the string message it returns\n"
            "3. Return that exact message as your final answer\n"
            "4. Do nothing else\n\n"
            "You do NOT call the tool multiple times. You do NOT analyze the output. "
            "You do NOT try to improve or modify the result. The tool's output IS the final answer."
        ),
        tools=[parse_ifc_file],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=False
    )
