#!/usr/bin/env python3
"""
Generate test_data SVG visualizations using the improved visualization tool.

This script creates clean SVG visualizations for test panels, providing consistent 
styling and professional rendering across all outputs.

USAGE:
    python scripts/generate_ifc_visualization.py

CREATES:
    test_data/good_panel.svg  - Good panel (centered window, low seismic zone)
    test_data/bad_panel.svg   - Bad panel (corner window, high seismic zone)

These SVGs use the same professional visualization as demo_output, with:
  - Proper stud proportions and spacing
  - Color-coded components (red=violations, gray=good)
  - Clean, consistent styling
  - Professional annotations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.deterministic_checker import PanelData, Stud, Opening
from tools.visualizer_tool import create_panel_visualization


def create_good_panel() -> PanelData:
    """Good panel: centered window, low seismic zone."""
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
    """Bad panel: corner window, high seismic zone."""
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


def create_mock_result(violations_list):
    """Create a mock DeterministicCheckResult object."""
    class MockResult:
        def __init__(self, violations):
            self.violations = violations
    
    # Convert violation dicts to objects with reason attribute
    violation_objs = []
    for v in violations_list:
        class V:
            def __init__(self, reason, severity="Unknown"):
                self.reason = reason
                self.severity = severity
        violation_objs.append(V(
            reason=v.get("reason", str(v)),
            severity=v.get("severity", "Unknown")
        ))
    
    return MockResult(violation_objs)


def generate_visualizations():
    """Generate test_data SVGs with professional styling."""
    test_data_dir = Path(__file__).parent.parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    panels_info = [
        ("good", create_good_panel(), 
         [  # No violations for good panel
         ]),
        ("bad", create_bad_panel(),
         [  # Example violations for bad panel (corner + seismic)
             {
                 "reason": "Corner window in high seismic zone requires extra bracing",
                 "severity": "High"
             },
             {
                 "reason": "Stress concentration at corner stud junction",
                 "severity": "High"
             }
         ])
    ]
    
    print("Generating test_data SVG visualizations...")
    print("="*70)
    
    for name, panel, violations in panels_info:
        # Create mock result
        result = create_mock_result(violations)
        
        # Generate SVG
        output_file = test_data_dir / f"{name}_panel.svg"
        svg_path = create_panel_visualization(
            panel,
            result,
            [],
            str(output_file)
        )
        print(f"✅ {svg_path}")
    
    print("="*70)
    print("\nGenerated test_data visualizations successfully!")
    print("  test_data/good_panel.svg")
    print("  test_data/bad_panel.svg")


if __name__ == "__main__":
    generate_visualizations()
