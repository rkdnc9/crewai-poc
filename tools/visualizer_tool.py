"""
Wall Panel Visualization Tool - Creates SVG Diagrams with Violations Highlighted

PURPOSE: Converts QC results (deterministic + LLM violations) into visual SVG diagrams.

HOW IT WORKS:
  1. Takes panel geometry + violations as input
  2. Creates SVG with panels drawn to scale (0.2px/mm = same as IFC tool)
  3. Color-codes components:
     - Gray studs = good, Red studs = bad
     - Blue windows = good, Yellow windows = warning
  4. Lists violation reasons below diagram
  5. Shows "✅ No violations found" for clean panels

USAGE:
  from tools.visualizer_tool import create_panel_visualization
  
  svg_path = create_panel_visualization(
      panel_data=panel,
      det_result=det_check_result,
      llm_violations=[{'reason': '...'}],
      output_path='output.svg'
  )
"""

from pathlib import Path
from tools.deterministic_checker import PanelData, DeterministicCheckResult


def create_panel_visualization(
    panel_data: PanelData,
    det_result: DeterministicCheckResult,
    llm_violations: list = None,
    output_path: str = "panel_visualization.svg"
) -> str:
    """
    Create a visual diagram of the wall panel with violations highlighted.
    
    Args:
        panel_data: Panel data with dimensions and components
        det_result: Deterministic check results with violations
        llm_violations: Additional LLM violations to include
        output_path: Path to save SVG file
        
    Returns:
        Path to the generated SVG file
    """
    
    # Convert to SVG extension
    output_path = Path(output_path)
    if output_path.suffix == '.png':
        output_path = output_path.with_suffix('.svg')
    
    # Scale for SVG (1mm = 0.2px) - same as IFC tool for consistency
    scale = 0.2
    width = panel_data.width_mm * scale
    height = panel_data.height_mm * scale
    margin = 50
    
    # Check for violations
    all_violations = list(det_result.violations) if det_result.violations else []
    if llm_violations:
        all_violations.extend(llm_violations)
    has_violations = bool(all_violations)
    
    # Start SVG
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + margin*2} {height + margin*2 + (120 if has_violations else 80)}" width="{int(width + margin*2)}" height="{int(height + margin*2 + (120 if has_violations else 80))}">',
        '  <defs>',
        '    <style>',
        '      text { font-family: Arial, sans-serif; }',
        '      .panel-bg { fill: #F5F5F5; stroke: #2C3E50; stroke-width: 2; }',
        '      .stud { stroke: #7F8C8D; stroke-width: 1; }',
        '      .stud-good { fill: #BDC3C7; }',
        '      .stud-bad { fill: #FF6B6B; }',
        '      .opening { stroke: #3498DB; stroke-width: 2; }',
        '      .opening-good { fill: #AED6F1; }',
        '      .opening-warn { fill: #FFD700; }',
        '      .label { font-size: 12px; font-weight: bold; }',
        '      .dimension { font-size: 11px; fill: #34495E; }',
        '      .violation-text { font-size: 9px; fill: #000; }',
        '    </style>',
        '  </defs>',
    ]
    
    # Draw panel background
    svg_lines.append(f'  <rect class="panel-bg" x="{margin}" y="{margin}" width="{width}" height="{height}"/>')
    
    # Draw studs
    stud_class = "stud-bad" if has_violations else "stud-good"
    for stud in panel_data.studs:
        x = margin + (stud.position_mm * scale)
        stud_width = stud.width_mm * scale
        svg_lines.append(f'  <rect class="stud {stud_class}" x="{x - stud_width/2}" y="{margin}" width="{stud_width}" height="{height}"/>')
    
    # Draw openings (windows/doors)
    opening_class = "opening-warn" if has_violations else "opening-good"
    for opening in panel_data.openings:
        x = margin + (opening.position_mm * scale)
        y = margin + ((panel_data.height_mm - opening.height_mm) / 2 * scale)
        w = opening.width_mm * scale
        h = opening.height_mm * scale
        
        svg_lines.append(f'  <rect class="opening {opening_class}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        svg_lines.append(f'  <text class="label" x="{x + w/2}" y="{y + h/2 + 4}" text-anchor="middle">Window {opening.width_mm:.0f}mm</text>')
    
    # Draw MEP ducts
    for duct in panel_data.ducts:
        x = margin + (duct.position_mm * scale)
        y = margin + (duct.diameter_mm / 2 * scale)
        size = 6 * scale
        svg_lines.append(f'  <circle class="stud stud-good" cx="{x}" cy="{y}" r="{size}"/>')
    
    # Add panel label
    label_x = margin + width / 2
    label_y = margin - 20
    svg_lines.append(f'  <text class="label" x="{label_x}" y="{label_y}" text-anchor="middle">{panel_data.name}</text>')
    
    # Add dimensions
    dim_x = margin + width / 2
    dim_y = margin + height + 30
    svg_lines.append(f'  <text class="dimension" x="{dim_x}" y="{dim_y}" text-anchor="middle">{panel_data.width_mm:.0f}mm</text>')
    
    dim_x2 = margin - 15
    dim_y2 = margin + height / 2
    svg_lines.append(f'  <text class="dimension" x="{dim_x2}" y="{dim_y2}" text-anchor="end" transform="rotate(-90 {dim_x2} {dim_y2})">{panel_data.height_mm:.0f}mm</text>')
    
    # Add violation summary
    if has_violations:
        violation_y = margin + height + 50
        svg_lines.append(f'  <text class="label" x="{margin + 10}" y="{violation_y}" fill="#C0392B">Violations Found:</text>')
        
        line_y = violation_y + 15
        
        # Deterministic violations
        if det_result.violations:
            svg_lines.append(f'  <text class="violation-text" x="{margin + 10}" y="{line_y}" font-weight="bold">Det:</text>')
            for v in det_result.violations[:3]:
                line_y += 12
                reason = v.reason if hasattr(v, 'reason') else str(v)
                svg_lines.append(f'  <text class="violation-text" x="{margin + 20}" y="{line_y}">• {reason[:45]}</text>')
            if len(det_result.violations) > 3:
                line_y += 12
                svg_lines.append(f'  <text class="violation-text" x="{margin + 20}" y="{line_y}">... +{len(det_result.violations) - 3} more</text>')
        
        # LLM violations
        if llm_violations:
            line_y += 12
            svg_lines.append(f'  <text class="violation-text" x="{margin + 10}" y="{line_y}" font-weight="bold">LLM:</text>')
            for v in llm_violations[:3]:
                line_y += 12
                if isinstance(v, dict):
                    reason = v.get('reason', v.get('description', 'Unknown'))
                else:
                    reason = str(v)
                svg_lines.append(f'  <text class="violation-text" x="{margin + 20}" y="{line_y}">• {reason[:45]}</text>')
            if len(llm_violations) > 3:
                line_y += 12
                svg_lines.append(f'  <text class="violation-text" x="{margin + 20}" y="{line_y}">... +{len(llm_violations) - 3} more</text>')
    else:
        # Show clean status
        status_y = margin + height + 50
        svg_lines.append(f'  <text class="label" x="{margin + width/2}" y="{status_y}" text-anchor="middle" fill="#27AE60">✅ No violations found</text>')
    
    svg_lines.append('</svg>')
    
    # Write SVG file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    return str(output_path)
