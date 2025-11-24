# Quick Reference

## Installation and Setup

```bash
uv sync
export OPENAI_API_KEY="your-api-key"
```

## Running Analysis

```bash
uv run scripts/demo.py
```

Processes test wall panels (`test_data/good_panel.ifc` and `test_data/bad_panel.ifc`) through the crew pipeline.

## Agents

| Agent                    | Purpose                                    |
| ------------------------ | ------------------------------------------ |
| QC Inspector             | Deterministic rule-based compliance checks |
| Code Consultant          | Contextual and edge case analysis          |
| Report Generator         | Synthesis of findings                      |
| Visualization Specialist | Visual representation of violations        |

## Output

- Console logs of agent execution and findings
- SVG visualizations in `demo_output/`
- Structured reports with violations and recommendations

## Project Structure

```
crew/
  agents.py          # Agent definitions
  tasks.py           # Task definitions
tools/
  ifc_parser_tool.py           # IFC file parsing
  deterministic_checker.py     # Rule-based checks
  llm_rule_checker.py          # LLM-based analysis
config/
  building_codes.json          # Building code rules
  exceptions.json              # Rule exceptions
test_data/
  good_panel.ifc               # Centered window, low seismic
  bad_panel.ifc                # Corner window, high seismic
```

## Key Files to Review

- `crew/agents.py` - Agent and tool definitions
- `crew/tasks.py` - Task specifications and workflows
- `scripts/demo.py` - Pipeline execution
