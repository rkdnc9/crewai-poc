#!/usr/bin/env python3
"""
Standalone Utility: Generate SVG Visualizations from IFC Files

PURPOSE: Convert IFC files to clean SVG visualizations WITHOUT QC analysis.
  Shows raw panel geometry (good for design reviews, presentations).

WHEN TO USE:
  - View raw panel geometry without violations  
  - Generate clean reference visualizations
  - Compare inputs (IFC) vs outputs (QC analysis)

WHAT IT DOES:
  1. Opens IFC file with IfcOpenShell
  2. Extracts geometry (dimensions, studs, windows, seismic zone, etc.)
  3. Generates SVG with consistent scale (0.2px/mm)
  4. Saves clean visualization

USAGE:
  python scripts/generate_ifc_visualization.py panel.ifc
  python scripts/generate_ifc_visualization.py panel.ifc custom_output.svg

TEST DATA:
  test_data/good_panel.ifc  → good_panel.svg (centered window)
  test_data/bad_panel.ifc   → bad_panel.svg (corner window, seismic zone 4)
Shows the actual panel geometry without any QC annotations or violations.
"""
import argparse
import sys
from pathlib import Path

import ifcopenshell


def extract_ifc_geometry(ifc_path: str) -> dict:
    ifc_file = ifcopenshell.open(ifc_path)
    
    geometry_data = {
        "width": 3000,
        "height": 2440,
        "wall_name": None,
        "stud_count": 6,
        "stud_spacing": 406,
        "window_count": 0,
        "window_width": 762,
        "window_position": None,
        "is_corner": False,
        "seismic_zone": 1
    }
    
    # Get wall info and extract properties
    for wall in ifc_file.by_type('IfcWall'):
        geometry_data["wall_name"] = wall.Name
        
        # Extract properties from property sets
        if wall.IsDefinedBy:
            for rel in wall.IsDefinedBy:
                if hasattr(rel, 'RelatingPropertyDefinition'):
                    pset = rel.RelatingPropertyDefinition
                    if hasattr(pset, 'HasProperties'):
                        for prop in pset.HasProperties:
                            if hasattr(prop, 'Name') and hasattr(prop, 'NominalValue'):
                                name = prop.Name
                                value = prop.NominalValue
                                
                                # Handle both numeric values and tuples
                                if isinstance(value, tuple):
                                    value = value[0]
                                if hasattr(value, 'wrappedValue'):
                                    value = value.wrappedValue
                                
                                try:
                                    if name == 'PanelWidth':
                                        geometry_data["width"] = float(value)
                                    elif name == 'PanelHeight':
                                        geometry_data["height"] = float(value)
                                    elif name == 'StudSpacing':
                                        geometry_data["stud_spacing"] = float(value)
                                    elif name == 'StudCount':
                                        geometry_data["stud_count"] = int(value)
                                    elif name == 'WindowCount':
                                        geometry_data["window_count"] = int(value)
                                    elif name == 'WindowWidth':
                                        geometry_data["window_width"] = float(value)
                                    elif name == 'WindowPosition':
                                        geometry_data["window_position"] = float(value)
                                    elif name == 'WindowIsCorner':
                                        geometry_data["is_corner"] = bool(value)
                                    elif name == 'SeismicZone':
                                        geometry_data["seismic_zone"] = int(value)
                                except (ValueError, TypeError):
                                    pass
    
    return geometry_data


