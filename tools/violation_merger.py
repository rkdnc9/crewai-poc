"""
Violation merger to combine deterministic and LLM-based check results.
"""

from typing import Dict


class ViolationMerger:
    """Merges deterministic and LLM-based violations into unified result"""

    @staticmethod
    def merge(det_result: dict, llm_result: dict) -> Dict:
        """Merge deterministic and LLM results into single report
        
        Args:
            det_result: Deterministic checker results
            llm_result: LLM analyzer results
            
        Returns:
            Merged result dictionary with all violations and analysis
        """
        det_violations = [v.get('violation_id') for v in det_result.get('violations', [])]
        llm_violations = llm_result.get('additional_violations', [])

        # Find violations LLM caught that deterministic missed
        llm_only = [v for v in llm_violations if v.get('violation_id') not in det_violations]

        # Determine final status
        total_violations = len(det_result.get('violations', [])) + len(llm_only)
        needs_review = len(llm_only) > 0 or llm_result.get('needs_engineer_review', False)
        
        if needs_review:
            final_status = "⚠️ NEEDS REVIEW"
        elif total_violations > 0:
            final_status = "❌ FAIL"
        else:
            final_status = "✅ PASS"

        merged = {
            "panel_id": det_result.get('panel_id', 'UNKNOWN'),
            "deterministic_result": det_result,
            "llm_result": llm_result,
            "llm_caught_additionally": llm_only,
            "total_violations": total_violations,
            "needs_review": needs_review,
            "final_status": final_status,
            "design_concerns": llm_result.get('design_concerns', []),
            "summary": llm_result.get('summary', 'Analysis complete')
        }

        return merged
