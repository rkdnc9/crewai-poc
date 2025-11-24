"""
Utility to extract structured data from CrewAI agent outputs.

CrewAI agents return text output. This utility parses that text to extract
structured violations and data for use by other agents and visualization.
"""

import json
import re
from typing import Dict, List


def extract_json_from_output(output_text: str) -> Dict:
    """
    Extract JSON from agent output text.
    
    Agents may return JSON embedded in prose. This tries to extract the JSON.
    
    Args:
        output_text: Raw text output from agent
        
    Returns:
        Parsed JSON as dictionary, or empty dict if not found
    """
    if not output_text:
        return {}
    
    # Try to find JSON block in the output
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, output_text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # If no JSON found, try the whole output
    try:
        return json.loads(output_text)
    except json.JSONDecodeError:
        return {}


def extract_violations_from_output(output_text: str) -> List:
    """
    Extract violations list from agent output.
    
    Looks for the final comprehensive report in the crew output.
    The final output is typically the last JSON block.
    
    Args:
        output_text: Raw text output from agent
        
    Returns:
        List of violation dictionaries with 'reason' and 'severity' keys
    """
    if not output_text:
        return []
    
    # Find all JSON blocks in the output
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, output_text, re.DOTALL)
    
    violations = []
    
    # Try each JSON block starting from the end (most recent/final report first)
    for match in reversed(matches):
        try:
            data = json.loads(match)
            if isinstance(data, dict):
                # Look for violations key
                if 'violations' in data and data['violations']:
                    found_violations = data['violations']
                    if found_violations:
                        return found_violations
                
                # Also check if this is a comprehensive report with violations array
                if 'all_violations' in data:
                    return data['all_violations']
        except json.JSONDecodeError:
            continue
    
    # If no structured violations found, return empty list
    return []


def merge_violations(det_violations: List, llm_violations: List) -> List:
    """
    Merge deterministic and LLM violations.
    
    Args:
        det_violations: List of deterministic violations
        llm_violations: List of LLM violations
        
    Returns:
        Merged list with source attribution
    """
    merged = []
    
    for v in det_violations:
        violation = dict(v) if isinstance(v, dict) else {'reason': str(v)}
        violation['source'] = 'deterministic'
        merged.append(violation)
    
    for v in llm_violations:
        violation = dict(v) if isinstance(v, dict) else {'reason': str(v)}
        violation['source'] = 'llm'
        merged.append(violation)
    
    return merged
