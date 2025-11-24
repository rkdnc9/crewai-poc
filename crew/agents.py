"""
CrewAI agents for wall panel quality control.
Includes deterministic checkers and LLM-based analyzers.
"""

from crewai import Agent


def create_parser_agent() -> Agent:
    """Parse IFC file into structured data"""
    return Agent(
        role="IFC Parser",
        goal="Extract wall panel data from IFC files into structured format",
        backstory=(
            "You are an expert at parsing IFC (Industry Foundation Classes) files "
            "and extracting structural information about prefab wall panels. You identify "
            "studs, openings, ducts, and other components with precision."
        ),
        verbose=False,
        allow_delegation=False
    )


def create_deterministic_checker_agent() -> Agent:
    """Run baseline rule checks"""
    return Agent(
        role="QC Inspector",
        goal="Check panel against deterministic building code rules",
        backstory=(
            "You are a quality control inspector with expertise in explicit building code "
            "requirements. You systematically verify that panels meet specific, measurable "
            "criteria like stud spacing, window support, and MEP clearances."
        ),
        verbose=False,
        allow_delegation=False
    )


def create_llm_analyzer_agent() -> Agent:
    """Run contextual analysis"""
    return Agent(
        role="Senior Building Code Consultant",
        goal="Identify context-dependent violations and design issues",
        backstory=(
            "You are a senior building code consultant with 20+ years in prefab construction. "
            "You understand seismic requirements, design intent, measurement tolerances, "
            "and context-dependent code rules. You catch subtle issues that automated "
            "rules miss while avoiding false positives."
        ),
        verbose=False,
        allow_delegation=False
    )


def create_report_agent() -> Agent:
    """Synthesize findings"""
    return Agent(
        role="Report Generator",
        goal="Create comprehensive and clear QC reports",
        backstory=(
            "You are an experienced technical writer skilled at synthesizing complex "
            "quality control findings into clear, actionable reports that are easy for "
            "engineers and project managers to understand."
        ),
        verbose=False,
        allow_delegation=False
    )


def create_visualizer_agent() -> Agent:
    """Create visual diagrams"""
    return Agent(
        role="Visualization Specialist",
        goal="Create visual diagrams of wall panels highlighting violations and good components",
        backstory=(
            "You are a CAD specialist and visualization expert. You create clear, "
            "color-coded diagrams that make it easy to see which components pass QC (green) "
            "and which have violations (red/yellow). Your visualizations help stakeholders "
            "quickly understand the QC findings at a glance."
        ),
        verbose=False,
        allow_delegation=False
    )


def create_remediation_specialist_agent() -> Agent:
    """Apply remediation fixes to create corrected panel"""
    return Agent(
        role="Remediation Specialist",
        goal="Apply remediation recommendations to generate fixed panel visualizations",
        backstory=(
            "You are a construction planning specialist who translates remediation "
            "recommendations into concrete fixes. You understand how to apply structural "
            "changes like adding jack studs, headers, and bracing to wall panels. You "
            "create visual representations of corrected panels to show stakeholders "
            "what the final result will look like after remediation."
        ),
        verbose=False,
        allow_delegation=False
    )