def create_svg_visualization(ifc_path: str, output_path: str = None) -> str:
    ifc_file = Path(ifc_path)
    if not ifc_file.exists():
        raise FileNotFoundError(f"IFC file not found: {ifc_path}")
    
    if output_path is None:
        output_path = ifc_file.parent / f"{ifc_file.stem}.svg"
    else:
        output_path = Path(output_path)
        # Convert PNG extension to SVG if specified
        if str(output_path).endswith('.png'):
            output_path = output_path.with_suffix('.svg')
    
    geometry = extract_ifc_geometry(ifc_path)
    
    # Scale for SVG (1mm = 0.2px)
    scale = 0.2
    width = geometry["width"] * scale
    height = geometry["height"] * scale
    
    # SVG header
    svg_lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + 100} {height + 150}" width="{int(width + 100)}" height="{int(height + 150)}">',
        f'  <defs>',
        f'    <style>',
        f'      text {{ font-family: Arial, sans-serif; }}',
        f'      .panel-bg {{ fill: #F5F5F5; stroke: #2C3E50; stroke-width: 2; }}',
        f'      .stud {{ fill: #BDC3C7; stroke: #7F8C8D; stroke-width: 1; }}',
        f'      .window {{ fill: #AED6F1; stroke: #3498DB; stroke-width: 2; }}',
        f'      .label {{ font-size: 14px; font-weight: bold; }}',
        f'      .dimension {{ font-size: 11px; fill: #34495E; }}',
        f'    </style>',
        f'  </defs>',
    ]
    
    # Draw panel background
    svg_lines.append(f'  <rect class="panel-bg" x="50" y="50" width="{width}" height="{height}"/>')
    
    # Draw studs
    if geometry["stud_count"] > 0:
        stud_width = 38 * scale
        for i in range(geometry["stud_count"]):
            x_pos = (width / (geometry["stud_count"] + 1)) * (i + 1) - stud_width / 2
            svg_lines.append(f'  <rect class="stud" x="{50 + x_pos}" y="50" width="{stud_width}" height="{height}"/>')
    
    # Draw window if present
    if geometry["window_count"] > 0:
        window_width = geometry["window_width"] * scale
        window_height = 400 * scale
        
        # Position: 50 = corner (left), centered otherwise
        if geometry["window_position"] == 50 or geometry["is_corner"]:
            # Corner window (left side)
            window_x = 50 + 100
        else:
            # Centered window
            window_x = 50 + (width - window_width) / 2
        
        window_y = 50 + (height - window_height) / 2
        svg_lines.append(f'  <rect class="window" x="{window_x}" y="{window_y}" width="{window_width}" height="{window_height}"/>')
    
    # Add panel label
    label_x = 50 + width / 2
    label_y = 30
    svg_lines.append(f'  <text class="label" text-anchor="middle" x="{label_x}" y="{label_y}">{geometry["wall_name"]}</text>')
    
    # Add dimensions
    dim_x = 50 + width / 2
    dim_y = 50 + height + 30
    svg_lines.append(f'  <text class="dimension" text-anchor="middle" x="{dim_x}" y="{dim_y}">{geometry["width"]:.0f}mm</text>')
    
    dim_x2 = 30
    dim_y2 = 50 + height / 2
    svg_lines.append(f'  <text class="dimension" text-anchor="middle" x="{dim_x2}" y="{dim_y2}" transform="rotate(-90 {dim_x2} {dim_y2})">{geometry["height"]:.0f}mm</text>')
    
    # Add seismic zone info if bad panel
    if geometry["seismic_zone"] > 1:
        info_y = 50 + height + 60
        svg_lines.append(f'  <text class="dimension" text-anchor="middle" x="{label_x}" y="{info_y}">Seismic Zone: {geometry["seismic_zone"]}</text>')
    
    if geometry["is_corner"]:
        info_y = 50 + height + 75
        svg_lines.append(f'  <text class="dimension" text-anchor="middle" x="{label_x}" y="{info_y}">⚠ Corner Window</text>')
    
    svg_lines.append('</svg>')
    
    # Write SVG file
    with open(output_path, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG visualization from IFC file"
    )
    parser.add_argument("ifc_file", help="Path to IFC file")
    parser.add_argument("output_path", nargs="?", help="Output SVG/PNG path (optional, converts to SVG)")
    
    args = parser.parse_args()
    
    try:
        print(f"Generating visualization for: {args.ifc_file}")
        viz_path = create_svg_visualization(args.ifc_file, args.output_path)
        print(f"✅ Saved: {viz_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
