"""
Deterministic QC checker for wall panels.
Implements rule-based violations detection for explicit building code requirements.
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class Stud(BaseModel):
    """Represents a vertical stud in the panel"""
    stud_id: str
    position_mm: float
    width_mm: float
    depth_mm: float


class Opening(BaseModel):
    """Represents a door or window opening"""
    opening_id: str
    opening_type: str  # "window" or "door"
    position_mm: float  # distance from left edge
    width_mm: float
    height_mm: float
    has_jack_studs: bool
    has_header: bool
    is_corner: bool


class Duct(BaseModel):
    """Represents an MEP duct in the panel"""
    duct_id: str
    position_mm: float
    diameter_mm: float
    clearance_from_stud_mm: float


class PanelData(BaseModel):
    """Structured panel data extracted from IFC"""
    panel_id: str
    name: str
    width_mm: float
    height_mm: float
    studs: List[Stud]
    openings: List[Opening]
    ducts: List[Duct]
    seismic_zone: int


class SeverityLevel(str, Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeterministicViolation(BaseModel):
    """Represents a detected violation"""
    violation_id: str
    rule_id: str
    element: str
    violation_type: str
    severity: SeverityLevel
    expected: Optional[float] = None
    actual: Optional[float] = None
    unit: str = ""
    passed: bool
    reason: str


class DeterministicCheckResult(BaseModel):
    """Result of all deterministic checks"""
    panel_id: str
    violations: List[DeterministicViolation]
    pass_fail: bool
    summary: str

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "panel_id": self.panel_id,
            "violations": [v.dict() for v in self.violations],
            "pass_fail": self.pass_fail,
            "summary": self.summary
        }


def check_stud_spacing(panel: PanelData, rules: dict) -> List[DeterministicViolation]:
    """Verify stud spacing meets spec"""
    violations = []
    
    if "stud_spacing" not in rules or "rules" not in rules["stud_spacing"]:
        return violations
    
    spacing_rule = rules["stud_spacing"]["rules"][0]
    std_spacing = rules["stud_spacing"]["standard_spacing_mm"]
    tolerance = rules["stud_spacing"]["tolerance_mm"]

    for i in range(len(panel.studs) - 1):
        actual_spacing = panel.studs[i + 1].position_mm - panel.studs[i].position_mm
        if abs(actual_spacing - std_spacing) > tolerance:
            violations.append(DeterministicViolation(
                violation_id=f"STUD_{i}_{i + 1}",
                rule_id=spacing_rule["id"],
                element=f"Studs {panel.studs[i].stud_id} to {panel.studs[i + 1].stud_id}",
                violation_type="spacing",
                severity=SeverityLevel(spacing_rule.get("severity", "high")),
                expected=std_spacing,
                actual=actual_spacing,
                unit="mm",
                passed=False,
                reason=f"Spacing {actual_spacing}mm exceeds tolerance of ±{tolerance}mm (expected {std_spacing}mm)"
            ))
    
    return violations


def check_window_support(panel: PanelData, rules: dict) -> List[DeterministicViolation]:
    """Verify windows have required support"""
    violations = []
    
    if "openings" not in rules or "rules" not in rules["openings"]:
        return violations
    
    window_rule = rules["openings"]["rules"][0]
    threshold = window_rule["width_threshold_mm"]

    for opening in panel.openings:
        if opening.opening_type == "window" and opening.width_mm < threshold:
            if not opening.has_jack_studs or not opening.has_header:
                violations.append(DeterministicViolation(
                    violation_id=f"WINDOW_{opening.opening_id}",
                    rule_id=window_rule["id"],
                    element=opening.opening_id,
                    violation_type="support",
                    severity=SeverityLevel(window_rule.get("severity", "critical")),
                    expected=1,
                    actual=0,
                    unit="boolean",
                    passed=False,
                    reason="Window missing jack studs or header"
                ))
    
    return violations


def check_duct_clearance(panel: PanelData, rules: dict) -> List[DeterministicViolation]:
    """Verify duct clearances"""
    violations = []
    
    if "mep_clearance" not in rules or "rules" not in rules["mep_clearance"]:
        return violations
    
    clearance_rule = rules["mep_clearance"]["rules"][0]
    min_clearance = rules["mep_clearance"]["duct_to_stud_mm"]

    for duct in panel.ducts:
        if duct.clearance_from_stud_mm < min_clearance:
            violations.append(DeterministicViolation(
                violation_id=f"DUCT_{duct.duct_id}",
                rule_id=clearance_rule["id"],
                element=duct.duct_id,
                violation_type="clearance",
                severity=SeverityLevel(clearance_rule.get("severity", "high")),
                expected=min_clearance,
                actual=duct.clearance_from_stud_mm,
                unit="mm",
                passed=False,
                reason=f"Clearance {duct.clearance_from_stud_mm}mm below minimum {min_clearance}mm"
            ))
    
    return violations


def run_deterministic_checks(panel: PanelData, rules: dict) -> DeterministicCheckResult:
    """Run all deterministic checks on a panel"""
    all_violations = []
    all_violations.extend(check_stud_spacing(panel, rules))
    all_violations.extend(check_window_support(panel, rules))
    all_violations.extend(check_duct_clearance(panel, rules))

    passed = len(all_violations) == 0
    summary = f"✅ PASS" if passed else f"❌ FAIL - {len(all_violations)} violations"

    return DeterministicCheckResult(
        panel_id=panel.panel_id,
        violations=all_violations,
        pass_fail=passed,
        summary=summary
    )
