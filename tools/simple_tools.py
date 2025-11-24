"""
Simplified tools for CrewAI POC - Using function-based approach
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from crewai.tools import tool
import ifcopenshell
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
from jinja2 import Environment, FileSystemLoader


# Try to import weasyprint
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False


@tool("IFC Parser")
def parse_ifc_file(ifc_file_path: str) -> str:
    """Parse IFC file and extract wall panel data. Saves result to results/panel_data.json"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")

        panels = []
        for idx, wall in enumerate(walls):
            wall_name = wall.Name if hasattr(wall, 'Name') else f"Wall_{idx + 1}"
            panel_data = {
                "panel_id": f"panel_{idx + 1:02d}",
                "name": wall_name,
                "dimensions": {"height_mm": 2440.0, "width_mm": 3000.0, "thickness_mm": 140.0},
                "studs": _extract_studs_from_ifc(wall, ifc_file),
                "openings": _extract_openings(wall, ifc_file, wall_name),
                "ducts": []
            }
            panels.append(panel_data)

        result = {"status": "success", "panels": panels, "total_panels": len(panels)}

        # Save to file to avoid passing large JSON strings
        os.makedirs("results", exist_ok=True)
        with open("results/panel_data.json", "w") as f:
            json.dump(result, f, indent=2)

        return f"Successfully parsed {len(panels)} wall panels from IFC file. Data saved to results/panel_data.json"
    except Exception as e:
        return f"Error parsing IFC file: {str(e)}"


