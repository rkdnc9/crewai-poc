"""
LLM prompt templates for contextual analysis of wall panels.
"""


def get_context_analysis_prompt(panel_json: str, deterministic_result: dict, exceptions: dict) -> str:
    """Prompt for contextual LLM analysis of panel violations"""
    return f"""You are a building code expert reviewing a prefab wall panel.

PANEL DATA:
{panel_json}

DETERMINISTIC CHECKS RESULT:
{deterministic_result}

KNOWN EXCEPTIONS (context-dependent rules):
{exceptions}

Analyze this panel for violations that require EXPERT JUDGMENT and CONTEXT:

1. Look for edge cases deterministic checks might miss
2. Consider seismic zone and regional requirements
3. Assess if violations are intentional design choices
4. Evaluate borderline measurements (within tolerance but concerning)
5. Flag design combinations that may be problematic

Return a JSON object with:
{{
  "additional_violations": [
    {{
      "violation_id": "LLM_001",
      "element": "element name",
      "violation_type": "type",
      "severity": "critical/high/medium/low",
      "reason": "detailed explanation",
      "recommendation": "how to fix"
    }}
  ],
  "design_concerns": ["concern 1", "concern 2"],
  "needs_engineer_review": true/false,
  "summary": "brief overall assessment"
}}

Only flag real concerns, not false positives."""
