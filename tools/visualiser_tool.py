"""
Visualiser Tool - Creates visual representations of wall panels with violations marked
"""
import json
import os
from typing import Dict, List, Any
from crewai.tools import BaseTool
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle


class VisualiserTool(BaseTool):
    name: str = "Panel Visualiser"
    description: str = (
        "Creates visual representations of wall panels with code violations highlighted in red. "
        "Generates PNG images showing panel layout, studs, openings, and ducts with violations marked. "
        "Saves output to results directory."
    )

    def _run(self, panel_data_json: str, violations_json: str, output_dir: str = "results") -> str:
        """
        Create visualization of panel with violations marked

        Args:
            panel_data_json: JSON string with panel data
            violations_json: JSON string with validation results
            output_dir: Directory to save output files

        Returns:
            JSON string with paths to generated files
        """
        try:
            panel_data = json.loads(panel_data_json)
            violations_data = json.loads(violations_json)

            if panel_data.get("status") == "error":
                return json.dumps({
                    "status": "error",
                    "message": "Cannot visualize - panel data contains errors"
                })

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            generated_files = []
            panels = panel_data.get("panels", [])
            violations_by_panel = {v["panel_id"]: v["violations"]
                                  for v in violations_data.get("violations", [])}

            for panel in panels:
                panel_id = panel["panel_id"]
                panel_violations = violations_by_panel.get(panel_id, [])

                # Generate visualization
                output_path = os.path.join(output_dir, f"{panel_id}_visualization.png")
                self._create_panel_visualization(panel, panel_violations, output_path)

                generated_files.append({
                    "panel_id": panel_id,
                    "file_path": output_path,
                    "violations_count": len(panel_violations)
                })

            result = {
                "status": "success",
                "generated_files": generated_files,
                "output_directory": output_dir
            }

            return json.dumps(result, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON input: {str(e)}"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Visualization error: {str(e)}"
            })

    def _create_panel_visualization(self, panel: Dict[str, Any],
                                   violations: List[Dict[str, Any]],
                                   output_path: str):
        """Create a 2D visualization of the panel with violations marked"""

        dimensions = panel["dimensions"]
        width_mm = dimensions["width_mm"]
        height_mm = dimensions["height_mm"]

        # Create figure with appropriate aspect ratio
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, width_mm)
        ax.set_ylim(0, height_mm)
        ax.set_aspect('equal')

        # Draw panel outline
        panel_rect = Rectangle((0, 0), width_mm, height_mm,
                               linewidth=2, edgecolor='black',
                               facecolor='lightgray', alpha=0.3)
        ax.add_patch(panel_rect)

        # Collect violation locations for highlighting
        violation_studs = set()
        violation_openings = set()
        violation_ducts = set()

        for violation in violations:
            if violation["type"] == "stud_spacing_violation":
                location = violation.get("location", {})
                violation_studs.add(location.get("stud_1", ""))
                violation_studs.add(location.get("stud_2", ""))
            elif violation["type"] in ["missing_jack_studs", "missing_header"]:
                location = violation.get("location", {})
                violation_openings.add(location.get("opening_id", ""))
            elif violation["type"] == "duct_clash":
                location = violation.get("location", {})
                violation_ducts.add(location.get("duct_id", ""))
                violation_studs.add(location.get("stud_id", ""))

        # Draw studs
        for stud in panel["studs"]:
            stud_id = stud["stud_id"]
            position = stud["position_mm"]
            width = stud["width_mm"]

            # Color red if part of violation, green otherwise
            color = 'red' if stud_id in violation_studs else 'green'
            alpha = 0.8 if stud_id in violation_studs else 0.6

            stud_rect = Rectangle((position - width/2, 0), width, height_mm,
                                 linewidth=1, edgecolor='black',
                                 facecolor=color, alpha=alpha)
            ax.add_patch(stud_rect)

            # Add stud label
            ax.text(position, height_mm * 0.05, stud_id,
                   rotation=90, fontsize=6, ha='center', va='bottom')

        # Draw openings
        for opening in panel["openings"]:
            opening_id = opening["opening_id"]
            position = opening.get("position_mm", 0)
            width = opening.get("width_mm", 0)
            height = opening.get("height_mm", 0)

            # Color red if part of violation, blue otherwise
            color = 'red' if opening_id in violation_openings else 'blue'
            alpha = 0.7 if opening_id in violation_openings else 0.5

            opening_rect = Rectangle((position - width/2, height_mm * 0.1),
                                    width, height,
                                    linewidth=2, edgecolor=color,
                                    facecolor='white', alpha=alpha, linestyle='--')
            ax.add_patch(opening_rect)

            # Add opening label
            ax.text(position, height_mm * 0.1 + height/2,
                   f"{opening['type']}\n{opening_id[-6:]}",
                   fontsize=7, ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Draw ducts
        for duct in panel["ducts"]:
            duct_id = duct["duct_id"]
            position = duct["position_mm"]
            radius = duct["diameter_mm"] / 2

            # Color red if part of violation, orange otherwise
            color = 'red' if duct_id in violation_ducts else 'orange'
            alpha = 0.8 if duct_id in violation_ducts else 0.6

            duct_circle = Circle((position, height_mm * 0.5), radius,
                                linewidth=2, edgecolor=color,
                                facecolor=color, alpha=alpha)
            ax.add_patch(duct_circle)

            # Add duct label
            ax.text(position, height_mm * 0.5, 'D',
                   fontsize=8, ha='center', va='center',
                   color='white', weight='bold')

        # Add title and labels
        status = "❌ FAIL" if violations else "✓ PASS"
        status_color = 'red' if violations else 'green'

        ax.set_title(f"Panel: {panel['name']} - {status}\n"
                    f"Violations: {len(violations)}",
                    fontsize=14, weight='bold', color=status_color)
        ax.set_xlabel('Width (mm)', fontsize=10)
        ax.set_ylabel('Height (mm)', fontsize=10)

        # Add legend
        legend_elements = [
            patches.Patch(facecolor='green', alpha=0.6, label='Studs (OK)'),
            patches.Patch(facecolor='red', alpha=0.8, label='Violations'),
            patches.Patch(facecolor='blue', alpha=0.5, edgecolor='blue', label='Openings'),
            patches.Patch(facecolor='orange', alpha=0.6, label='Ducts')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
