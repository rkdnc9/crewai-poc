"""
CrewAI Tools - Tools that crew agents can use to execute checks and generate outputs.

These tools are used by crew agents to perform their work. They are NOT called
directly from outside the crew - only agents use them during task execution.
"""

from tools.deterministic_checker import (
    PanelData, run_deterministic_checks
)
from tools.visualizer_tool import create_panel_visualization


def deterministic_check_tool(panel_data_dict: dict, building_codes: dict) -> dict:
    """
    Deterministic rule checker tool used by QC Inspector agent.
    
    Converts panel dict to PanelData object and runs deterministic checks.
    Returns violations as a dictionary for the agent to analyze.
    
    Args:
        panel_data_dict: Panel data as dictionary
        building_codes: Building code rules
        
    Returns:
        Dictionary with violation details
    """
    try:
        # Reconstruct PanelData from dict (simplified - assumes dict has required fields)
        # In a real implementation, you'd deserialize properly
        panel = PanelData(
            panel_id=panel_data_dict.get("panel_id", "UNKNOWN"),
            name=panel_data_dict.get("name", "Panel"),
            width_mm=panel_data_dict.get("width_mm", 3660),
            height_mm=panel_data_dict.get("height_mm", 2440),
            studs=panel_data_dict.get("studs", []),
            openings=panel_data_dict.get("openings", []),
            ducts=panel_data_dict.get("ducts", []),
            seismic_zone=panel_data_dict.get("seismic_zone", 1)
        )
        
        result = run_deterministic_checks(panel, building_codes)
        
        # Convert to JSON-serializable format
        violations = []
        if result.violations:
            for v in result.violations:
                violations.append({
                    "reason": v.reason if hasattr(v, 'reason') else str(v),
                    "severity": v.severity if hasattr(v, 'severity') else "Unknown",
                    "rule_id": v.rule_id if hasattr(v, 'rule_id') else "UNKNOWN"
                })
        
        return {
            "status": "success",
            "panel_id": panel.panel_id,
            "violations_count": len(violations),
            "violations": violations,
            "result_summary": f"Found {len(violations)} deterministic violations"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "violations": []
        }


def visualization_tool(
    panel_data_dict: dict,
    det_violations: list,
    llm_violations: list,
    output_file: str
) -> dict:
    """
    Visualization tool used by Visualization Specialist agent.
    
    Creates SVG visualization with violations highlighted.
    
    Args:
        panel_data_dict: Panel data as dictionary
        det_violations: Deterministic violations from QC Inspector
        llm_violations: LLM violations from Consultant
        output_file: Output file path
        
    Returns:
        Dictionary with visualization path and status
    """
    try:
        from tools.deterministic_checker import Stud, Opening
        
        # Reconstruct Stud objects
        studs = []
        for s in panel_data_dict.get("studs", []):
            if isinstance(s, dict):
                studs.append(Stud(
                    stud_id=s.get("id", ""),
                    position_mm=s.get("position_mm", 0),
                    width_mm=s.get("width_mm", 89),
                    depth_mm=s.get("depth_mm", 89)
                ))
            else:
                studs.append(s)
        
        # Reconstruct Opening objects
        openings = []
        for o in panel_data_dict.get("openings", []):
            if isinstance(o, dict):
                openings.append(Opening(
                    opening_id=o.get("id", ""),
                    opening_type=o.get("type", "window"),
                    position_mm=o.get("position_mm", 0),
                    width_mm=o.get("width_mm", 762),
                    height_mm=o.get("height_mm", 1200),
                    has_jack_studs=o.get("has_jack_studs", True),
                    has_header=o.get("has_header", True),
                    is_corner=o.get("is_corner", False)
                ))
            else:
                openings.append(o)
        
        # Reconstruct PanelData
        panel = PanelData(
            panel_id=panel_data_dict.get("panel_id", "UNKNOWN"),
            name=panel_data_dict.get("name", "Panel"),
            width_mm=panel_data_dict.get("width_mm", 3660),
            height_mm=panel_data_dict.get("height_mm", 2440),
            studs=studs,
            openings=openings,
            ducts=panel_data_dict.get("ducts", []),
            seismic_zone=panel_data_dict.get("seismic_zone", 1)
        )
        
        # Create a mock DeterministicCheckResult
        class MockResult:
            def __init__(self, violations):
                self.violations = violations
        
        # Convert violations to objects with reason attribute
        det_violations_objs = []
        for v in det_violations:
            if isinstance(v, dict):
                class V:
                    def __init__(self, reason, severity="Unknown", rule_id=""):
                        self.reason = reason
                        self.severity = severity
                        self.rule_id = rule_id
                det_violations_objs.append(V(
                    reason=v.get("reason", str(v)),
                    severity=v.get("severity", "Unknown"),
                    rule_id=v.get("rule_id", "")
                ))
            else:
                det_violations_objs.append(v)
        
        result = MockResult(det_violations_objs)
        
        svg_path = create_panel_visualization(
            panel,
            result,
            llm_violations,
            output_file
        )
        
        return {
            "status": "success",
            "svg_path": svg_path,
            "panel_id": panel.panel_id,
            "message": f"Visualization created at {svg_path}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e)
        }