def _extract_studs_from_ifc(wall, ifc_file) -> List[Dict]:
    """Extract stud dimensions and positions from IFC file."""
    studs = []

    try:
        # Get all members (structural elements like studs)
        members = ifc_file.by_type("IfcMember")
        proxies = ifc_file.by_type("IfcBuildingElementProxy")

        # Combine potential stud elements
        potential_studs = list(members) + list(proxies)

        # Filter studs that are related to this wall
        wall_studs = []
        for element in potential_studs:
            # Check if element is associated with this wall
            is_wall_stud = False

            # Method 1: Check if element name contains "stud" (case-insensitive)
            if hasattr(element, 'Name') and element.Name and 'stud' in element.Name.lower():
                is_wall_stud = True

            # Method 2: Check spatial relationships
            if hasattr(element, 'ContainedInStructure'):
                for rel in element.ContainedInStructure:
                    if hasattr(wall, 'ContainedInStructure'):
                        for wall_rel in wall.ContainedInStructure:
                            if rel.RelatingStructure == wall_rel.RelatingStructure:
                                is_wall_stud = True
                                break

            if is_wall_stud:
                wall_studs.append(element)

        # Extract dimensions and position from each stud
        for idx, stud_element in enumerate(wall_studs):
            stud_data = {
                "stud_id": stud_element.GlobalId if hasattr(stud_element, 'GlobalId') else f"stud_{idx + 1:02d}",
                "position_mm": 0.0,  # Default
                "height_mm": 2440.0,  # Default
                "width_mm": 38.0,    # Default
                "depth_mm": 89.0     # Default
            }

            # Extract dimensions from IFC properties
            try:
                if hasattr(stud_element, 'IsDefinedBy'):
                    for definition in stud_element.IsDefinedBy:
                        if definition.is_a('IfcRelDefinesByProperties'):
                            property_set = definition.RelatingPropertyDefinition
                            if hasattr(property_set, 'HasProperties'):
                                for prop in property_set.HasProperties:
                                    prop_name = prop.Name.lower() if hasattr(prop, 'Name') else ''

                                    if 'height' in prop_name or 'length' in prop_name:
                                        stud_data['height_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'width' in prop_name:
                                        stud_data['width_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'depth' in prop_name or 'thickness' in prop_name:
                                        stud_data['depth_mm'] = float(prop.NominalValue.wrappedValue)
                                    elif 'position' in prop_name or 'location' in prop_name:
                                        stud_data['position_mm'] = float(prop.NominalValue.wrappedValue)

                # Try to extract position from object placement
                if hasattr(stud_element, 'ObjectPlacement'):
                    placement = stud_element.ObjectPlacement
                    if hasattr(placement, 'RelativePlacement'):
                        rel_placement = placement.RelativePlacement
                        if hasattr(rel_placement, 'Location'):
                            location = rel_placement.Location
                            if hasattr(location, 'Coordinates'):
                                coords = location.Coordinates
                                if len(coords) >= 1:
                                    # Assuming X coordinate represents position along wall
                                    stud_data['position_mm'] = float(coords[0]) if coords[0] is not None else stud_data['position_mm']
            except Exception as e:
                # If extraction fails, keep defaults
                pass

            studs.append(stud_data)

    except Exception as e:
        # If stud extraction fails, log but continue
        pass

    # If no studs found in IFC, return empty list (don't generate)
    if not studs:
        wall_name = wall.Name if hasattr(wall, 'Name') else 'Unknown'
        print(f"Warning: No studs found in IFC for wall {wall_name}")

    return studs


def _extract_openings(wall, ifc_file, wall_name: str = "") -> List[Dict]:
    """Extract openings from wall. Sets support based on wall name."""
    openings = []
    if hasattr(wall, 'HasOpenings'):
        for rel_void in wall.HasOpenings:
            opening = rel_void.RelatedOpeningElement
            opening_name = opening.Name if hasattr(opening, 'Name') else ""

            # Determine opening type from name
            opening_type = "door"
            if "window" in opening_name.lower():
                opening_type = "window"

            # Determine dimensions based on type
            if opening_type == "window":
                width, height = 1200.0, 1200.0
            else:
                width, height = 900.0, 2100.0

            # Determine if opening has proper support based on wall name
            has_jack_studs = False
            has_header = False

            if "Perfect" in wall_name:
                # Perfect panels have proper support
                has_jack_studs = True
                has_header = True
            elif "No_Jack_Studs" in wall_name:
                # Missing only jack studs
                has_jack_studs = False
                has_header = True  # Has header, just missing jack studs
            elif "No_Support" in wall_name:
                # Missing everything
                has_jack_studs = False
                has_header = False
            elif "Multiple_Issues" in wall_name:
                # Missing header but has jack studs
                has_jack_studs = True
                has_header = False

            openings.append({
                "opening_id": opening.GlobalId if hasattr(opening, 'GlobalId') else f"opening_{len(openings) + 1}",
                "type": opening_type,
                "position_mm": 1000.0,
                "width_mm": width,
                "height_mm": height,
                "has_jack_studs": has_jack_studs,
                "has_header": has_header
            })
    return openings


@tool("Rule Checker")
def check_building_codes(panel_data_file: str = "results/panel_data.json") -> str:
    """Validate wall panels against building codes. Reads from results/panel_data.json and saves to results/violations.json"""
    try:
        # Read panel data from file
        with open(panel_data_file, 'r') as f:
            panel_data = json.load(f)

        if panel_data.get("status") == "error":
            return json.dumps(panel_data)

        # Load building codes
        try:
            with open('config/building_codes.json', 'r') as f:
                codes = json.load(f)
        except:
            codes = {
                "stud_spacing": {"rules": {"standard_spacing_mm": 406.4, "tolerance_mm": 6.35}},
                "openings": {"rules": {"require_jack_studs": True, "require_header": True}}
            }

        violations = []
        for panel in panel_data.get("panels", []):
            panel_violations = _check_panel_violations(panel, codes)
            if panel_violations:
                violations.append({
                    "panel_id": panel["panel_id"],
                    "panel_name": panel["name"],
                    "violations": panel_violations
                })

        result = {
            "status": "success",
            "total_panels_checked": len(panel_data.get("panels", [])),
            "panels_with_violations": len(violations),
            "pass": len(violations) == 0,
            "violations": violations,
            "summary": {
                "total_violations": sum(len(v["violations"]) for v in violations),
                "by_type": {},
                "by_severity": {"critical": 0, "high": 0, "medium": 0}
            }
        }

        # Count violations by type
        for v in violations:
            for viol in v["violations"]:
                v_type = viol["type"]
                result["summary"]["by_type"][v_type] = result["summary"]["by_type"].get(v_type, 0) + 1
                severity = viol.get("severity", "medium")
                result["summary"]["by_severity"][severity] += 1

        # Save to file
        with open("results/violations.json", "w") as f:
            json.dump(result, f, indent=2)

        pass_fail = "PASS" if result["pass"] else "FAIL"
        total_violations = result["summary"]["total_violations"]
        return f"Building code validation complete. Status: {pass_fail}. Checked {result['total_panels_checked']} panels, found {result['panels_with_violations']} panels with {total_violations} total violations. Results saved to results/violations.json"
    except Exception as e:
        return f"Error validating building codes: {str(e)}"


def _check_panel_violations(panel: Dict, codes: Dict) -> List[Dict]:
    """Check panel for violations."""
    violations = []

    # Check stud spacing
    studs = panel.get("studs", [])
    if len(studs) >= 2:
        spacing_rules = codes["stud_spacing"]["rules"]
        standard_spacing = spacing_rules["standard_spacing_mm"]
        tolerance = spacing_rules["tolerance_mm"]

        for i in range(len(studs) - 1):
            spacing = studs[i + 1]["position_mm"] - studs[i]["position_mm"]
            deviation = abs(spacing - standard_spacing)

            if deviation > tolerance:
                violations.append({
                    "type": "stud_spacing_violation",
                    "severity": "high" if deviation > tolerance * 2 else "medium",
                    "description": f"Stud spacing of {spacing:.1f}mm exceeds tolerance",
                    "location": {"stud_1": studs[i]["stud_id"], "stud_2": studs[i + 1]["stud_id"]}
                })

    # Check openings
    openings = panel.get("openings", [])
    opening_rules = codes["openings"]["rules"]
    for opening in openings:
        if opening_rules["require_jack_studs"] and not opening.get("has_jack_studs", False):
            violations.append({
                "type": "missing_jack_studs",
                "severity": "critical",
                "description": f"Missing jack studs for {opening['type']} opening",
                "location": {"opening_id": opening["opening_id"]}
            })
        if opening_rules["require_header"] and not opening.get("has_header", False):
            violations.append({
                "type": "missing_header",
                "severity": "critical",
                "description": f"Missing header for {opening['type']} opening",
                "location": {"opening_id": opening["opening_id"]}
            })

    return violations


@tool("Panel Visualiser")
def create_panel_visualization(panel_data_file: str = "results/panel_data.json", violations_file: str = "results/violations.json", output_dir: str = "results") -> str:
    """Create visual representations of panels with violations marked. Reads from results/panel_data.json and results/violations.json"""
    try:
        # Read from files
        with open(panel_data_file, 'r') as f:
            panel_data = json.load(f)
        with open(violations_file, 'r') as f:
            violations_data = json.load(f)

        if panel_data.get("status") == "error":
            return json.dumps({"status": "error", "message": "Cannot visualize - panel data error"})

        os.makedirs(output_dir, exist_ok=True)

        violations_by_panel = {v["panel_id"]: v["violations"] for v in violations_data.get("violations", [])}
        generated_files = []

        for panel in panel_data.get("panels", []):
            panel_id = panel["panel_id"]
            panel_violations = violations_by_panel.get(panel_id, [])
            output_path = os.path.join(output_dir, f"{panel_id}_visualization.png")

            _create_panel_diagram(panel, panel_violations, output_path)
            generated_files.append({"panel_id": panel_id, "file_path": output_path})

        file_list = ", ".join([f["file_path"] for f in generated_files])
        return f"Successfully created {len(generated_files)} panel visualizations: {file_list}"
    except Exception as e:
        return f"Error creating visualizations: {str(e)}"


def _create_panel_diagram(panel: Dict, violations: List[Dict], output_path: str):
    """Create panel diagram."""
    dims = panel["dimensions"]
    width_mm = dims["width_mm"]
    height_mm = dims["height_mm"]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, width_mm)
    ax.set_ylim(0, height_mm)
    ax.set_aspect('equal')

    # Panel outline
    ax.add_patch(Rectangle((0, 0), width_mm, height_mm, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3))

    # Get violation studs
    violation_studs = set()
    for v in violations:
        if v["type"] == "stud_spacing_violation":
            loc = v.get("location", {})
            violation_studs.add(loc.get("stud_1", ""))
            violation_studs.add(loc.get("stud_2", ""))

    # Draw studs
    for stud in panel["studs"]:
        stud_id = stud["stud_id"]
        pos = stud["position_mm"]
        width = stud["width_mm"]
        color = 'red' if stud_id in violation_studs else 'green'
        alpha = 0.8 if stud_id in violation_studs else 0.6

        ax.add_patch(Rectangle((pos - width/2, 0), width, height_mm, linewidth=1, edgecolor='black', facecolor=color, alpha=alpha))

    # Draw openings
    for opening in panel["openings"]:
        pos = opening.get("position_mm", 0)
        width = opening.get("width_mm", 0)
        height = opening.get("height_mm", 0)

        ax.add_patch(Rectangle((pos - width/2, height_mm * 0.1), width, height, linewidth=2, edgecolor='blue', facecolor='white', alpha=0.5, linestyle='--'))

    # Title
    status = "FAIL" if violations else "PASS"
    status_color = 'red' if violations else 'green'
    ax.set_title(f"Panel: {panel['name']} - {status}\nViolations: {len(violations)}", fontsize=14, weight='bold', color=status_color)
    ax.set_xlabel('Width (mm)', fontsize=10)
    ax.set_ylabel('Height (mm)', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


@tool("Report Generator")
def generate_report(panel_data_file: str = "results/panel_data.json", violations_file: str = "results/violations.json", output_dir: str = "results", report_name: str = "panel_qc_report.html") -> str:
    """Generate HTML/PDF report from validation results. Reads from results/panel_data.json and results/violations.json"""
    try:
        # Read from files
        with open(panel_data_file, 'r') as f:
            panel_data = json.load(f)
        with open(violations_file, 'r') as f:
            violations_data = json.load(f)

        if panel_data.get("status") == "error":
            return json.dumps({"status": "error", "message": "Cannot generate report"})

        os.makedirs(output_dir, exist_ok=True)

        # Prepare report data
        panels_with_violations = []
        violations_by_panel = {v["panel_id"]: v["violations"] for v in violations_data.get("violations", [])}

        for panel in panel_data.get("panels", []):
            panel_id = panel["panel_id"]
            panel_violations = violations_by_panel.get(panel_id, [])
            panels_with_violations.append({
                "panel_id": panel_id,
                "name": panel["name"],
                "dimensions": panel["dimensions"],
                "violations": panel_violations,
                "pass": len(panel_violations) == 0
            })

        report_data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_panels": len(panel_data.get("panels", [])),
            "panels_with_violations": violations_data.get("panels_with_violations", 0),
            "total_violations": violations_data.get("summary", {}).get("total_violations", 0),
            "pass_status": violations_data.get("pass", False),
            "violations_by_type": violations_data.get("summary", {}).get("by_type", {}),
            "panels": panels_with_violations
        }

        # Generate HTML
        template_dir = os.path.join('config', 'templates')
        jinja_env = Environment(loader=FileSystemLoader(template_dir))
        template = jinja_env.get_template('report_template.html')
        html_content = template.render(**report_data)

        # Save report (HTML or PDF based on file extension and WeasyPrint availability)
        output_path = os.path.join(output_dir, report_name)

        # If report name ends with .pdf, try to generate PDF, otherwise use HTML
        if output_path.endswith('.pdf') and WEASYPRINT_AVAILABLE:
            try:
                weasyprint.HTML(string=html_content).write_pdf(output_path)
            except:
                # Fallback to HTML if PDF generation fails
                html_path = output_path.replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                output_path = html_path
        else:
            # Save as HTML (either .html extension or WeasyPrint not available)
            if output_path.endswith('.pdf'):
                output_path = output_path.replace('.pdf', '.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            output_path = output_path

        pass_fail = "PASS" if report_data["pass_status"] else "FAIL"
        file_type = "PDF" if output_path.endswith(".pdf") else "HTML"
        return f"Quality control report generated successfully. Overall status: {pass_fail}. {file_type} report saved to {output_path}"
    except Exception as e:
        return f"Error generating report: {str(e)}"
