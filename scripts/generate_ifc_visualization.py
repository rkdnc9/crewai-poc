#!/usr/bin/env python3
"""
Generate neutral test_data SVG visualizations.

This script creates clean, neutral SVG visualizations for test panels with:
  - Gray studs (no color coding)
  - No violation annotations
  - Minimal labeling
  - Professional styling

These are visual representations of the input IFC geometry, not QC outputs.

USAGE:
    python scripts/generate_ifc_visualization.py

CREATES:
    test_data/good_panel.svg  - Good panel geometry (centered window, low seismic zone)
    test_data/bad_panel.svg   - Bad panel geometry (corner window, high seismic zone)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.deterministic_checker import PanelData, Stud, Opening


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
        name="Good Panel",
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
        name="Bad Panel",
        width_mm=3660,
        height_mm=2440,
        studs=studs,
        openings=openings,
        ducts=[],
        seismic_zone=4
    )


def create_neutral_svg(panel: PanelData, output_path: str) -> str:
    """
    Create a neutral SVG visualization with gray studs, no annotations.
    
    Args:
        panel: Panel data to visualize
        output_path: Path to save SVG file
        
    Returns:
        Path to the generated SVG file
    """
    from pathlib import Path
    output_path = Path(output_path)
    
    # Scale for SVG (1mm = 0.2px)
    scale = 0.2
    width = panel.width_mm * scale
    height = panel.height_mm * scale
    margin = 50
    
    # Start SVG with neutral styling
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + margin*2} {height + margin*2 + 60}" width="{int(width + margin*2)}" height="{int(height + margin*2 + 60)}">',
        '  <defs>',
        '    <style>',
        '      text { font-family: Arial, sans-serif; }',
        '      .panel-bg { fill: #F5F5F5; stroke: #2C3E50; stroke-width: 2; }',
        '      .stud { fill: #9B9B9B; stroke: #7F8C8D; stroke-width: 1; }',
        '      .opening { fill: #E8F4F8; stroke: #7F8C8D; stroke-width: 1; }',
        '      .label { font-size: 11px; font-weight: bold; fill: #2C3E50; }',
        '      .dimension { font-size: 10px; fill: #555; }',
        '    </style>',
        '  </defs>',
        '',
        f'  <!-- Panel background -->',
        f'  <rect class="panel-bg" x="{margin}" y="{margin}" width="{width}" height="{height}"/>',
        ''
    ]
    
    # Draw studs (all gray, neutral)
    for stud in panel.studs:
        stud_x = margin + (stud.position_mm * scale)
        stud_y = margin
        stud_width = stud.width_mm * scale
        stud_height = height
        svg_lines.append(
            f'  <rect class="stud" x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}"/>'
        )
    
    # Draw openings (light blue, neutral)
    for opening in panel.openings:
        opening_x = margin + (opening.position_mm * scale)
        opening_y = margin + (panel.height_mm - opening.height_mm) * scale / 2
        opening_width = opening.width_mm * scale
        opening_height = opening.height_mm * scale
        svg_lines.append(
            f'  <rect class="opening" x="{opening_x}" y="{opening_y}" width="{opening_width}" height="{opening_height}"/>'
        )
    
    # Dimensions at bottom
    svg_lines.append('')
    svg_lines.append(f'  <!-- Dimensions -->')
    svg_lines.append(f'  <text class="dimension" x="{margin + width/2}" y="{margin + height + 30}" text-anchor="middle">{panel.width_mm}mm</text>')
    svg_lines.append(f'  <text class="dimension" x="{margin - 25}" y="{margin + height/2}" text-anchor="middle" transform="rotate(-90 {margin - 25} {margin + height/2})">{panel.height_mm}mm</text>')
    
    svg_lines.append('</svg>')
    
    # Write file
    output_path.write_text('\n'.join(svg_lines))
    return str(output_path)


def generate_visualizations():
    """Generate neutral test_data SVGs."""
    test_data_dir = Path(__file__).parent.parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    panels = [
        ("good", create_good_panel()),
        ("bad", create_bad_panel())
    ]
    
    print("Generating neutral test_data SVG visualizations...")
    print("="*70)
    
    for name, panel in panels:
        output_file = test_data_dir / f"{name}_panel.svg"
        svg_path = create_neutral_svg(panel, str(output_file))
        print(f"✅ {svg_path}")
    
    print("="*70)
    print("\nGenerated test_data visualizations successfully!")
    print("  test_data/good_panel.svg   (neutral, gray studs)")
    print("  test_data/bad_panel.svg    (neutral, gray studs)")


if __name__ == "__main__":
    generate_visualizations()



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
        name="Good Panel",
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
        name="Bad Panel",
        width_mm=3660,
        height_mm=2440,
        studs=studs,
        openings=openings,
        ducts=[],
        seismic_zone=4
    )


def create_neutral_svg(panel: PanelData, output_path: str) -> str:
    """
    Create a neutral SVG visualization with gray studs, no annotations.
    
    Args:
        panel: Panel data to visualize
        output_path: Path to save SVG file
        
    Returns:
        Path to the generated SVG file
    """
    from pathlib import Path
    output_path = Path(output_path)
    
    # Scale for SVG (1mm = 0.2px)
    scale = 0.2
    width = panel.width_mm * scale
    height = panel.height_mm * scale
    margin = 50
    
    # Start SVG with neutral styling
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + margin*2} {height + margin*2 + 60}" width="{int(width + margin*2)}" height="{int(height + margin*2 + 60)}">',
        '  <defs>',
        '    <style>',
        '      text { font-family: Arial, sans-serif; }',
        '      .panel-bg { fill: #F5F5F5; stroke: #2C3E50; stroke-width: 2; }',
        '      .stud { fill: #9B9B9B; stroke: #7F8C8D; stroke-width: 1; }',
        '      .opening { fill: #E8F4F8; stroke: #7F8C8D; stroke-width: 1; }',
        '      .label { font-size: 11px; font-weight: bold; fill: #2C3E50; }',
        '      .dimension { font-size: 10px; fill: #555; }',
        '    </style>',
        '  </defs>',
        '',
        f'  <!-- Panel background -->',
        f'  <rect class="panel-bg" x="{margin}" y="{margin}" width="{width}" height="{height}"/>',
        ''
    ]
    
    # Draw studs (all gray, neutral)
    for stud in panel.studs:
        stud_x = margin + (stud.position_mm * scale)
        stud_y = margin
        stud_width = stud.width_mm * scale
        stud_height = height
        svg_lines.append(
            f'  <rect class="stud" x="{stud_x}" y="{stud_y}" width="{stud_width}" height="{stud_height}"/>'
        )
    
    # Draw openings (light blue, neutral)
    for opening in panel.openings:
        opening_x = margin + (opening.position_mm * scale)
        opening_y = margin + (panel.height_mm - opening.height_mm) * scale / 2
        opening_width = opening.width_mm * scale
        opening_height = opening.height_mm * scale
        svg_lines.append(
            f'  <rect class="opening" x="{opening_x}" y="{opening_y}" width="{opening_width}" height="{opening_height}"/>'
        )
    
    # Dimensions at bottom
    svg_lines.append('')
    svg_lines.append(f'  <!-- Dimensions -->')
    svg_lines.append(f'  <text class="dimension" x="{margin + width/2}" y="{margin + height + 30}" text-anchor="middle">{panel.width_mm}mm</text>')
    svg_lines.append(f'  <text class="dimension" x="{margin - 25}" y="{margin + height/2}" text-anchor="middle" transform="rotate(-90 {margin - 25} {margin + height/2})">{panel.height_mm}mm</text>')
    
    svg_lines.append('</svg>')
    
    # Write file
    output_path.write_text('\n'.join(svg_lines))
    return str(output_path)


def generate_visualizations():
    """Generate neutral test_data SVGs."""
    test_data_dir = Path(__file__).parent.parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    panels = [
        ("good", create_good_panel()),
        ("bad", create_bad_panel())
    ]
    
    print("Generating neutral test_data SVG visualizations...")
    print("="*70)
    
    for name, panel in panels:
        output_file = test_data_dir / f"{name}_panel.svg"
        svg_path = create_neutral_svg(panel, str(output_file))
        print(f"✅ {svg_path}")
    
    print("="*70)
    print("\nGenerated test_data visualizations successfully!")
    print("  test_data/good_panel.svg   (neutral, gray studs)")
    print("  test_data/bad_panel.svg    (neutral, gray studs)")


if __name__ == "__main__":
    generate_visualizations()
