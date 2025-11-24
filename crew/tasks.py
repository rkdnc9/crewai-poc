"""
CrewAI tasks for wall panel quality control workflow.
"""

from crewai import Task
from crew.agents import (
    create_parser_agent,
    create_deterministic_checker_agent,
    create_llm_analyzer_agent,
    create_report_agent
)


def create_parse_task(ifc_file_path: str) -> Task:
    """Create task to parse IFC file"""
    agent = create_parser_agent()
    return Task(
        description=f"""Parse the IFC file at {ifc_file_path} and extract:
        - Panel dimensions (width, height, thickness)
        - Stud positions and spacing
        - Door and window openings with their properties
        - MEP ducts and clearances
        - Any metadata about seismic zone or location
        
        Return structured data suitable for rule checking.""",
        expected_output="Structured panel data with all components",
        agent=agent
    )


def create_deterministic_check_task(panel_data: dict, building_codes: dict) -> Task:
    """Create task to run deterministic checks"""
    agent = create_deterministic_checker_agent()
    return Task(
        description=f"""Run deterministic QC checks on the panel data:

Panel: {panel_data}

Using these building codes:
{building_codes}

Check:
1. Stud spacing is within tolerance
2. Windows/doors have required support (jack studs, header)
3. MEP ducts have adequate clearance

Run the deterministic checks and return a detailed JSON report with:
- violations_count: number of violations found
- violations: list of violations with reason, severity, and rule_id
- result_summary: brief summary of findings

Example format:
{{
    "violations_count": 2,
    "violations": [
        {{"reason": "...", "severity": "High", "rule_id": "RULE_001"}},
        {{"reason": "...", "severity": "Critical", "rule_id": "RULE_002"}}
    ],
    "result_summary": "Found 2 deterministic violations"
}}""",
        expected_output="JSON report with deterministic violations, severity levels, and rule IDs",
        agent=agent
    )


def create_llm_analysis_task(panel_data: dict, det_result: dict, exceptions: dict) -> Task:
    """Create task for LLM contextual analysis"""
    from pathlib import Path
    
    # Load contextual rules
    rules_path = Path(__file__).parent.parent / "config" / "contextual_rules.md"
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            contextual_rules = f.read()
    except:
        contextual_rules = "# No contextual rules loaded"
    
    agent = create_llm_analyzer_agent()
    return Task(
        description=f"""Perform expert analysis on this panel considering context:

Panel Data: {panel_data}
Previous Deterministic Results: {det_result}
Context Exceptions: {exceptions}

CONTEXTUAL INSPECTION RULES (Natural Language Guidelines):
{contextual_rules}

Look for:
- Edge cases and design concerns
- Apply the contextual inspection rules from the playbook above
- Seismic zone considerations
- Corner placements that may be problematic
- Design combinations that raise concerns
- Borderline measurements that are technically compliant but concerning

Analyze the panel deeply and return a JSON report with additional violations from expert judgment.
For EACH violation, provide a detailed remediation plan with actionable steps.

Example format:
{{
    "violations_count": 2,
    "violations": [
        {{
            "reason": "Corner window in high seismic zone requires extra bracing",
            "severity": "High",
            "remediation": {{
                "steps": ["1. Install additional diagonal bracing", "2. Add hold-down hardware", "3. Verify with structural engineer"],
                "estimated_effort": "4 hours",
                "materials_needed": ["2x4 diagonal brace", "Simpson hold-down HD10", "structural screws"],
                "tools_required": ["drill", "impact driver", "level"],
                "requires_engineer_approval": true,
                "cost_impact": "medium",
                "safety_notes": "Ensure proper support before installing hardware"
            }}
        }},
        {{
            "reason": "Stress concentration at corner stud junction",
            "severity": "Moderate",
            "remediation": {{
                "steps": ["1. Add sister stud at junction", "2. Install backing plate", "3. Verify spacing"],
                "estimated_effort": "2 hours",
                "materials_needed": ["2x4 stud", "1/4 inch steel plate"],
                "tools_required": ["saw", "drill", "measuring tape"],
                "requires_engineer_approval": false,
                "cost_impact": "low",
                "safety_notes": "Standard safety precautions"
            }}
        }}
    ],
    "analysis_summary": "Found 2 context-dependent violations requiring expert judgment"
}}""",
        expected_output="JSON with additional violations from expert analysis, each with reason, severity, and detailed remediation plan",
        agent=agent
    )


def create_report_task(merged_results: dict) -> Task:
    """Create task to generate final report"""
    agent = create_report_agent()
    return Task(
        description=f"""Create a comprehensive QC report from these results:
{merged_results}

Include:
- Executive summary of all findings
- All violations (deterministic and LLM-found) with reasons and severity
- Design concerns identified
- Recommendations for addressing each violation
- Final pass/fail/review status for each violation

Return as a formatted JSON report.""",
        expected_output="Formatted JSON QC report with summary, violations, concerns, recommendations, and status",
        agent=agent
    )


def create_visualization_task(panel_data: dict, det_violations: list, llm_violations: list, output_file: str) -> Task:
    """Create task to generate visualization"""
    from crew.agents import create_visualizer_agent
    agent = create_visualizer_agent()
    return Task(
        description=f"""Create a visual SVG diagram of the wall panel with violations highlighted.

Panel Data: {panel_data}
Output File: {output_file}

IMPORTANT: Extract ALL violations from the previous task results in the crew context:
- Look for violations found by the QC Inspector agent (deterministic checks)
- Look for violations identified by the Building Code Consultant agent (expert analysis)
- Look for all violations mentioned in the Report Generator agent's comprehensive report

Create an SVG visualization that:
1. Draws the panel with all studs and openings
2. Color-codes components:
   - Gray studs for good, Red studs for violations
   - Blue windows for good, Yellow windows for warnings
3. Lists ALL violations found (both deterministic and LLM-identified) below the diagram with:
   - Reason for each violation
   - Severity level
4. Shows overall pass/fail status

Important: Do NOT show "No violations found" if any violations were detected. Include every violation.

Return the path to the generated SVG file and a summary of what was visualized.""",
        expected_output="Path to generated SVG file with all violations annotated and visualization summary",
        agent=agent
    )
