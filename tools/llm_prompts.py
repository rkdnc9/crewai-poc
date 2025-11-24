"""
LLM prompt templates for contextual analysis of wall panels.
"""


def get_context_analysis_prompt(panel_json: str, deterministic_result: dict, exceptions: dict, contextual_rules: str) -> str:
    """Prompt for contextual LLM analysis of panel violations
    
    Args:
        panel_json: Structured panel data as JSON string
        deterministic_result: Results from deterministic checks
        exceptions: Context-aware exceptions config
        contextual_rules: Natural language rules from contextual_rules.md
    
    Returns:
        Formatted prompt string for LLM analysis
    """
    return f"""You are a building code expert reviewing a prefab wall panel.

PANEL DATA:
{panel_json}

DETERMINISTIC CHECKS RESULT:
{deterministic_result}

KNOWN EXCEPTIONS (context-dependent rules):
{exceptions}

CONTEXTUAL INSPECTION RULES (Natural Language Guidelines):
{contextual_rules}

Analyze this panel for violations that require EXPERT JUDGMENT and CONTEXT:

1. Look for edge cases deterministic checks might miss
2. Apply the contextual inspection rules from the playbook above
3. Consider seismic zone and regional requirements
4. Assess if violations are intentional design choices
5. Evaluate borderline measurements (within tolerance but concerning)
6. Flag design combinations that may be problematic

Return a JSON object with:
{{
  "additional_violations": [
    {{
      "violation_id": "LLM_001",
      "element": "element name",
      "violation_type": "type",
      "severity": "critical/high/medium/low",
      "reason": "detailed explanation",
      "recommendation": "how to fix",
      "remediation": {{
        "steps": ["1. First action to take", "2. Second action", "3. Final verification"],
        "estimated_effort": "time estimate (e.g., 2 hours, 1 day)",
        "materials_needed": ["material 1", "material 2"],
        "tools_required": ["tool 1", "tool 2"],
        "requires_engineer_approval": true/false,
        "cost_impact": "low/medium/high",
        "safety_notes": "any safety precautions"
      }}
    }}
  ],
  "design_concerns": ["concern 1", "concern 2"],
  "needs_engineer_review": true/false,
  "summary": "brief overall assessment"
}}

Only flag real concerns, not false positives. Provide detailed, actionable remediation plans for each violation."""
