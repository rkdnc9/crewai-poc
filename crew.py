"""
CrewAI Crew Configuration - Orchestrates the wall panel QC workflow
"""
import os
from dotenv import load_dotenv
from crewai import Crew, Task, Process
from agents.parser_agent import create_parser_agent
from agents.rule_checker_agent import create_rule_checker_agent
from agents.visualiser_agent import create_visualiser_agent
from agents.reporter_agent import create_reporter_agent

# Load environment variables from .env file
load_dotenv()


class WallPanelQCCrew:
    """
    Wall Panel Quality Control Crew
    Orchestrates agents to perform automated design review of prefab wall panels
    """

    def __init__(self, ifc_file_path: str, output_dir: str = "results"):
        """
        Initialize the QC crew

        Args:
            ifc_file_path: Path to the IFC file to analyze
            output_dir: Directory for output files
        """
        self.ifc_file_path = ifc_file_path
        self.output_dir = output_dir

        # Create agents
        self.parser_agent = create_parser_agent()
        self.rule_checker_agent = create_rule_checker_agent()
        self.visualiser_agent = create_visualiser_agent()
        self.reporter_agent = create_reporter_agent()

    def create_tasks(self):
        """Define the sequential tasks for the crew"""

        # Task 1: Parse IFC file
        parse_task = Task(
            description=(
                f"Execute the IFC Parser tool ONCE with ifc_file_path='{self.ifc_file_path}'. "
                f"The tool returns a string message. That message IS your final answer. "
                f"Do not call the tool again. Do not analyze further. Just return the tool's message."
            ),
            expected_output=(
                "The exact text message returned by the IFC Parser tool"
            ),
            agent=self.parser_agent
        )

        # Task 2: Check building code compliance
        validate_task = Task(
            description=(
                'Execute the Rule Checker tool ONCE with these exact parameters: panel_data_file="results/panel_data.json". '
                "The tool returns a string message. That message IS your final answer. "
                "Do not call the tool again. Do not analyze further. Just return the tool's message."
            ),
            expected_output=(
                "The exact text message returned by the Rule Checker tool"
            ),
            agent=self.rule_checker_agent,
            context=[parse_task]
        )

        # Task 3: Create visual representations
        visualise_task = Task(
            description=(
                f'Execute the Panel Visualiser tool ONCE with these exact parameters: '
                f'panel_data_file="results/panel_data.json", violations_file="results/violations.json", output_dir="results". '
                f"The tool returns a string message. That message IS your final answer. "
                f"Do not call the tool again. Do not analyze further. Just return the tool's message."
            ),
            expected_output=(
                f"The exact text message returned by the Panel Visualiser tool"
            ),
            agent=self.visualiser_agent,
            context=[parse_task, validate_task]
        )

        # Task 4: Generate report
        report_task = Task(
            description=(
                f'Execute the Report Generator tool ONCE with these exact parameters: '
                f'panel_data_file="results/panel_data.json", violations_file="results/violations.json", '
                f'output_dir="results", report_name="panel_qc_report.html". '
                f"The tool returns a string message. That message IS your final answer. "
                f"Do not call the tool again. Do not analyze further. Just return the tool's message."
            ),
            expected_output=(
                f"The exact text message returned by the Report Generator tool"
            ),
            agent=self.reporter_agent,
            context=[parse_task, validate_task]
        )

        return [parse_task, validate_task, visualise_task, report_task]

    def run(self):
        """Execute the crew workflow"""

        # Create tasks
        tasks = self.create_tasks()

        # Create crew with sequential process
        crew = Crew(
            agents=[
                self.parser_agent,
                self.rule_checker_agent,
                self.visualiser_agent,
                self.reporter_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        # Execute the crew
        print("\n" + "="*70)
        print("Starting CrewAI Wall Panel Quality Control")
        print("="*70 + "\n")

        result = crew.kickoff()

        print("\n" + "="*70)
        print("✅ Quality Control Complete")
        print("="*70 + "\n")

        return result


def create_qc_crew(ifc_file_path: str, output_dir: str = "results") -> WallPanelQCCrew:
    """
    Factory function to create a Wall Panel QC Crew

    Args:
        ifc_file_path: Path to IFC file
        output_dir: Output directory for results

    Returns:
        Configured WallPanelQCCrew instance
    """
    return WallPanelQCCrew(ifc_file_path, output_dir)
