"""
Rule Checker Tool - Validates wall panels against building codes
"""
import json
from typing import Dict, List, Any
from crewai.tools import BaseTool
import numpy as np


class RuleCheckerTool(BaseTool):
    name: str = "Rule Checker"
    description: str = (
        "Validates wall panel data against building code requirements. "
        "Checks stud spacing, opening compliance, duct clearances, and structural integrity. "
        "Returns detailed violation report with specific error locations."
    )

    def _load_building_codes(self) -> Dict[str, Any]:
        """Load building code rules from configuration"""
        try:
            with open('config/building_codes.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default codes if file not found
            return {
                "stud_spacing": {
                    "rules": {
                        "standard_spacing_mm": 406.4,
                        "tolerance_mm": 6.35
                    }
                },
                "openings": {
                    "rules": {
                        "require_jack_studs": True,
                        "require_header": True
                    }
                },
                "ducts_and_services": {
                    "rules": {
                        "min_clearance_from_stud_mm": 25.4
                    }
                }
            }

    def _run(self, panel_data_json: str) -> str:
        """
        Validate panel data against building codes

        Args:
            panel_data_json: JSON string containing panel data from parser

        Returns:
            JSON string with validation results and violations
        """
        try:
            # Load building codes
            building_codes = self._load_building_codes()

            panel_data = json.loads(panel_data_json)

            if panel_data.get("status") == "error":
                return panel_data_json

            violations = []
            panels = panel_data.get("panels", [])

            for panel in panels:
                panel_violations = self._check_panel(panel, building_codes)
                if panel_violations:
                    violations.append({
                        "panel_id": panel["panel_id"],
                        "panel_name": panel["name"],
                        "violations": panel_violations
                    })

            result = {
                "status": "success",
                "total_panels_checked": len(panels),
                "panels_with_violations": len(violations),
                "pass": len(violations) == 0,
                "violations": violations,
                "summary": self._generate_summary(violations)
            }

            return json.dumps(result, indent=2)

        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "message": "Invalid JSON input"
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Validation error: {str(e)}"
            })

    def _check_panel(self, panel: Dict[str, Any], building_codes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check a single panel for all violations"""
        violations = []

        # Check stud spacing
        violations.extend(self._check_stud_spacing(panel, building_codes))

        # Check openings
        violations.extend(self._check_openings(panel, building_codes))

        # Check ducts
        violations.extend(self._check_ducts(panel, building_codes))

        # Check panel dimensions
        violations.extend(self._check_dimensions(panel, building_codes))

        return violations

    def _check_stud_spacing(self, panel: Dict[str, Any], building_codes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate stud spacing against code requirements"""
        violations = []
        studs = panel.get("studs", [])

        if len(studs) < 2:
            return violations

        spacing_rules = building_codes["stud_spacing"]["rules"]
        standard_spacing = spacing_rules["standard_spacing_mm"]
        tolerance = spacing_rules["tolerance_mm"]

        for i in range(len(studs) - 1):
            current_stud = studs[i]
            next_stud = studs[i + 1]

            spacing = next_stud["position_mm"] - current_stud["position_mm"]
            deviation = abs(spacing - standard_spacing)

            if deviation > tolerance:
                violations.append({
                    "type": "stud_spacing_violation",
                    "severity": "high" if deviation > tolerance * 2 else "medium",
                    "description": f"Stud spacing of {spacing:.1f}mm exceeds tolerance",
                    "location": {
                        "stud_1": current_stud["stud_id"],
                        "stud_2": next_stud["stud_id"],
                        "position_mm": current_stud["position_mm"]
                    },
                    "expected": standard_spacing,
                    "actual": spacing,
                    "deviation": deviation
                })

        return violations

    def _check_openings(self, panel: Dict[str, Any], building_codes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate door/window openings for proper framing"""
        violations = []
        openings = panel.get("openings", [])
        opening_rules = building_codes["openings"]["rules"]

        for opening in openings:
            # Check for jack studs
            if opening_rules["require_jack_studs"] and not opening.get("has_jack_studs", False):
                violations.append({
                    "type": "missing_jack_studs",
                    "severity": "critical",
                    "description": f"Missing required jack studs for {opening['type']} opening",
                    "location": {
                        "opening_id": opening["opening_id"],
                        "position_mm": opening.get("position_mm", 0),
                        "width_mm": opening.get("width_mm", 0)
                    }
                })

            # Check for header
            if opening_rules["require_header"] and not opening.get("has_header", False):
                violations.append({
                    "type": "missing_header",
                    "severity": "critical",
                    "description": f"Missing required header for {opening['type']} opening",
                    "location": {
                        "opening_id": opening["opening_id"],
                        "position_mm": opening.get("position_mm", 0)
                    }
                })

        return violations

    def _check_ducts(self, panel: Dict[str, Any], building_codes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate duct clearances from studs"""
        violations = []
        ducts = panel.get("ducts", [])
        studs = panel.get("studs", [])
        duct_rules = building_codes["ducts_and_services"]["rules"]
        min_clearance = duct_rules["min_clearance_from_stud_mm"]

        for duct in ducts:
            duct_position = duct["position_mm"]
            duct_radius = duct["diameter_mm"] / 2

            # Check clearance from each stud
            for stud in studs:
                stud_position = stud["position_mm"]
                distance = abs(duct_position - stud_position)

                # Account for stud width and duct radius
                actual_clearance = distance - (stud["width_mm"] / 2) - duct_radius

                if actual_clearance < min_clearance:
                    violations.append({
                        "type": "duct_clash",
                        "severity": "high",
                        "description": f"Duct clearance of {actual_clearance:.1f}mm is below minimum {min_clearance}mm",
                        "location": {
                            "duct_id": duct["duct_id"],
                            "stud_id": stud["stud_id"],
                            "duct_position_mm": duct_position,
                            "stud_position_mm": stud_position
                        },
                        "expected_clearance": min_clearance,
                        "actual_clearance": actual_clearance
                    })

        return violations

    def _check_dimensions(self, panel: Dict[str, Any], building_codes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate overall panel dimensions"""
        violations = []
        dimensions = panel.get("dimensions", {})

        if "panel_dimensions" in building_codes:
            dim_rules = building_codes["panel_dimensions"]["rules"]

            # Check max height
            if dimensions.get("height_mm", 0) > dim_rules.get("max_height_mm", float('inf')):
                violations.append({
                    "type": "dimension_violation",
                    "severity": "medium",
                    "description": f"Panel height exceeds maximum allowed",
                    "expected": dim_rules["max_height_mm"],
                    "actual": dimensions["height_mm"]
                })

        return violations

    def _generate_summary(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics of violations"""
        summary = {
            "total_violations": 0,
            "by_type": {},
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

        for panel_violation in violations:
            for violation in panel_violation["violations"]:
                summary["total_violations"] += 1

                # Count by type
                v_type = violation["type"]
                summary["by_type"][v_type] = summary["by_type"].get(v_type, 0) + 1

                # Count by severity
                severity = violation.get("severity", "medium")
                summary["by_severity"][severity] += 1

        return summary
