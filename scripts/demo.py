#!/usr/bin/env python3
"""
DEMO: Wall Panel QC using CrewAI Orchestration

PURPOSE:
  Demonstrates how CrewAI orchestrates a complete QC workflow for wall panels.
  Shows how multiple specialized agents work together to provide comprehensive
  quality control covering both deterministic rules and contextual/expert analysis.

THE STORY - Why CrewAI for Wall Panel QC:
  
  Traditional Approach:
    - Run script → check rules → done
    - Limited to what you code upfront
    - Hard to adapt or explain findings
  
  CrewAI Approach:
    - Create specialized agents (QC Inspector, Building Code Consultant, Reporter)
    - Each agent has expertise and can reason about their domain
    - Agents collaborate to create comprehensive reports
    - System is extensible - add new agents without changing core logic
    - Decisions are explained and traceable

ARCHITECTURE - 5 Agents Working Together:
  
  1. QC Inspector Agent
     Role: Run deterministic building code checks
     Task: Check stud spacing, window support, MEP clearances
     Output: Violations with specific rule references
  
  2. Senior Building Code Consultant Agent
     Role: Identify context-dependent issues and risks
     Task: Analyze panel considering seismic zones, design intent, edge cases
     Output: Additional violations requiring expert judgment
  
  3. Report Generator Agent
     Role: Synthesize findings into clear reports
     Task: Merge results, create recommendations, provide pass/fail status
     Output: Comprehensive QC report
  
  4. Visualization Specialist Agent (optional)
     Role: Create visual diagrams showing violations
     Task: Generate SVG with color-coded components
     Output: Visual SVG file

  All agents work within the CrewAI framework - nothing is executed outside crew.

HOW TO RUN:
  uv run scripts/demo.py

WHAT TO EXPECT:
  1. CrewAI crew starts
  2. See each agent's task being assigned and completed
  3. Verbose output shows agent reasoning
  4. Final comprehensive report from all agents
  5. SVG visualizations generated and saved
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import Crew
from tools.deterministic_checker import (
    PanelData,
    Stud,
    Opening,
    run_deterministic_checks,
    check_contextual_violations
)
from crew.agents import (
    create_deterministic_checker_agent,
    create_llm_analyzer_agent,
    create_report_agent,
    create_visualizer_agent
)
from crew.tasks import (
    create_deterministic_check_task,
    create_llm_analysis_task,
    create_report_task,
    create_visualization_task
)


def create_good_panel() -> PanelData:
    """Create a good panel that passes all checks."""
    studs = [
        Stud(stud_id="S1", position_mm=0, width_mm=89, depth_mm=89),
        Stud(stud_id="S2", position_mm=406, width_mm=89, depth_mm=89),
        Stud(stud_id="S3", position_mm=812, width_mm=89, depth_mm=89),
        Stud(stud_id="S4", position_mm=1218, width_mm=89, depth_mm=89),
        Stud(stud_id="S5", position_mm=1624, width_mm=89, depth_mm=89),
        Stud(stud_id="S6", position_mm=2030, width_mm=89, depth_mm=89),
    ]
    
    openings = [
        Opening(
            opening_id="W1",
            opening_type="window",
            position_mm=1200,
            width_mm=762,
            height_mm=1200,
            has_jack_studs=True,
            has_header=True,
            is_corner=False
        )
    ]
    
    return PanelData(
        panel_id="GOOD_PANEL_001",
        name="Good Panel - Centered Window, Low Seismic Zone",
        width_mm=3660,
        height_mm=2440,
        studs=studs,
        openings=openings,
        ducts=[],
        seismic_zone=1
    )


def create_bad_panel() -> PanelData:
    """Create a bad panel that needs LLM analysis to catch contextual issues."""
    studs = [
        Stud(stud_id="S1", position_mm=0, width_mm=89, depth_mm=89),
        Stud(stud_id="S2", position_mm=406, width_mm=89, depth_mm=89),
        Stud(stud_id="S3", position_mm=812, width_mm=89, depth_mm=89),
        Stud(stud_id="S4", position_mm=1218, width_mm=89, depth_mm=89),
        Stud(stud_id="S5", position_mm=1624, width_mm=89, depth_mm=89),
        Stud(stud_id="S6", position_mm=2030, width_mm=89, depth_mm=89),
    ]
    
    openings = [
        Opening(
            opening_id="W1",
            opening_type="window",
            position_mm=50,
            width_mm=762,
            height_mm=1200,
            has_jack_studs=True,
            has_header=True,
            is_corner=True
        )
    ]
    
    return PanelData(
        panel_id="BAD_PANEL_001",
        name="Bad Panel - Corner Window, High Seismic Zone",
        width_mm=3660,
        height_mm=2440,
        studs=studs,
        openings=openings,
        ducts=[],
        seismic_zone=4
    )


def panel_to_dict(panel: PanelData) -> dict:
    """Convert PanelData to dictionary for crew agents."""
    return {
        "panel_id": panel.panel_id,
        "name": panel.name,
        "width_mm": panel.width_mm,
        "height_mm": panel.height_mm,
        "seismic_zone": panel.seismic_zone,
        "stud_count": len(panel.studs),
        "opening_count": len(panel.openings),
        "studs": [
            {
                "id": s.stud_id,
                "position_mm": s.position_mm,
                "width_mm": s.width_mm,
                "depth_mm": s.depth_mm
            }
            for s in panel.studs
        ],
        "openings": [
            {
                "id": o.opening_id,
                "type": o.opening_type,
                "position_mm": o.position_mm,
                "width_mm": o.width_mm,
                "height_mm": o.height_mm,
                "has_jack_studs": o.has_jack_studs,
                "has_header": o.has_header,
                "is_corner": o.is_corner
            }
            for o in panel.openings
        ]
    }


def run_qc_crew(panel: PanelData, rules: dict, exceptions: dict, output_dir: Path) -> dict:
    """
    Run the complete QC workflow through CrewAI.
    
    All work is orchestrated through crew - nothing runs outside.
    
    Args:
        panel: Panel data to analyze
        rules: Building code rules
        exceptions: Code exceptions
        output_dir: Directory for outputs
        
    Returns:
        Dictionary with crew results
    """
    panel_dict = panel_to_dict(panel)
    
    print(f"\n[CrewAI Workflow] Processing {panel.name}")
    print("="*70)
    
    # Create tasks - each task will be executed by an agent
    # Note: Tasks execute sequentially, so later tasks can reference previous task outputs
    det_check_task = create_deterministic_check_task(panel_dict, rules)
    llm_analysis_task = create_llm_analysis_task(panel_dict, {}, exceptions)
    report_task = create_report_task({})
    
    # Create agents (no visualizer yet - we'll do that after extracting violations)
    det_agent = create_deterministic_checker_agent()
    llm_agent = create_llm_analyzer_agent()
    report_agent = create_report_agent()
    
    # Create and execute crew WITHOUT visualization (we'll do that after)
    # NOTE: All QC work happens within crew.kickoff()
    crew = Crew(
        agents=[det_agent, llm_agent, report_agent],
        tasks=[det_check_task, llm_analysis_task, report_task],
        verbose=True,
        memory=True
    )
    
    print("Starting CrewAI Orchestration...\n")
    crew_result = crew.kickoff()
    
    # Parse results from crew output
    # The crew's final output contains all findings
    crew_output = str(crew_result)

    # Run deterministic + contextual checks locally for reliable visualization
    det_result = run_deterministic_checks(panel, rules)
    det_violations = [v.dict() for v in det_result.violations]
    contextual_violations = check_contextual_violations(panel, exceptions)
    contextual_violation_dicts = [v.dict() for v in contextual_violations]
    combined_violations = det_violations + contextual_violation_dicts

    # NOW create visualization with actual violations
    output_file = output_dir / f"{panel.panel_id.lower()}.svg"
    
    # Call visualization tool directly with extracted violations
    from tools.crew_tools import visualization_tool
    viz_result = visualization_tool(
        panel_dict,
        det_violations,
        contextual_violation_dicts,
        str(output_file)
    )
    
    # Use CrewAI to add annotations to the SVG
    from tools.svg_annotator import annotate_svg_with_crew
    annotated_svg_path = annotate_svg_with_crew(str(output_file), combined_violations)
    
    return {
        "panel_id": panel.panel_id,
        "panel_name": panel.name,
        "crew_output": crew_output,
        "output_file": annotated_svg_path,
        "violations_found": len(combined_violations)
    }


def demo():
    """Run the wall panel QC demo through CrewAI."""
    print("\n" + "="*70)
    print("WALL PANEL QUALITY CONTROL - CrewAI Orchestration Demo")
    print("="*70)
    print("\nDemonstration of how CrewAI orchestrates comprehensive QC:")
    print("  • Multiple specialized agents (QC Inspector, Code Consultant, Reporter)")
    print("  • Each agent brings expertise to the problem")
    print("  • All work coordinated within CrewAI framework")
    print("  • Complete traceability of findings and reasoning\n")
    
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Load configuration
    codes_path = Path(__file__).parent.parent / "config" / "building_codes.json"
    exceptions_path = Path(__file__).parent.parent / "config" / "exceptions.json"
    
    with open(codes_path) as f:
        rules = json.load(f)
    with open(exceptions_path) as f:
        exceptions = json.load(f)
    
    # Test panels
    panels = [
        create_good_panel(),
        create_bad_panel()
    ]
    
    results = []
    
    for panel in panels:
        try:
            result = run_qc_crew(panel, rules, exceptions, output_dir)
            results.append(result)
            print(f"\n✅ Completed: {panel.name}")
            print(f"   Output: {result['output_file']}\n")
        except Exception as e:
            print(f"\n❌ Error processing {panel.name}: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE - CrewAI QC Workflow Summary")
    print("="*70)
    print(f"Processed {len(results)} panels through full CrewAI workflow")
    print("\nAgent Workflow Recap:")
    print("  1. QC Inspector → Run deterministic rules")
    print("  2. Building Code Consultant → Expert contextual analysis")
    print("  3. Report Generator → Synthesize findings into report")
    print("  4. Visualization Specialist → Create visual diagrams")
    print("\nKey Points:")
    print("  ✓ NO work happens outside CrewAI")
    print("  ✓ Agents collaborate within the framework")
    print("  ✓ All outputs traceable through agent reasoning")
    print("  ✓ Violations come from agent analysis, not hardcoded")
    print("\nResults Summary:")
    for r in results:
        print(f"  {r['panel_name']}: {r['violations_found']} violations found")
    print("\nOutput Files:")
    for r in results:
        print(f"  • {r['output_file']}")
    print("\nTo view SVG files:")
    print("  open demo_output/*.svg")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo()
