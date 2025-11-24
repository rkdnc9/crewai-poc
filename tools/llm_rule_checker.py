"""
LLM-based rule checker for contextual analysis of wall panels.
Uses CrewAI agent to perform expert judgment on code violations.
"""

import json
from crewai import Agent, Task, Crew, Process
from tools.llm_prompts import get_context_analysis_prompt


class LLMRuleChecker:
    """Performs LLM-based contextual analysis of wall panels"""

    def __init__(self):
        """Initialize the LLM rule checker agent"""
        self.agent = Agent(
            role="Senior Building Code Consultant",
            goal="Identify design and code violations that require expert judgment",
            backstory=(
                "You are a building code expert with 20+ years in prefab construction. "
                "You understand seismic requirements, design intent, measurement tolerances, "
                "and context-dependent code rules. You catch subtle issues that automated "
                "rules miss while avoiding false positives."
            ),
            verbose=False,
            allow_delegation=False
        )

    def analyze(self, panel_data: dict, det_result: dict, exceptions: dict) -> dict:
        """Run LLM analysis on panel
        
        Args:
            panel_data: Structured panel data
            det_result: Deterministic check results
            exceptions: Context-aware exceptions config
            
        Returns:
            Dictionary with additional violations and concerns
        """
        prompt = get_context_analysis_prompt(
            json.dumps(panel_data, indent=2),
            json.dumps(det_result, indent=2),
            json.dumps(exceptions, indent=2)
        )

        task = Task(
            description=prompt,
            expected_output="JSON with additional violations and concerns",
            agent=self.agent
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()

        # Parse JSON from LLM response
        try:
            result_str = str(result)
            if "```json" in result_str:
                json_str = result_str.split("```json")[1].split("```")[0]
            elif "```" in result_str:
                json_str = result_str.split("```")[1].split("```")[0]
            else:
                json_str = result_str
            
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError, ValueError):
            # Return default structure if parsing fails
            return {
                "additional_violations": [],
                "design_concerns": [],
                "needs_engineer_review": False,
                "summary": str(result)
            }
